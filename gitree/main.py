# gitree/main.py
from __future__ import annotations
import sys
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from .services.tree_service import run_tree_mode
from .services.parsing_service import ParsingService
from .utilities.logger import Logger, OutputBuffer
from .services.basic_args_handling_service import handle_basic_cli_args, resolve_root_paths
from .services.zipping_service import zip_roots
from .services.interactive import get_interactive_file_selection
from .objects.config import Config
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
    # Instances for Logger and Output Buffer
    # passed to every class instance
    logger = Logger()
    output_buffer = OutputBuffer()


    # Get the CLI args
    parsingService = ParsingService(logger=logger, output_buffer=output_buffer)
    config = parsingService.parse_args()


    # This one bellow is also used for determining whether to draw tree or not
    no_output_mode = config.copy or config.output or config.zip 


    # if some specific Basic CLI args given, execute and return
    # Handles for --version, --init-config, --config-user, --no-config
    if handle_basic_cli_args(config, logger): no_output_mode = True


    # Validate and resolve all paths
    roots = resolve_root_paths(config, logger=logger)
    selected_files_map = {}     # Map to keep track of selected files per root


    if config.interactive:        # Get files map from interactive selection
        selected_files_map = get_interactive_file_selection(roots=roots,    
            output_buffer=output_buffer, logger=logger, args=config,
        )
        # Filter roots based on interactive selection
        roots = list(selected_files_map.keys())


    # if zipping is requested
    if config.zip is not None:
        zip_roots(config, roots, output_buffer, logger, selected_files_map)

    # else, print the tree normally
    else:       
        run_tree_mode(config, roots, output_buffer, logger, selected_files_map)


    # print the output only if not in no-output mode
    output_value_exists = not output_buffer.empty()
    if not no_output_mode and output_value_exists:
        output_buffer.flush()


    # print the log if verbose mode
    if config.verbose:
        if not no_output_mode and output_value_exists: print()
        print("LOG:")
        logger.flush()


if __name__ == "__main__":
    main()
