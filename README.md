# gitree 🌴

**A CLI tool to provide LLM context for coding projects by combining project files into a single file with a number of different formats to choose from.**

<br>

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/shahzaibahmad05/gitree?logo=github)](https://github.com/shahzaibahmad05/gitree/stargazers)
[![PyPI](https://img.shields.io/pypi/v/gitree?logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/gitree/)
[![GitHub forks](https://img.shields.io/github/forks/shahzaibahmad05/gitree?color=blue)](https://github.com/shahzaibahmad05/gitree/network/members)
[![Contributors](https://img.shields.io/github/contributors/shahzaibahmad05/gitree)](https://github.com/shahzaibahmad05/gitree/graphs/contributors)
[![Issues closed](https://img.shields.io/github/issues-closed/shahzaibahmad05/gitree?color=orange)](https://github.com/shahzaibahmad05/gitree/issues)
[![PRs closed](https://img.shields.io/github/issues-pr-closed/shahzaibahmad05/gitree?color=yellow)](https://github.com/shahzaibahmad05/gitree/pulls)

</div>

---

## 📦 Installation

Install using **pip** (python package manager):

```bash
# Install the latest version using pip
pip install gitree
```

---

### 💡 Usage

To use this tool, refer to this **format**:

```bash
gitree [paths] [other CLI args/flags]
```

**To literally get started, I would recommend doing this:**

Open a terminal in any project and run:

```bash
# paths should default to .
# This will scan gitignores by default
gitree
```

Now try this for better visuals:

```bash
gitree --emoji
```

You _should_ see an output like this:

```text
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

Some useful commands you can use everyday with this tool:

```bash
# Copy all C++ code in your project, 
# with interactive selection for those files
gitree **/*.cpp --copy -i
```

```bash
# Zip the whole project files (respecting gitignore)
# creates project.zip in the same directory
gitree --zip project
```

```bash
# Export the file contents of your project, in different formats to choose from
gitree --export project --format tree
gitree --export project --format json
gitree --export project --format md
```

---

## 🧩 How it Works

```
    ╭────────────────────────────╮
    │           Start            │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │      Argument Parsing      │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │  Files/Folders Selection   │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │   Interactive Selection    │
    │      (only if used)        │
    ╰────────────────────────────╯
            │
            ├─────────────────────────┐
            │                         │
            ▼                         ▼
    ╭─────────────────╮    ╭─────────────────────╮
    │ Zipping Service │    │   Drawing Service   │
    ╰─────────────────╯    ╰─────────────────────╯
            │                  │
            │                  ├────────────────────┐
            │                  │                    │
            │                  ▼                    ▼
            │         ╭─────────────────╮  ╭──────────────────╮
            │         │  Copy Service   │  │  Export Service  │
            │         ╰─────────────────╯  ╰──────────────────╯
            │                  │                    │
            │                  └──────────┬─────────┘
            │                             │
            └─────────────────────────────┘
                           │
                           ▼
               ╭────────────────────────╮
               │    Output & Finish     │
               ╰────────────────────────╯

```

---

### 🏷️ Updating Gitree:

To update the tool, type:

```bash
pip install -U gitree
```

Pip will automatically replace the older version with the **latest release**.

---

## ✨ Overall Features

| Feature                           | Description                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------- |
| **Tree Visualization** | Generate a structure for any directory for visualizing and understanding the codebase |
| **Smart File Selection** | Control what's selected by the tool with custom ignore patterns, depth limits, and item caps |
| **Interactive Selection** | Gain full control of the output by reviewing what's selected by the file selection service |
| **Copy Your Codebase** | Instantly copy the whole codebase file contents to your clipboard to paste into LLMs |
| **Multiple Export Formats** | Export your codebase contents to files using tree, json and markdown formats |
| **Zipping the Whole Project** | Create project archives that automatically respect `.gitignore` rules |

---

## 🧪 Continuous Integration (CI)

Gitree uses **Continuous Integration (CI)** to ensure code quality and prevent regressions on every change.

### What CI Does

- Runs **automated checks** on every pull request
- Verifies that all **CLI arguments** work as expected
- Ensures the tool **behaves consistently** across updates

> [!NOTE]
> CI tests are continuously expanding as new features are added.

---

## ⚙️ CLI Arguments

The following optional arguments are available for use:

### General Options

| Argument              | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `--version`, `-v`     | Displays the **installed version**.                      |
| `--interactive`, `-i` | **Interactive selection UI**.                            |
| `--init-config`       | Create a default `config.json` in the current directory. |
| `--config-user`       | Open `config.json` in the **default editor**.            |
| `--no-config`         | Ignore `config.json` and use **hardcoded defaults**.     |

### Input/Output flags

| Argument                | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| `--max-depth`           | Limit recursion depth (e.g., `--max-depth 1`).                          |
| `--hidden-items`        | Include hidden files and directories (does not override `.gitignore`).  |
| `--exclude [pattern]`   | Exclude patterns (e.g., `--exclude *.pyc __pycache__`).                 |
| `--exclude-depth [n]`   | Limit depth for exclude patterns (e.g., `--exclude-depth 2`).           |
| `--gitignore-depth [n]` | Control discovery depth for `.gitignore` (e.g., `--gitignore-depth 0`). |
| `--no-gitignore`        | Ignore all `.gitignore` rules.                                          |
| `--max-items`           | Limit items per directory (default: 20).                                |
| `--max-entries`           | Limit entries (default: 40).                                          |
| `--no-max-entries`        | Disable total entries limit.                                          |
| `--no-files`            | Show only directories (hide files).                                     |
| `--emoji`, `-e`         | Use emojis in output.                                                   |
| `--summary`             | Print file/folder counts per level.                                     |
| `--include [pattern]`   | Include patterns (often used with interactive mode).                    |
| `--include-file-type`   | Include a specific file type (e.g., `.py`, `json`).                     |
| `--include-file-types`  | Include multiple file types (e.g., `png jpg json`).                     |

### Listing flags

| Argument                | Description                                                                |
| ----------------------- | -------------------------------------------------------------------------- |
| `--max-depth`           | Limit **recursion depth** (e.g., `--max-depth 1`).                         |
| `--hidden-items`        | Include **hidden files and directories** (does not override `.gitignore`). |
| `--exclude [pattern]`   | **Exclude patterns** (e.g., `--exclude *.pyc __pycache__`).                |
| `--exclude-depth [n]`   | Limit depth for **exclude patterns** (e.g., `--exclude-depth 2`).          |
| `--gitignore-depth [n]` | Control discovery depth for **.gitignore** (e.g., `--gitignore-depth 0`).  |
| `--no-gitignore`        | Ignore all **.gitignore** rules.                                           |
| `--max-items`           | Limit **items per directory** (default: 20).                               |
| `--no-max-items`            | Remove per-directory **item limit**.                                       |
| ` --no-files`           | Show only **directories** (hide files).                                    |

---

## 📝 File Contents in Exports

When using `--json`, `--tree`, or `--md` flags, **file contents are included by default**. This feature:

- ✅ Includes **text file contents** (up to 1MB per file)
- ✅ Detects and marks **binary files** as `[binary file]`
- ✅ Handles **large files** by marking them as `[file too large: X.XXmb]`
- ✅ Uses **syntax highlighting** in Markdown format based on file extension
- ✅ Works with all **filtering options** (`--exclude`, `--include`, `.gitignore`, etc.)

To export only the tree structure without file contents, use the `--no-contents` flag:

```bash
gitree --json output.json --no-contents

```

---

## Installation (for Contributors)

Clone the **repository**:

```bash
git clone https://github.com/ShahzaibAhmad05/gitree
```

Move into the **project directory**:

```bash
cd gitree
```

Setup a **Virtual Environment** (to avoid package conflicts):

```bash
python -m venv .venv
```

Activate the **virtual environment**:

```bash
.venv/Scripts/Activate      # on windows
.venv/bin/activate          # on linux/macOS
```

> [!WARNING]
> If you get an **execution policy error** on windows, run this:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

Install **dependencies** in the virtual environment:

```bash
pip install -r requirements.txt

```

The tool is now available as a **Python CLI** in your virtual environment.

For running the tool, type (**venv should be activated**):

```bash
gitree

```

For running **unit tests** after making changes:

```bash
python -m tests
```

---

## Contributions

> [!TIP]
> This is **YOUR** tool. Issues and pull requests are always welcome.

Gitree is kept intentionally small and readable, so contributions that preserve **simplicity** and follow [Contributing Guidelines](https://github.com/ShahzaibAhmad05/gitree?tab=contributing-ov-file) are especially appreciated.
