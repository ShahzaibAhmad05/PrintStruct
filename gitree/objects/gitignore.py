# gitree/objects/gitignore.py

"""
Code file for housing GitIgnore class
"""

# Defualt libs
from pathlib import Path
from typing import Iterable

# Dependencies
import pathspec

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class GitIgnore:
    """
    Minimal gitignore loader/matcher.

    - Create an object passing roots to it, and it's ready to be used.
    - excluded(path) tells if path is ignored by any root's combined patterns.
    """

    def __init__(self, ctx: AppContext, config: Config, gitignore_path: Path) -> None:
        """
        Initialize the gitignore matcher for a single directory by loading patterns
        from the provided .gitignore file.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            gitignore_path (Path): Path to the .gitignore file to load patterns from
        """

        # Bind app context and config with the object
        self.ctx = ctx
        self.config = config

        # Object attr
        self.enabled = not config.no_gitignore
        self.gitignore_depth = config.gitignore_depth

        # Setup specs for gitignore
        self._specs: list[tuple[Path, pathspec.PathSpec]]
        self._load_spec_from_gitignore(gitignore_path)


    def excluded(self, item_path: Path) -> bool:
        """
        Determine whether the given path is excluded by the loaded gitignore patterns.

        Args:
            item_path (Path): The path to check for exclusion

        Returns:
            bool: True if the path is ignored/excluded, otherwise False
        """
        if not self.enabled:
            return False

        p = item_path.resolve(strict=False)

        for root, spec in self._specs:
            try:
                rel = p.relative_to(root).as_posix()
            except ValueError:
                continue

            if spec.match_file(rel):
                return True
            if p.is_dir() and spec.match_file(rel + "/"):
                return True

        return False


    def _load_from_roots(self, roots: Iterable[Path]) -> None:
        """
        Load and combine gitignore patterns from all .gitignore files under the given roots.

        Args:
            roots (Iterable[Path]): Root directories to scan for .gitignore files
        """
        # Clears the specs if already present
        self._specs = []

        for root in self._norm_roots(roots):
            pats = self._collect_patterns(root)
            self._specs.append((root, pathspec.PathSpec.from_lines("gitwildmatch", pats)))


    def _load_spec_from_gitignore(self, gitignore_path: Path) -> None:
        """
        Load gitignore patterns from a single .gitignore file and create a PathSpec
        rooted at its parent directory.

        Args:
            gitignore_path (Path): Path to the .gitignore file to load
        """
        self._specs = []

        gi = Path(gitignore_path).resolve(strict=False)
        root = gi.parent

        patterns: list[str] = []
        try:
            lines = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            neg = line.startswith("!")
            pat = line[1:] if neg else line
            pat = pat.lstrip("/")
            patterns.append(("!" + pat) if neg else pat)

        self._specs.append((root, pathspec.PathSpec.from_lines("gitwildmatch", patterns)))


    def _norm_roots(self, roots: Iterable[Path]) -> list[Path]:
        """
        Normalize root paths into unique directory Paths.

        Args:
            roots (Iterable[Path]): Root paths to normalize

        Returns:
            list[Path]: A de-duplicated list of resolved directory roots
        """
        out: list[Path] = []
        for r in roots:
            rr = Path(r).resolve(strict=False)
            rr = rr if rr.is_dir() else rr.parent
            if rr not in out:
                out.append(rr)
        return out
    

    def _within_depth(self, root: Path, dirpath: Path) -> bool:
        """
        Check whether a directory is within the configured gitignore traversal depth
        relative to the given root.

        Args:
            root (Path): The root directory used as the depth baseline
            dirpath (Path): The directory path to test

        Returns:
            bool: True if dirpath is within depth, otherwise False
        """
        if self.gitignore_depth is None:
            return True
        try:
            return len(dirpath.relative_to(root).parts) <= self.gitignore_depth
        except Exception:
            return False
        

    def _collect_patterns(self, root: Path) -> list[str]:
        """
        Collect gitignore patterns from all .gitignore files under the root, prefixing
        patterns by their relative directory to emulate nested .gitignore behavior.

        Args:
            root (Path): Root directory to scan

        Returns:
            list[str]: Combined list of patterns collected under the root
        """
        patterns: list[str] = []

        for d in self._walk_dirs(root):
            gi = d / ".gitignore"
            if not gi.is_file():
                continue

            rel_dir = d.relative_to(root).as_posix()
            prefix = "" if rel_dir == "." else rel_dir + "/"

            try:
                lines = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                neg = line.startswith("!")
                pat = line[1:] if neg else line
                pat = prefix + pat.lstrip("/")
                patterns.append(("!" + pat) if neg else pat)

        return patterns
    

    def _walk_dirs(self, root: Path) -> Iterable[Path]:
        """
        Walk directories under the root using a stack-based traversal, respecting the
        configured depth and skipping symlinks.

        Args:
            root (Path): Root directory to traverse

        Returns:
            Iterable[Path]: Directories discovered during traversal, including root
        """
        stack = [root]
        while stack:
            d = stack.pop()
            yield d

            if not self._within_depth(root, d):
                continue

            try:
                for c in d.iterdir():
                    if c.is_dir() and not c.is_symlink():
                        stack.append(c)
            except PermissionError:
                continue
