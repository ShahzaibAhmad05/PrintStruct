import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class TestBasic(unittest.TestCase):
    
    def setUp(self):
        # Create a temp project directory for each test
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Minimal project structure
        (self.root / "file.txt").write_text("hello")


    def tearDown(self):
        # Cleanup temp directory
        self._tmpdir.cleanup()


    def _run_cli(self, *args, cwd=None):
        """
        Helper to run the CLI consistently.
        - args: extra CLI arguments, e.g. "--help"
        - cwd: working directory (defaults to self.root)
        """
        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
        )


    def test_entry_point_runs_and_lists_files(self):
        result = self._run_cli()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)


    def test_entry_point_help(self):
        # For help/version, cwd doesn't matter much, but keeping it consistent is fine.
        result = self._run_cli("--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("--help", result.stdout)


    def test_entry_point_version(self):
        result = self._run_cli("--version")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(".", result.stdout)
