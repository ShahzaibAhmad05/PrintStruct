# gitree/services/drawing_service.py

"""
Code file for housing ExportService Class
"""

# Defualt libs
from pathlib import Path
from typing import Any

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class ExportService:
    @staticmethod
    def run(ctx: AppContext, config: Config, tree_data: dict[str, Any]) -> None:
        """
        Export the already-drawn project structure in ctx.output_buffer, followed by file contents,
        and save it to a file based on config.format.
        """

        fmt = (getattr(config, "format", "") or "").strip().lower()
        output_path = Path(config.export)

        if fmt in ("txt", "tree"):
            lines = ExportService._export_txt(ctx, tree_data)

        elif fmt == "md":
            lines = ExportService._export_md(ctx, tree_data)

        elif fmt == "json":
            lines = ExportService._export_json(ctx, tree_data)

        else:
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")

        ctx.output_buffer.clear()


    @staticmethod
    def _export_txt(ctx: AppContext, tree_data: dict[str, Any]) -> list[str]:
        structure = ctx.output_buffer.get_value()
        out: list[str] = []

        out.extend(structure)
        out.append("")
        out.append("==== FILE CONTENTS ====")

        for fp in ExportService._iter_files(tree_data):
            out.append("")
            out.append(f"FILE: {fp}")
            out.append("-" * (6 + len(str(fp))))
            out.append(ExportService._read_text(fp).rstrip("\n"))

        return out


    @staticmethod
    def _export_md(ctx: AppContext, tree_data: dict[str, Any]) -> list[str]:
        structure = ctx.output_buffer.get_value()
        out: list[str] = []

        out.append("## Project Structure")
        out.extend(structure)       # Assuming structure is already in md format
        out.append("## Files")
        out.append("")

        for fp in ExportService._iter_files(tree_data):
            out.append(f"### File: {fp}")
            out.append("")
            out.append("```text")
            out.append(ExportService._read_text(fp).rstrip("\n"))
            out.append("```")
            out.append("")

        return out


    @staticmethod
    def _export_json(ctx: AppContext, tree_data: dict[str, Any]) -> list[str]:
        import json

        structure = ctx.output_buffer.get_value()

        files = [
            {
                "path": str(fp),
                "content": ExportService._read_text(fp),
            }
            for fp in ExportService._iter_files(tree_data)
        ]

        payload = {
            "structure": structure,
            "files": files,
        }

        return [json.dumps(payload, indent=2, ensure_ascii=False)]


    @staticmethod
    def _iter_files(tree_data: Any) -> list[Path]:
        """
        Flatten the resolved tree dict into a list of file Paths.

        Args:
            tree_data (Any): A resolved tree dict with "self" and "children"

        Returns:
            list[Path]: A list of file paths
        """

        if not isinstance(tree_data, dict):
            return []

        out: list[Path] = []

        def rec(node: dict[str, Any]) -> None:
            for child in node.get("children", []):
                if isinstance(child, dict):
                    rec(child)
                else:
                    p = child if isinstance(child, Path) else Path(str(child))
                    out.append(p)

        rec(tree_data)
        return out


    @staticmethod
    def _read_text(path: Path) -> str:
        """
        Read a file as text safely.

        Args:
            path (Path): The file path to read

        Returns:
            str: File content decoded as text
        """
        p = path if isinstance(path, Path) else Path(str(path))
        try:
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            try:
                return p.read_bytes().decode("utf-8", errors="ignore")
            except Exception:
                return ""


    @staticmethod
    def _ends_with_newline(out: Any) -> bool:
        """
        Check whether the underlying buffer already ends with a newline.

        Args:
            out (Any): Output buffer to check
        """
        try:
            v = out.getvalue()
            return bool(v) and v.endswith("\n")
        except Exception:
            return False
