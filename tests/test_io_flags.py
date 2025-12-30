import zipfile

from tests.base_setup import BaseCLISetup


class TestIOFlags(BaseCLISetup):
    # Note: There is no test for copy-to-clipboard currently
    # because real clipboard access is often unavailable/flaky in CI environments.

    def test_entry_point_zip(self):
        zip_path = self.root / "output.zip"

        result = self._run_cli("--zip", zip_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(zip_path.exists(), "Zip file was not created")

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            self.assertIn("file.txt", names)


    def test_entry_point_output(self):
        out_path = self.root / "tree_output.txt"

        result = self._run_cli("--output", out_path.name)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(out_path.exists(), "Output file was not created")

        content = out_path.read_text()
        self.assertIn("file.txt", content)


    def test_entry_point_init_config(self):
        config_path = self.root / "config.json"

        # Ensure config.json doesn't exist initially
        self.assertFalse(config_path.exists(), "config.json should not exist before test")

        result = self._run_cli("--init-config")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(config_path.exists(), "config.json was not created")

        # Verify it's valid JSON with expected keys
        import json
        with open(config_path) as f:
            config = json.load(f)

        # Check for some expected default keys
        self.assertIn("max_items", config)
        self.assertIn("emoji", config)
        self.assertIn("hidden_items", config)
