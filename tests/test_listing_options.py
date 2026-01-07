# tests/test_listing_flags.py
from gitree.constants.constant import FILE_EMOJI, EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI
from tests.base_setup import BaseCLISetup


class TestListingFlags(BaseCLISetup):
    """
    Tests directory listing CLI flags, including:
        - Displaying file and folder emojis (--emoji)
        - Limiting tree depth (--max-depth)
        - Showing hidden files & folders (--hidden-items)
        - Ordering files before folders (--files-first)
        - Inclusion overrides that bypass .gitignore (--include)
    """

    @staticmethod
    def __build_name_with_emoji(file_name: str, emoji: str):
        """
        Helper to prefix a file or folder name with an emoji.

        Args:
            file_name (str): Name fo the file or folder
            emoji (str): Emoji string to append

        Returns:
            str: Emoji-prefixed name
        """
        return emoji + " " + file_name


    def test_emoji(self):
        """
        Verify that the --emoji flag correctly prefixes files and folders
        with the appropriate emojis, including empty and normal directories.
        """
        file_path = self.root / "file.txt"
        file_path.write_text("hello", encoding="utf-8")
        # Create empty and simple directories to test both emojis
        (self.root / "empty_folder").mkdir()
        result = self.run_gitree("--emoji", "--no-color")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(self.__build_name_with_emoji('file.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('empty_folder', EMPTY_DIR_EMOJI), result.stdout)


    def test_max_depth(self):
        """
        Verity that the --max-depth flag limits the depth of the
        displayed directory tree.
        """
        result = self.run_gitree("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())


    def test_hidden_items(self):
        """
        Verify that hidden files and directories are shown only when
        the --hidden-items flag is used.
        """
        # Create hidden files and directories
        (self.root / ".hidden_file.txt").write_text("hidden")
        (self.root / ".hidden_dir").mkdir()
        (self.root / ".hidden_dir" / "nested.txt").write_text("nested")

        # Test without --hidden-items flag (default behavior)
        result_default = self.run_gitree()

        self.assertEqual(result_default.returncode, 0, msg=result_default.stderr)
        self.assertTrue(result_default.stdout.strip())
        self.assertNotIn(".hidden_file.txt", result_default.stdout)
        self.assertNotIn(".hidden_dir", result_default.stdout)

        # Test with --hidden-items flag
        result_with_flag = self.run_gitree("--hidden-items")

        self.assertEqual(result_with_flag.returncode, 0, msg=result_with_flag.stderr)
        self.assertTrue(result_with_flag.stdout.strip())
        self.assertIn("file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_dir", result_with_flag.stdout)


    def test_files_first(self):
        """
        Verify that the --files-first flag causes files to be listed
        before folders in the directory tree output.
        """
        # Create a folder and a file
        tmp_dir = "random_dir"
        tmp_file = "random_file.txt"
        (self.root / tmp_dir).mkdir()
        (self.root / tmp_file).write_text("data")

        # Test with --files-first flag
        result_files_first = self.run_gitree("--files-first")

        self.assertEqual(result_files_first.returncode, 0, msg=result_files_first.stderr)

        files_first_output = result_files_first.stdout
        file_index = files_first_output.find(tmp_file)
        folder_index = files_first_output.find(tmp_dir)

        self.assertTrue(
            file_index < folder_index,
            msg=f"Expected file before folder. File at {file_index}, Folder at {folder_index}"
        )


    def test_include_overrides_gitignore(self):
        """
        Verify that the --include flag can override .gitignore rules,
        ensuing ignored files are still included if explicitly specified.
        """
        # Create .gitignore that ignores .py files
        (self.root / ".gitignore").write_text("*.py\n*.log\n")
        (self.root / "script.py").write_text("python")
        (self.root / "error.log").write_text("log")
        (self.root / "data.json").write_text("{}")

