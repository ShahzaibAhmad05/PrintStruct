import argparse
from pathlib import Path
from ..utilities.utils import max_items_int
from ..utilities.utils import max_lines_int


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the gitree tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing all configuration options
    """
    ap = argparse.ArgumentParser(
        description="Print a directory tree (respects .gitignore).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
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
    """
    )

    # -------------------------
    # Positional arguments
    # -------------------------
    ap.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Root paths (supports multiple directories and file patterns)",
    )

    # =========================
    # BASIC / META CLI FLAGS
    # =========================
    basic = ap.add_argument_group("Basic CLI flags")

    basic.add_argument(
        "-v", "--version",
        action="store_true",
        help="Display the version of the tool",
    )
    basic.add_argument(
        "--init-config",
        action="store_true",
        help="Create a default config.json file in the current directory",
    )
    basic.add_argument(
        "--config-user",
        action="store_true",
        help="Open config.json in the default editor",
    )
    basic.add_argument(
        "--no-config",
        action="store_true",
        help="Ignore config.json and use hardcoded defaults",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Enable verbose output for debugging",
    )

    # =========================
    # INPUT / OUTPUT FLAGS
    # =========================
    io = ap.add_argument_group("Input / Output flags")

    io.add_argument(
        "-z", "--zip",
        default=argparse.SUPPRESS,
        help="Create a zip file containing files under path (respects .gitignore)",
    )
    io.add_argument(
        "--no-contents",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Don't include file contents when exporting",
    )
    io.add_argument(
        "--no-contents-for",
        nargs="+",
        default=[],
        metavar="PATH",
        help="Do not save file contents for specific files or directories",
    )
    io.add_argument(
        "--overrride-files",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Override files even if they exist (for file outputs)",
    )
    ap.add_argument(
        "-o", "--output",
        default=argparse.SUPPRESS,
        help="Save tree structure to file",
    )

    # =========================
    # LISTING / TREE FLAGS
    # =========================
    listing = ap.add_argument_group("Listing flags")

    ap.add_argument(
        "--format",
        choices=["txt", "json", "md"],
        default="txt",
        help="Format output only (txt, json, md)"
    )
    listing.add_argument(
        "--max-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Maximum depth to traverse",
    )
    ap.add_argument(
        "--max-lines",
        type=max_lines_int,
        default=argparse.SUPPRESS,
        help="Limit lines shown in the tree output",
    )
    listing.add_argument(
        "--hidden-items",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show hidden files and directories",
    )
    listing.add_argument(
        "--exclude",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Patterns of files to exclude (e.g. *.pyc, __pycache__)",
    )
    listing.add_argument(
        "--exclude-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Limit depth for --exclude patterns",
    )
    listing.add_argument(
        "--gitignore-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Limit depth for .gitignore processing",
    )
    listing.add_argument(
        "--max-items",
        type=max_items_int,
        default=argparse.SUPPRESS,
        help="Limit items shown per directory (use --no-limit for unlimited)",
    )
    ap.add_argument(
        "-c", "--copy",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Copy tree output to clipboard",
    )
    ap.add_argument(
        "-e", "--emoji",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show emojis in tree output, default is false",
    )
    ap.add_argument(
        "-i", "--interactive",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Interactive mode: select files to include",
    )
    ap.add_argument(
        "--include",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Patterns of files to include (e.g. *.py)",
    )
    ap.add_argument(
        "--include-file-types", "--include-file-type",
        nargs="*",
        default=argparse.SUPPRESS,
        dest="include_file_types",
        help="Include files of multiple types, or a specific type (e.g. png jpg)",
    )
    listing.add_argument(
        "-s", "--summary",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Print a summary of the number of files and folders at each level",
    )
    listing.add_argument(
        "--files-first",
        action="store_true",
        default=False,
        help="Print files before directories in the tree output",
    )
    ap.add_argument(
        "--no-color",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Disable colorized output",
    )

    # =========================
    # LISTING CONTROL FLAGS
    # =========================
    listing_control = ap.add_argument_group("Listing control flags",
        "Control flags to disable or negate listing behaviors")

    listing_control.add_argument(
        "--no-max-lines",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Disable max lines limit",
    )
    listing_control.add_argument(
        "--no-gitignore",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Ignore .gitignore rules",
    )
    listing_control.add_argument(
        "--no-limit",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show all items regardless of count",
    )
    listing_control.add_argument(
        "--no-files",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Hide files from the tree (only show directories)",
    )

    return ap.parse_args()

def correct_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    Correct and validate CLI arguments in place.

    Args:
        args: Parsed argparse.Namespace object

    Returns:
        Corrected argparse.Namespace object
    """
    # Fix output path if specified incorrectly
    if args.output is not None:
        args.output = fix_output_path(args.output, 
                        default_extensions={"txt": ".txt", "json": ".json", "md": ".md"}, 
                        format_str=args.format)
    if args.zip is not None:
        args.zip = fix_output_path(args.zip, default_extension=".zip")

    return args


def fix_output_path(output_path: str, default_extension: str="",
                    default_extensions: dict={}, format_str: str="") -> str:
    """
    Ensure the output path has a .txt extension.

    Args:
        output_path: The original output path string
        extension: The desired file extension (e.g., ".txt")

    Returns:
        The modified output path string with .txt extension if needed
    """
    path = Path(output_path)
    if path.suffix == '':
        if default_extension:
            path = path.with_suffix(default_extension)
        elif default_extensions:
            path = path.with_suffix(default_extensions[format_str])

    return str(path)
