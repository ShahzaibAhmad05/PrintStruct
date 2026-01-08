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
        if not config.no_color:
            config.no_color = config.copy or config.export

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
                default_extensions={"tree": ".txt", "json": ".json", "md": ".md"},
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
            Usage:
            - gitree first selects the items (files/dirs) using the path 
                given, then decides whether to zip/export the project
                (with contents), or to just print the tree structure of the
                project.

            - It respects gitignore rules by default unless --no-gitignore
                is used.
        
                
            Use-case Examples:

            gitree
                Print tree structure of current directory

            gitree tests/*.py --copy
                Select all .py files under the folder tests and 
                copy their contents along with the tree structure,
                useful for pasting codebase context to LLMs.

            gitree tests .github
                Select items only under these two folders, find 
                their parent folder, and print the tree structure
                for those.

            gitree --export proj --format json
                Export all items and their contents under the current 
                directory in a file named proj.json

            gitree --zip project
                Create a zip named project.zip of the whole project 
                respecting gitignore rules.
        """.strip()


    @staticmethod
    def _add_positional_args(ctx: AppContext, ap: argparse.ArgumentParser):
        ap.add_argument(
            "paths",
            nargs="*",
            default=["."],
            help="Root paths (supports multiple directories and file patterns), "
                "defaults to the current working directory",
        )


    @staticmethod
    def _add_general_options(ctx: AppContext, ap: argparse.ArgumentParser):
        general = ap.add_argument_group("general options")
        
        general.add_argument("-v", "--version", action="store_true",
            default=argparse.SUPPRESS,
            help="Display the version number of the tool")

        general.add_argument("--config-user", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Create a default config.json file in the current directory"
                " and open that file in the default editor")
        
        general.add_argument("--no-config", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Ignore both user-level and global-level config.json and use"
                " default and cli values for configuration")
        
        general.add_argument("--verbose", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Enable logger output to the console. Enabling this prints a log"
            " after the full workflow run. Helpful for debugging.")


    @staticmethod
    def _add_io_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        io = ap.add_argument_group("output & export options")

        io.add_argument("-z", "--zip", 
            default=argparse.SUPPRESS, 
            help="Create a zip archive of the given directory respecting gitignore rules.")
        
        io.add_argument("--export", 
            default=argparse.SUPPRESS, 
            help="Save project structure along with it's contents to a file"
                " with the format specified using --format")


    @staticmethod
    def _add_listing_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        listing = ap.add_argument_group("listing options")

        listing.add_argument("--format", choices=["tree", "json", "md"], 
            default="tree", help="Format output only")

        listing.add_argument("--max-items", type=max_items_int, 
            default=argparse.SUPPRESS, 
            help="Limit items to be selected per directory")
        
        listing.add_argument("--max-entries", type=max_entries_int, 
            default=argparse.SUPPRESS, 
            help="Limit entries (files/dirs) to be selected for the overall output")
        
        listing.add_argument("--max-depth", type=int, 
            default=argparse.SUPPRESS, 
            help="Maximum depth to traverse when selecting files")
        
        listing.add_argument("--gitignore-depth", type=int, 
            default=argparse.SUPPRESS, 
            help="Limit depth to look for during .gitignore processing")
        
        listing.add_argument("--hidden-items", action="store_true", 
            default=argparse.SUPPRESS, help="Show hidden files and directories")
        
        listing.add_argument("--exclude", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to specifically exclude")
        
        listing.add_argument("--exclude-depth", type=int, 
            default=argparse.SUPPRESS, help="Limit depth for exclude patterns")
        
        listing.add_argument("--include", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to specifically include")
        
        listing.add_argument("--include-file-types", "--include-file-type", nargs="*", 
            default=argparse.SUPPRESS, dest="include_file_types", 
            help="Include files of certain types")
        
        listing.add_argument("-c", "--copy", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Copy file contents and project structure to clipboard."
                " Similar to --export but copies to the clipboard instead")
        
        listing.add_argument("-e", "--emoji", action="store_true", 
            default=argparse.SUPPRESS, help="Show emojis in the output")
        
        listing.add_argument("-i", "--interactive", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Use interactive mode for further file selection")
        
        listing.add_argument("--files-first", action="store_true", 
            default=argparse.SUPPRESS, help="Print files before directories")
        
        listing.add_argument("--no-color", action="store_true", 
            default=argparse.SUPPRESS, help="Disable colored output")
        
        listing.add_argument("--no-contents", action="store_true", 
            default=argparse.SUPPRESS, help="Don't include file contents in export/copy")
        
        listing.add_argument("--no-contents-for", nargs="+",
            default=argparse.SUPPRESS, metavar="PATH",
            help="Exclude contents for specific files for export/copy")
        
        listing.add_argument("--max-file-size", type=float,
            default=argparse.SUPPRESS, metavar="MB", dest="max_file_size",
            help="Maximum file size in MB to include in exports (default: 1.0)")
        
        listing.add_argument("--override-files", action="store_true",
            default=argparse.SUPPRESS, help="Override existing files") 


    @staticmethod
    def _add_listing_control_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        listing_control = ap.add_argument_group("listing override options")

        listing_control.add_argument("--no-max-entries", action="store_true", 
            default=argparse.SUPPRESS, help="Disable --max-entries limit")
        
        listing_control.add_argument("--no-max-items", action="store_true", 
            default=argparse.SUPPRESS, help="Disable --max-items limit")
        
        listing_control.add_argument("--no-gitignore", action="store_true", 
            default=argparse.SUPPRESS, help="Do not use .gitignore rules")
        
        listing_control.add_argument("--no-files", action="store_true", 
            default=argparse.SUPPRESS, help="Hide files (show only directories)")
