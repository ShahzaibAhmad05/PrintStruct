import argparse
import random, os, pyperclip, sys
import fnmatch
from pathlib import Path
from typing import List, Optional


def max_items_int(v: str) -> int:
    n = int(v)
    if n < 1 or n > 10000:
        raise argparse.ArgumentTypeError(
            "--max-items must be >= 1 and <=10000 (or use --no-limit)"
        )
    return n


def get_unused_file_path(root_path: str) -> str:
    """
    Returns:
        str: an unused file ID in the root path given.
    """
    itr = 0
    while True:
        guessed_path = root_path + f"/{random.randint(100000, 999999)}"
        if not os.path.exists(guessed_path):
            return guessed_path
        elif itr >= 100000:
            raise argparse.ArgumentError(
                f"could not find unused zip path within {itr} iterations"
            )


def iter_dir(directory: Path) -> List[Path]:
    try:
        return list(directory.iterdir())
    except PermissionError:
        return []


def matches_extra(p: Path, root: Path, patterns: List[str], ignore_depth: Optional[int] = None) -> bool:
    # Check if path is within ignore_depth
    if ignore_depth is not None:
        try:
            depth = len(p.relative_to(root).parts)
            if depth > ignore_depth:
                return False
        except Exception:
            pass

    try:
        rel = p.relative_to(root).as_posix()
    except Exception:
        rel = p.name
    return any(fnmatch.fnmatchcase(rel, pat) or fnmatch.fnmatchcase(p.name, pat) for pat in patterns)


def copy_to_clipboard(text: str) -> bool:
    """
    Attempts to copy text to clipboard using pyperclip.

    Args:
      text (str): The text to copy.

    Returns:
      True if successful, False otherwise.
    """

    try:        # Try pyperclip
        pyperclip.copy(text)
        return True
    except Exception as e:
        print("pyperclip failed to copy to clipboard: ", e, file=sys.stderr)

    return False


def get_project_version() -> str:
    """Returns the current version of the project"""
    return "0.1.2"
