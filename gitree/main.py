# gitree/main.py
from __future__ import annotations
import sys
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from .services.tree_service import run_tree_mode
from .services.parsing_service import parse_args, correct_args
from .utilities.config import resolve_config
from .utilities.logger import Logger, OutputBuffer
from .services.basic_args_handling_service import handle_basic_cli_args, resolve_root_paths
from .services.zipping_service import zip_roots
from .services.interactive import get_interactive_file_selection
from pathlib import Path


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles argument parsing, configuration loading, and orchestrates the main
    functionality including tree printing, zipping, and file exports.

    For Contributors:
        - If you are adding features, make sure to keep the main function clean
        - Do not put implementation details here
        - Use services/ and utilities/ modules for logic, and import their functions here
    """
    args = parse_args()
    logger = Logger()
    output_buffer = OutputBuffer()


    # Resolve --no-contents-for paths
    args.no_contents_for = [Path(p).resolve() for p in args.no_contents_for]


    # Resolve configuration (handle user, global, and default config merging)
    args = resolve_config(args, logger=logger)


    # Fix any incorrect CLI args (paths missing extensions, etc.)
    args = correct_args(args)
    # This one bellow is also used for determining whether to draw tree or not
    no_output_mode = args.copy or args.output or args.zip 


    # if some specific Basic CLI args given, execute and return
    # Handles for --version, --init-config, --config-user, --no-config
    if handle_basic_cli_args(args, logger): no_output_mode = True


    # Validate and resolve all paths
    roots = resolve_root_paths(args, logger=logger)
    selected_files_map = {}     # Map to keep track of selected files per root


    if args.interactive:        # Get files map from interactive selection
        selected_files_map = get_interactive_file_selection(roots=roots,    
            output_buffer=output_buffer, logger=logger, args=args,
        )
        # Filter roots based on interactive selection
        roots = list(selected_files_map.keys())


    # if zipping is requested
    if args.zip is not None:
        zip_roots(args, roots, output_buffer, logger, selected_files_map)

    # else, print the tree normally
    else:       
        run_tree_mode(args, roots, output_buffer, logger, selected_files_map)


    # print the output only if not in no-output mode
    if not no_output_mode:
        output_buffer.flush()


    # print the log if verbose mode
    if args.verbose:
        if not no_output_mode: print()
        print("LOG:")
        logger.flush()


if __name__ == "__main__":
    main()
