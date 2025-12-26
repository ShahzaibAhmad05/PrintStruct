from __future__ import annotations
import sys, io, glob
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from .services.draw_tree import draw_tree, print_summary
from .services.zip_project import zip_project
from .services.parser import parse_args
from .utilities.utils import get_project_version, copy_to_clipboard
from .utilities.config import load_config, create_default_config, open_config_in_editor, get_default_config


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles argument parsing, configuration loading, and orchestrates the main
    functionality including tree printing, zipping, and file exports.
    """
    args = parse_args()

    # Handle config + version commands that exit immediately
    if args.init_config:
        create_default_config()
        return

    if args.config_user:
        open_config_in_editor()
        return

    if args.version:
        print(get_project_version())
        return

    # Load config file if it exists and --no-config is not set
    if not args.no_config:
        config = load_config()
        if config:      # If the user has setup a configuration file
            defaults = get_default_config()

            # Merge config values with args (CLI args take precedence)
            # Only use config value if arg is still at its default value
            if args.max_items == defaults["max_items"] and "max_items" in config:
                args.max_items = config["max_items"]
            if args.max_depth == defaults["depth"] and "depth" in config:
                args.max_depth = config["depth"]
            if args.gitignore_depth == defaults["gitignore_depth"] and "gitignore_depth" in config:
                args.gitignore_depth = config["gitignore_depth"]
            if args.exclude_depth == defaults["exclude_depth"] and "exclude_depth" in config:
                args.exclude_depth = config["exclude_depth"]
            if args.emoji == defaults["emoji"] and "emoji" in config:  
                # Note: --emoji flag uses action="store_false" (inverted)
                # Config uses intuitive naming: true = show emojis
                # But args.emoji is inverted: False = show emojis
                args.emoji = not config["emoji"]
            if args.hidden_items == defaults["show_all"] and "show_all" in config:
                args.hidden_items = config["show_all"]
            if args.no_gitignore == defaults["no_gitignore"] and "no_gitignore" in config:
                args.no_gitignore = config["no_gitignore"]
            if args.no_files == defaults["no_files"] and "no_files" in config:
                args.no_files = config["no_files"]
            if args.no_limit == defaults["no_limit"] and "no_limit" in config:
                args.no_limit = config["no_limit"]
            if args.summary == defaults["summary"] and "summary" in config:
                args.summary = config["summary"]

    # Validate and resolve all paths
    roots = []
    for path_str in args.paths:
        # Check if path contains glob wildcards
        if '*' in path_str or '?' in path_str:
            # Expand glob pattern
            matches = glob.glob(path_str)
            if not matches:
                print(f"Error: no matches found for pattern: {path_str}", file=sys.stderr)
                raise SystemExit(1)
            for match in matches:
                roots.append(Path(match).resolve())
        else:
            # Regular path without wildcards
            path = Path(path_str).resolve()
            if not path.exists():
                print(f"Error: path not found: {path}", file=sys.stderr)
                raise SystemExit(1)
            roots.append(path)

    # If --no-limit is set, disable max_items
    max_items = None if args.no_limit else args.max_items

    # Combine file types from both singular and plural flags
    include_file_types = []
    if args.include_file_type:
        include_file_types.append(args.include_file_type)
    if args.include_file_types:
        include_file_types.extend(args.include_file_types)

    if args.output is not None:     # TODO: relocate this code for file output
        # Determine filename
        filename = args.output
        # Add .txt extension only if no extension provided
        if not Path(filename).suffix:
            filename += '.txt'

    if args.copy or args.output is not None:
        # Capture stdout
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
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
                        include_file_types=include_file_types
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
                    include_file_types=include_file_types
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
                    include_file_types=include_file_types
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
                max_items=max_items,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                emoji=args.emoji,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=include_file_types
            )

            if args.summary:        # call summary if requested
                print_summary(
                    root,
                    respect_gitignore=not args.no_gitignore,
                    gitignore_depth=args.gitignore_depth,
                    extra_excludes=args.exclude,
                    include_patterns=args.include,
                    include_file_types=include_file_types
                )

        if args.output is not None:     # that file output code again
            # Write to file
            content = output_buffer.getvalue()

            # Wrap in markdown code block if .md extension
            if filename.endswith('.md'):
                content = f"```\n{content}```\n"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

        if args.copy:       # Capture output if needed for clipboard
            content = output_buffer.getvalue() + "\n"
            if not copy_to_clipboard(content):
                print("Warning: Could not copy to clipboard. Please install a clipboard utility (xclip, wl-copy) or ensure your environment supports it.", file=sys.stderr)
            # TODO: place an else statement here with a 
            # success message when verbose is added

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
                max_items=max_items,
                exclude_depth=args.exclude_depth,
                no_files=args.no_files,
                whitelist=selected_files,
                include_patterns=args.include,
                include_file_types=include_file_types,
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

if __name__ == "__main__":
    main()
