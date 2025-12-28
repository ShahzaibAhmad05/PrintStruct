import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from gitree.constants.constant import FILE_EMOJI, EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI


class TestListingFlags(unittest.TestCase):
    
    def setUp(self):
        # Create a temp project directory for each test
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Base project structure
        (self.root / "file.txt").write_text("hello")


    def tearDown(self):
        # Cleanup temp directory
        self._tmpdir.cleanup()


    def _run_cli(self, *args):
        """
        Helper to run the CLI consistently.
        - args: extra CLI arguments, e.g. "--max-depth 1"
        """
        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )


    @staticmethod
    def __build_name_with_emoji(file_name: str, emoji: str):
        return emoji + " " + file_name


    def test_entry_point_emoji(self):
        # Create empty and simple directories to test both emojis
        (self.root / "empty_folder").mkdir()
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text('foo')
        result = self._run_cli("--emoji")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(self.__build_name_with_emoji('file.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('nested.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('empty_folder', EMPTY_DIR_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('folder', NORMAL_DIR_EMOJI), result.stdout)


    def test_entry_point_no_files(self):
        # Additional structure specific to this test
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("folder", result.stdout)
        self.assertNotIn("file.txt", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_max_depth(self):
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_no_limit(self):
        # Override base structure for this test
        (self.root / "file.txt").unlink()
        (self.root / "folder").mkdir()

        for i in range(30):  # default limit is 20
            (self.root / "folder" / f"file{i}.txt").write_text("data")

        # We need to increase max-lines because default is 30 and we have >30 items
        result = self._run_cli("--no-limit", "--max-lines", "100")

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
