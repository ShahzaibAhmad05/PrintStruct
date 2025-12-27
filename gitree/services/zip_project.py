from pathlib import Path
from typing import List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.logger import Logger, OutputBuffer
from ..services.list_enteries import list_entries
import zipfile
import pathspec


def zip_project_to_handle(
    z: zipfile.ZipFile,
    *,
    root: Path,
    output_buffer: OutputBuffer,
    logger: Logger,
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    depth: Optional[int],
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    whitelist: Optional[Set[str]] = None,
    arcname_prefix: str = "",
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
) -> None:
    """
    Add files from root to an existing ZipFile handle, respecting .gitignore like draw_tree().
    Used for creating combined zips from multiple roots.
    arcname_prefix: prefix to add to archive names (e.g., "project1/")
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)

    def rec(dirpath: Path, rec_depth: int, patterns: List[str]) -> None:
        if depth is not None and rec_depth >= depth:
            return

        # extend patterns with this directory's .gitignore (same logic as draw_tree)
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

        # list entries WITHOUT max_items truncation (zip should include everything)
        entries, _ = list_entries(
            dirpath,
            root=root,
            output_buffer=output_buffer,
            logger=logger,
            gi=gi,
            spec=spec,
            show_all=show_all,
            extra_excludes=extra_excludes,
            max_items=None,
            exclude_depth=exclude_depth,
            no_files=no_files,
            include_patterns=include_patterns,
            include_file_types=include_file_types,
        )

        for entry in entries:
            if whitelist is not None:
                 entry_path = str(entry.absolute())
                 if entry.is_file():
                     if entry_path not in whitelist:
                         continue
                 elif entry.is_dir():
                     if not any(f.startswith(entry_path) for f in whitelist):
                         continue

            if entry.is_dir():
                rec(entry, rec_depth + 1, patterns)
            else:
                arcname = entry.relative_to(root).as_posix()
                if arcname_prefix:
                    arcname = arcname_prefix + "/" + arcname
                z.write(entry, arcname)

    if root.is_dir():
        rec(root, 0, [])
    else:
        # single file case
        arcname = root.name
        if arcname_prefix:
            arcname = arcname_prefix + "/" + arcname
        z.write(root, arcname)


def zip_project(
    root: Path,
    *,
    zip_stem: str,
    show_all: bool,
    extra_excludes: List[str],
    respect_gitignore: bool,
    gitignore_depth: Optional[int],
    depth: Optional[int],
    exclude_depth: Optional[int] = None,
    no_files: bool = False,
    whitelist: Optional[Set[str]] = None,
    include_patterns: List[str] = None,
    include_file_types: List[str] = None,
) -> None:
    """
    Create <zip_stem>.zip with all files under root, respecting .gitignore like draw_tree().
    Note: does NOT apply max_items (that limit is only for display).
    """
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore, gitignore_depth=gitignore_depth)
    zip_path = Path(f"{zip_stem}.zip").resolve()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:

        def rec(dirpath: Path, rec_depth: int, patterns: List[str]) -> None:
            if depth is not None and rec_depth >= depth:
                return

            # extend patterns with this directory's .gitignore (same logic as draw_tree)
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

            # list entries WITHOUT max_items truncation (zip should include everything)
            entries, _ = list_entries(
                dirpath,
                root=root,
                gi=gi,
                spec=spec,
                show_all=show_all,
                extra_excludes=extra_excludes,
                max_items=None,
                exclude_depth=exclude_depth,
                no_files=no_files,
                include_patterns=include_patterns,
                include_file_types=include_file_types,
            )

            for entry in entries:
                if whitelist is not None:
                     entry_path = str(entry.absolute())
                     if entry.is_file():
                         if entry_path not in whitelist:
                             continue
                     elif entry.is_dir():
                         if not any(f.startswith(entry_path) for f in whitelist):
                             continue

                if entry.is_dir():
                    rec(entry, rec_depth + 1, patterns)
                else:
                    arcname = entry.relative_to(root).as_posix()
                    z.write(entry, arcname)

        if root.is_dir():
            rec(root, 0, [])
        else:
            # single file case
            z.write(root, root.name)
