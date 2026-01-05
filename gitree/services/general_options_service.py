# gitree/services/general_options_service.py

"""
Code file for housing GeneralOptionsService.
"""

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..utilities.config_utility import create_default_config, open_config_in_editor
from gitree import __version__


class GeneralOptionsService:
    """
    Service to handle all General options.
    """
    
    @staticmethod
    def handle_args(ctx: AppContext, config: Config) -> None:
        """
        Public function to handle general options and point 
        no_printing attr to True if one was handled.

        Args:
            config (Config): config object created in main
        """

        if config.init_config:
            create_default_config(ctx)
        elif config.config_user:
            open_config_in_editor(ctx)
        elif config.version:
            print(__version__)

        # Set no_printing to True if any were handled
        config.no_printing = config.init_config or config.config_user or config.version
