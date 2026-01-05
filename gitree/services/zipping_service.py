# gitree/services/zipping_service.py

"""
Code file for housing ZippingService Class

Static methods; zips the resolved tree into the configured output path
"""

# Default libs
from typing import Any
from pathlib import Path
import zipfile

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class ZippingService:
    """
    Static class for zipping the resolved tree (dict format) into a zip file.
    """

    @staticmethod
    def run(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Zip all files contained in the given resolved tree dict into config.output.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            tree_data (dict[str, Any]): A resolved tree dict with "self" and "children"
        """
        
        if not getattr(config, "zip", False):
            return

        zip_path = Path(config.zip)
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        root = tree_data.get("self")
        root = root if isinstance(root, Path) else Path(str(root))

        files = ZippingService._collect_files(tree_data)

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fp in files:
                try:
                    arcname = ZippingService._arcname(root, fp)
                    zf.write(fp, arcname=arcname)
                except Exception:
                    continue


    @staticmethod
    def _collect_files(tree_data: dict[str, Any]) -> list[Path]:
        """
        Collect all file paths from the resolved tree dict.

        Args:
            tree_data (dict[str, Any]): A resolved tree dict with "self" and "children"

        Returns:
            list[Path]: A list of file Paths found in the tree
        """
        out: list[Path] = []

        def rec(node: dict[str, Any]) -> None:
            children = node.get("children", [])
            for child in children:
                if isinstance(child, dict):
                    rec(child)
                else:
                    p = child if isinstance(child, Path) else Path(str(child))
                    out.append(p)

        rec(tree_data)
        return out


    @staticmethod
    def _arcname(root: Path, file_path: Path) -> str:
        """
        Compute the archive name for a file so it is stored relative to the root.

        Args:
            root (Path): Root directory of the tree
            file_path (Path): File path to add to the archive

        Returns:
            str: Relative path inside the zip archive (POSIX separators)
        """
        try:
            rel = file_path.resolve(strict=False).relative_to(root.resolve(strict=False))
        except Exception:
            rel = Path(file_path.name)

        return rel.as_posix()
