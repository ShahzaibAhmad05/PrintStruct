# gitree/utilities/color_utility.py

"""
Code file for housing Color utility class

Static methods; wraps text with ANSI color escape codes
"""


class Color:
    """
    Utility class for wrapping text with ANSI color escape codes.
    """

    # Reset / styles
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    GREY = "\033[90m"        # aka bright black
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    @staticmethod
    def _wrap(code: str, text: str, reset: str=RESET) -> str:
        return f"{code}{text}{reset}"

    def default(text: str) -> str:
        return Color._wrap("", text, "")

    # styles
    @staticmethod
    def bold(text: str) -> str:
        return Color._wrap(Color.BOLD, text)

    @staticmethod
    def dim(text: str) -> str:
        return Color._wrap(Color.DIM, text)

    # standard colors
    @staticmethod
    def black(text: str) -> str:
        return Color._wrap(Color.BLACK, text)

    @staticmethod
    def red(text: str) -> str:
        return Color._wrap(Color.RED, text)

    @staticmethod
    def green(text: str) -> str:
        return Color._wrap(Color.GREEN, text)

    @staticmethod
    def yellow(text: str) -> str:
        return Color._wrap(Color.YELLOW, text)

    @staticmethod
    def blue(text: str) -> str:
        return Color._wrap(Color.BLUE, text)

    @staticmethod
    def magenta(text: str) -> str:
        return Color._wrap(Color.MAGENTA, text)

    @staticmethod
    def cyan(text: str) -> str:
        return Color._wrap(Color.CYAN, text)

    @staticmethod
    def white(text: str) -> str:
        return Color._wrap(Color.WHITE, text)

    # bright colors
    @staticmethod
    def grey(text: str) -> str:
        return Color._wrap(Color.GREY, text)

    @staticmethod
    def bright_red(text: str) -> str:
        return Color._wrap(Color.BRIGHT_RED, text)

    @staticmethod
    def bright_green(text: str) -> str:
        return Color._wrap(Color.BRIGHT_GREEN, text)

    @staticmethod
    def bright_yellow(text: str) -> str:
        return Color._wrap(Color.BRIGHT_YELLOW, text)

    @staticmethod
    def bright_blue(text: str) -> str:
        return Color._wrap(Color.BRIGHT_BLUE, text)

    @staticmethod
    def bright_magenta(text: str) -> str:
        return Color._wrap(Color.BRIGHT_MAGENTA, text)

    @staticmethod
    def bright_cyan(text: str) -> str:
        return Color._wrap(Color.BRIGHT_CYAN, text)

    @staticmethod
    def bright_white(text: str) -> str:
        return Color._wrap(Color.BRIGHT_WHITE, text)
