import tkinter as tk
import json

# clicking on the cell will highlight it and add it to the sequence file
# control + click on the cell will highlight the corresponding sequence value
# shift + click on the cell will show editable fields for the cell

SEQUENCE_FILE = "D_LED_sequence.json"  # Default sequence file name

class GridApp:
    def __init__(self, root, config):
        self.sequence_file = SEQUENCE_FILE
        self.root = root
        self.rows = config['rows']
        self.cols = config['cols']
        self.cell_width = config['cell_width']
        self.cell_height = config['cell_height']
        self.header_height = config['header_height']
        self.borderwidth = config['borderwidth']
        self.relief = config['relief']
        self.bg_color = config['bg_color']
        self.highlight_color = config['highlight_color']
        self.highlighted_color = config['highlighted_color']
        self.highlighted_cells = {}
        self.key_sequence = {}
        self.cell_data = {}  # Dictionary to store highlighted cells and their associated keys and values
        self.canvas = tk.Canvas(root)
        self.frame = tk.Frame(self.canvas)
        self.scroll_x = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.pack(side="bottom", fill="x")
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.create_grid()
        self.root.bind("<KeyRelease>", self.store_key)  # Bind key releas 
        self.led_positions_file = config['led_positions_file']
        self.load_highlighted_cells()  # Load highlighted cells from JSON file
        self.default_lumin = 30  # Default luminance
        self.default_sleepsec = 0.25  # Default sleep seconds
        self.default_waitsec = 0.25  # Default wait seconds

        sequence_frame = tk.Frame(root)  # Create a frame for the sequence display and scrollbar
        sequence_frame.pack(side="right", fill="y", padx=5, pady=(self.header_height * 20, 0))  # Adjust top padding to align with header

        self.sequence_display = tk.Text(sequence_frame, width=46, state="disabled", wrap="none")  # Increase width to 50
        sequence_scrollbar = tk.Scrollbar(sequence_frame, orient="vertical", command=self.sequence_display.yview)  # Create a scrollbar
        self.sequence_display.configure(yscrollcommand=sequence_scrollbar.set)  # Link the scrollbar to the text widget

        self.sequence_display.pack(side="left", fill="y")  # Pack the text widget
        sequence_scrollbar.pack(side="right", fill="y")  # Pack the scrollbar

        self.initialize_sequence_file()  # Initialize the sequence file
        self.update_sequence_display()  # Display existing sequence values in the sequence display pane
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Bind cleanup function to window close event
        self.sequence_display.bind("<Delete>", self.delete_sequence_node)  # Bind delete key to delete sequence node

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_grid(self):
        # Add column headers
        for col in range(self.cols):
            header = tk.Label(self.frame, text=str(col), borderwidth=0, relief=self.relief, width=self.cell_width, height=self.header_height)
            header.grid(row=0, column=col+1)  # Shift column numbering one cell to the right
        # Add row headers
        for row in range(1, self.rows + 1):
            header = tk.Label(self.frame, text=str(row-1), borderwidth=self.borderwidth, width=self.cell_width, height=self.header_height)
            header.grid(row=row, column=0)
        # Adjust row and column start to 1 to accommodate headers
        for row in range(1, self.rows + 1):
            for col in range(1, self.cols + 1):
                cell_text = f"x:{row-1},y:{col-1}\n"  # Change text to x and y
                cell = tk.Label(self.frame, text=cell_text, borderwidth=self.borderwidth, relief=self.relief, 
                                width=self.cell_width, height=self.cell_height, bg=self.bg_color, 
                                highlightbackground=self.highlight_color)
                cell.grid(row=row, column=col)
                cell.bind("<Button-1>", self.toggle_highlight)  # Ensure left-click event is bound to toggle_highlight

    def toggle_highlight(self, event):
        focused_widget = self.root.focus_get()
        cell_info = event.widget.grid_info()
        cell_position = f"{cell_info['row'] - 1},{cell_info['column'] - 1}"

        if cell_position in self.highlighted_cells:
            print(f"Clicked: {cell_position}")
            ref_number = self.highlighted_cells[cell_position]["ref"]

            # Highlight sequence values if the control key is held
            if event.state & 0x0004:  # Check if the control key is pressed
                self.highlight_sequence_value(ref_number)
            else:
                # Add to sequence file only if Control is not pressed
                self.append_to_sequence_file(cell_position, ref_number)

            # Show editable fields only if the shift key is held
            if event.state & 0x0001:  # Check if the shift key is pressed
                self.show_editable_fields(event.widget, cell_position)

    def highlight_sequence_value(self, ref_number):
        """Highlight the sequence value corresponding to the given ref_number."""
        self.sequence_display.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
        self.sequence_display.tag_configure("highlight", background="yellow")  # Configure highlight style

        # Search for the line containing the ref_number and highlight it
        lines = self.sequence_display.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{ref_number}."):  # Match the ref_number format in the sequence pane
                start_index = f"{i + 1}.0"
                end_index = f"{i + 1}.end"
                self.sequence_display.tag_add("highlight", start_index, end_index)
                break

    def show_editable_fields(self, widget, cell_position):
        # Create a popup frame for editing lu, s, and w values
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Node Values for {cell_position}")
        popup.geometry("200x180")  # Adjusted height to ensure buttons are fully visible

        # Retrieve current values or set defaults
        current_node = next((node for node in self.sequence if node["r"] == self.highlighted_cells[cell_position]["ref"]), {})
        lu_value = current_node.get("lu", 30)
        s_value = current_node.get("s", 0.25)
        w_value = current_node.get("w", 0.25)

        # Create labels and entry fields
        tk.Label(popup, text="LU:").pack()
        lu_entry = tk.Entry(popup)
        lu_entry.insert(0, str(lu_value))
        lu_entry.pack()

        tk.Label(popup, text="S:").pack()
        s_entry = tk.Entry(popup)
        s_entry.insert(0, str(s_value))
        s_entry.pack()

        tk.Label(popup, text="W:").pack()
        w_entry = tk.Entry(popup)
        w_entry.insert(0, str(w_value))
        w_entry.pack()

        # Save button to update the sequence
        def save_values():
            try:
                lu = float(lu_entry.get())
                s = float(s_entry.get())
                w = float(w_entry.get())
                # Update the node in the sequence for the current cell only
                for node in self.sequence:
                    if node["r"] == self.highlighted_cells[cell_position]["ref"]:
                        node["lu"] = lu
                        node["s"] = s
                        node["w"] = w
                        break
                # Update default values
                self.default_lumin = lu
                self.default_sleepsec = s
                self.default_waitsec = w

                # Update the config.json file with the new default values
                try:
                    with open('config.json', 'r') as f:
                        config = json.load(f)
                    config['default_lumin'] = self.default_lumin
                    config['default_sleepsec'] = self.default_sleepsec
                    config['default_waitsec'] = self.default_waitsec
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=4)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error updating config.json: {e}")

                # Save the updated sequence to the file
                with open(self.sequence_file, 'w') as f:
                    json.dump(self.sequence, f, indent=4)
                popup.destroy()
            except ValueError:
                print("Invalid input. Please enter numeric values.")

        # Create a cancel button to close the popup without saving
        def cancel():
            popup.destroy()

        # Create a frame to hold the buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        # Add Save and Cancel buttons to the frame
        tk.Button(button_frame, text="Save", command=save_values).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)

        # Set default values in the entry fields
        lu_entry.delete(0, tk.END)
        lu_entry.insert(0, str(self.default_lumin))
        s_entry.delete(0, tk.END)
        s_entry.insert(0, str(self.default_sleepsec))
        w_entry.delete(0, tk.END)
        w_entry.insert(0, str(self.default_waitsec))

    def append_to_sequence_file(self, cell_position, ref_number):
        if ref_number > 63:
            print(f"Ref number {ref_number} exceeds the limit of 63. Skipping save.")
            return  # Do not save if ref number exceeds 63

        row, col = map(int, cell_position.split(','))
        # Reload default values from config.json
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            default_lumin = config.get('default_lumin', 30)
            default_sleepsec = config.get('default_sleepsec', 0.25)
            default_waitsec = config.get('default_waitsec', 0.25)
        except (FileNotFoundError, json.JSONDecodeError):
            default_lumin = 30
            default_sleepsec = 0.25
            default_waitsec = 0.25

        # Obtain the "m" value from the "mod" field in highlighted_cells
        mod_value = self.highlighted_cells[cell_position]["mod"]
        m_value = mod_value.split(",")[0]  # Use the value on the left of the ","
        ch = int(mod_value.split(",")[1])  # Use the value on the right of the ","

        # Always add a new node to the sequence, allowing duplicates
        node = {
            "r": ref_number,
            "m": m_value,  # Add the "m" element
            "ch": ch,  # Add the "ch" element
            "x": row,
            "y": col,
            "lu": default_lumin,
            "s": default_sleepsec,
            "w": default_waitsec
        }
        self.sequence.append(node)  # Add the node to the in-memory sequence

        try:
            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequence, f, indent=4)  # Save the updated sequence to the file
            self.update_sequence_display()  # Update the sequence display pane
        except IOError as e:
            print(f"Error saving to {self.sequence_file}: {e}")

    def update_sequence_display(self):
        """Update the sequence display pane with the current sequence values."""
        self.sequence_display.config(state="normal")  # Enable editing temporarily
        self.sequence_display.delete(1.0, tk.END)  # Clear the display
        for node in self.sequence:
            self.sequence_display.insert(tk.END, f"{node['r']}.X:{node['x']},Y:{node['y']},"
                                                 f"LU:{node['lu']},S:{node['s']},W:{node['w']},"
                                                 f"M:{node['m']},CH:{node['ch']}\n")  # Add "m" and "ch"
        self.sequence_display.config(state="disabled")  # Disable editing

    def renumber_mod_sequence(self, mod_value):
        sequence = 0
        for cell_position, cell_data in self.highlighted_cells.items():
            if cell_data["mod"] == mod_value:
                new_key_with_sequence = f"{mod_value},{sequence}"
                self.highlighted_cells[cell_position]["mod"] = new_key_with_sequence
                row, col = map(int, cell_position.split(','))
                ref_number = self.highlighted_cells[cell_position]["ref"]
                cell_text = f"c:{col},r:{row}\nref:{ref_number}\nmod:{new_key_with_sequence}"
                for widget in self.frame.grid_slaves():
                    if widget.grid_info()['row'] == row + 1 and widget.grid_info()['column'] == col + 1:
                        widget.configure(text=cell_text)
                sequence += 1

    def renumber_refs(self):
        for i, cell_position in enumerate(self.highlighted_cells):
            self.highlighted_cells[cell_position]["ref"] = i

    def renumber_key_sequence(self):
        new_key_sequence = {}
        for cell_position, key_with_sequence in self.cell_data.items():
            key, _ = key_with_sequence.split(',')
            if key not in new_key_sequence:
                new_key_sequence[key] = 0
            else:
                new_key_sequence[key] += 1
            new_key_with_sequence = f"{key},{new_key_sequence[key]}"
            self.cell_data[cell_position] = new_key_with_sequence
            self.highlighted_cells[cell_position]["mod"] = new_key_with_sequence
            row, col = map(int, cell_position.split(','))
            ref_number = self.highlighted_cells[cell_position]["ref"]
            cell_text = f"c:{col},r:{row}\nref:{ref_number}\nmod:{new_key_with_sequence}"
            for widget in self.frame.grid_slaves():
                if widget.grid_info()['row'] == row + 1 and widget.grid_info()['column'] == col + 1:
                    widget.configure(text=cell_text)
        self.key_sequence = new_key_sequence
        self.renumber_refs()  # Renumber the ref numbers

    def save_highlighted_cells(self):
        with open(self.led_positions_file, 'w') as f:
            json.dump(self.highlighted_cells, f)  # Save highlighted_cells dictionary

    def load_highlighted_cells(self):
        try:
            with open(self.led_positions_file, 'r') as f:
                self.highlighted_cells = json.load(f)
                for cell_position, cell_data in self.highlighted_cells.items():
                    row, col = map(int, cell_position.split(','))
                    cell_text = f"x:{row},y:{col}\nref:{cell_data['ref']}\nmod:{cell_data['mod']}"  # Change text to x and y
                    for widget in self.frame.grid_slaves():
                        if widget.grid_info()['row'] == row + 1 and widget.grid_info()['column'] == col + 1:
                            widget.configure(bg=self.highlighted_color, text=cell_text)
        except FileNotFoundError:
            self.highlighted_cells = {}
            self.save_highlighted_cells()  # Create the file if it doesn't exist

    def store_key(self, event):
        if self.highlighted_cells:
            last_highlighted = list(self.highlighted_cells.keys())[-1]
            row, col = map(int, last_highlighted.split(','))
            key = event.char
            if key not in self.key_sequence:
                self.key_sequence[key] = 0  # Start sequence for a new key
            else:
                self.key_sequence[key] = min(self.key_sequence[key] + 1, 15)  # Increment sequence for the same key, but do not exceed 15
            if self.key_sequence[key] > 15:
                return  # Do not allow a key and sequence number to exceed 15

            # Ensure sequence numbers are unique and ordered for the same mod value
            mod_value = key
            sequence_numbers = [
                int(data["mod"].split(",")[1])
                for data in self.highlighted_cells.values()
                if data["mod"].startswith(mod_value)
            ]
            next_sequence = 0
            while (next_sequence in sequence_numbers and next_sequence <= 15):
                next_sequence += 1
            if next_sequence > 15:
                return  # Do not allow more than 15 sequence numbers for the same mod value

            key_with_sequence = f"{mod_value},{next_sequence}"
            ref_number = self.highlighted_cells[last_highlighted]["ref"]
            cell_text = f"c:{col},r:{row}\nref:{ref_number}\nmod:{key_with_sequence}"
            for widget in self.frame.grid_slaves():
                if widget.grid_info()['row'] == row + 1 and widget.grid_info()['column'] == col + 1:
                    widget.configure(text=cell_text)
            self.highlighted_cells[last_highlighted]["mod"] = key_with_sequence
            self.cell_data[last_highlighted] = key_with_sequence  # Store in cell_data dictionary
            self.save_highlighted_cells()
            self.renumber_refs()  # Renumber the ref numbers

    def repaint_canvas(self):
        for widget in self.frame.winfo_children():
            widget.update_idletasks()

    def initialize_sequence_file(self):
        try:
            with open(self.sequence_file, 'r') as f:
                self.sequence = json.load(f)  # Load existing sequence file
            self.update_sequence_display()  # Update the sequence display pane with loaded values
        except (FileNotFoundError, json.JSONDecodeError):  # Handle missing or invalid file
            self.sequence = []  # Initialize an empty sequence if the file doesn't exist or is invalid
            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequence, f, indent=4)

    def on_close(self):
        # Save the sequence to the file before closing
        with open(self.sequence_file, 'w') as f:
            json.dump(self.sequence, f, indent=4)
        self.root.destroy()  # Close the application

    def delete_sequence_node(self, event):
        """Delete the sequenced node corresponding to the highlighted sequence text."""
        try:
            # Get the currently highlighted text
            highlighted_ranges = self.sequence_display.tag_ranges("highlight")
            if highlighted_ranges:
                start_index = str(highlighted_ranges[0])  # Convert to string before splitting
                line_number = int(start_index.split(".")[0]) - 1  # Convert to 0-based index
                if 0 <= line_number < len(self.sequence):
                    print(f"Deleting sequence node: {self.sequence[line_number]}")
                    # Remove the node from the sequence
                    del self.sequence[line_number]
                    # Save the updated sequence to the file
                    with open(self.sequence_file, 'w') as f:
                        json.dump(self.sequence, f, indent=4)
                    # Update the sequence display pane
                    self.update_sequence_display()
        except Exception as e:
            print(f"Error deleting sequence node: {e}")

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    root = tk.Tk()
    root.title("LED Positions")
    app = GridApp(root, config)
    root.mainloop()
