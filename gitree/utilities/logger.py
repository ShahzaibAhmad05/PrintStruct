import sys
from typing import List


class Logger:
    """
    Logger class for storing and flushing debug information.

    This class collects debug messages in memory and prints them
    all at once when flush() is called.
    """

    def __init__(self):
        """
        Initialize the logger with an empty message list.
        """
        self._messages: List[str] = []

    def log(self, message: str) -> None:
        """
        Store a debug message.

        Args:
            message: The debug message to store
        """
        self._messages.append(message)

    def flush(self) -> None:
        """
        Print all stored debug messages to the terminal and clear the buffer.
        """
        for message in self._messages:
            print(message, file=sys.stderr)
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
