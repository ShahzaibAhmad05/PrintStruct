from pathlib import Path
from typing import Optional
import pathspec

class GitIgnoreMatcher:
    """
    Handles gitignore pattern matching for file and directory filtering.

    This class manages gitignore rules and determines whether paths should
    be ignored based on gitignore patterns.
    """

    def __init__(self, root: Path, enabled: bool = True, *, gitignore_depth: Optional[int] = None):
        """
        Initialize the GitIgnoreMatcher.

        Args:
            root (Path): The root directory path
            enabled (bool): Whether gitignore matching is enabled. Defaults to True
            gitignore_depth (Optional[int]): Maximum depth to search for gitignore files. None means unlimited
        """
        self.root = root
        self.enabled = enabled
        self.gitignore_depth = gitignore_depth

    def within_depth(self, dirpath: Path) -> bool:
        """
        Check if a directory is within the allowed gitignore depth.

        Args:
            dirpath (Path): The directory path to check

        Returns:
            bool: True if the directory is within the allowed depth, False otherwise
        """
        if self.gitignore_depth is None:
            return True
        try:
            return len(dirpath.relative_to(self.root).parts) <= self.gitignore_depth
        except Exception:
            return False

    def is_ignored(self, path: Path, spec: pathspec.PathSpec) -> bool:
        """
        Check if a path should be ignored based on gitignore patterns.

        Args:
            path (Path): The path to check
            spec (pathspec.PathSpec): The pathspec object containing gitignore patterns

        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        if not self.enabled:
            return False
        rel = path.relative_to(self.root).as_posix()
        if spec.match_file(rel):
            return True
        if path.is_dir() and spec.match_file(rel + "/"):
            return True
        return False