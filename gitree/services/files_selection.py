# gitree/services/selection.py
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Set

import pathspec, questionary

from ..utilities.gitignore import GitIgnoreMatcher
from ..services.list_enteries import list_entries


def collect_candidate_files(
    *,
    root: Path,
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    exclude_depth: Optional[int],
    no_files: bool,
    include_patterns: List[str],
    include_file_types: List[str],
    depth: Optional[int],
) -> List[str]:
    """
    Traverse root once and return candidate *file* paths (relative to root, POSIX style)
    after applying gitignore/exclude/include/no_files/hidden filters.
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    rel_files: List[str] = []

    def rec(dirpath: Path, current_depth: int, patterns: List[str]) -> None:
        if depth is not None and current_depth >= depth:
            return

        # extend patterns with this directory's .gitignore (same logic as draw_tree/zip_project)
        if respect_gitignore and gi.within_depth(dirpath):
            gi_path = dirpath / ".gitignore"
            if gi_path.is_file():
                rel_dir = dirpath.relative_to(root).as_posix()
                prefix_path = "" if rel_dir == "." else rel_dir + "/"
                for line in gi_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    neg = line.startswith("!")
                    pat = line[1:] if neg else line
                    pat = prefix_path + pat.lstrip("/")
                    patterns = patterns + [("!" + pat) if neg else pat]

        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

        entries, _ = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_excludes=extra_excludes,
            max_items=None,  # IMPORTANT: selection should not truncate
            exclude_depth=exclude_depth,
            no_files=no_files,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
        )

        for entry in entries:
            if entry.is_dir():
                rec(entry, current_depth + 1, patterns)
            else:
                rel_files.append(entry.relative_to(root).as_posix())

    if root.is_dir():
        rec(root, 0, [])
    else:
        # single file root case
        if not no_files:
            rel_files.append(root.name)

    return rel_files


def resolve_selected_files(
    *,
    root: Path,
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    exclude_depth: Optional[int],
    no_files: bool,
    include_patterns: List[str],
    include_file_types: List[str],
    depth: Optional[int],
    interactive: bool,
) -> Set[str]:
    """
    Returns the final set of selected file paths relative to root (POSIX style).
    If interactive=True, prompts the user to choose from the candidates.
    """
    candidates = collect_candidate_files(
        root=root,
        respect_gitignore=respect_gitignore,
        gitignore_depth=gitignore_depth,
        show_all=show_all,
        extra_excludes=extra_excludes,
        exclude_depth=exclude_depth,
        no_files=no_files,
        include_patterns=include_patterns,
        include_file_types=include_file_types,
        depth=depth,
    )

    if not candidates:
        return set()

    if not interactive:
        return set(candidates)

    choices = [questionary.Choice(rel, checked=True) for rel in candidates]
    selected = questionary.checkbox("Select files to include:", choices=choices).ask()
    if selected is None:
        return set()
    return set(selected)
