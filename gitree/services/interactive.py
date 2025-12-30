from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.styles import Style

from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import matches_file_type
from ..utilities.logger import Logger, OutputBuffer
from ..services.list_enteries import list_entries
import pathspec
import argparse


def select_files(
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
    respect_gitignore: bool = True,
    gitignore_depth: int = None,
    extra_excludes: List[str] = None,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
    include_file_types: List[str] = None,
    files_first: bool = False,
) -> Set[str]:

    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    extra_excludes = (extra_excludes or []) + (exclude_patterns or [])

    include_spec = None
    if include_patterns:
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns)

    tree: List[dict] = []
    folder_to_files: Dict[int, List[int]] = defaultdict(list)
    folder_to_subdirs: Dict[int, List[int]] = defaultdict(list)

    def collect(dirpath: Path, patterns: List[str], depth: int):
        if respect_gitignore and gi.within_depth(dirpath):
            gi_path = dirpath / ".gitignore"
            if gi_path.is_file():
                rel_dir = dirpath.relative_to(root).as_posix()
                prefix = "" if rel_dir == "." else rel_dir + "/"
                for line in gi_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    neg = line.startswith("!")
                    pat = line[1:] if neg else line
                    pat = prefix + pat.lstrip("/")
                    patterns = patterns + [("!" + pat) if neg else pat]

        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

        entries, _ = list_entries(
            dirpath,
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            gi=gi,
            spec=spec,
            show_all=False,
            extra_excludes=extra_excludes,
            max_items=None,
            exclude_depth=None,
            no_files=False,
        )

        folder_index = len(tree)
        rel_dir = dirpath.relative_to(root).as_posix() or "(root)"

        tree.append({
            "type": "dir",
            "path": rel_dir,
            "depth": depth,
            "checked": False,
        })

        for entry in entries:
            if entry.is_dir():
                child_index = len(tree)
                collect(entry, patterns, depth + 1)
                folder_to_subdirs[folder_index].append(child_index)
            else:
                rel_path = entry.relative_to(root).as_posix()

                if include_spec or include_file_types:
                    ok = False
                    if include_spec and include_spec.match_file(rel_path):
                        ok = True
                    if not ok and include_file_types:
                        ok = matches_file_type(entry, include_file_types)
                    if not ok:
                        continue

                file_index = len(tree)
                tree.append({
                    "type": "file",
                    "path": rel_path,
                    "depth": depth + 1,
                    "checked": False,
                })
                folder_to_files[folder_index].append(file_index)

    collect(root, [], 0)

    if not tree:
        return set()

    cursor = 0

    def toggle_dir(index: int, state: bool):
        tree[index]["checked"] = state

        for f in folder_to_files.get(index, []):
            tree[f]["checked"] = state

        for d in folder_to_subdirs.get(index, []):
            toggle_dir(d, state)

    def render() -> StyleAndTextTuples:
        lines: StyleAndTextTuples = []

        for i, item in enumerate(tree):
            indent = "  " * item["depth"]

            if item["checked"]:
                star = ("class:star", "[★ ] ")
            else:
                star = ("", "[ ] ")

            label = item["path"].split("/")[-1]
            if item["type"] == "dir":
                label += "/"

            cursor_style = "class:cursor" if i == cursor else ""

            lines.append((cursor_style, indent))
            lines.append(star)
            lines.append((cursor_style, label + "\n"))

        return lines


    kb = KeyBindings()

    @kb.add("up")
    def _(e):
        nonlocal cursor
        cursor = max(0, cursor - 1)

    @kb.add("down")
    def _(e):
        nonlocal cursor
        cursor = min(len(tree) - 1, cursor + 1)

    @kb.add(" ")
    def _(e):
        item = tree[cursor]
        new_state = not item["checked"]

        if item["type"] == "dir":
            toggle_dir(cursor, new_state)
        else:
            item["checked"] = new_state

    @kb.add("enter")
    def _(e):
        e.app.exit()

    style = Style.from_dict({
        "star": "fg:green",
        "cursor": "reverse",
    })

    @kb.add("c-c")
    def _(e):
        e.app.exit()



    app = Application(
        layout=Layout(Window(FormattedTextControl(render))),
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    app.run()

    return {
        str(root / item["path"])
        for item in tree
        if item["type"] == "file" and item["checked"]
    }


def get_interactive_file_selection(
    *,
    roots: List[Path],
    output_buffer: OutputBuffer,
    logger: Logger,
    args: argparse.Namespace,
) -> dict:

    selected_files_map = {}

    for root in roots:
        selected = select_files(
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            extra_excludes=args.exclude,
            exclude_patterns=args.exclude,
            include_patterns=args.include,
            include_file_types=args.include_file_types,
        )
        if selected:
            selected_files_map[root] = selected

    return selected_files_map
