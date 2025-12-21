# PrintStruct

A Python CLI tool for printing the structure of your project in a visually easy-to-read format. Respects `.gitignore` files when present so ignored files and folders are omitted from the output.

Example usage (on windows powershell):

````
PS C:/Users/Projects/PrintStruct> prst .
````

outputs:

````
PrintStruct
├─ LICENSE
├─ pyproject.toml
├─ README.md
├─ requirements.txt
└─ structure.py
````

<br>

## Quick Setup 

### Installation using pip:

- Run this command in your terminal:

````
pip install printstruct
````

### Installation (for Development purpose):

- Clone the repository (main branch):

````
git clone https://github.com/ShahzaibAhmad05/PrintStruct
````

- Move your terminal to the project

````
cd PrintStruct
````

- Open `pyproject.toml`, and name the keyword you want to use in terminals to call the tool under project.scripts (default is prst):

````
[project.scripts]
prst = "main:main"   # change prst to your preffered keyword
````

- Install the project on your system (globally) using pip:

````
pip install -r requirements.txt
````

and Done! The tool is installed as a python script on your system.

### Usage:

- Open a terminal in any project (any time) and run:

````
prst
````

This will print the whole structure of the repository as shown. In fact, You can also just type:
 
````
prst <directory_path>
````

in any terminal to get the structure of the directory printed.

### For Updates:

To update the tool simply follow the installation process again, but with the latest release version. Pip will automatically handle old version removal.

<br>

## Useful CLI args

*Other than the directory path*, here are some CLI args you can use with this script:

**--version** or **-v**

Displays the version of the tool installed on the system.

**--zip**

Zips the project, respecting gitignores. For example, `--zip a` should create `a.zip` in the same directory having the directory contents. If zip name is not given, it defaults to a random ID.

**--max-depth**

Limits how deep the directory recursion gets. For example, `--max-depth 1` should print the files and folders directly visible from the project root.

**--all** or **-a**

Includes hidden files and folders in the results. This does not override gitignore directives.

**--ignore** 

Adds further files or folders to ignore.

**--gitignore-depth**

Controls how deep the script looks for gitignore files. For example, `--gitignore-depth 0` should include only the gitignore present at the project root.

**--no-gitignore** 

Does not respect gitignore files if this flag is given.

**--max-items**

Max number of files/folders to display in each folder, the rest is shown as `... and x more items`. For example `--max-items 5` should display only 5 items per directory. 

Default for max items is 20.

**--no-limit**

Remove the `--max-items` limiter on printing files. 

<br>

## Contributions

Please feel free to open issues or submit pull requests to improve formatting, add features (e.g. colorized output), or add tests.
