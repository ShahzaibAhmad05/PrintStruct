from typing import List, Optional, Tuple
from pathlib import Path
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import iter_dir, matches_extra, matches_file_type
from ..utilities.logger import Logger, OutputBuffer
import pathspec


def list_entries(
    directory: Path,
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
    gi: GitIgnoreMatcher,
    spec: pathspec.PathSpec,
    show_all: bool,
    extra_excludes: List[str],
    max_items: Optional[int] = None,
    max_lines: Optional[int] = None,
    no_limit: bool = False,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
    files_first: bool = False,
) -> Tuple[List[Path], int]:
    """
    List and filter directory entries based on various criteria.

    Args:
        directory (Path): Directory to list entries from
        root (Path): Root directory for relative path calculations
        output_buffer (OutputBuffer): Buffer to write output to
        logger (Logger): Logger instance for logging
        gi (GitIgnoreMatcher): GitIgnore matcher instance
        spec (pathspec.PathSpec): Pathspec for gitignore patterns
        show_all (bool): If True, include hidden files
        extra_excludes (List[str]): Additional exclude patterns
        max_items (Optional[int]): Maximum number of items to return
        max_lines (Optional[int]): Maximum number of lines to return
        exclude_depth (Optional[int]): Depth limit for exclude patterns
        no_files (bool): If True, exclude files from results
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        Tuple[List[Path], int]: Tuple of (filtered paths list, count of truncated items)
    """
    out: List[Path] = []

    # Compile include pattern spec if provided
    include_spec = None
    if include_patterns:
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns)

    for e in iter_dir(directory):
        if not show_all and e.name.startswith("."):
            continue

        # Check for forced inclusion (overrides gitignore and other filters)
        is_force_included = False
        if include_spec or include_file_types:
            if e.is_file():
                if include_spec:
                    rel_path = e.relative_to(root).as_posix()
                    if include_spec.match_file(rel_path):
                        is_force_included = True

                if not is_force_included and include_file_types:
                    if matches_file_type(e, include_file_types):
                        is_force_included = True
            elif e.is_dir():
                if include_spec:
                    rel_path = e.relative_to(root).as_posix()
                    # Check if the directory itself matches the pattern
                    if include_spec.match_file(rel_path):
                        is_force_included = True
        
        if is_force_included:
            out.append(e)
            continue
        
        # Normal filters
        if gi.is_ignored(e, spec):
            continue
        if matches_extra(e, root, extra_excludes, exclude_depth):
            continue
        # Filter based on --no-files
        if no_files and e.is_file():
            continue

        out.append(e)

    if files_first:
        # Sort files first (is_file() is True/1, is_dir() is False/0)
        # We use -x.is_file() because True (1) comes after False (0)
        # in ascending sorts, so we negate it to put files at the top.
        out.sort(key=lambda x: (-x.is_file(), x.name.lower()))
    else:
        # Default: Directories first
        out.sort(key=lambda x: (x.is_file(), x.name.lower()))

    # Handle max_items limit
    truncated = 0
    if not no_limit and max_items is not None and len(out) > max_items:
        truncated = len(out) - max_items
        out = out[:max_items]

    return out, truncated
