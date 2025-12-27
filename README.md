# Gitree

**A git-aware CLI tool to provide LLM context for coding projects by combining project files into a single file with a number of different formats to choose from.**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Project Tree Visualization** | Generate clean directory trees with customizable depth and formatting |
| 🗜️ **Smart Zipping** | Create project archives that automatically respect `.gitignore` rules |
| 🎯 **Flexible Filtering** | Control what's shown with custom ignore patterns, depth limits, and item caps |
| 🔍 **Gitignore Integration** | Use `.gitignore` files at any depth level, or disable entirely when needed |
| 📋 **Multiple Output Formats** | Export to files, copy to clipboard, or display with emoji icons |
| 📁 **Directory-Only View** | Show just the folder structure without files for high-level overviews |
| 📈 **Project Summary** | Display file and folder counts at each directory level with summary mode |

## 🔥 The problems it solves:

* sharing project structure in issues or pull requests
* generating directory trees for documentation
* pasting project layouts into LLMs
* **converting entire codebases to a single json file using `.gitignore` for prompting LLMs.**

## 📦 Installation

Run this command in your terminal:

```
# Install using pip
pip install gitree       
```

### 💡 Usage

To use this tool, refer to this format:

```
gitree [path] [other CLI args/flags]
```

Open a terminal in any project and run:

```
# path should default to .
gitree                  
```

Example output:

```
Gitree
├─ gitree/
│  ├─ constants/
│  │  ├─ __init__.py
│  │  └─ constant.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ draw_tree.py
│  │  ├─ list_enteries.py
│  │  ├─ parser.py
│  │  └─ zip_project.py
│  ├─ utilities/
│  │  ├─ __init__.py
│  │  ├─ gitignore.py
│  │  └─ utils.py
│  ├─ __init__.py
│  └─ main.py
├─ CODE_OF_CONDUCT.md
├─ CONTRIBUTING.md
├─ LICENSE
├─ pyproject.toml
├─ README.md
├─ requirements.txt
└─ SECURITY.md
```

Using emojis as file/directory icons:

```
gitree --emoji
```

Example output:

```
Gitree
├─ 📂 gitree/
│  ├─ 📂 constants/
│  │  ├─ 📄 __init__.py
│  │  └─ 📄 constant.py
│  ├─ 📂 services/
│  │  ├─ 📄 __init__.py
│  │  ├─ 📄 draw_tree.py
│  │  ├─ 📄 list_enteries.py
│  │  ├─ 📄 parser.py
│  │  └─ 📄 zip_project.py
│  ├─ 📂 utilities/
│  │  ├─ 📄 __init__.py
│  │  ├─ 📄 gitignore.py
│  │  └─ 📄 utils.py
│  ├─ 📄 __init__.py
│  └─ 📄 main.py
├─ 📄 CODE_OF_CONDUCT.md
├─ 📄 CONTRIBUTING.md
├─ 📄 LICENSE
├─ 📄 pyproject.toml
├─ 📄 README.md
├─ 📄 requirements.txt
└─ 📄 SECURITY.md
```

For zipping a directory:

```
gitree --zip out
```

creates out.zip in the same directory.

## 🧭 Interactive Mode

Gitree supports an **interactive mode** that allows you to select files and directories step-by-step instead of relying only on CLI flags.

This is useful when:
- you want fine-grained control over included files
- you prefer a guided terminal-based selection flow
- you want to explore a project before exporting its structure

### Enable Interactive Mode

Use the `-i` or `--interactive` flag:

    gitree --interactive
    # or
    gitree -i

### How It Works

When interactive mode is enabled, Gitree will:

1. Scan the project directory (respecting `.gitignore`)
2. Present an interactive file and folder selection menu
3. Allow you to choose what to include or exclude
4. Generate output based on your selections

### Interactive Controls

During interactive selection, the following keys are supported:

- **↑ / ↓** — navigate items  
- **Space** — select / deselect item  
- **Enter** — confirm selection  
- **Esc / Ctrl+C** — exit interactive mode  

### Example

    gitree -i --emoji --out context.txt

This will:
- launch interactive selection
- display output using emojis
- save the result to `context.txt`


### Updating Gitree:

To update the tool, type:

```
pip install -U gitree
```

Pip will automatically replace the older version with the latest release.


## 🧪 Continuous Integration (CI)

Gitree uses Continuous Integration (CI) to ensure code quality and prevent regressions on every change.

### What CI Does
- Runs automated checks on every pull request
- Verifies that all CLI arguments work as expected
- Ensures the tool behaves consistently across updates

### Current Test Coverage

| Test Type | Description |
|----------|-------------|
| CLI Argument Tests | Validates all supported CLI flags and options |
| Workflow Checks | Ensures PRs follow required checks before merging |

> ℹ️ CI tests are continuously expanding as new features are added.


## ⚙️ CLI Arguments

In addition to the directory path, the following options are available:

| Argument            | Description |
|---------------------|-------------|
| `--version`, `-v`   | Displays the installed version. |
| `--max-depth`           | Limits recursion depth. Example: `--depth 1` shows only top-level files and folders. |
| `--hidden-items`    | Includes hidden files and directories. Does not override `.gitignore`. |
| `--exclude`         | Patterns of files to exclude. Example: `--exclude *.pyc __pycache__`. |
| `--exclude-depth`   | Limits depth for `--exclude` patterns. Example: `--exclude-depth 2` applies exclude rules only to first 2 levels. |
| `--gitignore-depth` | Controls how deeply `.gitignore` files are discovered. Example: `--gitignore-depth 0` uses only the root `.gitignore`. |
| `--no-gitignore`    | Ignores all `.gitignore` rules when set. |
| `--max-items`       | Limits items shown per directory. Extra items are summarized as `... and x more items`. Default: `20`. |
| `--no-limit`        | Removes the per-directory item limit. |
| `--no-files`        | Hide files from the tree (only show directories). |
| `--emoji`, `-e`     | Show emojis in tree output. |
| `--summary`         | Print a summary of the number of files and folders at each level. |
| `--zip [name]`, `-z` | Zips the project while respecting `.gitignore`. Example: `--zip a` creates `a.zip`. |
| `--json [file]`     | Export tree as JSON to specified file. Example: `--json tree.json`. |
| `--txt [file]`      | Export tree as text to specified file. Example: `--txt tree.txt`. |
| `--md [file]`       | Export tree as Markdown to specified file. Example: `--md tree.md`. |
| `--output [file]`, `-o` | Save tree structure to file. Example: `--output tree.txt` or `--output tree.md` for markdown format. |
| `--copy`, `-c`      | Copy tree output to clipboard. |
| `--include`         | Patterns of files to include (used in interactive mode). Example: `--include *.py *.js`. |
| `--include-file-type` | Include files of a specific type. Example: `--include-file-type json` or `--include-file-type .py`. Case-insensitive. |
| `--include-file-types` | Include files of multiple types. Example: `--include-file-types png jpg json`. Case-insensitive. |
| `--json [file]`     | Export tree as JSON to specified file. **By default, includes file contents** (up to 1MB per file). |
| `--txt [file]`      | Export tree as text to specified file. **By default, includes file contents** (up to 1MB per file). |
| `--md [file]`       | Export tree as Markdown to specified file. **By default, includes file contents** with syntax highlighting (up to 1MB per file). |
| `--no-contents`     | Don't include file contents when exporting to JSON, TXT, or MD formats. Only the tree structure will be included. |
| `--interactive`, `-i` | Interactive mode: select files to include using a terminal-based UI. |
| `--include`         | Patterns of files to include. Example: `--include *.py *.js`. |
| `--init-config`     | Create a default `config.json` file in the current directory. |
| `--config-user`     | Open `config.json` in the default editor. |
| `--no-config`       | Ignore `config.json` and use hardcoded defaults. |


## 📝 File Contents in Exports

When using `--json`, `--txt`, or `--md` flags, **file contents are included by default**. This feature:

- ✅ Includes text file contents (up to 1MB per file)
- ✅ Detects and marks binary files as `[binary file]`
- ✅ Handles large files by marking them as `[file too large: X.XXmb]`
- ✅ Uses syntax highlighting in Markdown format based on file extension
- ✅ Works with all filtering options (`--exclude`, `--include`, `.gitignore`, etc.)

To export only the tree structure without file contents, use the `--no-contents` flag:

```bash
gitree --json output.json --no-contents
```


## Installation (for Contributors)

Clone the repository:

```
git clone https://github.com/ShahzaibAhmad05/Gitree
```

Move into the project directory:

```
cd Gitree
```

Setup a Virtual Environment (to avoid package conflicts):

```
python -m venv .venv
```

Activate the virtual environment:

```
.venv/Scripts/Activate      # on windows
.venv/bin/activate          # on linux/macOS
```

If you get an execution policy error on windows, run this:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Install dependencies in the virtual environment:

```
pip install -r requirements.txt
```

The tool is now available as a Python CLI in your virtual environment.

For running the tool, type (venv should be activated):

```
gitree
```

For running tests after making any changes:

```
python -m unittest discover tests
```


## Contributions

This is **YOUR** tool. Issues and pull requests are welcome.

Gitree is kept intentionally small and readable, so contributions that preserve simplicity are especially appreciated.
