# main.py
from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import List, Optional

import pathspec


BRANCH = "├─ "
LAST   = "└─ "
VERT   = "│  "
SPACE  = "   "


class GitIgnoreMatcher:
    def __init__(self, root: Path, enabled: bool = True, *, gitignore_depth: Optional[int] = None):
        self.root = root
        self.enabled = enabled
        self.gitignore_depth = gitignore_depth

    def within_depth(self, dirpath: Path) -> bool:
        if self.gitignore_depth is None:
            return True
        try:
            return len(dirpath.relative_to(self.root).parts) <= self.gitignore_depth
        except Exception:
            return False

    def is_ignored(self, path: Path, spec: pathspec.PathSpec) -> bool:
        if not self.enabled:
            return False
        rel = path.relative_to(self.root).as_posix()
        if spec.match_file(rel):
            return True
        if path.is_dir() and spec.match_file(rel + "/"):
            return True
        return False


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("path", nargs="?", default=".", help="Root path")
    ap.add_argument("--max-depth", type=int, default=None)
    ap.add_argument("--all", "-a", action="store_true")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--gitignore-depth", type=int, default=None)
    ap.add_argument("--no-gitignore", action="store_true")
    return ap.parse_args()


def iter_dir(directory: Path) -> List[Path]:
    try:
        return list(directory.iterdir())
    except PermissionError:
        return []


def matches_extra(p: Path, root: Path, patterns: List[str]) -> bool:
    try:
        rel = p.relative_to(root).as_posix()
    except Exception:
        rel = p.name
    return any(fnmatch.fnmatchcase(rel, pat) or fnmatch.fnmatchcase(p.name, pat) for pat in patterns)


def list_entries(
    directory: Path,
    *,
    root: Path,
    gi: GitIgnoreMatcher,
    spec: pathspec.PathSpec,
    show_all: bool,
    extra_ignores: List[str],
) -> List[Path]:
    out: List[Path] = []
    for e in iter_dir(directory):
        if not show_all and e.name.startswith("."):
            continue
        if gi.is_ignored(e, spec):
            continue
        if matches_extra(e, root, extra_ignores):
            continue
        out.append(e)

    out.sort(key=lambda x: (x.is_file(), x.name.lower()))
    return out


def draw_tree(
    root: Path,
    *,
    max_depth: Optional[int],
    show_all: bool,
    extra_ignores: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
) -> None:
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    print(root.resolve())

    def rec(dirpath: Path, prefix: str, depth: int, patterns: List[str]) -> None:
        if max_depth is not None and depth >= max_depth:
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

        entries = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_ignores=extra_ignores,
        )

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""
            print(prefix + connector + entry.name + suffix)

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT), depth + 1, patterns)

    if root.is_dir():
        rec(root, "", 0, [])


def main() -> None:
    args = parse_args()
    root = Path(args.path).resolve()

    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)

    draw_tree(
        root=root,
        max_depth=args.max_depth,
        show_all=args.all,
        extra_ignores=args.ignore,
        respect_gitignore=not args.no_gitignore,
        gitignore_depth=args.gitignore_depth,
    )


if __name__ == "__main__":
    main()
