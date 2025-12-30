import sys
from typing import List, Literal, Dict


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


    def __init__(self):
        """
        Initialize the logger with an empty message and outputs list.
        """
        self._LEVEL_NAMES: Dict[int, str] = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
        }
        self._messages: List[str] = []


    def log(self, level: str | None, message: str) -> None:
        """
        Store a debug message.

        Args:
            message: The debug message to store
        """
        if level is None:
            self._messages.append(message)
        else:  
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
    

    def _append_level(self, level: str, message: str) -> str:
        """
        Append the log level to the message.

        Args:
            level: The log level
            message: The original message

        Returns:
            The message prefixed with the log level
        """
        return f"[{self._LEVEL_NAMES[level]}] {message}"


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
        self.logger.log(level=None, message=message)


    def flush(self) -> None:
        """
        Flush the output buffer.
        """
        if self.logger.get_logs():
            self.logger.flush()


    def get_value(self) -> List[str]:
        """
        Get the entire contents of the output buffer as a list of strings.

        Returns:
            str: The contents of the output buffer
        """
        return "\n".join(self.logger.get_logs())
    

    def clear(self) -> None:   
        """
        Clear the output buffer.
        """
        self.logger.clear()
    