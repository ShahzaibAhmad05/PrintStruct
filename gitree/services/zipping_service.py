from pathlib import Path
from typing import List, Optional, Set
from ..utilities.gitignore import GitIgnoreMatcher
from ..utilities.logger import Logger, OutputBuffer
from .list_enteries import list_entries
import zipfile, pathspec, argparse


class ZippingService:
    def __init__(
        self,
        output_buffer: OutputBuffer,
        logger: Logger,
        respect_gitignore: bool = True,
        gitignore_depth: Optional[int] = None,
        depth: Optional[int] = None,
        exclude_depth: Optional[int] = None,
    ):
        self.output_buffer = output_buffer
        self.logger = logger
        self.respect_gitignore = respect_gitignore
        self.gitignore_depth = gitignore_depth
        self.depth = depth
        self.exclude_depth = exclude_depth

    def zip_project_to_handle(
        self,
        z: zipfile.ZipFile,
        zipPath: Path,
        *,
        root: Path,
        show_all: bool,
        extra_excludes: List[str],
        no_files: bool = False,
        whitelist: Optional[Set[str]] = None,
        arcname_prefix: str = "",
        include_patterns: List[str] = None,
        include_file_types: List[str] = None,
    ) -> None:
        gi = GitIgnoreMatcher(root, enabled=self.respect_gitignore, gitignore_depth=self.gitignore_depth)
        export_zip_resolved = zipPath.resolve()

        def rec(dirpath: Path, rec_depth: int, patterns: List[str]) -> None:
            if self.depth is not None and rec_depth >= self.depth:
                return

            if self.respect_gitignore and gi.within_depth(dirpath):
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
                output_buffer=self.output_buffer,
                logger=self.logger,
                gi=gi,
                spec=spec,
                show_all=show_all,
                extra_excludes=extra_excludes,
                max_items=None,
                exclude_depth=self.exclude_depth,
                no_files=no_files,
                include_patterns=include_patterns,
                include_file_types=include_file_types,
            )

            for entry in entries:
                if export_zip_resolved is not None and entry.resolve() == export_zip_resolved:
                    self.logger.log(Logger.WARNING, "Infinite zipping detected, skipping this file.")
                    continue

                if whitelist is not None:
                    entry_path = str(entry.absolute())
                    if entry.is_file() and entry_path not in whitelist:
                        continue
                    elif entry.is_dir() and not any(f.startswith(entry_path) for f in whitelist):
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
            arcname = root.name
            if arcname_prefix:
                arcname = arcname_prefix + "/" + arcname
            z.write(root, arcname)

    def zip_project(
        self,
        root: Path,
        *,
        zip_stem: str,
        show_all: bool,
        extra_excludes: List[str],
        no_files: bool = False,
        whitelist: Optional[Set[str]] = None,
        include_patterns: List[str] = None,
        include_file_types: List[str] = None,
    ) -> None:
        zip_path = Path(f"{zip_stem}.zip").resolve()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            self.zip_project_to_handle(
                z=z,
                zipPath=zip_path,
                root=root,
                show_all=show_all,
                extra_excludes=extra_excludes,
                no_files=no_files,
                whitelist=whitelist,
                arcname_prefix="",
                include_patterns=include_patterns,
                include_file_types=include_file_types,
            )

    def zip_roots(
        self,
        args: argparse.Namespace,
        roots: List[Path],
        selected_files_map: Optional[dict] = None
    ) -> None:
        zip_path = Path(args.zip).resolve()
        selected_files_map = selected_files_map or {}
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for root in roots:
                selected_files = selected_files_map.get(root)
                prefix = ""
                if len(roots) > 1 and root.is_dir():
                    prefix = root.name
                self.zip_project_to_handle(
                    z=z,
                    zipPath=zip_path,
                    root=root,
                    show_all=args.hidden_items,
                    extra_excludes=args.exclude,
                    no_files=args.no_files,
                    whitelist=selected_files,
                    arcname_prefix=prefix,
                    include_patterns=args.include,
                    include_file_types=args.include_file_types,
                )
