import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
import zipfile


class TestIOFlags(unittest.TestCase):
    # Note: There is no test for copy-to-clipboard currently
    # because real clipboard access is often unavailable/flaky in CI environments.

    def setUp(self):
        # Create a temp project directory for each test
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Minimal project structure
        (self.root / "file.txt").write_text("hello")


    def tearDown(self):
        # Cleanup temp directory
        self._tmpdir.cleanup()


    def _run_cli(self, *args):
        """
        Helper to run the CLI consistently.
        - args: extra CLI arguments, e.g. "--zip output.zip"
        """
        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
        )


    def test_entry_point_zip_creates_archive(self):
        zip_path = self.root / "output.zip"

        result = self._run_cli("--zip", zip_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(zip_path.exists(), "Zip file was not created")

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            self.assertIn("file.txt", names)


    def test_entry_point_output_writes_tree_file(self):
        out_path = self.root / "tree_output.txt"

        result = self._run_cli("--output", out_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(out_path.exists(), "Output file was not created")

        content = out_path.read_text()
        self.assertIn("file.txt", content)
