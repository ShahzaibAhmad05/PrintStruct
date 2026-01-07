# gitree/objects/config.py

"""
Code file to house Config class.
"""

# Default libs
import argparse, json, os, sys, subprocess, platform
from pathlib import Path
from typing import Any

# Deps from this project
from .app_context import AppContext
from ..utilities.logging_utility import Logger


class Config:
    def __init__(self, ctx: AppContext, args: argparse.Namespace):
        """ 
        Config declared here from lowest to highest priority.
        Initializer to build four types of config.
        """
        self.defaults: dict[str, Any] = self._build_default_config()
        self.global_cfg: dict[str, Any] = {}
        self.user_cfg: dict[str, Any] = self._build_user_config()
        self.cli: dict[str, Any] = vars(args)


        # Disable user- and global-level configuration if --no-config is used
        if hasattr(args, "no_config"):
            self.user_cfg = {}
            self.global_cfg = {}


    def _build_user_config(self) -> dict[str, Any]:
        """ 
        Returns a dict of the user config, if available.
        """

        config_path = Config._get_user_config_path()

        # Make sure the configuration file has been setup
        if not os.path.exists(config_path): return {}

        with open(config_path, "r") as file:
            user_cfg = json.load(file)

        return user_cfg
    

    def _get(self, key: str) -> Any:
        """
        Returns the value of the key with the following precedence:

        Precedence: CLI > user > global > defaults > fallback default
        """

        if key in self.cli:
            return self.cli[key]
        if key in self.user_cfg:
            return self.user_cfg[key]
        if key in self.global_cfg:
            return self.global_cfg[key]
        if key in self.defaults:
            return self.defaults[key]
        
        raise KeyError      # If key was not in any of the dicts


    def __getattr__(self, name: str) -> Any:
        """
        Allow attribute-style access:
        cfg.max_items converted to cfg.get("max_items")
        """
        try:
            return self._get(name)
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{name}'")


    @staticmethod
    def _build_default_config() -> dict[str, Any]:
        """
        Returns the default configuration values.

        NOTE: This must contain all the configuration keys, since it is
        meant to be a last resort.
        """

        return {
            # General Options
            "version": False,
            "init_config": False,
            "config_user": False,
            "no_config": False,
            "verbose": False,

            # Output & export options
            "zip": "",
            "export": "",

            # Listing options
            "format": "txt",
            "max_items": 20,
            "max_entries": 40,
            "max_depth": 5,
            "gitignore_depth": 5,
            "hidden_items": False,
            "exclude": [],
            "exclude_depth": 5,
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
            "max_file_size": 1.0,

            # Listing override options
            "no_gitignore": False,
            "no_files": False,
            "no_max_items": False,
            "no_max_entries": False,

            # Inner tool control (not to be given to the user)
            "no_printing": False  
        }
    

    @staticmethod
    def _get_user_config_path() -> Path:
        """ Return the default user config path for gitree """
        path = Path(".gitree/config.json")
        path.parent.mkdir(exist_ok=True, parents=True)
        return path


    @staticmethod
    def create_default_config(ctx: AppContext) -> None:
        """
        Creates a default config.json file with all defaults.
        """
        config_path = Config._get_user_config_path()


        # Get default config values
        config = Config._build_default_config()

        # Delete "system/cli only" keys from the config dict
        del config["no_printing"]
        del config["version"]
        del config["init_config"]
        del config["no_config"]
        del config["config_user"]


        try:
            # Override the config file if exists (useful for replacing corrupted config file)
            if config_path.exists(): ctx.logger.log(Logger.WARNING, 
                "Config file already exists. This will be overriden.")


            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                f.write('\n')


            ctx.logger.log(Logger.DEBUG, f"Created config.json at {config_path.absolute()}")
            ctx.logger.log(Logger.DEBUG, 
                "Edit this file to customize default settings for this project.")

        except Exception as e:
            ctx.logger.log(Logger.ERROR, f"Could not create config.json: {e}")


    @staticmethod
    def open_config_in_editor(ctx: AppContext) -> None:
        """
        Opens config.json in the default text editor.
        """
        config_path = Config._get_user_config_path()

        # Create config if it doesn't exist
        if not config_path.exists():
            ctx.logger.log(Logger.INFO, f"config.json not found. Creating default config...")
            Config.create_default_config(ctx)

        # Try to get editor from environment variable first
        editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')

        try:
            if editor:
                # Use user's preferred editor from environment
                subprocess.run([editor, str(config_path)], check=True)

            else:
                # Fall back to platform-specific default text editor
                ctx.logger.log(Logger.WARNING, 
                    "No text editor found, fallback to platform-specific editors")
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
                    ctx.logger.log(Logger.ERROR, f"Unsupported platform: {system}")

        except Exception as e:
            ctx.logger.log(Logger.ERROR, f"Could not open editor: {e}")
            ctx.logger.log(Logger.ERROR, f"Please manually open: {config_path.absolute()}")
            ctx.logger.log(Logger.ERROR,
                f"Or set your EDITOR environment variable to your preferred editor.")
        
