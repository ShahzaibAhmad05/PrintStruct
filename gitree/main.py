"""
Code file for housing the main function.
"""

# Default libs
import sys, time
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

# Deps from this project
from .services.parsing_service import ParsingService
from .services.general_options_service import GeneralOptionsService
from .services.resolve_items_service import ResolveItemsService
from .services.drawing_service import DrawingService
from .services.zipping_service import ZippingService
from .services.export_service import ExportService
from .services.copy_service import CopyService
from .services.analysis_service import AnalysisService  # <-- added

from .objects.app_context import AppContext
from .objects.config import Config
from .utilities.logging_utility import Logger
from .services.interactive_selection_service import InteractiveSelectionService


def flush_buffers(ctx: AppContext, config: Config):
    """ 
    Handle flushing the buffers. 
    """

    # print the export only if not in no_printing and buffer not empty
    if not config.no_printing and not ctx.output_buffer.empty():
        ctx.output_buffer.flush()

    # print the log if verbose mode
    if config.verbose:
        if not config.no_printing and not ctx.output_buffer.empty(): 
            print()
        print("LOG:")
        ctx.logger.flush()


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles the main workflow of the app.
    """
    
    # Record time for performance noting
    start_time = time.time()

    # Initialize app context
    ctx = AppContext()

    # Prepare the config object (this has all the args now)
    config = ParsingService.parse_args(ctx)

    # Enable printing explicitly for analysis
    if getattr(config, "analysis", False):
        config.no_printing = False

    # if general options used, they are executed here 
    # Handles for --version, --init-config, --config-user, --no-config
    GeneralOptionsService.handle_args(ctx, config)

    # This service returns all the items to include resolved in a dict
    resolved_root = ResolveItemsService.resolve_items(ctx, config)

    # Select files interactively if requested
    # NOTE: this one is currently broken
    if config.interactive:
        resolved_root = InteractiveSelectionService.run(ctx, config, resolved_root)

    # handle --analysis ---
    if getattr(config, "analysis", False):
        analysis_service = AnalysisService(resolved_root)
        analysis_result = analysis_service.run_analysis()
        print(f"Analysis complete. Saved {len(analysis_result)} items to 'analysis.json'.")
        return

    # Everything is ready
    # Now do the final operations
    if config.zip:
        ZippingService.run(ctx, config, resolved_root)

    else:
        DrawingService.draw(ctx, config, resolved_root)
        
        if config.copy:
            CopyService.run(ctx, config, resolved_root)

        elif config.export:
            ExportService.run(ctx, config, resolved_root)

    # Log performance (time)
    ctx.logger.log(Logger.INFO, f"Total time for run: {int((time.time()-start_time)*1000)} ms")

    # Flush the buffers to the console before exiting
    flush_buffers(ctx, config)


if __name__ == "__main__":
    main()
