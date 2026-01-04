# gitree/services/tree_formatting_service.py
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import read_file_contents, get_language_hint
from ..utilities.logger import Logger, OutputBuffer
from .list_enteries import list_entries
from ..constants.constant import (BRANCH, LAST, SPACE, VERT,
                                  FILE_EMOJI, EMPTY_DIR_EMOJI,
                                  NORMAL_DIR_EMOJI)
import pathspec


def build_tree_data(
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
    depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
    max_entries: Optional[int] = None,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    whitelist: Optional[Set[str]] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
    include_contents: bool = True,
    no_contents_for: Optional[List[Path]] = None
) -> Dict[str, Any]:
    """
    Build hierarchical tree structure as dictionary.

    Args:
        include_contents: If True, include file contents in the tree data (default: True)

    Returns:
        Dict with structure: {"name": str, "type": "file"|"directory", "children": [...], "contents": str (optional)}
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    if no_contents_for is None:
        no_contents_for = []
    else:
        # Ensure all paths are resolved
        no_contents_for = [p.resolve() if isinstance(p, Path) else Path(p).resolve() for p in no_contents_for]


    tree_root = {
        "name": root.name,
        "type": "directory",
        "children": []
    }

    entries=1 # Count lines for max_entries limit
    stop_writing=False # Flag to stop writing when max_entries is reached

    def rec(dirpath: Path, current_depth: int, patterns: List[str]) -> List[Dict[str, Any]]:
        """Recursively build tree data for a directory."""
        nonlocal entries, stop_writing
        if depth is not None and current_depth >= depth:
            return []

        if stop_writing:
            return []
        # Handle .gitignore patterns
        if respect_gitignore and gi.within_depth(dirpath):
            gi_path = dirpath / ".gitignore"
            if gi_path.is_file():
                rel_dir = dirpath.relative_to(root).as_posix()
                prefix_path = "" if rel_dir == "." else rel_dir + "/"
                for line in gi_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    neg = line.startswith("!")
                    pat = line[1:] if neg else line
                    pat = prefix_path + pat.lstrip("/")
                    patterns = patterns + [("!" + pat) if neg else pat]

        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

        # Get entries
        entry_list, truncated = list_entries(
            dirpath,
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_excludes=extra_excludes,
            max_items=max_items,
            max_entries=max_entries,
            exclude_depth=exclude_depth,
            no_files=no_files,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
        )

        # Filter by whitelist
        filtered_entries = []
        for entry in entry_list:
            entry_path = str(entry.absolute())
            if whitelist is not None:
                if entry.is_file():
                    if entry_path not in whitelist:
                        continue
                elif entry.is_dir():
                    if not any(f.startswith(entry_path) for f in whitelist):
                        continue
            filtered_entries.append(entry)

        entry_list = filtered_entries

        # Build children list
        children = []
        for i, entry in enumerate(entry_list):
            if stop_writing:
                break

            if max_entries is not None and entries >= max_entries:
                remaining = len(entry_list) - i + truncated
                children.append({"name": "... and more entries", "type": "truncated"})
                stop_writing = True
                break

            if entry.is_file():
                file_node = {
                    "name": entry.name,
                    "type": "file",
                    "path": str(entry.relative_to(root).as_posix())
                }

                # FIX: only touch file_node inside the file branch
                if include_contents and entry.resolve() not in no_contents_for:
                    file_node["contents"] = read_file_contents(entry)

                children.append(file_node)
                entries += 1

            elif entry.is_dir():
                entries += 1
                child_node = {
                    "name": entry.name,
                    "type": "directory",
                    "children": rec(entry, current_depth + 1, patterns)
                }
                children.append(child_node)


        # Add truncation marker if needed
        if truncated > 0 and not stop_writing:
            children.append({
                "name": f"... and {truncated} more items",
                "type": "truncated"
            })
            entries += 1

        return children

    if root.is_dir():
        tree_root["children"] = rec(root, 0, [])

    return tree_root


def format_json(tree_data: Dict[str, Any]) -> str:
    """
    Convert tree data to JSON string with proper indentation.
    """
    return json.dumps(tree_data, indent=2, ensure_ascii=False)


def format_text_tree(tree_data: Dict[str, Any], emoji: bool = False, include_contents: bool = False) -> str:
    """
    Convert tree data to text tree format (ASCII art style).

    Args:
        tree_data: Hierarchical tree structure
        emoji: If True, don't show emoji icons (matches draw_tree behavior)
        include_contents: If True, append file contents after the tree

    Returns:
        String with ASCII tree structure and optionally file contents
    """
    lines = [tree_data["name"]]
    file_contents_list = []  # Store file paths and contents

    def rec(node: Dict[str, Any], prefix: str) -> None:
        children = node.get("children", [])
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = LAST if is_last else BRANCH

            # Handle truncation marker
            if child["type"] == "truncated":
                lines.append(prefix + connector + child["name"])
                continue

            # Add emoji or not (emoji flag is inverted - False means show emojis)
            if emoji:
                # emoji=True means don't show emoji icons
                suffix = "/" if child["type"] == "directory" else ""
                lines.append(prefix + connector + child["name"] + suffix)
            else:
                # emoji=False means show emoji icons
                if child["type"] == "file":
                    emoji_str = FILE_EMOJI
                else:  # directory
                    # For directories, use normal dir emoji (we don't check if empty in tree data)
                    emoji_str = NORMAL_DIR_EMOJI
                lines.append(prefix + connector + emoji_str + " " + child["name"])

            # Collect file contents if present
            if include_contents and child["type"] == "file" and "contents" in child:
                file_contents_list.append({
                    "path": child.get("path", child["name"]),
                    "contents": child["contents"]
                })

            # Recursively process children
            if child.get("children"):
                next_prefix = prefix + (SPACE if is_last else VERT)
                rec(child, next_prefix)

    rec(tree_data, "")
    tree_export = "\n".join(lines)

    # Append file contents if requested
    if include_contents and file_contents_list:
        tree_export += "\n\n" + "=" * 80 + "\n"
        tree_export += "FILE CONTENTS\n"
        tree_export += "=" * 80 + "\n\n"

        for item in file_contents_list:
            tree_export += f"File: {item['path']}\n"
            tree_export += "-" * 80 + "\n"
            tree_export += item['contents']
            tree_export += "\n" + "-" * 80 + "\n\n"

    return tree_export


def format_markdown_tree(tree_data: Dict[str, Any], emoji: bool = False, include_contents: bool = False) -> str:
    """
    Convert tree data to markdown format with code blocks.

    Args:
        tree_data: Hierarchical tree structure
        emoji: If True, don't show emoji icons (matches draw_tree behavior)
        include_contents: If True, include file contents in code blocks

    Returns:
        String with markdown-formatted tree and optionally file contents in code blocks
    """
    lines = [tree_data["name"]]
    file_contents_list = []  # Store file paths and contents

    def rec(node: Dict[str, Any], prefix: str) -> None:
        children = node.get("children", [])
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = LAST if is_last else BRANCH

            # Handle truncation marker
            if child["type"] == "truncated":
                lines.append(prefix + connector + child["name"])
                continue

            # Add emoji or not
            if emoji:
                suffix = "/" if child["type"] == "directory" else ""
                lines.append(prefix + connector + child["name"] + suffix)
            else:
                if child["type"] == "file":
                    emoji_str = FILE_EMOJI
                else:
                    emoji_str = NORMAL_DIR_EMOJI
                lines.append(prefix + connector + emoji_str + " " + child["name"])

            # Collect file contents if present
            if include_contents and child["type"] == "file" and "contents" in child:
                file_contents_list.append({
                    "path": child.get("path", child["name"]),
                    "name": child["name"],
                    "contents": child["contents"]
                })

            # Recursively process children
            if child.get("children"):
                next_prefix = prefix + (SPACE if is_last else VERT)
                rec(child, next_prefix)

    rec(tree_data, "")

    # Build markdown export
    md_export = "```\n"
    md_export += "\n".join(lines)
    md_export += "\n```\n"

    # Append file contents in code blocks if requested
    if include_contents and file_contents_list:
        md_export += "\n## File Contents\n\n"

        for item in file_contents_list:
            # Get language hint for syntax highlighting
            lang_hint = get_language_hint(Path(item['name']))

            md_export += f"### {item['path']}\n\n"
            md_export += f"```{lang_hint}\n"
            md_export += item['contents']
            md_export += "\n```\n\n"

    return md_export


def write_exports(
    logger: Logger,
    tree_data: Dict[str, Any],
    export_path: str,
    md: bool=False,
    json: bool=False,
    txt: bool=False,
    emoji: bool = False,
    include_contents: bool = True
) -> None:
    """
    Write tree data to multiple export files simultaneously.

    Args:
        tree_data: Hierarchical tree structure
        json_path: Path to JSON export file (if None, skip)
        txt_path: Path to TXT export file (if None, skip)
        md_path: Path to Markdown export file (if None, skip)
        emoji: Emoji flag for text formatting
        include_contents: If True, include file contents in exports (default: True)
    """
    if md: func = format_markdown_tree
    elif json: func = format_json
    elif txt: func = format_text_tree

    try:
        if export_path:
            content = func(tree_data)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except IOError as e:
        logger.log(Logger.ERROR, f"Error writing export file: {e}")
        raise
    except Exception as e:
        logger.log(Logger.ERROR, f"Unexpected error during file export: {e}")
        raise
