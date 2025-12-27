import argparse
from pathlib import Path
from ..utilities.utils import max_items_int


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the gitree tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing all configuration options
    """
    ap = argparse.ArgumentParser(
        description="Print a directory tree (respects .gitignore)."
    )

    # positional arg that should keep defaults
    ap.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Root paths (supports multiple directories and file patterns)",
    )

    # Config-mergeable options
    # (SUPPRESS means: absent unless user explicitly sets them)
    ap.add_argument(
        "--max-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Maximum depth to traverse",
    )
    ap.add_argument(
        "--hidden-items",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show hidden files and directories",
    )
    ap.add_argument(
        "--exclude",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Patterns of files to exclude (e.g. *.pyc, __pycache__)",
    )
    ap.add_argument(
        "--exclude-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Limit depth for --exclude patterns",
    )
    ap.add_argument(
        "--gitignore-depth",
        type=int,
        default=argparse.SUPPRESS,
        help="Limit depth for .gitignore processing",
    )
    ap.add_argument(
        "--no-gitignore",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Ignore .gitignore rules",
    )
    ap.add_argument(
        "--max-items",
        type=max_items_int,
        default=argparse.SUPPRESS,
        help="Limit items shown per directory (use --no-limit for unlimited)",
    )
    ap.add_argument(
        "--overrride-files",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Override files even if they exist (for file outputs)"
    )
    ap.add_argument(
        "-z", "--zip",
        default=argparse.SUPPRESS,
        help="Create a zip file containing files under path (respects .gitignore)",
    )
    ap.add_argument(
        "--json",
        metavar="FILE",
        default=argparse.SUPPRESS,
        help="Export tree as JSON to specified file",
    )
    ap.add_argument(
        "--txt",
        metavar="FILE",
        default=argparse.SUPPRESS,
        help="Export tree as text to specified file",
    )
    ap.add_argument(
        "--md",
        metavar="FILE",
        default=argparse.SUPPRESS,
        help="Export tree as Markdown to specified file",
    )
    ap.add_argument(
        "-o", "--output",
        default=argparse.SUPPRESS,
        help="Save tree structure to file",
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
        "-s", "--summary",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Print a summary of the number of files and folders at each level",
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
        "--include-file-type", "--include-file-types",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Include files of multiple types, or a specific type (e.g. png jpg)",
    )
    ap.add_argument(
        "--no-limit",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show all items regardless of count",
    )
    ap.add_argument(
        "--no-files",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Hide files from the tree (only show directories)",
    )
    ap.add_argument(
        "--no-contents",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Don't include file contents when exporting",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Enable verbose output for debugging",
    )

    # Control / meta flags (not config-backed)
    ap.add_argument(
        "-v", "--version",
        action="store_true",
        help="Display the version of the tool",
    )
    ap.add_argument(
        "--init-config",
        action="store_true",
        help="Create a default config.json file in the current directory",
    )
    ap.add_argument(
        "--config-user",
        action="store_true",
        help="Open config.json in the default editor",
    )
    ap.add_argument(
        "--no-config",
        action="store_true",
        help="Ignore config.json and use hardcoded defaults",
    )
    ap.add_argument(
        "--no-contents-for",
        nargs="+",
        default=[],
        metavar="PATH",
        help="Do not save file contents for specific files or directories"
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
        args.output = fix_output_path(args.output, default_extension=".txt")
    if args.zip is not None:
        args.zip = fix_output_path(args.zip, default_extension=".zip")

    return args


def fix_output_path(output_path: str, default_extension: str) -> str:
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
        path = path.with_suffix(default_extension)

    return str(path)
