# gitree/services/basic_args_handling_service.py
from ..utilities.config import create_default_config, open_config_in_editor
from ..objects.app_context import AppContext
from ..objects.config import Config
import argparse, glob, sys
from pathlib import Path
from typing import List
from gitree import __version__


def resolve_root_paths(ctx: AppContext, args: argparse.Namespace) -> List[Path]:
    roots: list[Path] = []

    def add_root(p: Path):
        p = p.resolve()

        # files → parent directory
        if p.is_file():
            p = p.parent

        # dedupe + collapse nested roots
        for i, r in enumerate(list(roots)):
            if p == r or p.is_relative_to(r):
                return
            if r.is_relative_to(p):
                roots[i] = p
                return

        roots.append(p)

    for path_str in args.paths:
        # force recursive behavior for "*.py"
        if path_str.strip() == "*.py":
            path_str = "**/*.py"

        if any(ch in path_str for ch in "*?["):
            matches = glob.glob(path_str, recursive=True)
            if not matches:
                ctx.logger.log(ctx.logger.WARNING, f"no matches found for pattern: {path_str}")
                continue
            for m in matches:
                add_root(Path(m))
        else:
            p = Path(path_str).resolve()
            if not p.exists():
                ctx.logger.log(ctx.logger.ERROR, f"path not found: {p}")
                print(f"ERROR: path not found {p}", file=sys.stderr)
                continue
            add_root(p)
            
    return roots


def handle_basic_cli_args(ctx: AppContext, config: Config) -> None:
    """
    Handle basic CLI args and point no_printing aattr to false if one was handled.

    Args:
        config (Config): config object created in main
    """

    if config.init_config:
        create_default_config(ctx)
        config.no_printing = False

    if config.config_user:
        open_config_in_editor(ctx)
        config.no_printing = False

    if config.version:
        print(__version__)
        config.no_printing = False
