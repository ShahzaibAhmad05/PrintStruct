from gitree.constants.constant import FILE_EMOJI, EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI
from tests.base_setup import BaseCLISetup


class TestListingFlags(BaseCLISetup):

    @staticmethod
    def __build_name_with_emoji(file_name: str, emoji: str):
        return emoji + " " + file_name


    def test_entry_point_emoji(self):
        # Create empty and simple directories to test both emojis
        (self.root / "empty_folder").mkdir()
        result = self._run_cli("--emoji", "--no-color")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(self.__build_name_with_emoji('file.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('nested.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('empty_folder', EMPTY_DIR_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('folder', NORMAL_DIR_EMOJI), result.stdout)


    def test_entry_point_no_files(self):
        result = self._run_cli("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("folder", result.stdout)
        self.assertNotIn("file.txt", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_max_depth(self):
        result = self._run_cli("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_no_limit(self):
        # Override base structure for this test
        (self.root / "file.txt").unlink()

        for i in range(30):  # default limit is 20
            (self.root / "folder" / f"file{i}.txt").write_text("data")

        result = self._run_cli("--no-limit", "--no-max-lines")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())

        for i in range(30):
            self.assertIn(f"file{i}.txt", result.stdout)


    def test_entry_point_hidden_items(self):
        # Create hidden files and directories
        (self.root / ".hidden_file.txt").write_text("hidden")
        (self.root / ".hidden_dir").mkdir()
        (self.root / ".hidden_dir" / "nested.txt").write_text("nested")

        # Test without --hidden-items flag (default behavior)
        result_default = self._run_cli()

        self.assertEqual(result_default.returncode, 0, msg=result_default.stderr)
        self.assertTrue(result_default.stdout.strip())
        self.assertIn("file.txt", result_default.stdout)
        self.assertNotIn(".hidden_file.txt", result_default.stdout)
        self.assertNotIn(".hidden_dir", result_default.stdout)

        # Test with --hidden-items flag
        result_with_flag = self._run_cli("--hidden-items")

        self.assertEqual(result_with_flag.returncode, 0, msg=result_with_flag.stderr)
        self.assertTrue(result_with_flag.stdout.strip())
        self.assertIn("file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_dir", result_with_flag.stdout)


    def test_entry_point_files_first(self):
        # Create a folder and a file
        tmp_dir = "random_dir"
        tmp_file = "random_file.txt"
        (self.root / tmp_dir).mkdir()
        (self.root / tmp_file).write_text("data")

        # Test with --files-first flag
        result_files_first = self._run_cli("--files-first")

        self.assertEqual(result_files_first.returncode, 0, msg=result_files_first.stderr)

        files_first_output = result_files_first.stdout
        file_index = files_first_output.find(tmp_file)
        folder_index = files_first_output.find(tmp_dir)

        self.assertTrue(
            file_index < folder_index,
            msg=f"Expected file before folder. File at {file_index}, Folder at {folder_index}"
        )


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


    def test_entry_point_include(self):
        # Create a .gitignore to test that --include overrides it
        (self.root / ".gitignore").write_text("*.py\n")
        (self.root / "script.py").write_text("python")
        (self.root / "data.json").write_text("{}")
        (self.root / "folder" / "test.py").write_text("test")

        # Without --include, .py files should be ignored
        result_without = self._run_cli()
        self.assertNotIn("script.py", result_without.stdout)
        self.assertNotIn("test.py", result_without.stdout)

        # With --include *.py, .py files should be force-included despite gitignore
        result = self._run_cli("--include", "*.py")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        # Should force-include .py files (overriding gitignore)
        self.assertIn("script.py", result.stdout)
        self.assertIn("test.py", result.stdout)
        # Should still show other files that pass normal filters
        self.assertIn("file.txt", result.stdout)
        self.assertIn("data.json", result.stdout)
        self.assertIn("folder", result.stdout)


    def test_entry_point_exclude(self):
        # Create multiple file types
        (self.root / "script.py").write_text("python")
        (self.root / "data.json").write_text("{}")
        (self.root / "readme.md").write_text("docs")
        (self.root / "folder" / "test.py").write_text("test")

        # Test --exclude to hide .py files
        result = self._run_cli("--exclude", "*.py")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        # Should show non-.py files
        self.assertIn("file.txt", result.stdout)
        self.assertIn("data.json", result.stdout)
        self.assertIn("readme.md", result.stdout)
        self.assertIn("folder", result.stdout)
        # Should NOT show .py files
        self.assertNotIn("script.py", result.stdout)
        self.assertNotIn("test.py", result.stdout)


    def test_entry_point_exclude_multiple_patterns(self):
        # Create various files
        (self.root / "file.log").write_text("log")
        (self.root / "cache.tmp").write_text("temp")
        (self.root / "data.json").write_text("{}")
        (self.root / "folder" / "debug.log").write_text("debug")

        # Test --exclude with multiple patterns
        result = self._run_cli("--exclude", "*.log", "*.tmp")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        # Should show files not matching exclude patterns
        self.assertIn("file.txt", result.stdout)
        self.assertIn("data.json", result.stdout)
        self.assertIn("folder", result.stdout)
        # Should NOT show excluded files
        self.assertNotIn("file.log", result.stdout)
        self.assertNotIn("cache.tmp", result.stdout)
        self.assertNotIn("debug.log", result.stdout)
