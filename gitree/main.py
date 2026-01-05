# gitree/main.py

"""
Code file for housing the main function.
"""

# Default libs
import sys
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

# Deps from this project
from .services.parsing_service import ParsingService
from .services.general_options_service import GeneralOptionsService
from .services.resolve_items_service import ResolveItemsService
from .services.drawing_service import DrawingService
# from .services.zipping_service import ZippingService
from .objects.app_context import AppContext
from .services.interactive_selection_service import InteractiveSelectionService


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles the main workflow of the app.
    """

    # Initialize app context
    ctx = AppContext()


    # Prepare the config object (this has all the args now)
    config = ParsingService.parse_args(ctx)


    # if general options used, they are executed here 
    # Handles for --version, --init-config, --config-user, --no-config
    GeneralOptionsService.handle_args(ctx, config)


    # This service returns all the items to include resolved in a dict
    # Hover over ResolveItemsService to check the format which it returns
    resolved_root = ResolveItemsService.resolve_items(ctx, config)


    # Select files interactively if requested
    # TODO: this one is currently broken
    if config.interactive:
        resolved_root = InteractiveSelectionService.run(ctx, config, resolved_root)


    with open("test.json", "w") as file:
        import json     # Debug
        json.dump(resolved_root, file, indent=4, default=str)


    # Everything is ready
    # Now do the final operations
    if config.copy:
        pass

    elif config.export:
        pass

    elif config.zip:
        pass

    elif not config.no_printing:
        DrawingService.draw(ctx, config, resolved_root)


    # print the export only if not in no-export mode
    if not config.no_printing and not ctx.output_buffer.empty():
        ctx.output_buffer.flush()


    # print the log if verbose mode
    if config.verbose:
        if not config.no_printing and not ctx.output_buffer.empty(): 
            print()
        print("LOG:")
        ctx.logger.flush()


if __name__ == "__main__":
    main()
