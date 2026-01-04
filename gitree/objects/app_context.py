from ..utilities.logger import Logger, OutputBuffer
from dataclasses import dataclass


@dataclass
class AppContext:
    logger: Logger
    output: OutputBuffer
