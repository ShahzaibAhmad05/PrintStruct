# main.py
from __future__ import annotations
import sys, io, pyperclip
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from .services.draw_tree import draw_tree
from .services.zip_project import zip_project
from .services.parser import parse_args
from .utilities.utils import get_project_version


def main() -> None:
    args = parse_args()

    if args.version:
        print(get_project_version())
        return

    # Validate all paths
    roots = []
    original_paths = []  # Store original path strings for headers
    for path_str in args.paths:
        path = Path(path_str).resolve()
        if not path.exists():
            print(f"Error: path not found: {path}", file=sys.stderr)
            raise SystemExit(1)
        roots.append(path)
        original_paths.append(path_str)

    if args.copy and not pyperclip.is_available():
        print("Could not find a copy mechanism for your system.")
        print("If you are on Linux, you need to install 'xclip' (on X11) or 'wl-clipboard' (on Wayland).")
        print("On other enviroments, you need to install qtpy or PyQt5 via pip.")
        return

    # If --no-limit is set, disable max_items
    max_items = None if args.no_limit else args.max_items

    if args.output is not None:     # TODO: relocate this code for file output
        # Determine filename
        filename = args.output
        if not filename.endswith(('.txt', '.md')):
            filename += '.txt'

    if args.copy or args.output is not None:
        # Capture stdout
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output_buffer

    # if zipping is requested
    if args.zip is not None:
        for i, (root, path_str) in enumerate(zip(roots, original_paths)):
            # Use 'w' mode for first path, 'a' for subsequent paths
            mode = 'w' if i == 0 else 'a'
            # Use directory name as prefix for multiple paths to avoid conflicts
            arcname_prefix = root.name if len(roots) > 1 else None
            zip_project(
                root=root,
                zip_stem=args.zip,
                show_all=args.all,
                extra_ignores=args.ignore,
                respect_gitignore=not args.no_gitignore,
                gitignore_depth=args.gitignore_depth,
                max_depth=args.max_depth,
                mode=mode,
                arcname_prefix=arcname_prefix,
            )
    else:       # else, print the tree normally
        # Show headers only if multiple paths
        show_headers = len(roots) > 1

        for i, (root, path_str) in enumerate(zip(roots, original_paths)):
            # Print header for multi-path display
            if show_headers:
                if i > 0:
                    print()  # Blank line between trees
                print(f"=== {path_str} ===")

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
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output_buffer.getvalue())

        if args.copy:       # Capture output if needed for clipboard
            pyperclip.copy(output_buffer.getvalue() + "\n")


if __name__ == "__main__":
    main()
