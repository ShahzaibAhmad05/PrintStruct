import questionary
from pathlib import Path
from typing import List, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.utils import matches_file_type
from ..services.list_enteries import list_entries
import pathspec

def select_files(
    root: Path,
    respect_gitignore: bool = True,
    gitignore_depth: int = None,
    extra_excludes: List[str] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None
) -> Set[str]:
    """
    Present an interactive prompt for users to select files from a directory tree.

    Args:
        root (Path): Root directory path to scan
        respect_gitignore (bool): If True, respect .gitignore rules. Defaults to True
        gitignore_depth (int): Maximum depth to search for .gitignore files
        extra_excludes (List[str]): Additional exclude patterns
        include_patterns (List[str]): Patterns for files to include
        include_file_types (List[str]): File types (extensions) to include

    Returns:
        Set[str]: Set of selected absolute file paths
    """
    files_to_select = []

    # We need to flatten the tree to a list for the prompt
    # Reusing recursion logic similar to print_summary but collecting paths

    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    extra_excludes = extra_excludes or []

    # Compile exclude matcher from extra_excludes
    exclude_spec = None
    if extra_excludes:
        exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", extra_excludes)

    # Compile include matcher
    include_spec = None
    if include_patterns:
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns)

    def collect_files(dirpath: Path, patterns: List[str]):
        """
        Recursively collect files from directory, applying gitignore and filter rules.

        Args:
            dirpath (Path): Directory path to scan
            patterns (List[str]): List of gitignore patterns to apply

        Returns:
            None: Populates the files_to_select list in the parent scope
        """
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

        entries, _ = list_entries(
            dirpath,
            root=root,
            gi=gi,
            spec=spec,
            show_all=False,
            extra_excludes=extra_excludes,
            max_items=None, # Show all potential files for selection
            exclude_depth=None,
            no_files=False,
        )

        for entry in entries:
            if entry.is_dir():
                collect_files(entry, patterns)
            else:
                # Store relative path for display
                rel_path = entry.relative_to(root).as_posix()

                # Filter based on include patterns or file types (if any provided)
                if include_spec or include_file_types:
                    matches_include = False

                    # Check if matches include patterns
                    if include_spec and include_spec.match_file(rel_path):
                        matches_include = True

                    # Check if matches file types
                    if not matches_include and include_file_types and matches_file_type(entry, include_file_types):
                        matches_include = True

                    # Only include if it matches at least one criterion
                    if not matches_include:
                        continue

                files_to_select.append(questionary.Choice(rel_path, checked=True))

    collect_files(root, [])

    if not files_to_select:
        print("No files found to select (check your include/exclude patterns).")
        return set()

    selected_rels = questionary.checkbox(
        "Select files to include:",
        choices=files_to_select
    ).ask()

    if selected_rels is None: # Cancelled
        return set()

    return {str(root / rel) for rel in selected_rels}
