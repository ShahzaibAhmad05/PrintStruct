import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class TestListingFlags(unittest.TestCase):
    
    def setUp(self):
        # Create a temp project directory for each test
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Base project structure
        (self.root / "file.txt").write_text("hello")


    def tearDown(self):
        # Cleanup temp directory
        self._tmpdir.cleanup()


    def _run_cli(self, *args):
        """
        Helper to run the CLI consistently.
        - args: extra CLI arguments, e.g. "--max-depth 1"
        """
        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
        )


    def test_entry_point_emoji(self):
        result = self._run_cli("--emoji")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)


    def test_entry_point_no_files(self):
        # Additional structure specific to this test
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("folder", result.stdout)
        self.assertNotIn("file.txt", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_max_depth(self):
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_no_limit(self):
        # Override base structure for this test
        (self.root / "file.txt").unlink()
        (self.root / "folder").mkdir()

        for i in range(30):  # default limit is 20
            (self.root / "folder" / f"file{i}.txt").write_text("data")

        result = self._run_cli("--no-limit")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())

        for i in range(30):
            self.assertIn(f"file{i}.txt", result.stdout)
