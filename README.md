# gitree 🌴

**A CLI tool that helps generate structured context for LLMs by combining project files into a single, exportable format.**

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

# to update gitree
pip install -U gitree
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
| **Large/Binary Files Handling** | Automatically detects binary and large files and marks or skips them during export |


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

| Argument          | Description                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `--version`, `-v` | Display the **version number** of the tool.                                                                       |
| `--config-user`   | Create a **default config.json** file in the current directory and open that file in the **default editor**.        |
| `--no-config`     | Ignore both **user-level and global-level** `config.json` and use **default and CLI values** for configuration.       |
| `--verbose`       | Enable **logger output** to the console. Enabling this prints a log after the full workflow run. Helpful for **debugging**. |

### Output & Export Options

| Argument          | Description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `--zip`, `-z`     | Create a **zip archive** of the given directory respecting **gitignore rules**.                      |
| `--export`        | Save **project structure** along with its **contents** to a file with the format specified using `--format`. |
| `--format`        | **Format output** only. Options: `tree`, `json`, `md`.                                           |

### Listing Options

| Argument                     | Description                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `--max-items`                | Limit **items to be selected** per directory.                                           |
| `--max-entries`              | Limit **entries (files/dirs)** to be selected for the overall output.                   |
| `--max-depth`                | **Maximum depth** to traverse when selecting files.                                     |
| `--gitignore-depth`          | Limit depth to look for during **`.gitignore` processing**.                             |
| `--hidden-items`             | Show **hidden files and directories**.                                                  |
| `--exclude [pattern ...]`    | **Patterns of files** to specifically exclude.                                          |
| `--exclude-depth`            | Limit depth for **exclude patterns**.                                                   |
| `--include [pattern ...]`    | **Patterns of files** to specifically include.                                          |
| `--include-file-types`       | Include files of **certain types**.                                                     |
| `--copy`, `-c`               | **Copy file contents** and project structure to **clipboard**. Similar to `--export` but copies to the clipboard instead. |
| `--emoji`, `-e`              | Show **emojis** in the output.                                                          |
| `--interactive`, `-i`        | Use **interactive mode** for further file selection.                                    |
| `--files-first`              | Print **files before directories**.                                                     |
| `--no-color`                 | Disable **colored output**.                                                             |
| `--no-contents`              | Don't include **file contents** in export/copy.                                         |
| `--no-contents-for [path ...]` | Exclude **contents for specific files** for export/copy.                              |
| `--max-file-size`            | **Maximum file size** in MB to include in exports (default: 1.0).                       |
| `--override-files`           | **Override existing files**.                                                            |

### Listing Override Options

| Argument           | Description                                |
| ------------------ | ------------------------------------------ |
| `--no-max-entries` | Disable **`--max-entries` limit**.             |
| `--no-max-items`   | Disable **`--max-items` limit**.               |
| `--no-gitignore`   | Do not use **`.gitignore` rules**.             |
| `--no-files`       | Hide files (show only **directories**).        |

---


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
