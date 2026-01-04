# tests/test_listing_control_flags.py
from tests.base_setup import BaseCLISetup


class TestListingControlFlags(BaseCLISetup):
    """
    Test class for listing control flags (--no-* flags).
    These flags control what gets displayed in the tree output.
    """

    def test_entry_point_no_files(self):
        result = self._run_cli("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("folder", result.stdout)
        self.assertNotIn("file.txt", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_no_max_items(self):
        # Override base structure for this test
        (self.root / "file.txt").unlink()

        for i in range(30):  # default limit is 20
            (self.root / "folder" / f"file{i}.txt").write_text("data")

        result = self._run_cli("--no-max-items", "--no-max-entries")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())

        for i in range(30):
            self.assertIn(f"file{i}.txt", result.stdout)


    def test_entry_point_no_color(self):
        # Create additional structure
        (self.root / ".hidden_file").write_text("hidden")

        # Test with color (default) - should contain ANSI color codes
        result_with_color = self._run_cli("--hidden-items")

        self.assertEqual(result_with_color.returncode, 0, msg=result_with_color.stderr)
        self.assertTrue(result_with_color.stdout.strip())
        # Check that ANSI escape sequences are present (color codes start with \x1b[)
        self.assertIn("\x1b[", result_with_color.stdout, msg="Expected ANSI color codes in output")

        # Test with --no-color flag - should NOT contain ANSI color codes
        result_no_color = self._run_cli("--hidden-items", "--no-color")

        self.assertEqual(result_no_color.returncode, 0, msg=result_no_color.stderr)
        self.assertTrue(result_no_color.stdout.strip())
        self.assertNotIn("\x1b[", result_no_color.stdout, msg="Expected no ANSI color codes with --no-color flag")
