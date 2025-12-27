from ..utilities.config import create_default_config, open_config_in_editor
import argparse, glob, sys
from pathlib import Path
from typing import List


def get_project_version() -> str:
    """
    Returns the current version of the project
    """
    return "0.0.0 (dev)"


def resolve_root_paths(args: argparse.Namespace) -> List[str]:
    """
    Resolve and validate root paths from CLI arguments.

    Args:
        args: Parsed argparse.Namespace object with a `paths` attribute

    Returns:
        A list of resolved Path objects
    """
    roots = []
    
    for path_str in args.paths:
        # Check if path contains glob wildcards
        if '*' in path_str or '?' in path_str:
            # Expand glob pattern
            matches = glob.glob(path_str)
            if not matches:
                print(f"Error: no matches found for pattern: {path_str}", file=sys.stderr)
                raise SystemExit(1)
            for match in matches:
                roots.append(Path(match).resolve())
        else:
            # Regular path without wildcards
            path = Path(path_str).resolve()
            if not path.exists():
                print(f"Error: path not found: {path}", file=sys.stderr)
                raise SystemExit(1)
            roots.append(path)

    return roots


def handle_basic_cli_args(args: argparse.Namespace) -> bool:
    """
    Handle basic CLI args and returns True if one was handled.

    Args:
        args: Parsed argparse.Namespace object
    """
    if args.init_config:
        create_default_config()
        return True
    
    if args.config_user:
        open_config_in_editor()
        return True

    if args.version:
        print(get_project_version())
        return True
    
    return False
