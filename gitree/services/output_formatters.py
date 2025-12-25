import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..services.list_enteries import list_entries
from ..constants.constant import (BRANCH, LAST, SPACE, VERT,
                                  FILE_EMOJI, EMPTY_DIR_EMOJI,
                                  NORMAL_DIR_EMOJI)
import pathspec


def build_tree_data(
    root: Path,
    *,
    depth: Optional[int],
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    max_items: Optional[int] = None,
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    whitelist: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Build hierarchical tree structure as dictionary.

    Returns:
        Dict with structure: {"name": str, "type": "file"|"directory", "children": [...]}
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    tree_root = {
        "name": root.name,
        "type": "directory",
        "children": []
    }

    def rec(dirpath: Path, current_depth: int, patterns: List[str]) -> List[Dict[str, Any]]:
        """Recursively build tree data for a directory."""
        if depth is not None and current_depth >= depth:
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
        entries, truncated = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_excludes=extra_excludes,
            max_items=max_items,
            exclude_depth=exclude_depth,
            no_files=no_files,
        )

        # Filter by whitelist
        filtered_entries = []
        for entry in entries:
            entry_path = str(entry.absolute())
            if whitelist is not None:
                if entry.is_file():
                    if entry_path not in whitelist:
                        continue
                elif entry.is_dir():
                    if not any(f.startswith(entry_path) for f in whitelist):
                        continue
            filtered_entries.append(entry)

        entries = filtered_entries

        # Build children list
        children = []
        for entry in entries:
            if entry.is_file():
                children.append({
                    "name": entry.name,
                    "type": "file"
                })
            elif entry.is_dir():
                child_node = {
                    "name": entry.name,
                    "type": "directory",
                    "children": rec(entry, current_depth + 1, patterns)
                }
                children.append(child_node)

        # Add truncation marker if needed
        if truncated > 0:
            children.append({
                "name": f"... and {truncated} more items",
                "type": "truncated"
            })

        return children

    if root.is_dir():
        tree_root["children"] = rec(root, 0, [])

    return tree_root


def format_json(tree_data: Dict[str, Any]) -> str:
    """Convert tree data to JSON string with proper indentation."""
    return json.dumps(tree_data, indent=2, ensure_ascii=False)


def format_text_tree(tree_data: Dict[str, Any], emoji: bool = False) -> str:
    """
    Convert tree data to text tree format (ASCII art style).

    Args:
        tree_data: Hierarchical tree structure
        emoji: If True, don't show emoji icons (matches draw_tree behavior)

    Returns:
        String with ASCII tree structure
    """
    lines = [tree_data["name"]]

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

            # Recursively process children
            if child.get("children"):
                next_prefix = prefix + (SPACE if is_last else VERT)
                rec(child, next_prefix)

    rec(tree_data, "")
    return "\n".join(lines)


def write_outputs(
    tree_data: Dict[str, Any],
    json_path: Optional[str],
    txt_path: Optional[str],
    md_path: Optional[str],
    emoji: bool = False
) -> None:
    """
    Write tree data to multiple output files simultaneously.

    Args:
        tree_data: Hierarchical tree structure
        json_path: Path to JSON output file (if None, skip)
        txt_path: Path to TXT output file (if None, skip)
        md_path: Path to Markdown output file (if None, skip)
        emoji: Emoji flag for text formatting
    """
    try:
        if json_path:
            content = format_json(tree_data)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(content)

        if txt_path:
            content = format_text_tree(tree_data, emoji=emoji)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(content)

        if md_path:
            content = format_text_tree(tree_data, emoji=emoji)
            # Wrap in markdown code block
            content = f"```\n{content}\n```\n"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

    except IOError as e:
        print(f"Error writing output file: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during file output: {e}")
        raise
