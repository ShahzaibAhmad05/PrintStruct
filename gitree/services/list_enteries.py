from typing import List, Optional, Tuple
from pathlib import Path
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import iter_dir, matches_extra
import pathspec


def list_entries(
    directory: Path,
    *,
    root: Path,
    gi: GitIgnoreMatcher,
    spec: pathspec.PathSpec,
    show_all: bool,
    extra_ignores: List[str],
    max_items: Optional[int] = None,
    ignore_depth: Optional[int] = None,
    no_files: bool = False,
) -> Tuple[List[Path], int]:
    out: List[Path] = []
    for e in iter_dir(directory):
        if not show_all and e.name.startswith("."):
            continue
        if gi.is_ignored(e, spec):
            continue
        if matches_extra(e, root, extra_ignores, ignore_depth):
            continue
        # Filter based on --no-files
        if no_files and e.is_file():
            continue
        out.append(e)

    out.sort(key=lambda x: (x.is_file(), x.name.lower()))

    # Handle max_items limit
    truncated = 0
    if max_items is not None and len(out) > max_items:
        truncated = len(out) - max_items
        out = out[:max_items]

    return out, truncated
