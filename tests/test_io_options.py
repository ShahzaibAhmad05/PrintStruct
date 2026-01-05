# tests/test_io_flags.py
import zipfile

from tests.base_setup import BaseCLISetup


class TestIOFlags(BaseCLISetup):
    # Note: There is no test for copy-to-clipboard currently
    # because real clipboard access is often unavailable/flaky in CI environments.

    def test_zip(self):
        zip_path = self.root / "output.zip"

        result = self._run_cli("--zip", zip_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(zip_path.exists(), "Zip file was not created")

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            self.assertIn("file.txt", names)


    def test_export(self):
        out_path = self.root / "tree_export.txt"

        result = self._run_cli("--export", out_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(out_path.exists(), "Export file was not created")

        content = out_path.read_text()
        self.assertIn("file.txt", content)
        