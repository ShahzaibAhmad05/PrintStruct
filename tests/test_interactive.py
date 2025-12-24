import unittest
from pathlib import Path
import tempfile
import sys
import os
from unittest.mock import MagicMock, patch

# Adjust path to find gitree package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from gitree.services.draw_tree import draw_tree
from gitree.services.zip_project import zip_project

class TestInteractiveMode(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)
        
        # Create a dummy structure
        # root/
        #   file1.txt
        #   file2.txt
        #   folder/
        #     file3.txt
        #     file4.txt
        
        (self.root / "file1.txt").touch()
        (self.root / "file2.txt").touch()
        (self.root / "folder").mkdir()
        (self.root / "folder" / "file3.txt").touch()
        (self.root / "folder" / "file4.txt").touch()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_draw_tree_whitelist(self):
        # Whitelist specific files
        whitelist = {
            str(self.root / "file1.txt"),
            str(self.root / "folder" / "file3.txt")
        }
        
        # Capture stdout
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output
        
        draw_tree(
            root=self.root,
            depth=None,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None,
            whitelist=whitelist
        )
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # file1.txt should be present
        self.assertIn("file1.txt", output)
        # file3.txt should be present
        self.assertIn("file3.txt", output)
        # file2.txt should NOT be present
        self.assertNotIn("file2.txt", output)
        # file4.txt should NOT be present
        self.assertNotIn("file4.txt", output)
        # folder should be present (as it contains file3.txt)
        self.assertIn("folder", output)

    def test_zip_project_whitelist(self):
        whitelist = {
            str(self.root / "file1.txt"),
            str(self.root / "folder" / "file3.txt")
        }
        
        zip_stem = str(self.root / "test_zip")
        
        zip_project(
            root=self.root,
            zip_stem=zip_stem,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            ignore_depth=None,
            depth=None,
            gitignore_depth=None,
            whitelist=whitelist
        )
        
        zip_path = Path(f"{zip_stem}.zip")
        self.assertTrue(zip_path.exists())
        
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_names = z.namelist()
            
            # Windows/Posix path normalization for zip contents usually uses forward slash
            self.assertIn("file1.txt", file_names)
            self.assertIn("folder/file3.txt", file_names)
            self.assertNotIn("file2.txt", file_names)
            self.assertNotIn("folder/file4.txt", file_names)

if __name__ == '__main__':
    unittest.main()
