# gitree/utilities/config.py

"""
Code file for housing config-related functions.

These functions might be moved to Config class completely during refactoring.
"""

# Default libs
import json, sys, os, subprocess, platform
from pathlib import Path
from typing import Any

# Deps from this project
from ..utilities.logger import Logger  
from ..objects.app_context import AppContext
from ..objects.config import Config


def get_config_path() -> Path:
    """
    Returns the path to config.json in the current directory.
    """
    return Path("config.json")


def get_default_config() -> dict[str, Any]:
    """
    Returns the default configuration values.
    """
    return {
        # General Options
        "version": False,
        "init_config": False,
        "config_user": False,
        "no_config": False,
        "verbose": False,

        # Output & export options
        "zip": None,
        "export": None,

        # Listing options
        "format": "txt",
        "max_items": 20,
        "max_entries": 40,
        "max_depth": None,
        "gitignore_depth": None,
        "hidden_items": False,
        "exclude": [],
        "exclude_depth": None,
        "include": [],
        "include_file_types": [],
        "copy": False,
        "emoji": False,
        "interactive": False,
        "files_first": False,
        "no_color": False,
        "no_contents": False,
        "no_contents_for": [],
        "override_files": True,

        # Listing override options
        "no_gitignore": False,
        "no_files": False,
        "no_max_items": False,
        "no_max_entries": False,

        # Inner tool behaviour control
        "no_printing": False  
    }


def load_user_config(ctx: AppContext) -> dict[str, Any] | None:
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
        ctx.logger.log(Logger.ERROR, 
            f"invalid JSON in config.json at line {e.lineno}, column {e.colno}")
        ctx.logger.log(Logger.ERROR, f"  {e.msg}")

    except Exception as e:
        ctx.logger.log(Logger.ERROR, f"Error: Could not read config.json: {e}")

    # TODO: Implement actual validation of the config
    # but please TRY to not make it a bloated function this time
    # Validate the config
    # validate_config(ctx, config)

    return config


def create_default_config(ctx: AppContext) -> None:
    """
    Creates a default config.json file with all defaults and comments.
    """
    config_path = get_config_path()

    if config_path.exists():
        ctx.logger.log(Logger.WARNING, f"config.json already exists at {config_path.absolute()}")
        return

    # Create config with comments (as a formatted string)
    # JSON doesn't support comments, so we'll create clean JSON
    config = get_default_config()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write('\n')

        ctx.logger.log(Logger.DEBUG, f"Created config.json at {config_path.absolute()}")
        ctx.logger.log(Logger.DEBUG, "Edit this file to customize default settings for this project.")
    except Exception as e:
        ctx.logger.log(Logger.ERROR, f"Could not create config.json: {e}", file=sys.stderr)


def open_config_in_editor(ctx: AppContext) -> None:
    """
    Opens config.json in the default text editor.
    """
    config_path = get_config_path()

    # Create config if it doesn't exist
    if not config_path.exists():
        ctx.logger.log(Logger.INFO, f"config.json not found. Creating default config...")
        create_default_config(ctx)

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
        ctx.logger.log(Logger.ERROR, f"Could not open editor: {e}")
        ctx.logger.log(Logger.ERROR, f"Please manually open: {config_path.absolute()}")
        ctx.logger.log(Logger.ERROR, 
            f"Or set your EDITOR environment variable to your preferred editor.")
