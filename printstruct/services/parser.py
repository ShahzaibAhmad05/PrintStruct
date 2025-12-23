import argparse
import os
from ..utilities.utils import max_items_int, get_unused_file_path

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("path", nargs="?", default=".", help="Root path")
    ap.add_argument("--depth", type=int, default=None)
    ap.add_argument("--all", "-a", action="store_true")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--ignore-depth", type=int, default=None, help="Limit depth for --ignore patterns")
    ap.add_argument("--gitignore-depth", type=int, default=None)
    ap.add_argument("--no-gitignore", action="store_true")
    ap.add_argument("--max-items", type=max_items_int, default=20, help="Limit items shown per directory (default: 20). Use --no-limit for unlimited.")
    ap.add_argument("--version", "-v", action="store_true", help="Display the version of the tool")
    ap.add_argument("--zip", "-z", default=None, help="Create a zip file containing files under path (respects .gitignore)")
    ap.add_argument("--out", "-o", default=None, help="Save tree structure to file")
    ap.add_argument("--copy", "-c", action="store_true", help="Copy tree output to clipboard")
    ap.add_argument("--no-limit", action="store_true", help="Show all items regardless of count")
    return ap.parse_args()
