import argparse, json, os
from typing import Any


class Config:

    def __init__(self, args: argparse.Namespace):
        """ 
        Config declared here from lowest to highest priority.
        Initializer to build four types of config.
        """
        self.defaults: dict[str, Any]        
        self.global_cfg: dict[str, Any]
        self.user_cfg: dict[str, Any]
        self.cli: dict[str, Any]             # highest priority

        # Build config for each dict
        self.defaults = self._build_default_config()
        self.global_cfg = {}
        self.user_cfg = self._build_user_config()
        self.cli = vars(args)


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
            "max_items": 20,
            "max_lines": 40,
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
            "no_color": False,
            "no_gitignore": False,
            "no_files": False,
            "no_limit": False,
            "no_max_lines": False,
            "no_contents": False,
            "override_files": True,
            "summary": False,
            "verbose": False,
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
        