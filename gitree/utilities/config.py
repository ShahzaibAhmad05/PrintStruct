import json
import sys
import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import argparse


def get_config_path() -> Path:
    """
    Returns the path to config.json in the current directory.
    """
    return Path("config.json")


def get_default_config() -> Dict[str, Any]:
    """
    Returns the default configuration values.
    """
    return {
        "max_items": 20,
        "max_depth": None,
        "gitignore_depth": None,
        "exclude_depth": None,

        "hidden_items": False,
        "exclude": [],
        "include": [],
        "include_file_type": None,
        "include_file_types": [],

        # export/IO related
        "zip": None,
        "json": None,
        "txt": None,
        "md": None,
        "output": None,
        "copy": False,

        # modes
        "interactive": False,

        # toggles
        "emoji": False, 
        "no_gitignore": False,
        "no_files": False,
        "no_limit": False,
        "no_contents": False,
        "summary": False,
    }


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validates the configuration values.
    Exits with error if validation fails.
    """
    # Define which keys can be None or int
    optional_int_keys = ["depth", "gitignore_depth", "exclude_depth"]

    for key, value in config.items():
        # Skip unknown keys (forward compatibility)
        if key not in get_default_config():
            continue

        # Handle None values
        if value is None:
            # These keys can be None
            if key in optional_int_keys or key in ["depth", "gitignore_depth", "exclude_depth"]:
                continue
            else:
                print(f"Error: '{key}' cannot be null in config.json", file=sys.stderr)
                sys.exit(1)

        # Type checking based on key
        if key == "max_items":
            if not isinstance(value, int):
                print(f"Error: 'max_items' must be int, got {type(value).__name__} in config.json", file=sys.stderr)
                sys.exit(1)
            if value < 1 or value > 10000:
                print(f"Error: 'max_items' must be between 1 and 10000, got {value} in config.json", file=sys.stderr)
                sys.exit(1)
        elif key in optional_int_keys:
            if not isinstance(value, int):
                print(f"Error: '{key}' must be int or null, got {type(value).__name__} in config.json", file=sys.stderr)
                sys.exit(1)
            if value < 0:
                print(f"Error: '{key}' cannot be negative, got {value} in config.json", file=sys.stderr)
                sys.exit(1)
        elif key in ["emoji", "show_all", "no_gitignore", "no_files", "no_limit", "summary"]:
            if not isinstance(value, bool):
                print(f"Error: '{key}' must be boolean (true/false), got {type(value).__name__} in config.json", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: Unknown configuration key '{key}' in config.json", file=sys.stderr)
            sys.exit(1)


def load_user_config() -> Optional[Dict[str, Any]]:
    """
    Loads configuration from config.json if it exists.
    Returns None if file doesn't exist.
    Exits with error if file is invalid.
    """
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json at line {e.lineno}, column {e.colno}", file=sys.stderr)
        print(f"  {e.msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read config.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate the config
    validate_config(config)

    return config


def create_default_config() -> None:
    """
    Creates a default config.json file with all defaults and comments.
    """
    config_path = get_config_path()

    if config_path.exists():
        print(f"config.json already exists at {config_path.absolute()}")
        return

    # Create config with comments (as a formatted string)
    # JSON doesn't support comments, so we'll create clean JSON
    config = get_default_config()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write('\n')

        print(f"Created config.json at {config_path.absolute()}")
        print("Edit this file to customize default settings for this project.")
    except Exception as e:
        print(f"Error: Could not create config.json: {e}", file=sys.stderr)
        sys.exit(1)


def open_config_in_editor() -> None:
    """
    Opens config.json in the default text editor.
    """
    config_path = get_config_path()

    # Create config if it doesn't exist
    if not config_path.exists():
        print(f"config.json not found. Creating default config...")
        create_default_config()

    # Try to get editor from environment variable first
    editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')

    try:
        if editor:
            # Use user's preferred editor from environment
            subprocess.run([editor, str(config_path)], check=True)
        else:
            # Fall back to platform-specific default text editor
            system = platform.system()

            if system == "Darwin":  # macOS
                # Use -t flag to open in default text editor, not browser
                subprocess.run(["open", "-t", str(config_path)], check=True)
            elif system == "Linux":
                # Try common editors in order of preference
                for cmd in ["xdg-open", "nano", "vim", "vi"]:
                    try:
                        subprocess.run([cmd, str(config_path)], check=True)
                        break
                    except FileNotFoundError:
                        continue
                else:
                    raise Exception("No suitable text editor found")
            elif system == "Windows":
                # Use notepad as default text editor
                subprocess.run(["notepad", str(config_path)], check=True)
            else:
                raise Exception(f"Unsupported platform: {system}")

    except Exception as e:
        print(f"Error: Could not open editor: {e}", file=sys.stderr)
        print(f"Please manually open: {config_path.absolute()}", file=sys.stderr)
        print(f"Or set your EDITOR environment variable to your preferred editor.", file=sys.stderr)
        sys.exit(1)


def merge_config_with_args(config: dict, args: argparse.Namespace) -> argparse.Namespace:
    """
    Replaces the absent values in the args with values from config.

    Args:
        config: Configuration dictionary loaded from config.json
        args: Parsed command-line arguments
    
    Returns:
        argparse.Namespace: Merged arguments with config values filled in
    """
    for key, value in config.items():
        arg_key = key.replace("-", "_")

        if not hasattr(args, arg_key):
            # handle inverted emoji flag
            if arg_key == "emoji":
                setattr(args, arg_key, not value)
            else:
                setattr(args, arg_key, value)

    return args
