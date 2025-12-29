import unittest
import tempfile
import subprocess
import sys
from pathlib import Path


class BaseCLISetup(unittest.TestCase):
    """
    Base class for CLI setup.
    Inherit from this class to create test classes with reusable setup
    """

    def setUp(self):
        # Create a temp project directory for each test
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Base project structure
        (self.root / "file.txt").write_text("hello")

        # Folder with nested file, common for most tests
        folder = self.root / "folder"
        folder.mkdir()
        (folder / "nested.txt").write_text("nested")

    def tearDown(self):
        # Cleanup temp directory
        self._tmpdir.cleanup()


    def _run_cli(self, *args):
        """
        Helper to run the CLI consistently.
        - args: extra CLI arguments, e.g. "--max-depth 1", "--help", "--zip output.zip"
        - cwd: working directory (defaults to self.root)
        """
        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
