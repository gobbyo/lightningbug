import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def select_json_file():
    """Open a file dialog to select a JSON file."""
    file_path = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    return file_path

def modify_values(json_data, key, percentage):
    """Modify the specified key's values by a percentage."""
    for item in json_data:
        if key in item:
            try:
                item[key] = round(item[key] * (percentage / 100), 2)
            except (TypeError, ValueError):
                print(f"Skipping invalid value for key '{key}' in item: {item}")
    return json_data

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Step 1: Select the JSON file
    file_path = select_json_file()
    if not file_path:
        messagebox.showinfo("No File Selected", "No file was selected. Exiting.")
        return

    # Step 2: Load the JSON file
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to load JSON file: {e}")
        return

    # Step 3: Ask the user which key to modify
    key = simpledialog.askstring("Input", "Enter the key to modify (lu, s, or w):")
    if key not in ["lu", "s", "w"]:
        messagebox.showerror("Invalid Key", "The key must be 'lu', 's', or 'w'. Exiting.")
        return

    # Step 4: Ask the user for the percentage change
    try:
        percentage = float(simpledialog.askstring("Input", "Enter the percentage change (e.g., 10 for +10%, -10 for -10%):"))
    except (TypeError, ValueError):
        messagebox.showerror("Invalid Input", "Invalid percentage value. Exiting.")
        return

    # Step 5: Modify the values
    modified_data = modify_values(json_data, key, percentage)

    # Step 6: Save the modified JSON file
    save_path = filedialog.asksaveasfilename(
        title="Save Modified JSON File",
        defaultextension=".json",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if not save_path:
        messagebox.showinfo("No Save Location", "No save location was selected. Exiting.")
        return

    try:
        with open(save_path, 'w') as file:
            json.dump(modified_data, file, indent=4)
        messagebox.showinfo("Success", f"Modified JSON file saved to: {save_path}")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to save JSON file: {e}")

if __name__ == "__main__":
    main()