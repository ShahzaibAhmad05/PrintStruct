from pathlib import Path
from typing import List, Optional
from ..utilities.gitignore import GitIgnoreMatcher
from ..services.list_enteries import list_entries
from ..constants.constant import BRANCH, LAST, SPACE, VERT
import pathspec


def draw_tree(
    root: Path,
    *,
    depth: Optional[int],
    show_all: bool,
    extra_ignores: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
    ignore_depth: Optional[int] = None,
) -> None:
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    print(root.name)

    def rec(dirpath: Path, prefix: str, current_depth: int, patterns: List[str]) -> None:
        if depth is not None and current_depth >= depth:
            return

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

        entries, truncated = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_ignores=extra_ignores,
            max_items=max_items,
            ignore_depth=ignore_depth,
        )

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1 and truncated == 0
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""
            print(prefix + connector + entry.name + suffix)

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT),  current_depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            # truncation line is always last among displayed items
            print(prefix + LAST + f"... and {truncated} more items")

    if root.is_dir():
        rec(root, "", 0, [])
        