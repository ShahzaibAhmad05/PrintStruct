import argparse
import os
from ..utilities.utils import max_items_int, get_unused_file_path

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the gitree tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing all configuration options
    """
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("paths", nargs="*", default=["."], help="Root paths (supports multiple directories and file patterns)")
    ap.add_argument("--max-depth", type=int, default=None, help="Maximum depth to traverse")
    ap.add_argument("--hidden-items", action="store_true", help="Show hidden files and directories")
    ap.add_argument("--exclude", nargs="*", default=[], help="Patterns of files to exclude (e.g. *.pyc, __pycache__)")
    ap.add_argument("--exclude-depth", type=int, default=None, help="Limit depth for --exclude patterns")
    ap.add_argument("--gitignore-depth", type=int, default=None)
    ap.add_argument("--no-gitignore", action="store_true")
    ap.add_argument("--max-items", type=max_items_int, default=20, help="Limit items shown per directory (default: 20). Use --no-limit for unlimited.")
    ap.add_argument("-v", "--version", action="store_true", help="Display the version of the tool")
    ap.add_argument("-z", "--zip", default=None, help="Create a zip file containing files under path (respects .gitignore)")
    ap.add_argument("--json", default=None, metavar="FILE", help="Export tree as JSON to specified file")
    ap.add_argument("--txt", default=None, metavar="FILE", help="Export tree as text to specified file")
    ap.add_argument("--md", default=None, metavar="FILE", help="Export tree as Markdown to specified file")
    ap.add_argument("-o", "--output", default=None, help="Save tree structure to file")
    ap.add_argument("-c", "--copy", action="store_true", help="Copy tree output to clipboard")
    ap.add_argument("-e", "--emoji", action="store_false", help="Show emojis in tree output")
    ap.add_argument("--summary",action="store_true",help="Print a summary of the number of files and folders at each level")
    ap.add_argument("-i", "--interactive", action="store_true", help="Interactive mode: select files to include")
    ap.add_argument("--include", nargs="*", default=[], help="Patterns of files to include (e.g. *.py)")
    ap.add_argument("--include-file-type", type=str, default=None, help="Include files of a specific type (e.g. json, py)")
    ap.add_argument("--include-file-types", nargs="*", default=[], help="Include files of multiple types (e.g. png jpg)")
    ap.add_argument("--init-config", action="store_true", help="Create a default config.json file in the current directory")
    ap.add_argument("--config-user", action="store_true", help="Open config.json in the default editor")
    ap.add_argument("--no-limit", action="store_true", help="Show all items regardless of count")
    ap.add_argument("--no-files", action="store_true", help="Hide files from the tree (only show directories)")
    ap.add_argument("--no-config", action="store_true", help="Ignore config.json and use hardcoded defaults")
    ap.add_argument("--no-contents", action="store_true", help="Don't include file contents when exporting to JSON, TXT, or MD formats")

    return ap.parse_args()
