import os
import tkinter as tk
from tkinter import messagebox, filedialog
import time

def get_files_and_folders(path, include_subfolders=True):
    """
    Get all files and folders in the specified path.
    """
    files = []
    folders = []
    if include_subfolders:
        for root, dirs, filenames in os.walk(path):
            for folder in dirs:
                full_path = os.path.join(root, folder)
                folders.append(full_path)
            for filename in filenames:
                files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                files.append(file_path)
            elif os.path.isdir(file_path):
                folders.append(file_path)
    return files, folders

def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    """
    return os.path.getsize(file_path)

def get_last_access_time(file_path):
    """
    Get the last access time of a file in seconds since the epoch.
    """
    return os.path.getatime(file_path)

def suggest_deletion(files, percent_to_free_up):
    """
    Suggest files to delete based on size and last access time.
    """
    # Calculate total size of all files
    total_size = sum(get_file_size(file_path) for file_path in files)

    # Sort files by last access time
    files.sort(key=get_last_access_time)

    # Calculate how much space to free up
    space_to_free_up = total_size * (percent_to_free_up / 100)
    space_freed = 0

    # Suggest files for deletion
    suggested_files = []
    for file_path in files:
        try:
            file_size = get_file_size(file_path)
            if space_freed + file_size <= space_to_free_up:
                last_access_time = get_last_access_time(file_path)
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_access_time))
                suggested_files.append((file_path, file_size, formatted_time))
                space_freed += file_size
            else:
                break
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return suggested_files

def perform_deletion(files_to_delete, text_files_to_delete):
    """
    Delete the specified files and folders and remove them from the displayed list.
    """
    for file_info in files_to_delete:
        file_path = file_info[0]
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
            # Remove deleted item from the displayed list
            text_files_to_delete.delete(file_info[3], file_info[4])
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def on_submit():
    directory = entry_directory.get()
    percent_to_free_up = entry_percentage.get()
    try:
        percent_to_free_up = float(percent_to_free_up)
        if not 0 <= percent_to_free_up <= 100:
            raise ValueError("Percentage must be between 0 and 100")
    except ValueError:
        messagebox.showerror("Error", "Invalid percentage value. Please enter a number between 0 and 100.")
        return

    include_subfolders = checkbox_subfolders_var.get()  # Get the state of the checkbox
    files, _ = get_files_and_folders(directory, include_subfolders)
    suggested_files = suggest_deletion(files, percent_to_free_up)

    # Open confirmation dialog
    confirm_deletion(suggested_files)

def on_choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)

def confirm_deletion(files_to_delete=[]):
    """
    Display a confirmation dialog for deletion and allow the user to edit the list.
    """
    confirm_dialog = tk.Toplevel()
    confirm_dialog.title("Confirm Deletion")

    label = tk.Label(confirm_dialog, text="Review and edit the list of files and folders to be deleted:")
    label.pack(padx=10, pady=5)

    # Create a Text widget for displaying the files to delete
    text_files_to_delete = tk.Text(confirm_dialog, width=100, height=20)
    text_files_to_delete.pack(padx=10, pady=5)

    # Add a scrollbar to the Text widget
    scrollbar = tk.Scrollbar(confirm_dialog, command=text_files_to_delete.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_files_to_delete.config(yscrollcommand=scrollbar.set)

    for idx, file_info in enumerate(files_to_delete):
        file_path, file_size, formatted_time = file_info
        # Insert file info into the Text widget and save index range for deletion
        start_idx = f"{idx}.0"
        end_idx = f"{idx}.end"
        text_files_to_delete.insert(tk.END, f"File: {file_path}\nSize: {file_size} bytes\nLast accessed: {formatted_time}\n\n")
        files_to_delete[idx] = file_info + (start_idx, end_idx)  # Save index range for deletion

    def confirm():
        nonlocal files_to_delete  # Use nonlocal to access outer scope variable
        files_to_delete_text = text_files_to_delete.get("1.0", "end")
        files_to_delete = [file_info for file_info in files_to_delete if file_info[0] in files_to_delete_text]  # Update files_to_delete
        confirm_dialog.destroy()
        perform_deletion(files_to_delete, text_files_to_delete)

    confirm_button = tk.Button(confirm_dialog, text="Confirm Deletion", command=confirm)
    confirm_button.pack(padx=10, pady=5)

root = tk.Tk()
root.title("Disk Cleanup Suggestion Tool by @cwhitese")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_directory = tk.Label(frame, text="Directory:")
label_directory.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry_directory = tk.Entry(frame, width=50)
entry_directory.grid(row=0, column=1, padx=5, pady=5)

choose_directory_button = tk.Button(frame, text="Choose Directory", command=on_choose_directory)
choose_directory_button.grid(row=0, column=2, padx=5, pady=5)

label_percentage = tk.Label(frame, text="Percentage to Free Up:")
label_percentage.grid(row=1, column=0, padx=5, pady=5, sticky="e")

entry_percentage = tk.Entry(frame, width=10)
entry_percentage.grid(row=1, column=1, padx=5, pady=5)

# Checkbox for including subfolders
checkbox_subfolders_var = tk.BooleanVar()
checkbox_subfolders = tk.Checkbutton(frame, text="Include Subfolders", variable=checkbox_subfolders_var)
checkbox_subfolders.grid(row=2, column=1, padx=5, pady=5)

submit_button = tk.Button(frame, text="Submit", command=on_submit)
submit_button.grid(row=3, column=1, padx=5, pady=5)

root.mainloop()
