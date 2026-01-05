# gitree/utilities/utils.py

"""
Utility functions for the tool.
"""

# Default libs
import argparse, random, os, sys
from pathlib import Path

# Dependencies
import pathspec, pyperclip

# Deps from this project
from .logging_utility import Logger


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


def copy_to_clipboard(text: str, logger: Logger) -> bool:
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
        logger.log(Logger.ERROR, "pyperclip failed to copy to clipboard: ", e, file=sys.stderr)

    return False


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary by looking for null bytes in the first 8KB.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file appears to be binary, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True  # Treat unreadable files as binary


def read_file_contents(file_path: Path, max_size_mb: float = 1.0) -> str:
    """
    Read file contents with size limit and binary detection.

    Args:
        file_path: Path to the file to read
        max_size_mb: Maximum file size in megabytes (default: 1.0)

    Returns:
        File contents as string, or a placeholder message if the file is too large/binary/unreadable
    """
    max_size_bytes = int(max_size_mb * 1024 * 1024)

    try:
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size_bytes:
            return f"[file too large: {file_size / (1024 * 1024):.2f}MB]"

        # Check if binary
        if is_binary_file(file_path):
            return "[binary file]"

        # Read file contents
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    except PermissionError:
        return "[permission denied]"
    except Exception as e:
        return f"[error reading file: {str(e)}]"


def get_language_hint(file_path: Path) -> str:
    """
    Get language hint for syntax highlighting based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language hint string for markdown code blocks
    """
    ext = file_path.suffix.lower()

    # Map common extensions to language hints
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.html': 'html',
        '.htm': 'html',
        '.xml': 'xml',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'conf',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.rst': 'rst',
        '.tex': 'latex',
        '.sql': 'sql',
        '.r': 'r',
        '.R': 'r',
        '.m': 'matlab',
        '.vim': 'vim',
        '.lua': 'lua',
        '.perl': 'perl',
        '.pl': 'perl',
    }

    return lang_map.get(ext, '')
