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

---

## ✨ Features

| Feature                           | Description                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------- |
| 📊 **Project Tree Visualization** | Generate clean directory trees with customizable depth and formatting         |
| 🗜️ **Smart Zipping**              | Create project archives that automatically respect `.gitignore` rules         |
| 🎯 **Flexible Filtering**         | Control what's shown with custom ignore patterns, depth limits, and item caps |
| 🔍 **Gitignore Integration**      | Use `.gitignore` files at any depth level, or disable entirely when needed    |
| 📋 **Multiple Export Formats**    | Export to files, copy to clipboard, or display with emoji icons               |
| 📁 **Directory-Only View**        | Show just the folder structure without files for high-level overviews         |
| 📈 **Project Summary**            | Display file and folder counts at each directory level with summary mode      |

---

## 🔥 The problems it solves:

- **sharing project structure** in issues or pull requests
- **generating directory trees** for documentation
- **pasting project layouts** into **LLMs**
- **converting entire codebases** to a **single json file** using `.gitignore` for prompting LLMs.

---

## 📦 Installation

Install using **pip** (python package manager):

```bash
# Install the latest version using pip
pip install gitree

# Get the stable version instead (older, lacks features)
pip install gitree==0.1.3

```

---

### 💡 Usage

To use this tool, refer to this **format**:

```bash
gitree [path] [other CLI args/flags]

```

Open a terminal in any project and run:

```bash
# path should default to .
gitree

```

Example output:

```text
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

Using **emojis** as file/directory icons:

```bash
gitree --emoji

```

Example output:

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

For **zipping** a directory:

```bash
gitree --zip out

```

creates **out.zip** in the same directory.

For **combining interactive selection with export**:

```bash
gitree --export project -i

```

This allows you to interactively select files and save the export to **project.txt**.

---

## 🧭 Interactive Mode

Gitree supports an **interactive mode** that allows you to select files and directories step-by-step instead of relying only on CLI flags.

> [!TIP] > **This is useful when:**
>
> - you want **fine-grained control** over included files
> - you prefer a **guided terminal-based selection flow**
> - you want to **explore a project** before exporting its structure

### Enable Interactive Mode

Use the `-i` or `--interactive` flag:

```bash
gitree --interactive
# or
gitree -i

```

### How It Works

When interactive mode is enabled, **Gitree** will:

1. **Scan** the project directory (respecting `.gitignore`)
2. **Present** an interactive file and folder selection menu
3. **Allow** you to choose what to include or exclude
4. **Generate** output based on your selections

### Interactive Controls

During interactive selection, the following **keys** are supported:

- **↑ / ↓** — navigate items
- **Space** — select / deselect item
- **Enter** — confirm selection
- **Esc / Ctrl+C** — exit interactive mode

### Example

```bash
gitree -i --emoji --out context.txt

```

This will:

- launch **interactive selection**
- display output using **emojis**
- save the result to `context.txt`

---

### Updating Gitree:

To update the tool, type:

```bash
pip install -U gitree

```

Pip will automatically replace the older version with the **latest release**.

---

## 🧪 Continuous Integration (CI)

Gitree uses **Continuous Integration (CI)** to ensure code quality and prevent regressions on every change.

### What CI Does

- Runs **automated checks** on every pull request
- Verifies that all **CLI arguments** work as expected
- Ensures the tool **behaves consistently** across updates

### Current Test Coverage

| Test Type          | Description                                       |
| ------------------ | ------------------------------------------------- |
| CLI Argument Tests | Validates all supported CLI flags and options     |
| Workflow Checks    | Ensures PRs follow required checks before merging |

> [!NOTE]
> CI tests are continuously expanding as new features are added.

---

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

When using `--json`, `--txt`, or `--md` flags, **file contents are included by default**. This feature:

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
git clone [https://github.com/ShahzaibAhmad05/Gitree](https://github.com/ShahzaibAhmad05/Gitree)

```

Move into the **project directory**:

```bash
cd Gitree

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

For running **tests** after making any changes:

```bash
python -m unittest discover tests

```

---

## Contributions

> [!TIP]
> This is **YOUR** tool. Issues and pull requests are welcome.

Gitree is kept intentionally small and readable, so contributions that preserve **simplicity** are especially appreciated.
