# tests/test_io_flags.py
import zipfile

from tests.base_setup import BaseCLISetup


class TestIOFlags(BaseCLISetup):
    """
    Tests I/O-related CLI flags, including:
        - Creating zip archives using --zip
        - Exporting tree output to a file using --export
    """

    # Note: There is no test for copy-to-clipboard currently
    # because real clipboard access is often unavailable/flaky in CI environments.

    def test_zip(self):
        """
        Verify that the --zip flag creates a zip archive containing
        the expected project files.
        """
        file_path = self.root / "file.txt"
        file_path.write_text("hello", encoding="utf-8")

        zip_path = self.root / "output.zip"

        result = self.run_gitree("--zip", zip_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(zip_path.exists(), "Zip file was not created")

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            self.assertIn("file.txt", names)


    def test_export(self):
        """
        Verify that the --export flag writes the directory tree output
        to a file and includes file contents.
        """
        out_path = self.root / "tree_export.txt"

        result = self.run_gitree("--export", out_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(out_path.exists(), "Export file was not created")

        content = out_path.read_text()
        self.assertIn("CONTENTS", content)

