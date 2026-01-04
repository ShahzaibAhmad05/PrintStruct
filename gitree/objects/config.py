# gitree/objects/config.py

"""
Code file to house Config class.
"""

# Default libs
import argparse, json, os
from typing import Any

# Deps from this project
from .app_context import AppContext


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


    def _build_user_config(self) -> dict[str, Any]:
        """ Returns a dict of the user config """
        config_path = self._get_user_config_path()

        # Make sure the configuration file has been setup
        if not os.path.exists(config_path): return {}

        with open(config_path, "r") as file:
            user_cfg = json.load(file)

        return user_cfg


    def _build_default_config(self) -> dict[str, Any]:
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
    

    @staticmethod
    def _get_user_config_path() -> str:
        """ Return the default user config path for gitree """
        return ".gitree/config.json"
    

    def __getattr__(self, name: str) -> Any:
        """
        Allow attribute-style access:
        cfg.max_items converted to cfg.get("max_items")
        """
        try:
            return self._get(name)
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{name}'")
        