# gitree/services/parsing_service.py

"""
Code file for housing ParsingService class. Includes arguments adding,
correction, and processing for argparse.
"""

# Default libs
import argparse

# Dependencies
from pathlib import Path

# Imports from this project
from ..utilities.functions_utility import max_items_int, max_entries_int
from ..objects.config import Config
from ..objects.app_context import AppContext


class ParsingService:
    """
    CLI parsing service for gitree tool. 

    Wraps argument parsing and validation into a class. Call parse_args
    to get a Config object.
    """

    @staticmethod
    def parse_args(ctx: AppContext) -> Config:
        """
        Public function to parse command-line arguments for the gitree tool.

        Returns:
            Config: Configuration object to be used in-place of args
        """

        ap = argparse.ArgumentParser(
            description="Print a directory tree (respects .gitignore).",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=ParsingService._examples_text()
        )

        ParsingService._add_positional_args(ctx, ap)
        ParsingService._add_general_options(ctx, ap)
        ParsingService._add_io_flags(ctx, ap)
        ParsingService._add_listing_flags(ctx, ap)
        ParsingService._add_listing_control_flags(ctx, ap)

        args = ap.parse_args()
        ctx.logger.log(ctx.logger.DEBUG, f"Parsed arguments: {args}")


        # Correct the arguments before returning to avoid complexity
        # in implementation in main function, then return a Config object
        args = ParsingService._correct_args(ctx, args)


        # Prepare the config object to return from this function
        config = Config(ctx, args)
        config.no_printing = config.copy or config.export or config.zip 
        return ParsingService._fix_contradicting_args(ctx, config)
    

    @staticmethod
    def _fix_contradicting_args(ctx: AppContext, config: Config) -> Config:
        """
        Prevents unexpected behaviour of the tool if contradictory options are used
        """
        # TODO: Implement this function
        return config

    
    @staticmethod
    def _correct_args(ctx: AppContext, args: argparse.Namespace) -> argparse.Namespace:
        """
        Correct and validate CLI arguments in place.
        """
        
        if getattr(args, "export", None) is not None:
            args.export = ParsingService._fix_output_path(
                ctx, args.export,
                default_extensions={"txt": ".txt", "json": ".json", "md": ".md"},
                format_str=args.format
            )

        if getattr(args, "zip", None) is not None:
            args.zip = ParsingService._fix_output_path(ctx, args.zip, default_extension=".zip")

        ctx.logger.log(ctx.logger.DEBUG, f"Corrected arguments: {args}")

        return args
    

    @staticmethod
    def _fix_output_path(ctx: AppContext, output_path: str, default_extension: str = "",
        default_extensions: dict | None = None, format_str: str = "") -> str:
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
    

    @staticmethod
    def _examples_text() -> str:
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


    @staticmethod
    def _add_positional_args(ctx: AppContext, ap: argparse.ArgumentParser):
        ap.add_argument(
            "paths",
            nargs="*",
            default=["."],
            help="Root paths (supports multiple directories and file patterns)",
        )


    @staticmethod
    def _add_general_options(ctx: AppContext, ap: argparse.ArgumentParser):
        general = ap.add_argument_group("general options")
        general.add_argument("-v", "--version", action="store_true", 
            default=argparse.SUPPRESS, help="Display the version of the tool")
        general.add_argument("--init-config", action="store_true", 
            default=argparse.SUPPRESS, help="Create a default config.json file")
        general.add_argument("--config-user", action="store_true", 
            default=argparse.SUPPRESS, help="Open config.json in the default editor")
        general.add_argument("--no-config", action="store_true", 
            default=argparse.SUPPRESS, help="Ignore config.json and use defaults")
        general.add_argument("--verbose", action="store_true", 
            default=argparse.SUPPRESS, help="Enable verbose output")


    @staticmethod
    def _add_io_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        io = ap.add_argument_group("output & export options")

        io.add_argument("-z", "--zip", 
            default=argparse.SUPPRESS, help="Create a zip archive of the given path")
        io.add_argument("--export", 
            default=argparse.SUPPRESS, help="Save tree structure to file")


    @staticmethod
    def _add_listing_flags(ctx: AppContext, ap: argparse.ArgumentParser):
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
        listing.add_argument("--override-files", action="store_true",
            default=argparse.SUPPRESS, help="Override existing files") 


    @staticmethod
    def _add_listing_control_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        listing_control = ap.add_argument_group("listing override options")

        listing_control.add_argument("--no-max-entries", action="store_true", 
            default=argparse.SUPPRESS, help="Disable max entries limit")
        listing_control.add_argument("--no-gitignore", action="store_true", 
            default=argparse.SUPPRESS, help="Ignore .gitignore rules")
        listing_control.add_argument("--no-max-items", action="store_true", 
            default=argparse.SUPPRESS, help="Show all items regardless of count")
        listing_control.add_argument("--no-files", action="store_true", 
            default=argparse.SUPPRESS, help="Hide files (only directories)")
