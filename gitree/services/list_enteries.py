from typing import List, Optional, Tuple
from pathlib import Path
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import iter_dir, matches_extra, matches_file_type
import pathspec


def list_entries(
    directory: Path,
    *,
    root: Path,
    gi: GitIgnoreMatcher,
    spec: pathspec.PathSpec,
    show_all: bool,
    extra_excludes: List[str],
    max_items: Optional[int] = None,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
) -> Tuple[List[Path], int]:
    """
    List and filter directory entries based on various criteria.

    Args:
        directory (Path): Directory to list entries from
        root (Path): Root directory for relative path calculations
        gi (GitIgnoreMatcher): GitIgnore matcher instance
        spec (pathspec.PathSpec): Pathspec for gitignore patterns
        show_all (bool): If True, include hidden files
        extra_excludes (List[str]): Additional exclude patterns
        max_items (Optional[int]): Maximum number of items to return
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
        if gi.is_ignored(e, spec):
            continue
        if matches_extra(e, root, extra_excludes, exclude_depth):
            continue
        # Filter based on --no-files
        if no_files and e.is_file():
            continue

        # Apply inclusion filters (if any specified)
        if include_spec or include_file_types:
            # Directories always pass (needed for traversal)
            if e.is_dir():
                out.append(e)
                continue

            # Files must match at least one inclusion criterion
            matches_include = False

            # Check if matches include patterns
            if include_spec:
                rel_path = e.relative_to(root).as_posix()
                if include_spec.match_file(rel_path):
                    matches_include = True

            # Check if matches file types
            if not matches_include and include_file_types:
                if matches_file_type(e, include_file_types):
                    matches_include = True

            # Only include if it matches at least one criterion
            if matches_include:
                out.append(e)
        else:
            # No inclusion filters, include everything
            out.append(e)

    out.sort(key=lambda x: (x.is_file(), x.name.lower()))

    # Handle max_items limit
    truncated = 0
    if max_items is not None and len(out) > max_items:
        truncated = len(out) - max_items
        out = out[:max_items]

    return out, truncated
