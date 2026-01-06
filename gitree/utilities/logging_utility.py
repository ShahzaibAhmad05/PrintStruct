# gitree/utilities/logger.py

"""
Code file for housing Logger and OutputBuffer classes.
"""


class Logger:
    """
    Logger class for storing and flushing debug information.

    Collect debug messages in memory via log() and print them
    all at once using flush() method.
    """

    # Constant log levels
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


    def __init__(self):
        """
        Initialize the logger with an empty buffer.
        """

        self._LEVEL_NAMES: dict[int, str] = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
        }
        self._messages: list[str] = []


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
        self.clear()


    def clear(self) -> None:
        """
        Clear all stored messages without printing them.
        """

        self._messages.clear()

    
    def empty(self) -> bool:
        """ 
        Check if the logger is empty. Uses the __len__ function.
        """

        return len(self) == 0
    

    def get_logs(self) -> list[str]:
        """
        Get a copy of the stored messages in the buffer.

        Returns:
            List[str]: a list of the stored messages
        """

        return self._messages.copy()


    def __len__(self) -> int:
        """
        Return the number of stored messages.

        Returns:
            Number of messages in the buffer
        """

        return len(self._messages)
    

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


class OutputBuffer(Logger):
    """
    A custom output buffer to capture stdout writes. A wrapper around Logger.
    """

    def __init__(self):
        """
        Initialize the output buffer with a reference to a Logger.
        """
        super().__init__()


    def write(self, message: str) -> None:
        """
        Write a message to the logger's output storage.

        Args:
            message: The message to write
        """
        super().log(level=None, message=message)


    def get_value(self) -> list[str]:
        """
        Get the entire contents of the output buffer as a list of strings.

        Returns:
            str: The contents of the output buffer
        """
        return super().get_logs()
    

    def flush(self) -> None:
        """ 
        A modification for the parent class flush() function. Flushes the
        buffer to the terminal.
        """

        if super().empty():
            return      # Do not print anything

        for message in self.get_value():
            print(message)
    