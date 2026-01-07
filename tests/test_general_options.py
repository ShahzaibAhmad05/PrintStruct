# tests/test_basic.py

"""
Code file for TestGeneralOptions class.

If you find something missing here, it's most likely declared in the
BaseCLISetup class, since this class inherits from that one.
"""

from tests.base_setup import BaseCLISetup


class TestGeneralOptions(BaseCLISetup):
    """
    Tests general CLI behavior & options, including:
        - Running gitree with no arguments
        - Displaying version information (--version)
        - Enabling verbose logging (--verbose)
        - Initializing the user config file (--init-config)
    """

    def test_no_arg(self):
        """
        Test if it is working without any CLI arguments.
        It should print a tree structure (root name in this case),
        which includes the name "tmp"
        """

        # Vars
        args_str = ""

        # Test
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(0, result.returncode,
            msg="Failed default run. " +
                f"Non-zero exit code: {result.returncode}")

        self.assertIn("tmp", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"'tmp' not found in output: \n\n{result.stdout}")


    def test_version(self):
        """
        Test if it prints the version.
        Should work for developer version too.
        using: --version
        """

        # Vars
        args_str = "--version"

        # Test
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        self.assertIn(".", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"No dots found in the output: \n\n{result.stdout}")


    def test_verbose(self):
        """
        Test if the logging utility is working properly
        using: --verbose.
        """

        # Vars
        args_str = "--verbose"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
            self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        self.assertIn("LOG", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected str 'LOG' not found in output: \n\n{result.stdout}")


    def test_init_config(self):
        """
        Test if the user config is being created properly.
        """

        # Vars
        args_str = "--init-config"
        config_path = self.root / ".gitree/config.json"

        # Test
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
            self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(config_path.exists(),
            msg=self.failed_run_msg(args_str) +
            "config.json was not created")
