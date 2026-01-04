# gitree/main.py

"""
Code file for housing the main function.
"""

# Default libs
import sys
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

# Deps from this project
from .services.tree_service import run_tree_mode
from .services.parsing_service import ParsingService
from .services.basic_args_handling_service import handle_basic_cli_args, resolve_root_paths
from .services.zipping_service import ZippingService
from .services.interactive import get_interactive_file_selection
from .objects.app_context import AppContext


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles the main workflow of the app.
    """

    # Initialize app context
    ctx = AppContext()


    # Prepare the config object (this has all the args now)
    config = ParsingService.parse_args(ctx)


    # if some specific Basic CLI args given, execute and return
    # Handles for --version, --init-config, --config-user, --no-config
    handle_basic_cli_args(ctx, config)


    # Validate and resolve all paths
    roots = resolve_root_paths(ctx, config)
    selected_files_map = {}     # Map to keep track of selected files per root


    # Handle interactive selection first
    if config.interactive:        # Get files map from interactive selection
        selected_files_map = get_interactive_file_selection(ctx, config, roots)
        # Filter roots based on interactive selection
        roots = list(selected_files_map.keys())


    # if zipping is requested
    if config.zip is not None:
        # Initialize ZippingService with common state
        zipping_service = ZippingService(ctx, config)
        zipping_service.zip_roots(config, roots, selected_files_map)


    # else, print the tree normally
    else:       
        run_tree_mode(ctx, config, roots, selected_files_map)


    # print the export only if not in no-export mode
    output_value_exists = not ctx.output_buffer.empty()
    if not config.no_printing and output_value_exists:
        ctx.output_buffer.flush()


    # print the log if verbose mode
    if config.verbose:
        if not config.no_printing and output_value_exists: 
            print()
        print("LOG:")
        ctx.logger.flush()


if __name__ == "__main__":
    main()
