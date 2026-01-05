# gitree/utilities/utils.py

"""
Utility functions for the tool.
"""

# Default libs
import argparse


def max_items_int(v: str) -> int:
    """
    Validate and convert max-items argument to integer.

    Args:
        v (str): String value from command line argument

    Returns:
        int: Validated integer between 1 and 10000

    Raises:
        argparse.ArgumentTypeError: If value is outside valid range
    """
    n = int(v)
    if n < 1 or n > 10000:
        raise argparse.ArgumentTypeError(
            "--max-items must be >= 1 and <=10000 (or use --no-max-items)")
    return n


def max_entries_int(v: str) -> int:
    """
    Validate and convert max-entries argument to integer.

    Args:
        v (str): String value from command line argument

    Returns:
        int: Validated integer between 1 and 10000

    Raises:
        argparse.ArgumentTypeError: If value is outside valid range
    """
    n = int(v)
    if n < 1 or n > 10000:
        raise argparse.ArgumentTypeError(
            "--max-entries must be >= 1 and <=10000")
    return n
