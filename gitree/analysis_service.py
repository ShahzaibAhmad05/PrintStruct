
import json
from pathlib import Path

class AnalysisService:
    def __init__(self, resolved_root):
        """
        resolved_root: list of Path objects
        """
        self.resolved_root = resolved_root

    def run_analysis(self, save_to_file=True, output_file="analysis.json"):
        """
        Iterate through resolved_root, get file contents, and optionally save to JSON.
        """
        analysis_result = []

        for path in self.resolved_root:
            try:
                if path.is_file():
                    content = path.read_text(encoding="utf-8")
                    analysis_result.append({
                        "path": str(path),
                        "content": content
                    })
                else:
                    analysis_result.append({
                        "path": str(path),
                        "content": None
                    })
            except Exception as e:
                analysis_result.append({
                    "path": str(path),
                    "error": str(e)
                })

        if save_to_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis_result, f, indent=4)

        return analysis_result
