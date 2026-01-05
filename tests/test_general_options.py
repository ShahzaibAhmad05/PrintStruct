# tests/test_basic.py
from tests.base_setup import BaseCLISetup


class TestGeneralOptions(BaseCLISetup):

    def test_version(self):
        result = self._run_cli("--version")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(".", result.stdout)


    def test_init_config(self):
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


    def test_verbose(self):
        result = self._run_cli("--verbose")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("LOG", result.stdout)
