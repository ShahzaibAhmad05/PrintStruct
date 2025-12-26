from pathlib import Path
from typing import List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..services.list_enteries import list_entries
from ..constants.constant import (BRANCH, LAST, SPACE, VERT, 
                                  FILE_EMOJI, EMPTY_DIR_EMOJI, 
                                  NORMAL_DIR_EMOJI)
import pathspec
from collections import defaultdict  


def draw_tree(
    root: Path,
    *,
    depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    emoji: bool = False,
    whitelist: Optional[Set[str]] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
) -> None:
    """
    Recursively print a directory tree structure with visual formatting.

    Args:
        root (Path): Root directory path to start the tree from
        depth (Optional[int]): Maximum depth to traverse. None for unlimited
        show_all (bool): If True, include hidden files and directories
        extra_excludes (List[str]): Additional exclude patterns
        respect_gitignore (bool): If True, respect .gitignore rules
        gitignore_depth (Optional[int]): Maximum depth to search for .gitignore files
        max_items (Optional[int]): Maximum number of items to show per directory
        exclude_depth (Optional[int]): Depth limit for exclude patterns
        no_files (bool): If True, only show directories
        emoji (bool): If True, hide emoji icons in output
        whitelist (Optional[Set[str]]): Set of file paths to exclusively include
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        None: Prints tree structure to stdout
    """
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
            extra_excludes=extra_excludes,
            max_items=max_items,
            exclude_depth=exclude_depth,
            no_files=no_files,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
        )

        filtered_entries = []
        for entry in entries:
            entry_path = str(entry.absolute())
            if whitelist is not None:
                # If it's a file, it must be in the whitelist
                if entry.is_file():
                   if entry_path not in whitelist:
                       continue
                # If it's a dir, it must contain whitelisted files
                elif entry.is_dir():
                   # check if any whitelisted file starts with this dir path
                   if not any(f.startswith(entry_path) for f in whitelist):
                       continue
            filtered_entries.append(entry)
        
        entries = filtered_entries



        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1 and truncated == 0
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""
            if emoji:
                print(prefix + connector + entry.name + suffix)
            else:
                if entry.is_file():
                    emoji_str = FILE_EMOJI
                else:
                    try:
                        emoji_str = EMPTY_DIR_EMOJI if (entry.is_dir() and not any(entry.iterdir())) else NORMAL_DIR_EMOJI
                    except PermissionError:
                        emoji_str = NORMAL_DIR_EMOJI
                print(prefix + connector + emoji_str + " " + entry.name + suffix)

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT),  current_depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            # truncation line is always last among displayed items
            print(prefix + LAST + f"... and {truncated} more items")

    if root.is_dir():
        rec(root, "", 0, [])


def print_summary(
    root: Path,
    *,
    respect_gitignore: bool = True,
    gitignore_depth: Optional[int] = None,
    extra_excludes: Optional[List[str]] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
) -> None:
    """
    Print a summary showing the count of directories and files at each depth level.

    Args:
        root (Path): Root directory path to analyze
        respect_gitignore (bool): If True, respect .gitignore rules. Defaults to True
        gitignore_depth (Optional[int]): Maximum depth to search for .gitignore files
        extra_excludes (Optional[List[str]]): Additional exclude patterns
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        None: Prints summary statistics to stdout
    """
    summary = defaultdict(lambda: {"dirs": 0, "files": 0})
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    extra_excludes = extra_excludes or []

    def count(dirpath: Path, current_depth: int, patterns: List[str]):
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
            show_all=False,
            extra_excludes=extra_excludes,
            max_items=None,
            exclude_depth=None,
            no_files=False,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
        )

        for entry in entries:
            if entry.is_dir():
                summary[current_depth]["dirs"] += 1
                count(entry, current_depth + 1, patterns)
            else:
                summary[current_depth]["files"] += 1

    count(root, 0, [])

    print("\nDirectory Summary:")
    for level in sorted(summary):
        print(f"Level {level}: {summary[level]['dirs']} dirs, {summary[level]['files']} files")
