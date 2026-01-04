# gitree/services/interactive.py

"""
Interactive file selection UI for gitree.

This module provides a full-screen terminal UI that allows users to
interactively select files from a project directory using a hierarchical
(tree-like) view.
"""

# Default libs
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict

# Dependencies
import pathspec
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.styles import Style

# Deps from this project
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import matches_file_type
from ..services.list_enteries import list_entries
from ..objects.app_context import AppContext
from ..objects.config import Config


def select_files(ctx: AppContext, config: Config, root: Path) -> Set[str]:
    """
    Launch an interactive terminal UI for selecting files under a root directory.

    The UI presents a hierarchical tree of directories and files. Users can:
    - Navigate using ↑ / ↓
    - Select or deselect items using Space
    - Select a directory to recursively select all contents
    - Refine the selection by deselecting individual files
    - Confirm with Enter or exit with Ctrl+C

    Returns:
        A set of absolute file paths selected by the user.
    """

    gi = GitIgnoreMatcher(ctx, config, root)
    include_spec = pathspec.PathSpec.from_lines("gitwildmatch", config.include)

    # Flat list representing the tree in render order
    tree: List[dict] = []

    # Mapping from directory index -> file indices
    folder_to_files: Dict[int, List[int]] = defaultdict(list)

    # Mapping from directory index -> subdirectory indices
    folder_to_subdirs: Dict[int, List[int]] = defaultdict(list)


    def collect(dirpath: Path, patterns: List[str], depth: int):
        """
        Recursively walk the directory tree and populate the UI tree structure.

        This function:
        - Applies gitignore rules
        - Applies include/exclude filters
        - Records directory and file relationships for recursive selection
        """

        if not config.no_gitignore and gi.within_depth(dirpath):
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

        entries, _ = list_entries(ctx, config, dirpath, root=root, gi=gi, spec=spec)

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

                if include_spec or config.include_file_types:
                    ok = False
                    if include_spec and include_spec.match_file(rel_path):
                        ok = True
                    if not ok and config.include_file_types:
                        ok = matches_file_type(entry, config.include_file_types)
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
        """
        Recursively toggle a directory and all its contents.

        This updates:
        - The directory itself
        - All files under it
        - All nested subdirectories and their files
        """
        tree[index]["checked"] = state
        for f in folder_to_files.get(index, []):
            tree[f]["checked"] = state
        for d in folder_to_subdirs.get(index, []):
            toggle_dir(d, state)


    def render_header() -> StyleAndTextTuples:
        """Render the fixed instruction bar at the top of the UI."""
        return [
            ("class:hint", "↑/↓ "),
            ("class:hint", "Move"),
            ("class:hint", "   |   "),
            ("class:hint", "Space "),
            ("class:hint", "Toggle"),
            ("class:hint", "   |   "),
            ("class:hint", "Enter "),
            ("class:hint", "Confirm"),
            ("class:hint", "   |   "),
            ("class:hint", "Ctrl+C "),
            ("class:hint", "Exit\n"),
        ]


    def render_tree() -> StyleAndTextTuples:
        """Render the file/directory tree with indentation and selection markers."""
        lines: StyleAndTextTuples = []

        for i, item in enumerate(tree):
            indent = "  " * item["depth"]

            if item["checked"]:
                star = ("class:star", "[ ✓ ] ")
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

    @kb.add("c-c")
    def _(e):
        e.app.exit()

    style = Style.from_dict({
        "star": "fg:green",
        "cursor": "reverse",
        "hint": "fg:#888888",
    })

    app = Application(
        layout=Layout(
            HSplit([
                Window(
                    FormattedTextControl(render_header),
                    height=1,
                    dont_extend_height=True,
                ),
                Window(
                    FormattedTextControl(render_tree),
                ),
            ])
        ),
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


def get_interactive_file_selection(ctx: AppContext, config: Config, roots: List[Path]) -> dict:
    """
    Run the interactive file selection UI for one or more root directories.

    This function acts as the public entry point used by the CLI.
    It delegates the UI to `select_files` and aggregates the results.

    Returns:
        A mapping of root directory -> selected file paths.
    """

    selected_files_map = {}

    for root in roots:
        selected = select_files(ctx, config, root)
        if selected:
            selected_files_map[root] = selected

    return selected_files_map
