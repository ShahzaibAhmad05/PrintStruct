# gitree/utilities/colors.py

"""
Color utility for terminal output using colorama.

Provides functions to colorize directory tree output with support for:
- Directories (blue)
- Files (default/white)
- Hidden items (cyan)

This code file might be removed along with the coloroma dependency later.
"""

# Dependencies
from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
# strip=False ensures colors are always included, even when output is redirected
# autoreset=False so we manually control when to add reset codes
init(autoreset=False, strip=False)


def colorize_directory(text: str, is_hidden: bool = False) -> str:
    """
    Colorize directory names.

    Args:
        text: The directory name to colorize
        is_hidden: Whether the directory is hidden (starts with .)

    Returns:
        Colorized text string
    """
    if is_hidden:
        return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
    return f"{Fore.BLUE}{text}{Style.RESET_ALL}"


def colorize_file(text: str, is_hidden: bool = False) -> str:
    """
    Colorize file names.

    Args:
        text: The file name to colorize
        is_hidden: Whether the file is hidden (starts with .)

    Returns:
        Colorized text string
    """
    if is_hidden:
        return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
    # Use default color for regular files
    return text


def colorize_text(text: str, is_directory: bool, is_hidden: bool = False) -> str:
    """
    Colorize text based on type.

    Args:
        text: The text to colorize
        is_directory: Whether this is a directory
        is_hidden: Whether the item is hidden (starts with .)

    Returns:
        Colorized text string
    """
    if is_directory:
        return colorize_directory(text, is_hidden)
    return colorize_file(text, is_hidden)
