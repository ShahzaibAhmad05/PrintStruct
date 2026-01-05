# gitree/services/drawing_service.py

"""
Code file for housing InteractiveSelectionService Class
"""

# Defualt libs
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from collections import defaultdict

# Dependencies
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.styles import Style

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class InteractiveSelectionService:
    @staticmethod
    def run(ctx: AppContext, config: Config, resolved_root: Dict[str, Any]) -> Dict[str, Any]:
        """
        Launch an interactive terminal UI for selecting files under the given resolved root dict.

        The UI presents a hierarchical tree of directories and files. Users can:
        - Navigate using ↑ / ↓
        - Select or deselect items using Space
        - Select a directory to recursively select all contents
        - Refine the selection by deselecting individual files
        - Confirm with Enter or exit with Ctrl+C

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            resolved_root (dict): A resolved root dict with "self" as a Path and "children" as nested items

        Returns:
            dict: The updated resolved root dict in the same format as the input
        """
        from prompt_toolkit.data_structures import Point

        tree: List[dict] = []
        folder_to_files: Dict[int, List[int]] = defaultdict(list)
        folder_to_subdirs: Dict[int, List[int]] = defaultdict(list)

        root_path = resolved_root.get("self")
        if not isinstance(root_path, Path):
            root_path = Path(str(root_path))

        InteractiveSelectionService._build_tree(
            resolved_root=resolved_root,
            root=root_path,
            depth=0,
            tree=tree,
            folder_to_files=folder_to_files,
            folder_to_subdirs=folder_to_subdirs,
        )

        if not tree:
            return resolved_root

        cursor = 0

        def toggle_dir(index: int, state: bool):
            """
            Recursively toggle a directory and all its contents.

            This updates:
            - The directory itself
            - All files under it
            - All nested subdirectories and their files

            Args:
                index (int): The index of the directory in the flat UI tree
                state (bool): The new checked state to apply
            """
            tree[index]["checked"] = state
            for f in folder_to_files.get(index, []):
                tree[f]["checked"] = state
            for d in folder_to_subdirs.get(index, []):
                toggle_dir(d, state)

        def render_header() -> StyleAndTextTuples:
            """
            Render the fixed instruction bar at the top of the UI.

            Returns:
                StyleAndTextTuples: The formatted text tuples for the header bar
            """
            return [
                ("class:hint", "↑/↓ "),
                ("class:hint", "Move"),
                ("class:hint", "   |   "),
                ("class:hint", "Space "),
                ("class:hint", "Toggle"),
                ("class:hint", "   |   "),
                ("class:hint", "Enter "),
                ("class:hint", "Confirm"),
                ("class:hint", "   |   "),
                ("class:hint", "Ctrl+C "),
                ("class:hint", "Exit\n"),
            ]

        def render_tree() -> StyleAndTextTuples:
            """
            Render the file/directory tree with indentation and selection markers.

            Returns:
                StyleAndTextTuples: The formatted text tuples representing the tree view
            """
            lines: StyleAndTextTuples = []

            for i, item in enumerate(tree):
                indent = "  " * item["depth"]

                if item["checked"]:
                    star = ("class:star", "[ ✓ ] ")
                else:
                    star = ("", "[ ] ")

                label = item["path"].split("/")[-1]
                if item["type"] == "dir":
                    label += "/"

                cursor_style = "class:cursor" if i == cursor else ""

                lines.append((cursor_style, indent))
                lines.append(star)
                lines.append((cursor_style, label + "\n"))

            return lines

        tree_control = FormattedTextControl(render_tree, focusable=True, show_cursor=False)

        tree_window = Window(
            tree_control,
            always_hide_cursor=True,
        )

        def _sync_control_cursor():
            """
            Sync the prompt_toolkit cursor position with our selected index.

            This makes the Window auto-scroll to keep the selected row visible.
            """
            tree_control.cursor_position = Point(x=0, y=cursor)

        _sync_control_cursor()

        kb = KeyBindings()

        @kb.add("up")
        def _(e):
            nonlocal cursor
            cursor = max(0, cursor - 1)
            _sync_control_cursor()
            e.app.invalidate()

        @kb.add("down")
        def _(e):
            nonlocal cursor
            cursor = min(len(tree) - 1, cursor + 1)
            _sync_control_cursor()
            e.app.invalidate()

        @kb.add(" ")
        def _(e):
            item = tree[cursor]
            new_state = not item["checked"]

            if item["type"] == "dir":
                toggle_dir(cursor, new_state)
            else:
                item["checked"] = new_state

            e.app.invalidate()

        @kb.add("enter")
        def _(e):
            e.app.exit()

        @kb.add("c-c")
        def _(e):
            e.app.exit()

        style = Style.from_dict({
            "star": "fg:green",
            "cursor": "reverse",
            "hint": "fg:#888888",
        })

        @kb.add("pageup")
        def _(e):
            tree_window.vertical_scroll = max(0, tree_window.vertical_scroll - 10)
            e.app.invalidate()

        @kb.add("pagedown")
        def _(e):
            tree_window.vertical_scroll = tree_window.vertical_scroll + 10
            e.app.invalidate()

        app = Application(
            layout=Layout(
                HSplit([
                    Window(
                        FormattedTextControl(render_header),
                        height=1,
                        dont_extend_height=True,
                    ),
                    tree_window,
                ])
            ),
            key_bindings=kb,
            style=style,
            full_screen=True,
            mouse_support=True,
        )

        app.layout.focus(tree_window)

        app.run()

        selected_files = {
            (root_path / item["path"])
            for item in tree
            if item["type"] == "file" and item["checked"]
        }

        return InteractiveSelectionService._filter_resolved_root(resolved_root, selected_files)


    @staticmethod
    def _build_tree(
        resolved_root: Dict[str, Any],
        root: Path,
        depth: int,
        tree: List[dict],
        folder_to_files: Dict[int, List[int]],
        folder_to_subdirs: Dict[int, List[int]],
    ) -> None:
        """
        Flatten the resolved root dict into a render-order tree suitable for the UI.

        This function:
        - Adds directory nodes and file nodes
        - Tracks folder -> files and folder -> subfolders relationships for recursive toggling

        Args:
            resolved_root (dict): The resolved root dict with "self" and "children"
            root (Path): The root path used to compute relative display paths
            depth (int): Current depth level for indentation
            tree (list[dict]): The flat render-order list to populate
            folder_to_files (dict[int, list[int]]): Directory index -> file indices mapping
            folder_to_subdirs (dict[int, list[int]]): Directory index -> directory indices mapping
        """

        dir_path = resolved_root.get("self")
        if not isinstance(dir_path, Path):
            dir_path = Path(str(dir_path))

        folder_index = len(tree)
        rel_dir = dir_path.relative_to(root).as_posix() or "(root)"

        tree.append({
            "type": "dir",
            "path": rel_dir,
            "depth": depth,
            "checked": False,
        })

        children = resolved_root.get("children", [])
        for child in children:
            if isinstance(child, dict):
                child_index = len(tree)
                folder_to_subdirs[folder_index].append(child_index)
                InteractiveSelectionService._build_tree(
                    resolved_root=child,
                    root=root,
                    depth=depth + 1,
                    tree=tree,
                    folder_to_files=folder_to_files,
                    folder_to_subdirs=folder_to_subdirs,
                )
            else:
                child_path = child if isinstance(child, Path) else Path(str(child))
                rel_path = child_path.relative_to(root).as_posix()

                file_index = len(tree)
                tree.append({
                    "type": "file",
                    "path": rel_path,
                    "depth": depth + 1,
                    "checked": False,
                })
                folder_to_files[folder_index].append(file_index)


    @staticmethod
    def _filter_resolved_root(resolved_root: Dict[str, Any], selected_files: Set[Path]) -> Dict[str, Any]:
        """
        Filter the resolved root dict in-place style (by rebuilding) to keep only selected files
        and directories that contain selected descendants.

        Args:
            resolved_root (dict): The resolved root dict to filter
            selected_files (set[Path]): The set of selected file paths

        Returns:
            dict: A resolved root dict in the same format containing only selected paths
        """

        root_path = resolved_root.get("self")
        if not isinstance(root_path, Path):
            root_path = Path(str(root_path))

        children = resolved_root.get("children", [])
        new_children: List[Any] = []

        for child in children:
            if isinstance(child, dict):
                filtered_child = InteractiveSelectionService._filter_resolved_root(child, selected_files)
                if filtered_child.get("children"):
                    new_children.append(filtered_child)
            else:
                child_path = child if isinstance(child, Path) else Path(str(child))
                if child_path in selected_files:
                    new_children.append(child)

        return {
            "self": root_path,
            "children": new_children,
        }
