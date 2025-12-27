import sys
from typing import List, Literal


class Logger:
    """
    Logger class for storing and flushing debug information.

    This class collects debug messages in memory and prints them
    all at once when flush() is called.
    """

    # Constant log levels
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
        
    # Dict for translating levels into names
    VALID_LEVEL = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


    def __init__(self):
        """
        Initialize the logger with an empty message and outputs list.
        """
        self._messages: List[str] = []


    def log(self, level: VALID_LEVEL ,message: str) -> None:
        """
        Store a debug message.

        Args:
            message: The debug message to store
        """
        self._messages.append(self._append_level(level, message))


    def flush(self) -> None:
        """
        Print all stored debug messages to the terminal and clear the buffer.
        """
        if not self._messages:
            print("No log messages to display.")
            return
        
        for message in self._messages:
            print(message)
        self._messages.clear()


    def clear(self) -> None:
        """
        Clear all stored messages without printing them.
        """
        self._messages.clear()


    def __len__(self) -> int:
        """
        Return the number of stored messages.

        Returns:
            Number of messages in the buffer
        """
        return len(self._messages)
    

    def get_logs(self) -> List[str]:
        """
        Get a copy of the stored messages.

        Returns:
            List of stored messages
        """
        return self._messages.copy()
    

    def _append_level(self, level: VALID_LEVEL, message: str) -> str:
        """
        Append the log level to the message.

        Args:
            level: The log level
            message: The original message

        Returns:
            The message prefixed with the log level
        """
        return f"[{level}] {message}"


class OutputBuffer:
    """
    A custom output buffer to capture stdout writes. A wrapper around Logger.
    """

    def __init__(self):
        """
        Initialize the output buffer with a reference to a Logger.

        Args:
            logger: Logger instance to store output messages
        """
        self.logger = Logger()


    def write(self, message: str) -> None:
        """
        Write a message to the logger's output storage.

        Args:
            message: The message to write
        """
        self.logger.store(message)


    def flush(self) -> None:
        """
        Flush the output buffer.
        """
        for message in self.logger.get_logs():
            print(message)  # Print each message on a newline
