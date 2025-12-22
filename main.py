# main.py
from __future__ import annotations

import argparse
import fnmatch
import os
import random
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

import pathspec

if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from util.gitignore import GitIgnoreMatcher


BRANCH = "├─ "
LAST   = "└─ "
VERT   = "│  "
SPACE  = "   "

def max_items_int(v: str) -> int:
    n = int(v)
    if n < 1 or n > 10000:
        raise argparse.ArgumentTypeError(
            "--max-items must be >= 1 and <=10000 (or use --no-limit)"
        )
    return n


def get_unused_file_path(root_path: str) -> str:
    """
    Returns:
        str: an unused file ID in the root path given.
    """
    itr = 0
    while True:
        guessed_path = root_path + f"/{random.randint(100000, 999999)}"
        if not os.path.exists(guessed_path):
            return guessed_path
        elif itr >= 100000:
            raise argparse.ArgumentError(
                f"could not find unused zip path within {itr} iterations"
            )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("path", nargs="?", default=".", help="Root path")
    ap.add_argument("--max-depth", type=int, default=None)
    ap.add_argument("--all", "-a", action="store_true")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--gitignore-depth", type=int, default=None)
    ap.add_argument("--no-gitignore", action="store_true")
    ap.add_argument("--max-items", type=max_items_int, default=20, help="Limit items shown per directory (default: 20). Use --no-limit for unlimited.")
    ap.add_argument("--version", "-v", action="store_true", help="Display the version of the tool")
    ap.add_argument("--zip", nargs="?", default=None, const=get_unused_file_path(os.getcwd()), help="Create a zip file containing files under path (respects .gitignore and name defaults to a random ID)")
    ap.add_argument("--no-limit", action="store_true", help="Show all items regardless of count")
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
    max_items: Optional[int] = None,
) -> Tuple[List[Path], int]:
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

    # Handle max_items limit
    truncated = 0
    if max_items is not None and len(out) > max_items:
        truncated = len(out) - max_items
        out = out[:max_items]

    return out, truncated


def draw_tree(
    root: Path,
    *,
    max_depth: Optional[int],
    show_all: bool,
    extra_ignores: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
) -> None:
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    print(root.name)

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

        entries, truncated = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_ignores=extra_ignores,
            max_items=max_items,
        )

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1 and truncated == 0
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""
            print(prefix + connector + entry.name + suffix)

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT), depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            # truncation line is always last among displayed items
            print(prefix + LAST + f"... and {truncated} more items")

    if root.is_dir():
        rec(root, "", 0, [])


def zip_project(
    root: Path,
    *,
    zip_stem: str,
    show_all: bool,
    extra_ignores: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_depth: Optional[int],
) -> None:
    """
    Create <zip_stem>.zip with all files under root, respecting .gitignore like draw_tree().
    Note: does NOT apply max_items (that limit is only for display).
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    zip_path = Path(f"{zip_stem}.zip").resolve()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:

        def rec(dirpath: Path, depth: int, patterns: List[str]) -> None:
            if max_depth is not None and depth >= max_depth:
                return

            # extend patterns with this directory's .gitignore (same logic as draw_tree)
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

            # list entries WITHOUT max_items truncation (zip should include everything)
            entries, _ = list_entries(
                dirpath,
                root=root,
                gi=gi,
                spec=spec,
                show_all=show_all,
                extra_ignores=extra_ignores,
                max_items=None,
            )

            for entry in entries:
                if entry.is_dir():
                    rec(entry, depth + 1, patterns)
                else:
                    arcname = entry.relative_to(root).as_posix()
                    z.write(entry, arcname)

        if root.is_dir():
            rec(root, 0, [])
        else:
            # single file case
            z.write(root, root.name)


def get_project_version() -> str:
    """Return installed package version (works anywhere)."""
    try:
        from importlib.metadata import version, PackageNotFoundError  # py3.8+
        return version("PrintStruct") # or "printstruct" also usually works
    except Exception:
        return "unknown"


def main() -> None:
    args = parse_args()

    if args.version:
        print(get_project_version())
        return

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)

    # If --no-limit is set, disable max_items
    max_items = None if args.no_limit else args.max_items

    # if zipping is requested
    if args.zip is not None:
        zip_project(
            root=root,
            zip_stem=args.zip,
            show_all=args.all,
            extra_ignores=args.ignore,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_depth=args.max_depth,
        )

    # else, print the tree normally
    else:
        draw_tree(
        root=root,
        max_depth=args.max_depth,
        show_all=args.all,
        extra_ignores=args.ignore,
        respect_gitignore=not args.no_gitignore,
        gitignore_depth=args.gitignore_depth,
        max_items=max_items,
    )


if __name__ == "__main__":
    main()
