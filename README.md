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

### Updating Gitree:

To update the tool, type:

```
pip install -U gitree
```

Pip will automatically replace the older version with the latest release.


## ⚙️ CLI Arguments

In addition to the directory path, the following options are available:

| Argument            | Description |
|---------------------|-------------|
| `--version`, `-v`   | Displays the installed version. |
| `--depth`           | Limits recursion depth. Example: `--depth 1` shows only top-level files and folders. |
| `--all`, `-a`       | Includes hidden files and directories. Does not override `.gitignore`. |
| `--ignore`          | Adds extra files or directories to ignore. |
| `--ignore-depth`    | Limits depth for `--ignore` patterns. Example: `--ignore-depth 2` applies ignore rules only to first 2 levels. |
| `--gitignore-depth` | Controls how deeply `.gitignore` files are discovered. Example: `--gitignore-depth 0` uses only the root `.gitignore`. |
| `--no-gitignore`    | Ignores all `.gitignore` rules when set. |
| `--max-items`       | Limits items shown per directory. Extra items are summarized as `... and x more items`. Default: `20`. |
| `--no-limit`        | Removes the per-directory item limit. |
| `--no-files`        | Hide files from the tree (only show directories). |
| `--emoji`           | Show emojis in tree output. |
| `--summary`         | Print a summary of the number of files and folders at each level. |
| `--zip [name]`, `-z` | Zips the project while respecting `.gitignore`. Example: `--zip a` creates `a.zip`. If no name is provided, a random ID is used. |
| `--out [file]`, `-o` | Save tree structure to file. Example: `--out tree.txt` or `--out tree.md` for markdown format. |
| `--copy`, `-c`      | Copy tree output to clipboard. |


## Installation (for Contributors)

Clone the repository:

```
git clone https://github.com/ShahzaibAhmad05/Gitree
```

Move into the project directory:

```
cd Gitree
```

Install dependencies:

```
pip install -r requirements.txt
```

The tool is now available as a Python CLI on your system.

For running directly from main without installing:

```
python -m gitree.main
```


## Contributions

This is **YOUR** tool. Issues and pull requests are welcome.

Gitree is kept intentionally small and readable, so contributions that preserve simplicity are especially appreciated.
