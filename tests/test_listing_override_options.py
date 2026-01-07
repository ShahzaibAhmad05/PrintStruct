# tests/test_listing_control_flags.py
from tests.base_setup import BaseCLISetup


class TestListingControlFlags(BaseCLISetup):
    """
    Tests listing control flags (--no-* flags) that modify tree output.
    Includes:
        - --no-files: hide files from the output
        - --no-color: disables ANSI color codes in output
    """

    def test_no_files(self):
        """
        Verify that the --no-files flag correctly hides files from
        the directory tree output.
        """
        result = self.run_gitree("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertNotIn("nested.txt", result.stdout)


    def test_no_color(self):
        """
        Verify that the --no-color flag disables ANSI color codes
        in the directory tree output while default output still includes color.
        """
        # Create additional structure
        (self.root / ".hidden_file").write_text("hidden")

        # Test with color (default) - should contain ANSI color codes
        result_with_color = self.run_gitree("--hidden-items")

        self.assertEqual(result_with_color.returncode, 0, msg=result_with_color.stderr)
        self.assertTrue(result_with_color.stdout.strip())
        # Check that ANSI escape sequences are present (color codes start with \x1b[)
        self.assertIn("\x1b[", result_with_color.stdout, msg="Expected ANSI color codes in output")

        # Test with --no-color flag - should NOT contain ANSI color codes
        result_no_color = self.run_gitree("--hidden-items", "--no-color")

        self.assertEqual(result_no_color.returncode, 0, msg=result_no_color.stderr)
        self.assertTrue(result_no_color.stdout.strip())
        self.assertNotIn("\x1b[", result_no_color.stdout, msg="Expected no ANSI color codes with --no-color flag")
