# gitree/services/copy_service.py

"""
Code file for housing CopyService Class. 

Static methods; copies exported output to clipboard
"""

# Dependencies
import pyperclip

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..services.export_service import ExportService
from ..utilities.logging_utility import Logger


class CopyService:
    """
    This class depends on file contents inclusion logic from ExportService.
    """
    
    @staticmethod
    def run(ctx: AppContext, config: Config, tree_data: dict) -> None:
        """
        Copy the exported project structure + file contents to clipboard,
        using the same format as --export.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict): The resolved tree dict
        """

        fmt = (getattr(config, "format", "") or "").strip().lower()

        if fmt in ("txt", "tree"):
            lines = ExportService._export_txt(ctx, tree_data)

        elif fmt == "md":
            lines = ExportService._export_md(ctx, tree_data)

        elif fmt == "json":
            lines = ExportService._export_json(ctx, tree_data)

        try:
            pyperclip.copy("\n".join(lines))
        except Exception as e:
            ctx.logger.log(Logger.ERROR, f"Failed to copy to clipboard: {e}")

        ctx.output_buffer.clear()
