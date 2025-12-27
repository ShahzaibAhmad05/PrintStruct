# gitree/main.py
from __future__ import annotations
import sys, io, glob
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from .services.draw_tree import draw_tree, print_summary
from .services.zip_project import zip_project
from .services.parser import parse_args
from .utilities.utils import copy_to_clipboard
from .utilities.config import resolve_config
from .utilities.logger import Logger, OutputBuffer
from .services.files_selection import resolve_selected_files
from .services.handle_basic_cli import handle_basic_cli_args, resolve_root_paths, correct_cli_args


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles argument parsing, configuration loading, and orchestrates the main
    functionality including tree printing, zipping, and file exports.
    """
    args = parse_args()
    logger = Logger()
    output_buffer = OutputBuffer()


    # Resolve configuration (handle user, global, and default config merging)
    resolve_config(args)


    # Fix any incorrect CLI args (paths missing extensions, etc.)
    args = correct_cli_args(args)


    # if some specific Basic CLI args given, execute and return
    # Handles for --version, --init-config, --config-user, --no-config
    if handle_basic_cli_args(args): return


    # Validate and resolve all paths
    roots = resolve_root_paths(args)


    if args.copy or args.output is not None:
        # Capture stdout
        output_buffer = io.StringIO()
        sys.stdout = output_buffer

    # if zipping is requested
    if args.zip is not None:
        import zipfile
        zip_path = Path(f"{args.zip}.zip" if "." not in args.zip else f"{args.zip}").resolve()

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for root in roots:
                # Interactive mode for each path (if enabled)
                selected_files = None
                if args.interactive:
                    from .services.interactive import select_files
                    selected_files = select_files(
                        root=root,
                        respect_gitignore=not args.no_gitignore,
                        gitignore_depth=args.gitignore_depth,
                        exclude_patterns=args.exclude,
                        include_patterns=args.include,
                        include_file_types=args.include_file_types
                    )
                    if not selected_files:
                        continue

                # Add this root to the zip (in append mode logic)
                from .services.zip_project import zip_project_to_handle
                # Only use prefix for directories when multiple roots, not for files
                prefix = ""
                if len(roots) > 1 and root.is_dir():
                    prefix = root.name
                zip_project_to_handle(
                    z=z,
                    root=root,
                    show_all=args.hidden_items,
                    extra_excludes=args.exclude,
                    respect_gitignore=not args.no_gitignore,
                    gitignore_depth=args.gitignore_depth,
                    exclude_depth=args.exclude_depth,
                    depth=args.max_depth,
                    no_files=args.no_files,
                    whitelist=selected_files,
                    arcname_prefix=prefix,
                    include_patterns=args.include,
                    include_file_types=args.include_file_types
                )
    else:       # else, print the tree normally
        for i, root in enumerate(roots):
            # Interactive mode for each path (if enabled)
            selected_files = None
            if args.interactive:
                from .services.interactive import select_files
                selected_files = select_files(
                    root=root,
                    respect_gitignore=not args.no_gitignore,
                    gitignore_depth=args.gitignore_depth,
                    extra_excludes=args.exclude,
                    include_patterns=args.include,
                    exclude_patterns=args.exclude,
                    include_file_types=args.include_file_types
                )
                if not selected_files:
                    continue

            # Add header for multiple paths
            if len(roots) > 1:
                if i > 0:
                    print()  # Empty line between trees
                print(f"=== {root} ===")

            draw_tree(
                root=root,
                depth=args.max_depth,
                show_all=args.hidden_items,
                extra_excludes=args.exclude,
                respect_gitignore=not args.no_gitignore,
                gitignore_depth=args.gitignore_depth,
                max_items=args.max_items,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                emoji=args.emoji,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=args.include_file_types
            )

            if args.summary:        # call summary if requested
                print_summary(
                    root,
                    respect_gitignore=not args.no_gitignore,
                    gitignore_depth=args.gitignore_depth,
                    extra_excludes=args.exclude,
                    include_patterns=args.include,
                    include_file_types=args.include_file_types
                )

        if args.output is not None:     # that file output code again
            # Write to file
            content = output_buffer.getvalue()

            # Wrap in markdown code block if .md extension
            if args.output.endswith('.md'):
                content = f"```\n{content}```\n"

            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)

        if args.copy:       # Capture output if needed for clipboard
            content = output_buffer.getvalue() + "\n"
            if not copy_to_clipboard(content):
                output_buffer.write("Warning: Could not copy to clipboard. Please install a clipboard utility (xclip, wl-copy) or ensure your environment supports it.")
            else:
                logger.write(Logger.INFO, "Tree output copied to clipboard successfully.\n")


        # Handle file outputs
        if args.json or args.txt or args.md:
            from .services.output_formatters import build_tree_data, write_outputs

            # Include contents by default, unless --no-contents is specified
            include_contents = not args.no_contents

            tree_data = build_tree_data(
                root=root,
                depth=args.max_depth,
                show_all=args.hidden_items,
                extra_excludes=args.exclude,
                respect_gitignore=not args.no_gitignore,
                gitignore_depth=args.gitignore_depth,
                max_items=args.max_items,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=args.include_file_types,
                include_contents=include_contents
            )

            write_outputs(
                tree_data=tree_data,
                json_path=args.json,
                txt_path=args.txt,
                md_path=args.md,
                emoji=args.emoji,
                include_contents=include_contents
            )

    output_buffer.flush()
    if args.verbose:
        print("\nLOG:")
        logger.flush()


if __name__ == "__main__":
    main()
