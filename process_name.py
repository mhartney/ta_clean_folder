"""Formats input path basename and returns.
Removes / replaces specific characters often found in
package downloads. Removes special characters that are
not letters or numbers. Ensures words are seperated 
by only one underscore."""

import os
import re
import json
from pathlib import Path


def remove_unwanted_text(path: str) -> str:
    """Remove unwanted characters and complete
    several checks on input text."""

    path_dir, base = split_path(path)
    print(f"\nChecking folder name '{base}' ...")

    # Remove extensions.
    new_base = remove_extensions(base)

    # Remove unwanted chars / make replacements.
    new_base = edit_basename(new_base)
    return os.path.join(path_dir, new_base)


def split_path(in_path=str) -> str:
    """Returns dirpath / base."""
    if in_path[-1] == "/":
        in_path = in_path[:-1]
    dirpath, basename = os.path.split(in_path)
    return dirpath, basename


def resources_path(filename: str) -> Path:
    """Return text file path from program dir."""
    program_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(program_dir, "clean_resources", filename)


def remove_extensions(basename) -> str:
    """Reads list of extensions from file and 
    checks basename. If present, program removes."""
    ext_path = resources_path("extensions_list.json")
    with open(ext_path) as file:
        ext_list = json.load(file)
    
    # Remove ext if present.
    for ext in ext_list["extensions"]:
        basename = basename.replace(ext, '_')
    return basename
    


def edit_basename(input_base:str) -> str:
    """Iterate through a sequence of regex to
    edit the folder name."""
    DIR_NAME_SUBSITUTIONS = (
    (r"^PKG", ''),   # Remove 'PKG' at start.
    (r"[\s\.\\-]+", '_'),   # Space, '-', '.'
    (r"[&+]", "_and_"),  # '&' or '+'  
    (r"[^a-zA-Z0-9_]", ''), # Remove special chars.
    (r"_{2,}", '_'),  # Only 1 underscore.
    (r"^_+|_+$", '') # Remove underscores at bookends.
    )
    
    for pattern, sub in DIR_NAME_SUBSITUTIONS:
        input_base = re.sub(pattern, sub, input_base)
    output_base = input_base
    return output_base


def main(path=str) -> str:
    edited_path = remove_unwanted_text(path)
    return edited_path


INPUT_PATH = None  # Path provided in clean_folder.py
if __name__ == "__main__":
    main(INPUT_PATH)
