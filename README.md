# gitree 🌴

**A git-aware CLI tool to provide LLM context for coding projects by combining project files into a single file with a number of different formats to choose from.**

<br>

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/shahzaibahmad05/gitree?logo=github)](https://github.com/shahzaibahmad05/gitree/stargazers)
[![PyPI](https://img.shields.io/pypi/v/gitree?logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/gitree/)
[![GitHub forks](https://img.shields.io/github/forks/shahzaibahmad05/gitree?color=blue)](https://github.com/shahzaibahmad05/gitree/network/members)
[![Contributors](https://img.shields.io/github/contributors/shahzaibahmad05/gitree)](https://github.com/shahzaibahmad05/gitree/graphs/contributors)
[![Issues closed](https://img.shields.io/github/issues-closed/shahzaibahmad05/gitree?color=orange)](https://github.com/shahzaibahmad05/gitree/issues)
[![PRs closed](https://img.shields.io/github/issues-pr-closed/shahzaibahmad05/gitree?color=yellow)](https://github.com/shahzaibahmad05/gitree/pulls)

</div>



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

Install using pip (python package manager):

```
# Install the latest version using pip
pip install gitree    

# Get the stable version instead (older, lacks features)
pip install gitree==0.1.3
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

Gitree uses Continuous Integration (CI) to ensure code quality and prevent breaking features on changes/refactoring.


### What CI Does
- Runs automated checks on every pull request
- Verifies that all CLI arguments work as expected
- Ensures the tool behaves consistently across updates


### Current Test Coverage

| Test Type | Description |
|----------|-------------|
| CLI Argument Tests | Currently validates most-used CLI flags and options |
| Workflow Checks | Every Pull Request requires passing these checks before merging |

> [!NOTE]
> ℹ️ CI tests are continuously expanding as new features are added.


### Implementation details
The CI configuration is defined in `.github/workflows/`

Each workflow file specifies:
- Trigger conditions (i.e. pull request)
- The Python version(s) used
- The commands executed during the pipeline

If any step fails, the pipeline will fail and the pull request cannot be merged until the issue is resolved.



## ⚙️ CLI Arguments

In addition to the directory path, the following options are available:

### Basic CLI flags
| Argument | Description |
|----------|-------------|
| `--version`, `-v` | Displays the installed version. |
| `--interactive`, `-i` | Interactive selection UI. |
| `--init-config` | Create a default `config.json` in the current directory. |
| `--config-user` | Open `config.json` in the default editor. |
| `--no-config` | Ignore `config.json` and use hardcoded defaults. |

### Input/Output flags
| Argument | Description |
|----------|-------------|
| `--zip [name]`, `-z` | Zip the project (respects `.gitignore`). Example: `--zip a` → `a.zip`. |
| `--json [file]` | Export tree as JSON (includes file contents by default, up to 1MB/file). |
| `--txt [file]` | Export tree as text (includes file contents by default, up to 1MB/file). |
| `--md [file]` | Export tree as Markdown (includes contents with syntax highlighting). |
| `--output [file]`, `-o` | Save tree structure to file (text or markdown). |
| `--copy`, `-c` | Copy output to clipboard. |
| `--no-contents` | Export only the tree structure (no file contents). |

### Listing flags
| Argument | Description |
|----------|-------------|
| `--max-depth` | Limit recursion depth (e.g., `--max-depth 1`). |
| `--hidden-items` | Include hidden files and directories (does not override `.gitignore`). |
| `--exclude [pattern]` | Exclude patterns (e.g., `--exclude *.pyc __pycache__`). |
| `--exclude-depth [n]` | Limit depth for exclude patterns (e.g., `--exclude-depth 2`). |
| `--gitignore-depth [n]` | Control discovery depth for `.gitignore` (e.g., `--gitignore-depth 0`). |
| `--no-gitignore` | Ignore all `.gitignore` rules. |
| `--max-items` | Limit items per directory (default: 20). |
| `--max-lines` | Limit lines (default: 40). |
| `--no-limit` | Remove per-directory item limit. |
| `--no-max-lines` | Disable total lines limit. |
| `--no-files` | Show only directories (hide files). |
| `--emoji`, `-e` | Use emojis in output. |
| `--summary` | Print file/folder counts per level. |
| `--include [pattern]` | Include patterns (often used with interactive mode). |
| `--include-file-type` | Include a specific file type (e.g., `.py`, `json`). |
| `--include-file-types` | Include multiple file types (e.g., `png jpg json`). |



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
