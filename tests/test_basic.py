from tests.base_setup import BaseCLISetup


class TestBasic(BaseCLISetup):

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
