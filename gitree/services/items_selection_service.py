# gitree/services/items_selection_service.py

"""
Code file for the ItemsSelectionService class.
"""

# default libs
from typing import Any
import os, glob, time
from pathlib import Path

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..objects.gitignore import GitIgnore
from ..utilities.logging_utility import Logger
from ..utilities.gitignore_utility import GitIgnoreMatcher


class ItemsSelectionService:
    """
    Static class for resolving the args and forming an items dict.
    """

    def resolve_items(ctx: AppContext, config: Config, start_time: float) -> dict[str, Any]:
        """
        Resolves the items to include in the output using the config object. This 
        function is heavy on performance, so a start_time is needed to log performance.

        Args:
            start_time (float): relative time value to log performance of the service

        Returns:
            dict: A dict of the resolved items
        """

        # Log time at entry
        ctx.logger.log(Logger.DEBUG, 
            f"Entered ItemsSelectionService at: {round((time.time()-start_time)*1000, 2)} ms")


        # Resolve all the root paths first
        # NOTE: the root path is appended at the end of the list of resolved paths
        resolved_include_paths = ItemsSelectionService._resolve_given_paths(
            ctx, config, config.paths + config.include)
        ctx.logger.log(Logger.DEBUG, 
            f"Selected includes at: {round((time.time()-start_time)*1000, 2)} ms")
        
        resolved_exclude_paths = ItemsSelectionService._resolve_given_paths(
            ctx, config, config.exclude)
        ctx.logger.log(Logger.DEBUG, 
            f"Selected excludes at: {round((time.time()-start_time)*1000, 2)} ms")
        

        # Safety check to avoid crashes on no paths found
        if not resolved_include_paths:
            ctx.logger.log(Logger.ERROR, "No included paths were found matching given args")
            return {}


        # Start from the parent dir and keep adding items recursively
        # includes resolving hidden_files, gitignore, include and exclude
        resolved_items = ItemsSelectionService._resolve_items_rec_wrapper(ctx, config, 
            resolved_include_paths=resolved_include_paths, curr_depth=0,
            gitignore_matcher=GitIgnoreMatcher(), start_time=start_time,
            curr_dir=resolved_include_paths[-1], 
            exclude_paths=resolved_exclude_paths[:-1])
        
        ctx.logger.log(Logger.DEBUG, 
            f"Exited ItemsSelectionService at: {round((time.time()-start_time)*1000, 2)} ms")

        return resolved_items

    @staticmethod
    def _resolve_given_paths(ctx: AppContext, config: Config, attr: list[str]) -> list[Path]:
        """
        Resolve the given paths in the CLI args. Handles glob patterns, simple paths,
        and common-parent-search.

        Args:
            attr (list[str]): An attr to resolve the matching paths for

        Returns:
            list[Path]: A list of paths to be added, with the parent appended at the end
        """

        calculated_paths: list[Path] = []
        base_path = Path(os.getcwd())          # This is needed to resolve paths later


        if not attr:        # Safety check
            return [base_path]


        # Separately resolve for glob patterns and proper paths
        # Handles for *, ?, [] based patterns
        for path_str in attr:

            # If a glob pattern is provided
            if ItemsSelectionService._isglob(path_str):

                # Include underlying and hidden items as well
                matched_paths = glob.glob(path_str, recursive=True, include_hidden=True)

                # If the glob could not be resolved
                if not matched_paths:
                    ctx.logger.log(Logger.WARNING, 
                        f"No matches found for glob pattern '{path_str}'")
                    
                # Append the matches to the calculated paths
                for path_str in matched_paths:
                    calculated_paths.append(Path(path_str).resolve(strict=False))
                
            else:
                path = Path(path_str)
                resolved_path = (base_path / path).resolve(strict=False)
                calculated_paths.append(resolved_path)


        # Replace the placeholder for the parent path in the calculated paths
        if calculated_paths:
            try:
                calculated_paths.append(Path(os.path.commonpath(calculated_paths)))
            except ValueError as e:
                print(e)
                exit(1)

        return calculated_paths


    @staticmethod
    def _resolve_items_rec_wrapper(ctx: AppContext, config: Config, *,
        resolved_include_paths: list[Path], curr_dir: Path, curr_depth: int, 
        exclude_paths: list[Path], start_time: float,
        gitignore_matcher: GitIgnoreMatcher) -> tuple[dict[str, Any], int]:
        """
        Resolve the paths recursively.

        Returns:
            dict[str, Any]: A dict of the resolved root and a list of children paths
            int: current entries to keep track of the number of entries during recursion
        """

        # Vars to be used by the inner recursive function
        curr_entries: int = 0
        

        def _resolve_items_rec(ctx: AppContext, config: Config, *,
            resolved_include_paths: list[Path], curr_dir: Path, curr_depth: int, 
            exclude_paths: list[Path], start_time: float,
            gitignore_matcher: GitIgnoreMatcher) -> tuple[dict[str, Any], int]:

            nonlocal curr_entries

            resolved_root: dict[str, Any] = {
                "self": curr_dir,
                "children": []
            }
            ctx.logger.log(Logger.DEBUG, 
                f"Entered {curr_dir.name} at: {round((time.time()-start_time)*1000, 2)} ms")


            # Implementation for --max-depth
            if curr_depth > config.max_depth - 1:
                return resolved_root, curr_entries
            

            # Determine whether the current directory is under the given paths
            dir_under_given_paths = ItemsSelectionService._dir_path_under_given_paths(
                config, curr_dir)
            

            # Get the dir's children, sorted order, and files first
            children_to_add = sorted(curr_dir.iterdir(), key=lambda p: (p.is_dir(), p.name.lower()))


            # Setup gitignore object for this dir (if there is a .gitignore)
            if curr_depth <= config.gitignore_depth and (curr_dir / ".gitignore").is_file():
                gitignore_matcher.add_gitignore(
                    GitIgnore(ctx, config, gitignore_path=(curr_dir / ".gitignore")))


            items_added = 0
            # Now traverse the dir and add items
            for item_path in children_to_add:

                # If --no-files is used, then skip files
                if item_path.is_file() and config.no_files: continue


                # NOTE: this whole if-elif block bellow basically solves the problem of
                # all the files and dirs appearing in the output when only the patterns
                # of some files in some dirs is mentioned.


                # If current dir path is not given
                if not dir_under_given_paths:
                    
                    # If it is a file and it is not is resolved paths
                    # and if the current dir we are working for, is not given in paths
                    if (item_path.is_file() and not item_path in resolved_include_paths):
                        continue


                    # TODO: Pass a list of the important dirs into this function to avoid
                    # this check and improve performance
                    # Like if a file gets added to included paths it's parent dirs
                    # should get added too, and then this elif statement can be removed

                    # If it is a dir and it has no file under it that is in resolved_paths
                    elif (item_path.is_dir() and not any(ItemsSelectionService._isunder(
                            t, [item_path]) for t in resolved_include_paths)):
                        continue


                # If reached --max-items or --max-entries, then exit
                # NOTE: This is ok for now, but needs to be corrected later
                if ((not config.no_max_items and items_added >= config.max_items) or
                    (not config.no_max_entries and curr_entries >= config.max_entries)): 
                    break


                # Check if it is a hidden file/dir or hidden-items flag is not used
                if not config.hidden_items and ItemsSelectionService._ishidden(item_path):
                    continue

                
                # if within exclude depth and the item is in excludes
                if curr_depth <= config.exclude_depth and ItemsSelectionService._isunder(
                    item_path, exclude_paths):
                    continue


                # if within gitignore depth and gitignore says it is excluded
                if (curr_depth <= config.gitignore_depth and 
                    gitignore_matcher.excluded(item_path)):
                    continue


                # if within include depth and the item is in includes 
                if (ItemsSelectionService._isunder(item_path, resolved_include_paths)):
                        
                        items_added += 1
                        curr_entries += 1  
                        
                        # If the item is a file then append directly, else resolve for it
                        if item_path.is_file():
                            resolved_root["children"].append(item_path)

                        else:      
                            resolved_dir = _resolve_items_rec(
                                ctx, config, resolved_include_paths=resolved_include_paths, curr_dir=item_path, gitignore_matcher=gitignore_matcher, start_time=start_time,
                                exclude_paths=exclude_paths, curr_depth=curr_depth+1)
                                
                            resolved_root["children"].append(resolved_dir)
                            
            return resolved_root
        

        # Use the inner recursive function
        return _resolve_items_rec(ctx, config, resolved_include_paths=resolved_include_paths, 
            curr_dir=curr_dir, curr_depth=curr_depth,
            exclude_paths=exclude_paths, start_time=start_time, 
            gitignore_matcher=gitignore_matcher)


    @staticmethod
    def _dir_path_under_given_paths(config: Config, dir_path: Path) -> bool:
        """ 
        Check if the dir path was given by the user
        """

        given_paths: list[Path] = []

        for path_str in config.paths:
            if not ItemsSelectionService._isglob(path_str): 
                given_paths.append(Path(path_str).resolve(strict=False))

        return ItemsSelectionService._isunder(dir_path, given_paths)
    

    @staticmethod
    def _isglob(path_str: str) -> bool:
        return any(c in path_str for c in "*?[")
    

    @staticmethod
    def _ishidden(item_path: Path) -> bool:
        return item_path.name.startswith(".")
    
    
    @staticmethod
    def _isunder(path: Path, parents: list[Path]) -> bool:
        return any(path == p or path.is_relative_to(p) for p in parents)
