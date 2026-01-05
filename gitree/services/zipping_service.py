# gitree/services/drawing_service.py

"""
Code file for housing ZippingService Class

Static methods; draws into the output_buffer in AppContext
"""

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class ZippingService:

    @staticmethod
    def zip(ctx: AppContext, config: Config) -> None:
        pass