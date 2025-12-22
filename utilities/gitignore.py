from pathlib import Path
from typing import Optional
import pathspec

class GitIgnoreMatcher:
    def __init__(self, root: Path, enabled: bool = True, *, gitignore_depth: Optional[int] = None):
        self.root = root
        self.enabled = enabled
        self.gitignore_depth = gitignore_depth

    def within_depth(self, dirpath: Path) -> bool:
        if self.gitignore_depth is None:
            return True
        try:
            return len(dirpath.relative_to(self.root).parts) <= self.gitignore_depth
        except Exception:
            return False

    def is_ignored(self, path: Path, spec: pathspec.PathSpec) -> bool:
        if not self.enabled:
            return False
        rel = path.relative_to(self.root).as_posix()
        if spec.match_file(rel):
            return True
        if path.is_dir() and spec.match_file(rel + "/"):
            return True
        return False