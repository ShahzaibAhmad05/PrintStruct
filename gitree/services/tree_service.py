# gitree/services/tree_service.py

"""
Code file for the tree drawing service used in main. This might
just be wrapped into a class later.
"""

# Default libs
import sys
from pathlib import Path

# Dependencies
import pathspec

# Deps from this project
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.logger import Logger
from ..utilities.utils import copy_to_clipboard
from ..constants.constant import (BRANCH, LAST, SPACE, VERT, FILE_EMOJI, 
    EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI)
from ..utilities.colors import colorize_text
from ..objects.config import Config
from ..objects.app_context import AppContext
from .list_enteries import list_entries
from .tree_formatting_service import (build_tree_data, 
    format_markdown_tree, format_json, format_text_tree)


def draw_tree(ctx: AppContext, config: Config, root: Path) -> None:
    """
    Recursively store a directory tree structure with visual formatting
    to the output_buffer in app ctx.

    Args:
        ctx (AppContext): The app context to be used by the function
        config (Config): Config object containing the configuration
        root (Path): Root directory path to start the tree from
    """

    gi = GitIgnoreMatcher(ctx, config, root)

    ctx.output_buffer.write(root.name)
    entries = 1
    truncation_prefix = None

    # Track if any files matched include patterns for warning messages
    files_matched_include_patterns = False
    files_matched_include_types = False

    def rec(dirpath: Path, prefix: str, current_depth: int, patterns: list[str]) -> None:
        nonlocal files_matched_include_patterns, files_matched_include_types
        nonlocal entries, truncation_prefix
        
        if config.max_depth is not None and current_depth >= config.max_depth:
            return

        if not config.no_gitignore and gi.within_depth(dirpath):
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

        entry_list, truncated = list_entries(ctx, config, dirpath, root, gi, spec)

        # Track if any files matched include patterns
        if config.include:
            include_spec_check = pathspec.PathSpec.from_lines("gitwildmatch", config.include)
            for entry in entry_list:
                if entry.is_file():
                    rel_path = entry.relative_to(root).as_posix()
                    if include_spec_check.match_file(rel_path):
                        files_matched_include_patterns = True
                        break

        if config.include_file_types:
            from ..utilities.utils import matches_file_type
            for entry in entry_list:
                if entry.is_file():
                    if matches_file_type(entry, config.include_file_types):
                        files_matched_include_types = True
                        break

        filtered_entries = []
        for entry in entry_list:
            entry_path = str(entry.absolute())
            if config.include:
                # If it's a file, it must be in the whitelist
                if entry.is_file():
                   if entry_path not in config.include:
                       continue
                # If it's a dir, it must contain whitelisted files
                elif entry.is_dir():
                   # check if any whitelisted file starts with this dir path
                   if not any(f.startswith(entry_path) for f in config.include):
                       continue
            filtered_entries.append(entry)

        entry_list = filtered_entries



        for i, entry in enumerate(entry_list):
            if config.max_entries is not None and entries >= config.max_entries:
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
            if not config.no_color:
                entry_name = colorize_text(entry_name, is_directory=entry.is_dir(), is_hidden=is_hidden)

            if not config.emoji:
                ctx.output_buffer.write(prefix + connector + entry_name)
            else:
                if entry.is_file():
                    emoji_str = FILE_EMOJI
                else:
                    try:
                        emoji_str = EMPTY_DIR_EMOJI if (entry.is_dir() and not any(entry.iterdir())) else NORMAL_DIR_EMOJI
                    except PermissionError:
                        emoji_str = NORMAL_DIR_EMOJI
                ctx.output_buffer.write(prefix + connector + emoji_str + " " + entry.name + suffix)
            
            entries += 1

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT),  current_depth + 1, patterns)

        # Show truncation message if items were hidden
        if truncated > 0:
            if config.max_entries is not None and entries >= config.max_entries:
                if truncation_prefix is None:
                    truncation_prefix = prefix
                entries += 1
            else:
                # truncation line is always last among displayed items
                ctx.output_buffer.write(prefix + LAST + f"... and {truncated} more items")
                entries += 1

    if root.is_dir():
        rec(root, "", 0, [])


    # Print warnings to stderr if include patterns/types were specified but no files matched
    if config.include and not files_matched_include_patterns:
        patterns_str = ", ".join(config.include)
        print(f"Warning: No files found matching --include patterns: {patterns_str}", file=sys.stderr)

    if config.include_file_types and not files_matched_include_types:
        types_str = ", ".join(config.include_file_types)
        print(f"Warning: No files found matching --include-file-types: {types_str}", file=sys.stderr)
        
    if truncation_prefix is not None:
        remaining = entries - config.max_entries
        ctx.output_buffer.write(truncation_prefix + LAST + f"... and {remaining} more entries")


def run_tree_mode(ctx: AppContext, config: Config, roots: list[Path],
    selected_files_map: dict | None = None) -> None:
    """
    Run the normal tree-printing workflow.
    """

    for i, root in enumerate(roots):
        # Interactive mode handled in main.py now
        selected_files = selected_files_map.get(root)
        # Add header for multiple paths
        if len(roots) > 1:
            if i > 0:
                ctx.output_buffer.write("")  # Empty line between trees
            ctx.output_buffer.write(str(root))

        # Determine max_entries based on flags
        if config.no_max_entries:
            config.max_entries = None

        draw_tree(ctx, config, root)

    # Write to output file if requested
    if config.export is not None:
        # If format is tree, write whatever was drawn to the buffer.
        if config.format == "tree":
            content = ctx.output_buffer.get_value()

        else:
            # For json/md we must build structured tree data (not the unicode rendering)
            include_contents = not config.no_contents

            # NOTE: keeps previous behavior: export uses last processed root
            tree_data = build_tree_data(ctx, config, root)

            if config.format:
                if config.format == "md":
                    content = format_markdown_tree(tree_data, include_contents=True)
                elif config.format == "txt":
                    content = format_text_tree(tree_data, include_contents=True)
                elif config.format == "json":
                    content = format_json(tree_data)
            else:
                # fallback safety
                content = ctx.output_buffer.get_value()

        with open(config.export, "w", encoding="utf-8") as f:
            f.write(content)


    if config.copy:
        # Copy the formatted Export, not always the unicode tree
        content_to_copy = ctx.output_buffer.get_value()
        if config.format in ("json", "md"):

            include_contents = not config.no_contents

            tree_data = build_tree_data(ctx, config, root)

            if config.format == "json":
                content_to_copy = format_json(tree_data)
            elif config.format == "md":
                content_to_copy = format_markdown_tree(tree_data, include_contents=include_contents)
            elif config.format == "txt":
                content_to_copy = format_text_tree(tree_data, include_contents=include_contents)
            else:
                content_to_copy = format_text_tree(tree_data, include_contents=include_contents)


        if not copy_to_clipboard(content_to_copy, logger=ctx.logger):
            ctx.output_buffer.write(
                "Warning: Could not copy to clipboard. "
                "Please install a clipboard utility (xclip, wl-copy) "
                "or ensure your environment supports it."
            )
        else:
            ctx.output_buffer.clear()
            ctx.logger.log(ctx.logger.INFO, "Tree Export copied to clipboard successfully.")
