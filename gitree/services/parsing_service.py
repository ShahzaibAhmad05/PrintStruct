# gitree/services/parsing_service.py
import argparse
from pathlib import Path
from ..utilities.utils import max_items_int, max_entries_int
from ..utilities.logger import Logger, OutputBuffer
from ..objects.config import Config


class ParsingService:
    """
    CLI parsing service for gitree tool. 
    Wraps argument parsing and validation into a class.
    """

    def __init__(self, *, logger: Logger, output_buffer: OutputBuffer):
        """
        Initialize the parsing service.

        Args:
            logger: Optional logger instance for debug/info messages
        """
        self.logger = logger
        self.output_buffer = output_buffer

    # ------------------------------
    # Public method to parse args
    # ------------------------------

    def parse_args(self) -> Config:
        """
        Parse command-line arguments for the gitree tool.

        Returns:
            config (Config): Configuration object storing information for args
        """
        ap = argparse.ArgumentParser(
            description="Print a directory tree (respects .gitignore).",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=self._examples_text()
        )

        self._add_positional_args(ap)
        self._add_general_options(ap)
        self._add_io_flags(ap)
        self._add_listing_flags(ap)
        self._add_listing_control_flags(ap)

        args = ap.parse_args()
        if self.logger:
            self.logger(Logger.DEBUG, "Parsed arguments: %s", args)

        # Correct the arguments before returning to avoid complexity
        # in implementation in main function
        args = self._correct_args(args)
        return Config(args)

    # -------------------------
    # Private helper methods
    # -------------------------

    def _correct_args(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Correct and validate CLI arguments in place.
        """
        # Change 'output' to 'export' here
        if getattr(args, "export", None) is not None:
            args.export = self._fix_output_path(
                args.export,
                default_extensions={"txt": ".txt", "json": ".json", "md": ".md"},
                format_str=args.format
            )
        if getattr(args, "zip", None) is not None:
            args.zip = self._fix_output_path(args.zip, default_extension=".zip")

        if self.logger:
            self.logger.debug("Corrected arguments: %s", args)
        return args
    

    def _fix_output_path(
        self,
        output_path: str,
        default_extension: str = "",
        default_extensions: dict | None = None,
        format_str: str = ""
    ) -> str:
        """
        Ensure the output path has a correct extension.
        """
        default_extensions = default_extensions or {}
        path = Path(output_path)

        if path.suffix == "":
            if default_extension:
                path = path.with_suffix(default_extension)
            elif format_str and format_str in default_extensions:
                path = path.with_suffix(default_extensions[format_str])

        return str(path)
    

    def _examples_text(self) -> str:
        return """
            Examples:
            gitree
                Print tree of current directory

            gitree src --max-depth 2
                Print tree for 'src' directory up to depth 2

            gitree . --exclude *.pyc __pycache__
                Exclude compiled Python files

            gitree --export tree.json --no-contents
                Export tree as JSON without file contents

            gitree --zip project.zip src/
                Create a zip archive from src directory
            """.strip()


    def _add_positional_args(self, ap: argparse.ArgumentParser):
        ap.add_argument(
            "paths",
            nargs="*",
            default=["."],
            help="Root paths (supports multiple directories and file patterns)",
        )


    def _add_general_options(self, ap: argparse.ArgumentParser):
        basic = ap.add_argument_group("general options")
        basic.add_argument("-v", "--version", action="store_true", 
            default=argparse.SUPPRESS, help="Display the version of the tool")
        basic.add_argument("--init-config", action="store_true", 
            default=argparse.SUPPRESS, help="Create a default config.json file")
        basic.add_argument("--config-user", action="store_true", 
            default=argparse.SUPPRESS, help="Open config.json in the default editor")
        basic.add_argument("--no-config", action="store_true", 
            default=argparse.SUPPRESS, help="Ignore config.json and use defaults")
        basic.add_argument("--verbose", action="store_true", 
            default=argparse.SUPPRESS, help="Enable verbose output")


    def _add_io_flags(self, ap: argparse.ArgumentParser):
        io = ap.add_argument_group("output & export options")

        io.add_argument("-z", "--zip", 
            default=argparse.SUPPRESS, help="Create a zip archive of the given path")
        io.add_argument("--export", 
            default=argparse.SUPPRESS, help="Save tree structure to file")


    def _add_listing_flags(self, ap: argparse.ArgumentParser):
        listing = ap.add_argument_group("listing options")

        listing.add_argument("--format", choices=["txt", "json", "md"], 
            default="txt", help="Format output only")
        
        listing.add_argument("--max-items", type=max_items_int, 
            default=argparse.SUPPRESS, help="Limit items per directory")
        listing.add_argument("--max-entries", type=max_entries_int, 
            default=argparse.SUPPRESS, help="Limit entries shown in tree output")
        listing.add_argument("--max-depth", type=int, 
            default=argparse.SUPPRESS, help="Maximum depth to traverse")
        listing.add_argument("--gitignore-depth", type=int, 
            default=argparse.SUPPRESS, help="Limit depth for .gitignore processing")
        
        listing.add_argument("--hidden-items", action="store_true", 
            default=argparse.SUPPRESS, help="Show hidden files and directories")
        listing.add_argument("--exclude", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to exclude")
        listing.add_argument("--exclude-depth", type=int, 
            default=argparse.SUPPRESS, help="Limit depth for exclude patterns")
        listing.add_argument("--include", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to include")
        listing.add_argument("--include-file-types", "--include-file-type", nargs="*", 
            default=argparse.SUPPRESS, dest="include_file_types", 
            help="Include files of certain types")
        listing.add_argument("-c", "--copy", action="store_true", 
            default=argparse.SUPPRESS, help="Copy output to clipboard")
        listing.add_argument("-e", "--emoji", action="store_true", 
            default=argparse.SUPPRESS, help="Show emojis")
        listing.add_argument("-i", "--interactive", action="store_true", 
            default=argparse.SUPPRESS, help="Interactive mode")
        
        listing.add_argument("--files-first", action="store_true", 
            default=argparse.SUPPRESS, help="Print files before directories")
        listing.add_argument("--no-color", action="store_true", 
            default=argparse.SUPPRESS, help="Disable color output")
        listing.add_argument("--no-contents", action="store_true", 
            default=argparse.SUPPRESS, help="Don't include file contents")
        listing.add_argument("--no-contents-for", nargs="+", 
            default=argparse.SUPPRESS, metavar="PATH", 
            help="Exclude contents for specific files")
        listing.add_argument("--overrride-files", action="store_true", 
            default=argparse.SUPPRESS, help="Override existing files") 


    def _add_listing_control_flags(self, ap: argparse.ArgumentParser):
        listing_control = ap.add_argument_group("listing override options")

        listing_control.add_argument("--no-max-entries", action="store_true", 
            default=argparse.SUPPRESS, help="Disable max entries limit")
        listing_control.add_argument("--no-gitignore", action="store_true", 
            default=argparse.SUPPRESS, help="Ignore .gitignore rules")
        listing_control.add_argument("--no-limit", action="store_true", 
            default=argparse.SUPPRESS, help="Show all items regardless of count")
        listing_control.add_argument("--no-files", action="store_true", 
            default=argparse.SUPPRESS, help="Hide files (only directories)")
