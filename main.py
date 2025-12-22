# main.py
from __future__ import annotations
import sys, os, io
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from services.draw_tree import draw_tree
from services.zip_project import zip_project
from services.parser import parse_args
from utilities.utils import get_project_version


def main() -> None:
    args = parse_args()

    if args.version:
        print(get_project_version())
        return

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)

    # If --no-limit is set, disable max_items
    max_items = None if args.no_limit else args.max_items

    if args.output is not None:     # TODO: relocate this code for file output
        # Determine filename
        filename = args.output
        if not filename.endswith(('.txt', '.md')):
            filename += '.txt'

        # Check if file exists and prompt user
        if os.path.exists(filename):
            response = input(f"File '{filename}' already exists. Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                return
            
        # Capture stdout
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output_buffer

    # if zipping is requested
    if args.zip is not None:
        zip_project(
            root=root,
            zip_stem=args.zip,
            show_all=args.all,
            extra_ignores=args.ignore,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_depth=args.max_depth,
        )
    else:       # else, print the tree normally
        draw_tree(
            root=root,
            max_depth=args.max_depth,
            show_all=args.all,
            extra_ignores=args.ignore,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_items=max_items,
        )
        if args.output is not None:     # that file output code again
            # Restore stdout
            sys.stdout = original_stdout
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output_buffer.getvalue())


if __name__ == "__main__":
    main()
