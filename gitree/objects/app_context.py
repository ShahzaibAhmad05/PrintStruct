# gitree/objects/app_context.py

"""
Context object for the app.

Helps avoid passing hundreds of args to functions and using global vars just 
for the app context. 
"""

# Default libs
from dataclasses import dataclass

# Deps in the same project
from ..utilities.logger import Logger, OutputBuffer


@dataclass
class AppContext:
    logger: Logger
    output: OutputBuffer
