import argparse
import os
from ..utilities.utils import max_items_int, get_unused_file_path

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("path", nargs="?", default=".", help="Root path")
    ap.add_argument("--depth", type=int, default=None)
    ap.add_argument("-a", "--all", action="store_true")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--ignore-depth", type=int, default=None, help="Limit depth for --ignore patterns")
    ap.add_argument("--gitignore-depth", type=int, default=None)
    ap.add_argument("--no-gitignore", action="store_true")
    ap.add_argument("--max-items", type=max_items_int, default=20, help="Limit items shown per directory (default: 20). Use --no-limit for unlimited.")
    ap.add_argument("-v", "--version", action="store_true", help="Display the version of the tool")
    ap.add_argument("-z", "--zip", default=None, help="Create a zip file containing files under path (respects .gitignore)")
    ap.add_argument("-o", "--out", default=None, help="Save tree structure to file")
    ap.add_argument("-c", "--copy", action="store_true", help="Copy tree output to clipboard")
    ap.add_argument("--emoji", action="store_false", help="Show emojis in tree output")
    ap.add_argument("--summary",action="store_true",help="Print a summary of the number of files and folders at each level")
    ap.add_argument("--interactive", "-i", action="store_true", help="Interactive mode: select files to include")
    ap.add_argument("--include", nargs="*", default=[], help="Patterns of files to include (e.g. *.py)")
    ap.add_argument("--exclude", nargs="*", default=[], help="Patterns of files to exclude (e.g. *.pyc)")
    ap.add_argument("--init-config", action="store_true", help="Create a default config.json file in the current directory")
    ap.add_argument("--config-user", action="store_true", help="Open config.json in the default editor")
    ap.add_argument("--no-limit", action="store_true", help="Show all items regardless of count")
    ap.add_argument("--no-files", action="store_true", help="Hide files from the tree (only show directories)")
    ap.add_argument("--no-config", action="store_true", help="Ignore config.json and use hardcoded defaults")
    
    return ap.parse_args()
