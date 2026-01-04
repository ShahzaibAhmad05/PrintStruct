# gitree/services/list_enteries.py

"""
Code file for housing list_entries.
"""

# Default libs
from pathlib import Path

# Dependencies
import pathspec

# Deps from this project
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import iter_dir, matches_extra, matches_file_type
from ..utilities.logger import Logger
from ..objects.app_context import AppContext
from ..objects.config import Config


def list_entries(ctx: AppContext, config: Config, directory: Path, root: Path,
    gi: GitIgnoreMatcher, spec: pathspec.PathSpec) -> tuple[list[Path], int]:
    """
    List and filter directory entries based on various criteria.

    Args:
        ctx (AppContext): App context for the function to use
        directory (Path): Directory to list entries from
        root (Path): Root directory for relative path calculations
        gi (GitIgnoreMatcher): GitIgnore matcher instance
        spec (pathspec.PathSpec): Pathspec for gitignore patterns

    Returns:
        tuple[list[Path], int]: tuple of (filtered paths list, count of truncated items)
    """

    out: list[Path] = []

    # Compile include pattern spec if provided
    include_spec = None
    if config.include:
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", config.include)

    for e in iter_dir(directory):
        # Check for forced inclusion (overrides gitignore, hidden files, and other filters)
        is_force_included = False
        if include_spec or config.include_file_types:
            if e.is_file():
                if include_spec:
                    rel_path = e.relative_to(root).as_posix()
                    if include_spec.match_file(rel_path):
                        is_force_included = True

                if not is_force_included and config.include_file_types:
                    if matches_file_type(e, config.include_file_types):
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

        # Normal filters (hidden files check moved here, after force-include logic)
        if not config.hidden_items and e.name.startswith("."):
            continue
        if gi.is_ignored(e, spec):
            continue
        if matches_extra(e, root, config.exclude, config.exclude_depth):
            continue
        # Filter based on --no-files
        if config.no_files and e.is_file():
            continue

        out.append(e)

    if config.files_first:
        # Sort files first (is_file() is True/1, is_dir() is False/0)
        # We use -x.is_file() because True (1) comes after False (0)
        # in ascending sorts, so we negate it to put files at the top.
        out.sort(key=lambda x: (-x.is_file(), x.name.lower()))
    else:
        # Default: Directories first
        out.sort(key=lambda x: (x.is_file(), x.name.lower()))

    # Handle max_items limit
    truncated = 0
    if not config.no_max_items and config.max_items is not None and len(out) > config.max_items:
        truncated = len(out) - config.max_items
        out = out[:config.max_items]

    return out, truncated
