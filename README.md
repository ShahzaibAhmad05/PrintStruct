# PrintStruct

**PrintStruct** is a clean, lightweight Python CLI that prints a directory tree of your project **while respecting `.gitignore`**, with optional zipping support.

The problems it solves:

* sharing project structure in issues or pull requests
* generating directory trees for documentation
* pasting project layouts into LLMs
* zipping projects for feeding to LLMs using `.gitignore` directions

<br>

## Quick Start (10 seconds)

### Installation using pip (recommended):

Run this command in your terminal:

```
pip install printstruct
```

### Usage:

Open a terminal in any project and run:

```
prst
```

This prints the directory structure of the current folder.

You can also specify a path explicitly:

```
prst <directory_path>
```

Example (Windows PowerShell):

```
PS C:/Users/Projects/PrintStruct> prst .
```

Output:

```
PrintStruct
├─ LICENSE
├─ pyproject.toml
├─ README.md
├─ requirements.txt
└─ structure.py
```

### Updating PrintStruct:

To update the tool, reinstall it using pip. Pip will automatically replace the older version with the latest release.

<br>

## Useful CLI arguments

In addition to the directory path, the following options are available:

| Argument | Description |
|--------|-------------|
| `--version`, `-v` | Displays the installed version. |
| `--zip [name]` | Zips the project while respecting `.gitignore`. Example: `--zip a` creates `a.zip`. If no name is provided, a random ID is used. |
| `--depth` | Limits recursion depth. Example: `--depth 1` shows only top-level files and folders. |
| `--all`, `-a` | Includes hidden files and directories. Does not override `.gitignore`. |
| `--ignore` | Adds extra files or directories to ignore. |
| `--gitignore-depth` | Controls how deeply `.gitignore` files are discovered. Example: `--gitignore-depth 0` uses only the root `.gitignore`. |
| `--no-gitignore` | Ignores all `.gitignore` rules when set. |
| `--max-items` | Limits items shown per directory. Extra items are summarized as `... and x more items`. Default: `20`. |
| `--no-limit` | Removes the per-directory item limit. |


<br>

<br>

## Installation (for Contributors)

Clone the repository:

```
git clone https://github.com/ShahzaibAhmad05/PrintStruct
```

Move into the project directory:

```
cd PrintStruct
```

Install dependencies:

```
pip install -r requirements.txt
```

The tool is now available as a Python CLI on your system.

For running directly from main without installing:

```
python -m printstruct.main
```

<br>

## Contributions

Issues and pull requests are welcome.
Ideas that would fit well include improved formatting, colorized output, test coverage, and performance optimizations.

PrintStruct is intentionally small and readable, so contributions that preserve simplicity are especially appreciated.