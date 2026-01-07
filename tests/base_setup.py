# tests/base_setup.py

"""
Code file for the BaseCliSetup. All test classes should inherit
from this root class.
"""

import unittest
import tempfile
import subprocess
import sys
from pathlib import Path


class BaseCLISetup(unittest.TestCase):
    """
    Base class for CLI setup.
    Inherit from this class to create test classes with reusable setup.
    """

    def setUp(self):
        """
        Create a temporary directory for each test.

        Use self.root everywhere to create temporary files
        """

        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

        # Vars to be used for all other tests
        self.base_call = "gitree "


    def tearDown(self):
        """
        Cleanup temporary directory after tests.
        """

        self._tmpdir.cleanup()


    def run_gitree(self, *args):
        """
        Helper to run gitree with the CLI consistently. The path given to the tool is
        the temporary dir path.

        Args:
            args (tuple): extra CLI arguments, e.g. "--max-depth 1", "--help", "--zip output.zip"
        """

        return subprocess.run(
            [sys.executable, "-m", "gitree.main", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )


    def failed_run_msg(self, args_str: str) -> str:
        """
        Generate message for the failed run.
        """

        return f"Failed run '{self.base_call} {args_str}'. "


    def non_zero_exitcode_msg(self, exitcode: int) -> str:
        """
        Generate message for the non-zero exitcode issue.
        """

        return f"Non-zero exit code: '{exitcode}'. "


    def no_output_msg(self) -> str:
        """
        Generate message for the no-output issue.
        """

        return "No output from the tool. "

