from pathlib import Path
from typing import List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from .list_enteries import list_entries
from ..utilities.logger import Logger, OutputBuffer
from ..utilities.utils import copy_to_clipboard
from ..utilities.colors import colorize_text
from ..constants.constant import (BRANCH, LAST, SPACE, VERT,
                                  FILE_EMOJI, EMPTY_DIR_EMOJI,
                                  NORMAL_DIR_EMOJI)
import pathspec
from collections import defaultdict


def draw_tree(
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
    depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
    max_lines: Optional[int] = None,
    no_limit: bool = False,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    emoji: bool = False,
    no_color: bool = False,
    whitelist: Optional[Set[str]] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
    files_first: bool = False,
) -> None:
    """
    Recursively print a directory tree structure with visual formatting.

    Args:
        root (Path): Root directory path to start the tree from
        output_buffer (OutputBuffer): Buffer to write output to
        logger (Logger): Logger instance for logging
        depth (Optional[int]): Maximum depth to traverse. None for unlimited
        show_all (bool): If True, include hidden files and directories
        extra_excludes (List[str]): Additional exclude patterns
        respect_gitignore (bool): If True, respect .gitignore rules
        gitignore_depth (Optional[int]): Maximum depth to search for .gitignore files
        max_items (Optional[int]): Maximum number of items to show per directory
        max_lines (Optional[int]): Maximum number of lines to show
        exclude_depth (Optional[int]): Depth limit for exclude patterns
        no_files (bool): If True, only show directories
        emoji (bool): If True, show emoji icons in output
        no_color (bool): If True, disable colorized output
        whitelist (Optional[Set[str]]): Set of file paths to exclusively include
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        None: Prints tree structure to stdout
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    output_buffer.write(root.name)
    lines = 1
    truncation_prefix = None

    def rec(dirpath: Path, prefix: str, current_depth: int, patterns: List[str]) -> None:
        nonlocal lines, truncation_prefix
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
            output_buffer=output_buffer,
            logger=logger,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_excludes=extra_excludes,
            max_items=max_items,
            no_limit=no_limit,
            exclude_depth=exclude_depth,
            no_files=no_files,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
            files_first=files_first,
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
            if max_lines is not None and lines >= max_lines:
                if truncation_prefix is None:
                    truncation_prefix = prefix
                
                lines += 1
                if entry.is_dir():
                    rec(entry, prefix + SPACE, current_depth + 1, patterns)
                continue

            is_last = i == len(entries) - 1 and truncated == 0
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""

            # Determine if item is hidden (starts with .)
            is_hidden = entry.name.startswith(".")

            # Apply color to entry name if colors are enabled
            entry_name = entry.name + suffix
            if not no_color:
                entry_name = colorize_text(entry_name, is_directory=entry.is_dir(), is_hidden=is_hidden)

            if not emoji:
                output_buffer.write(prefix + connector + entry_name)
            else:
                if entry.is_file():
                    emoji_str = FILE_EMOJI
                else:
                    try:
                        emoji_str = EMPTY_DIR_EMOJI if (entry.is_dir() and not any(entry.iterdir())) else NORMAL_DIR_EMOJI
                    except PermissionError:
                        emoji_str = NORMAL_DIR_EMOJI
                output_buffer.write(prefix + connector + emoji_str + " " + entry.name + suffix)
            
            lines += 1

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT),  current_depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            if max_lines is not None and lines >= max_lines:
                if truncation_prefix is None:
                    truncation_prefix = prefix
                lines += 1
            else:
                # truncation line is always last among displayed items
                output_buffer.write(prefix + LAST + f"... and {truncated} more items")
                lines += 1

    if root.is_dir():
        rec(root, "", 0, [])

    if truncation_prefix is not None:
        remaining = lines - max_lines
        output_buffer.write(truncation_prefix + LAST + f"... and {remaining} more lines")


def print_summary(
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
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
        output_buffer (OutputBuffer): Buffer to write output to
        logger (Logger): Logger instance for logging
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

    output_buffer.write("\nDirectory Summary:")
    for level in sorted(summary):
        output_buffer.write(f"Level {level}: {summary[level]['dirs']} dirs, {summary[level]['files']} files")


def run_tree_mode(
    args,
    roots: List[Path],
    output_buffer,
    logger,
    selected_files_map: Optional[dict] = None
) -> None:
    """
    Run the normal tree-printing workflow (non-zip mode).
    """
    selected_files_map = selected_files_map or {}

    for i, root in enumerate(roots):
        # Interactive mode handled in main.py now
        selected_files = selected_files_map.get(root)

        # Add header for multiple paths
        if len(roots) > 1:
            if i > 0:
                output_buffer.write("")  # Empty line between trees
            output_buffer.write(str(root))

        # Determine max_lines based on flags
        max_lines = args.max_lines
        if args.no_max_lines:
            max_lines = None

        draw_tree(
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            depth=args.max_depth,
            show_all=args.hidden_items,
            extra_excludes=args.exclude,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_items=args.max_items,
            max_lines=max_lines,
            no_limit=args.no_limit,
            exclude_depth=args.exclude_depth,
            no_files=args.no_files,
            emoji=args.emoji,
            no_color=args.no_color,
            whitelist=selected_files,
            include_patterns=args.include,
            include_file_types=args.include_file_types,
            files_first=args.files_first,
        )

        if args.summary:
            print_summary(
                root=root,
                output_buffer=output_buffer,
                logger=logger,
                respect_gitignore=not args.no_gitignore,
                gitignore_depth=args.gitignore_depth,
                extra_excludes=args.exclude,
                include_patterns=args.include,
                include_file_types=args.include_file_types,
            )

    # Write to output file if requested
    if args.output is not None:
        content = output_buffer.get_value()

        if args.output.endswith(".md"):
            content = f"```\n{content}```\n"

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)

    # Copy to clipboard if requested
    if args.copy:
        if not copy_to_clipboard(output_buffer.get_value(), logger=logger):
            output_buffer.write(
                "Warning: Could not copy to clipboard. "
                "Please install a clipboard utility (xclip, wl-copy) "
                "or ensure your environment supports it."
            )
        else:
            output_buffer.clear()
            logger.log(logger.INFO, "Tree output copied to clipboard successfully.")

    # Handle file exports
    if args.json or args.txt or args.md:
        from .tree_formatting_service import build_tree_data, write_outputs

        include_contents = not args.no_contents

        # NOTE: exports use the last processed root (matches previous behavior)
        tree_data = build_tree_data(
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            depth=args.max_depth,
            show_all=args.hidden_items,
            extra_excludes=args.exclude,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_items=args.max_items,
            max_lines=args.max_lines,
            exclude_depth=args.exclude_depth,
            no_files=args.no_files,
            whitelist=selected_files,
            include_patterns=args.include,
            include_file_types=args.include_file_types,
            include_contents=include_contents,
            no_contents_for=args.no_contents_for
        )

        write_outputs(
            logger=logger,
            tree_data=tree_data,
            json_path=args.json,
            txt_path=args.txt,
            md_path=args.md,
            emoji=args.emoji,
            include_contents=include_contents,
        )
