# gitree/objects/app_context.py

"""
Context object for the app.

Helps avoid passing hundreds of args to functions and using global vars just 
for the app context. 
"""

# Deps in the same project
from ..utilities.logger import Logger, OutputBuffer


class AppContext:
    def __init__(self) -> None:
        """ Constructor for app ctx """
        self.logger = Logger()
        self.output_buffer = OutputBuffer()
