# gitree/services/drawing_service.py

"""
Code file for housing DrawingService Class

Static methods; draws into the output_buffer in AppContext
"""

# Default libs
from typing import Any
import json

# Deps from this project
from ..constants.constant import (FILE_EMOJI, NORMAL_DIR_EMOJI, EMPTY_DIR_EMOJI,
    BRANCH, LAST, VERT, SPACE)
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..utilities.color_utility import Color


class DrawingService:
    """
    This class contains methods to help draw the directory structure of the
    project into the output_buffer of AppContext, in multiple different formats.
    """

    @staticmethod
    def draw(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Wrapper function to call the drawing based on config.format

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict[str, Any]): The resolved tree dict to draw
        """

        if config.format == "txt":
            DrawingService._draw_tree(ctx, config, tree_data)

        elif config.format == "md":
            DrawingService._draw_md(ctx, config, tree_data)

        elif config.format == "json":
            DrawingService._draw_json(ctx, config, tree_data)


    @staticmethod
    def _draw_tree(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Draw the resolved tree structure in the "tree" format.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict[str, Any]): The resolved tree dict to draw
        """

        def _p(x: Any) -> str:
            return x.as_posix() if hasattr(x, "as_posix") else str(x)

        def _name(p: str) -> str:
            s = p.rstrip("/\\")
            return s.split("/")[-1].split("\\")[-1] if s else s

        def _is_dir(node: Any) -> bool:
            return isinstance(node, dict)

        def _emoji_for(node: Any) -> str:
            if not config.emoji:
                return ""
            if _is_dir(node):
                ch = node.get("children", [])
                return EMPTY_DIR_EMOJI if len(ch) == 0 else NORMAL_DIR_EMOJI
            return FILE_EMOJI

        def _children_sorted(children: list[Any]) -> list[Any]:
            if config.files_first:
                return sorted(children, key=lambda c: (0 if not _is_dir(c) else 1, _name(_p(c.get("self") if _is_dir(c) else c)).lower()))
            return sorted(children, key=lambda c: (0 if _is_dir(c) else 1, _name(_p(c.get("self") if _is_dir(c) else c)).lower()))

        def _write_line(prefix: str, connector: str, node: Any) -> None:
            p = _p(node.get("self") if _is_dir(node) else node)
            label = _name(p)
            em = _emoji_for(node)

            if config.no_color:
                color = Color.default
            elif DrawingService._is_hidden(p):
                color = Color.grey
            elif _is_dir(node):
                color = Color.cyan
            else:
                color = Color.default

            if em:
                ctx.output_buffer.write(f"{prefix}{connector}{em} {color(label)}")
            else:
                ctx.output_buffer.write(f"{prefix}{connector}{color(label)}")

        root_path = _p(tree_data.get("self"))
        root_label = _name(root_path)
        root_emoji = _emoji_for(tree_data)

        if root_emoji:
            ctx.output_buffer.write(f"{root_emoji} "
                f"{Color.cyan(root_label) if not config.no_color else root_label}")
        else:
            ctx.output_buffer.write(f"{Color.cyan(root_label) if not config.no_color else root_label}")

        def _rec(node: dict[str, Any], prefix: str) -> None:
            kids = _children_sorted(node.get("children", []))
            for i, child in enumerate(kids):
                connector = LAST if i == len(kids) - 1 else BRANCH
                _write_line(prefix, connector, child)
                if _is_dir(child):
                    next_prefix = prefix + (SPACE if connector == LAST else VERT)
                    _rec(child, next_prefix)

        _rec(tree_data, "")


    @staticmethod
    def _draw_md(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Draw the resolved tree structure in the "md" format.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict[str, Any]): The resolved tree dict to draw
        """
        ctx.output_buffer.write("```text")
        DrawingService._draw_tree(ctx, config, tree_data)
        ctx.output_buffer.write("```")


    @staticmethod
    def _draw_json(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Draw the resolved tree structure in the "json" format.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict[str, Any]): The resolved tree dict to draw
        """

        def _norm(node: Any) -> Any:
            if isinstance(node, dict):
                s = node.get("self")
                return {
                    "self": s.as_posix() if hasattr(s, "as_posix") else str(s),
                    "children": [_norm(c) for c in node.get("children", [])],
                }
            return node.as_posix() if hasattr(node, "as_posix") else str(node)

        ctx.output_buffer.write(json.dumps(_norm(tree_data), indent=2))


    @staticmethod
    def _is_hidden(p: str) -> bool:
        s = p.replace("\\", "/").strip("/")
        parts = [x for x in s.split("/") if x]
        return any(part.startswith(".") for part in parts)
