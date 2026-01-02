from ..utilities.config import create_default_config, open_config_in_editor
from ..utilities.logger import Logger, OutputBuffer
import argparse, glob, sys
from pathlib import Path
from typing import List


def get_project_version() -> str:
    """
    Returns the current version of the project
    """
    return "0.3.0"


def resolve_root_paths(args: argparse.Namespace, logger: Logger) -> List[Path]:
    roots: List[Path] = []
    print(roots)

    # If user didn't pass any paths, default to where they ran the command
    if not getattr(args, "paths", None):
        return [Path.cwd().resolve()]

    for path_str in args.paths:

        if '*' in path_str or '?' in path_str:
            matches = glob.glob(path_str)
            if not matches:
                logger.log(Logger.ERROR, f"no matches found for pattern: {path_str}")
                continue
            for match in matches:
                roots.append(Path(match).resolve())
                
        else:
            path = Path(path_str).resolve()
            if not path.exists():
                logger.log(Logger.ERROR, f"path not found: {path}", file=sys.stderr)
                continue
            roots.append(path)

    return roots


def handle_basic_cli_args(args: argparse.Namespace, logger: Logger) -> bool:
    """
    Handle basic CLI args and returns True if one was handled.

    Args:
        args: Parsed argparse.Namespace object
        logger: Logger instance for logging
    """
    if args.init_config:
        create_default_config(logger)
        return True

    if args.config_user:
        open_config_in_editor(logger)
        return True

    if args.version:
        print(get_project_version())
        return True

    return False
