"""Searches for zip files in folder and unzips
in new folder based on zip name. Creates a record 
of original zip file on disk, before deleting zip file. 
Sets new permissions on unzipped content."""

import os
import zipfile
import stat
from clean_resources import tools


def get_zip_paths(path=str) -> tuple:
    """Search for zip file in input path and check if valid."""
    filepaths = []
    for dirpath, _, files in os.walk(path):
        for file in files:
            # Find zip files.
            if file.endswith(".zip"):
                target_zip = os.path.join(dirpath, file)
                # Check if zip file is empty / readable.
                filepaths = check_zip_file(target_zip, filepaths)
    return tuple(filepaths)


def generate_zip_vars(zip_path=str) -> str:
    """Splits / edits input zip path and returns edited name."""
    # Path parent folder / path, then filename.
    zip_dirpath, zip_basename = os.path.split(zip_path)

    # Filename without extension '.zip'.
    zip_name = zip_basename[:-4]
    return zip_dirpath, zip_basename, zip_name


def check_zip_file(zip_path=str, zip_files=list) -> list:
    """Opens zip file and checks if empty,
    adds valid files to list."""
    filename = os.path.basename(zip_path)
    try:
        with zipfile.ZipFile(zip_path, "r") as my_zip:
            if len(my_zip.namelist()) == 0:
                raise ValueError
            else:
                print(f"ZIP file found: {filename}")
                zip_files.append(zip_path)
    except ValueError:
        file = os.path.basename(zip_path)
        tools.red(f"'{file}' is empty or invalid.")
    return zip_files


def create_output_dir(input_path) -> str:
    """Create output dir if doesn't exist."""
    dirpath, _, z_name = generate_zip_vars(input_path)
    output_dir = f"{dirpath}/{z_name}_unzipped"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def unzip_file(zip_f=str):
    """Unzip file in new folder under parent."""
    # Remove new lines from zip contents var.
    zip_contents = generate_file_list(zip_f)
    file_list = [file.replace("\n", "") for file in zip_contents]

    # Open zip file and use file list to unzip verbosely.
    unzipped_dir = create_output_dir(zip_f)
    with zipfile.ZipFile(zip_f, "r") as z_file:
        tools.bold(f"\nOutput Folder: {unzipped_dir}")
        for file in file_list:
            print(f"Extracting '{file}'")
            z_file.extract(file, unzipped_dir)
    print("Extraction complete.")

    # Update permissions on unzipped folder.
    set_permissions(unzipped_dir)


def set_permissions(starting_dir):
    """Recursively sets permissions to
    files / folders under input path."""
    perms = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH
    os.chmod(starting_dir, perms)
    for dirpath, dirname, files in os.walk(starting_dir):
        for directory in dirname:
            folder_path = os.path.join(dirpath, directory)
            os.chmod(folder_path, perms)
            print(f"Updated Permissions: {folder_path}")
        for f in files:
            f_path = os.path.join(dirpath, f)
            os.chmod(f_path, perms)


def generate_file_list(zip_path=str) -> list:
    """Returns contents of zip in list."""
    file_list = []
    with zipfile.ZipFile(zip_path, "r") as my_zip:
        for file in my_zip.namelist():
            file_list.append(file + "\n")
    return file_list


def write_list_to_file(input_zipfile=str):
    """Writes contents of input zip to text file."""
    # Get zip contents.
    zip_contents = generate_file_list(input_zipfile)

    # Get zip basename.
    _, zip_base, _ = generate_zip_vars(input_zipfile)

    # Write file.
    output_path = get_text_path(input_zipfile)
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(f"FILENAME: {zip_base}\n")
        out_file.write(f"PATH: {input_zipfile}\n\nCONTENTS:\n")
        out_file.writelines(zip_contents)
        out_file.write("\nThis file was unzipped and then removed from disk.\n")
        print(f"\nPrinted '{zip_base}' contents to '{output_path}'.")


def get_text_path(in_z_path=str) -> str:
    """Returns path for output text file."""
    zip_dir, _, zip_name = generate_zip_vars(in_z_path)
    out_path = os.path.join(zip_dir, f"{zip_name}_zip_contents.txt")
    return out_path


def check_zip(file_path) -> bool:
    """Compare files in zip and in unzipped folder."""
    # Counts files / folders and combines num.
    disk_item_num = 0
    unzipped_dir = create_output_dir(file_path)
    for dirpath, folders, files in os.walk(unzipped_dir):
        if dirpath == unzipped_dir:
            disk_item_num += len(folders)
            disk_item_num += len(files)
        folders.clear()     # Cleared subfolders, so won't descend further.
        
    # Collects zip file list, ignoring parent folder.
    items = []
    with zipfile.ZipFile(file_path, "r") as my_zip:
        for item in my_zip.namelist():  
            parent = os.path.basename(unzipped_dir) + '/'
            if item != parent:  
                items.append(item)

    # Reads only first level of zip file.
    z_items = set([f.split('/')[0] for f in items])
    zip_item_num = len([f for f in z_items if f])

    # Compare numbers and if they match, return true.
    if disk_item_num == zip_item_num:
        tools.green(f"File number on disk '{disk_item_num}' matches ZIP '{zip_item_num}'.")
        return True
    elif disk_item_num != zip_item_num:
        tools.red(f"File number on disk '{disk_item_num}' doesn't match ZIP '{zip_item_num}'.")
        return False  


# Main.
def main(input_folder_path=str):
    print('')
    zip_files = get_zip_paths(input_folder_path)
    out_txt_paths = []

    for zip_file in zip_files:
        # Unzip file into folder.
        unzip_file(zip_file)

        # Write the zip's file list to text.
        write_list_to_file(zip_file)
        out_txt_file = get_text_path(zip_file)
        out_txt_paths.append(out_txt_file)

    print_count = 0
    for zip_file in zip_files:
        remove_prompt = """
        Zip files have all been extracted. The program can check files have been 
        unzipped successfully, and then delete or you can choose to be prompted 
        before each file is deleted. 
        \nDo you want to be prompted before deleting?"""
        if print_count == 0:
            remove_prompt_opt = tools.user_input(remove_prompt)
            print_count += 1
        
        tools.yellow(f"\n{zip_file}")
        completed_successfully = check_zip(zip_file)
        if completed_successfully and remove_prompt_opt:
            delete_prompt = tools.user_input("Delete ZIP file?")
            if delete_prompt:
                os.remove(zip_file)
                tools.green("ZIP file has now been deleted.")
            else:
                print("ZIP file not deleted.")
        elif completed_successfully and not remove_prompt_opt:
            os.remove(zip_file)
            tools.green("ZIP file has now been deleted.")
        else:
            tools.yellow("Unzip may not have been successful. Did not delete. Please investigate further.")

    # Print zip file record paths.
    print('')
    if out_txt_paths:
        for num, f in enumerate(out_txt_paths, 1):
            print(f"Zip Record {num}: {f}")
    else:
        print("No ZIP files found in input folder.")


INPUT_FOLDER = None  # Path provided in clean_folder.py
if __name__ == "__main__":
    main(INPUT_FOLDER)
