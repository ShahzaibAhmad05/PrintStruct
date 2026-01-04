# gitree/services/tree_service.py
import sys
from pathlib import Path
from typing import List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from .list_enteries import list_entries
from ..utilities.logger import Logger, OutputBuffer
from ..utilities.utils import copy_to_clipboard
from ..constants.constant import (BRANCH, LAST, SPACE, VERT,
                                  FILE_EMOJI, EMPTY_DIR_EMOJI,
                                  NORMAL_DIR_EMOJI)
from ..utilities.colors import colorize_text
from .tree_formatting_service import write_exports, build_tree_data, format_markdown_tree, format_json, format_text_tree
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
    max_entries: Optional[int] = None,
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
        output_buffer (OutputBuffer): Buffer to write Export to
        logger (Logger): Logger instance for logging
        depth (Optional[int]): Maximum depth to traverse. None for unlimited
        show_all (bool): If True, include hidden files and directories
        extra_excludes (List[str]): Additional exclude patterns
        respect_gitignore (bool): If True, respect .gitignore rules
        gitignore_depth (Optional[int]): Maximum depth to search for .gitignore files
        max_items (Optional[int]): Maximum number of items to show per directory
        max_entries (Optional[int]): Maximum number of entries to show
        exclude_depth (Optional[int]): Depth limit for exclude patterns
        no_files (bool): If True, only show directories
        emoji (bool): If True, show emoji icons in Export
        no_color (bool): If True, disable colorized Export
        whitelist (Optional[Set[str]]): Set of file paths to exclusively include
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        None: Prints tree structure to stdout
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    output_buffer.write(root.name)
    entries = 1
    truncation_prefix = None

    # Track if any files matched include patterns for warning messages
    files_matched_include_patterns = False
    files_matched_include_types = False

    def rec(dirpath: Path, prefix: str, current_depth: int, patterns: List[str]) -> None:
        nonlocal files_matched_include_patterns, files_matched_include_types
        nonlocal entries, truncation_prefix
        
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

        entry_list, truncated = list_entries(
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

        # Track if any files matched include patterns
        if include_patterns:
            include_spec_check = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns)
            for entry in entry_list:
                if entry.is_file():
                    rel_path = entry.relative_to(root).as_posix()
                    if include_spec_check.match_file(rel_path):
                        files_matched_include_patterns = True
                        break

        if include_file_types:
            from ..utilities.utils import matches_file_type
            for entry in entry_list:
                if entry.is_file():
                    if matches_file_type(entry, include_file_types):
                        files_matched_include_types = True
                        break

        filtered_entries = []
        for entry in entry_list:
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

        entry_list = filtered_entries



        for i, entry in enumerate(entry_list):
            if max_entries is not None and entries >= max_entries:
                if truncation_prefix is None:
                    truncation_prefix = prefix
                
                entries += 1
                if entry.is_dir():
                    rec(entry, prefix + SPACE, current_depth + 1, patterns)
                continue

            is_last = i == len(entry_list) - 1 and truncated == 0
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
            
            entries += 1

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT),  current_depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            if max_entries is not None and entries >= max_entries:
                if truncation_prefix is None:
                    truncation_prefix = prefix
                entries += 1
            else:
                # truncation line is always last among displayed items
                output_buffer.write(prefix + LAST + f"... and {truncated} more items")
                entries += 1

    if root.is_dir():
        rec(root, "", 0, [])


    # Print warnings to stderr if include patterns/types were specified but no files matched
    if include_patterns and not files_matched_include_patterns:
        patterns_str = ", ".join(include_patterns)
        print(f"Warning: No files found matching --include patterns: {patterns_str}", file=sys.stderr)

    if include_file_types and not files_matched_include_types:
        types_str = ", ".join(include_file_types)
        print(f"Warning: No files found matching --include-file-types: {types_str}", file=sys.stderr)
        
    if truncation_prefix is not None:
        remaining = entries - max_entries
        output_buffer.write(truncation_prefix + LAST + f"... and {remaining} more entries")


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

        # Determine max_entries based on flags
        max_entries = args.max_entries
        if args.no_max_entries:
            max_entries = None

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
            max_entries=max_entries,
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

    # Write to output file if requested
    if args.export is not None:
        # If format is tree, write whatever was drawn to the buffer.
        if args.format == "tree":
            content = output_buffer.get_value()

        else:
            # For json/md we must build structured tree data (not the unicode rendering)
            include_contents = not args.no_contents

            # NOTE: keeps previous behavior: export uses last processed root
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
                max_entries=args.max_entries,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=args.include_file_types,
                include_contents=include_contents,
                no_contents_for=args.no_contents_for
            )

            if args.format:
                if args.format == "md":
                    content = format_markdown_tree(tree_data, include_contents=True)
                elif args.format == "txt":
                    content = format_text_tree(tree_data, include_contents=True)
                elif args.format == "json":
                    content = format_json(tree_data)
            else:
                # fallback safety
                content = output_buffer.get_value()

        with open(args.export, "w", encoding="utf-8") as f:
            f.write(content)


    if args.copy:
        # Copy the formatted Export, not always the unicode tree
        content_to_copy = output_buffer.get_value()
        if args.format in ("json", "md"):

            include_contents = not args.no_contents

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
                max_entries=args.max_entries,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=args.include_file_types,
                include_contents=include_contents,
                no_contents_for=args.no_contents_for
            )

            if args.format == "json":
                content_to_copy = format_json(tree_data)
            elif args.format == "md":
                content_to_copy = format_markdown_tree(tree_data, include_contents=include_contents)
            elif args.format == "txt":
                content_to_copy = format_text_tree(tree_data, include_contents=include_contents)
            else:
                content_to_copy = format_text_tree(tree_data, include_contents=include_contents)



        if not copy_to_clipboard(content_to_copy, logger=logger):
            output_buffer.write(
                "Warning: Could not copy to clipboard. "
                "Please install a clipboard utility (xclip, wl-copy) "
                "or ensure your environment supports it."
            )
        else:
            output_buffer.clear()
            logger.log(logger.INFO, "Tree Export copied to clipboard successfully.")
