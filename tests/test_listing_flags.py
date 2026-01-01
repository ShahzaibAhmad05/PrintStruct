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


    def test_entry_point_max_depth(self):
        result = self._run_cli("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


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


    def test_entry_point_include_overrides_hidden(self):
        # Create hidden files that match include pattern
        (self.root / ".hidden.py").write_text("hidden python file")
        (self.root / "folder" / ".secret.py").write_text("secret")
        (self.root / "visible.py").write_text("visible")

        # Without --include, hidden .py files should not appear
        result_without = self._run_cli()
        self.assertNotIn(".hidden.py", result_without.stdout)
        self.assertNotIn(".secret.py", result_without.stdout)

        # With --include *.py, even hidden .py files should appear
        result_with = self._run_cli("--include", "*.py")
        self.assertEqual(result_with.returncode, 0, msg=result_with.stderr)
        self.assertIn(".hidden.py", result_with.stdout)
        self.assertIn(".secret.py", result_with.stdout)
        self.assertIn("visible.py", result_with.stdout)


    def test_entry_point_include_overrides_gitignore(self):
        # Create .gitignore that ignores .py files
        (self.root / ".gitignore").write_text("*.py\n*.log\n")
        (self.root / "script.py").write_text("python")
        (self.root / "error.log").write_text("log")
        (self.root / "data.json").write_text("{}")


    def test_entry_point_include(self):
        # Create a .gitignore to test that --include overrides it
        (self.root / ".gitignore").write_text("*.py\n")
        (self.root / "script.py").write_text("python")
        (self.root / "data.json").write_text("{}")
        (self.root / "folder" / "test.py").write_text("test")

        # Without --include, .py files should be ignored
        result_without = self._run_cli()
        self.assertNotIn("script.py", result_without.stdout)
        self.assertNotIn("error.log", result_without.stdout)
        self.assertIn("data.json", result_without.stdout)

        # With --include *.py, .py files should appear despite gitignore
        result_with = self._run_cli("--include", "*.py")
        self.assertEqual(result_with.returncode, 0, msg=result_with.stderr)
        self.assertIn("script.py", result_with.stdout)
        # .log files still ignored (not in include pattern)
        self.assertNotIn("error.log", result_with.stdout)
        # Other files still appear
        self.assertIn("data.json", result_with.stdout)


    def test_entry_point_include_file_types_overrides_hidden(self):
        # Create hidden JSON and Python files
        (self.root / ".config.json").write_text("{}")
        (self.root / ".secret.py").write_text("secret")
        (self.root / "data.json").write_text("{}")
        (self.root / "readme.md").write_text("docs")

        # Without include-file-types, hidden files not shown
        result_without = self._run_cli()
        self.assertNotIn(".config.json", result_without.stdout)
        self.assertNotIn(".secret.py", result_without.stdout)

        # With --include-file-types json, even hidden .json files should appear
        result_with = self._run_cli("--include-file-types", "json")
        self.assertEqual(result_with.returncode, 0, msg=result_with.stderr)
        self.assertIn(".config.json", result_with.stdout)
        self.assertIn("data.json", result_with.stdout)
        # .py files not included (different type)
        self.assertNotIn(".secret.py", result_with.stdout)
        # Other files still appear
        self.assertIn("readme.md", result_with.stdout)


    def test_entry_point_include_file_types_overrides_gitignore(self):
        # Create .gitignore that ignores JSON files
        (self.root / ".gitignore").write_text("*.json\n*.yaml\n")
        (self.root / "config.json").write_text("{}")
        (self.root / "settings.yaml").write_text("yaml")
        (self.root / "readme.md").write_text("docs")

        # Without include-file-types, .json and .yaml files should be ignored
        result_without = self._run_cli()
        self.assertEqual(result_without.returncode, 0, msg=result_without.stderr)
        self.assertNotIn("config.json", result_without.stdout)
        self.assertNotIn("settings.yaml", result_without.stdout)
        # Base file.txt and readme.md should appear
        self.assertIn("file.txt", result_without.stdout)
        self.assertIn("readme.md", result_without.stdout)

        # With --include-file-types json, .json files should appear despite gitignore
        result_with = self._run_cli("--include-file-types", "json")
        self.assertEqual(result_with.returncode, 0, msg=result_with.stderr)
        self.assertIn("config.json", result_with.stdout)
        # .yaml still ignored (not in include types)
        self.assertNotIn("settings.yaml", result_with.stdout)
        # Other files still appear
        self.assertIn("file.txt", result_with.stdout)
        self.assertIn("readme.md", result_with.stdout)


    def test_entry_point_include_no_match_warning(self):
        # Create files that don't match the include pattern
        (self.root / "data.json").write_text("{}")
        (self.root / "readme.md").write_text("docs")

        # Search for .py files that don't exist
        result = self._run_cli("--include", "*.py", "*.cpp")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # Warning should appear in stderr
        self.assertIn("No files found matching --include patterns", result.stderr)
        self.assertIn("*.py", result.stderr)


    def test_entry_point_include_file_types_no_match_warning(self):
        # Create files that don't match the include file types
        (self.root / "data.json").write_text("{}")
        (self.root / "readme.md").write_text("docs")

        # Search for file types that don't exist
        result = self._run_cli("--include-file-types", "rs", "go", "cpp")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # Warning should appear in stderr
        self.assertIn("No files found matching --include-file-types", result.stderr)
        self.assertIn("rs", result.stderr)
        # self.assertNotIn("test.py", result_without.stdout)

        # With --include *.py, .py files should be force-included despite gitignore
        result = self._run_cli("--include", "*.py")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        # Should force-include .py files (overriding gitignore)
        # self.assertIn("script.py", result.stdout)
        # self.assertIn("test.py", result.stdout)
        # # Should still show other files that pass normal filters
        # self.assertIn("file.txt", result.stdout)
        # self.assertIn("data.json", result.stdout)
        # self.assertIn("folder", result.stdout)


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
