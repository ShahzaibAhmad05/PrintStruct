import argparse
from pathlib import Path
from ..utilities.utils import max_items_int, max_lines_int


class ParsingService:
    """
    CLI parsing service for gitree tool.
    Wraps argument parsing and validation into a class.
    """

    def __init__(self, logger=None):
        """
        Initialize the parsing service.

        Args:
            logger: Optional logger instance for debug/info messages
        """
        self.logger = logger

    # -------------------------
    # Public method to parse args
    # -------------------------
    def parse_args(self) -> argparse.Namespace:
        """
        Parse command-line arguments for the gitree tool.

        Returns:
            argparse.Namespace: Parsed command-line arguments containing all configuration options
        """
        ap = argparse.ArgumentParser(
            description="Print a directory tree (respects .gitignore).",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=self._examples_text()
        )

        self._add_positional_args(ap)
        self._add_basic_flags(ap)
        self._add_io_flags(ap)
        self._add_listing_flags(ap)
        self._add_listing_control_flags(ap)

        args = ap.parse_args()
        if self.logger:
            self.logger.debug("Parsed arguments: %s", args)
        return args

    # -------------------------
    # Correct CLI args
    # -------------------------
    def correct_args(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Correct and validate CLI arguments in place.
        """
        if getattr(args, "output", None) is not None:
            args.output = self._fix_output_path(
                args.output,
                default_extensions={"txt": ".txt", "json": ".json", "md": ".md"},
                format_str=getattr(args, "format", "")
            )
        if getattr(args, "zip", None) is not None:
            args.zip = self._fix_output_path(args.zip, default_extension=".zip")

        if self.logger:
            self.logger.debug("Corrected arguments: %s", args)
        return args

    # -------------------------
    # Private helper methods
    # -------------------------
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

gitree --json tree.json --no-contents
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

    def _add_basic_flags(self, ap: argparse.ArgumentParser):
        basic = ap.add_argument_group("Basic CLI flags")
        basic.add_argument("-v", "--version", action="store_true", help="Display the version of the tool")
        basic.add_argument("--init-config", action="store_true", help="Create a default config.json file")
        basic.add_argument("--config-user", action="store_true", help="Open config.json in the default editor")
        basic.add_argument("--no-config", action="store_true", help="Ignore config.json and use defaults")
        basic.add_argument("--verbose", action="store_true", default=argparse.SUPPRESS, help="Enable verbose output")

    def _add_io_flags(self, ap: argparse.ArgumentParser):
        io = ap.add_argument_group("Input / Output flags")
        io.add_argument("-z", "--zip", default=argparse.SUPPRESS, help="Create a zip archive")
        io.add_argument("--no-contents", action="store_true", default=argparse.SUPPRESS, help="Don't include file contents")
        io.add_argument("--no-contents-for", nargs="+", default=[], metavar="PATH", help="Exclude contents for specific files")
        io.add_argument("--overrride-files", action="store_true", default=argparse.SUPPRESS, help="Override existing files")  # <-- triple r
        io.add_argument("-o", "--output", default=argparse.SUPPRESS, help="Save tree structure to file")

    def _add_listing_flags(self, ap: argparse.ArgumentParser):
        listing = ap.add_argument_group("Listing flags")
        listing.add_argument("--format", choices=["txt", "json", "md"], default="txt", help="Format output only")
        listing.add_argument("--max-depth", type=int, default=argparse.SUPPRESS, help="Maximum depth to traverse")
        listing.add_argument("--max-lines", type=max_lines_int, default=argparse.SUPPRESS, help="Limit lines shown in tree output")
        listing.add_argument("--hidden-items", action="store_true", default=argparse.SUPPRESS, help="Show hidden files and directories")
        listing.add_argument("--exclude", nargs="*", default=argparse.SUPPRESS, help="Patterns of files to exclude")
        listing.add_argument("--exclude-depth", type=int, default=argparse.SUPPRESS, help="Limit depth for exclude patterns")
        listing.add_argument("--gitignore-depth", type=int, default=argparse.SUPPRESS, help="Limit depth for .gitignore processing")
        listing.add_argument("--max-items", type=max_items_int, default=argparse.SUPPRESS, help="Limit items per directory")
        listing.add_argument("-c", "--copy", action="store_true", default=argparse.SUPPRESS, help="Copy output to clipboard")
        listing.add_argument("-e", "--emoji", action="store_true", default=argparse.SUPPRESS, help="Show emojis")
        listing.add_argument("-i", "--interactive", action="store_true", default=argparse.SUPPRESS, help="Interactive mode")
        listing.add_argument("--include", nargs="*", default=argparse.SUPPRESS, help="Patterns of files to include")
        listing.add_argument("--include-file-types", "--include-file-type", nargs="*", default=argparse.SUPPRESS, dest="include_file_types", help="Include files of certain types")
        listing.add_argument("-s", "--summary", action="store_true", default=argparse.SUPPRESS, help="Print summary of files/folders")
        listing.add_argument("--files-first", action="store_true", default=False, help="Print files before directories")
        listing.add_argument("--no-color", action="store_true", default=argparse.SUPPRESS, help="Disable color output")

    def _add_listing_control_flags(self, ap: argparse.ArgumentParser):
        listing_control = ap.add_argument_group("Listing control flags", "Control flags to disable listing behaviors")
        listing_control.add_argument("--no-max-lines", action="store_true", default=argparse.SUPPRESS, help="Disable max lines limit")
        listing_control.add_argument("--no-gitignore", action="store_true", default=argparse.SUPPRESS, help="Ignore .gitignore rules")
        listing_control.add_argument("--no-limit", action="store_true", default=argparse.SUPPRESS, help="Show all items regardless of count")
        listing_control.add_argument("--no-files", action="store_true", default=argparse.SUPPRESS, help="Hide files (only directories)")


def parse_args(*args, logger=None, **kwargs) -> argparse.Namespace:
    return ParsingService(logger=logger).parse_args(*args, **kwargs)

def correct_args(args: argparse.Namespace) -> argparse.Namespace:
    return ParsingService().correct_args(args)
