# PrintStruct

A Python CLI script for printing the structure of your project in a visually easy-to-read format. Respects `.gitignore` files when present so ignored files and folders are omitted from the output.

<br>

## Quick Setup

- Clone or copy this repository.

````
git clone https://github.com/shahzaibahmad05/printstruct
````

- Run the script from your project root:

````
python structure.py <your_project_path>
````

**Note**: It is recommended to put `structure.py` in your *projects* directory, so you can simply do:

````
python structure.py <project_directory_name>
````

<br>

## Useful CLI args

Other than the directory path, here are some CLI args you can use with this script:

**--max-depth**

Limits how deep the directory recursion gets. For example, `--max-depth 1` should print the files and folders directly visible from the project root.

**--all** or **-a**

Includes hidden files and folders in the results. This does not override gitignore directives.

**--ignore** 

Adds further files or folders to ignore.

**--gitignore-depth**

Controls how deep the script looks for gitignore files. For example, `--gitignore-depth 0` should include only the gitignore present at the project root.

<br>

## Contributions

Please feel free to open issues or submit pull requests to improve formatting, add features (e.g. colorized output), or add tests.
