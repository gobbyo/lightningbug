import tkinter as tk
import json

class GridApp:
    def __init__(self, root, config):
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
        self.sequence_file = "LED_sequence.json"
        self.initialize_sequence_file()  # Initialize the sequence file
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Bind cleanup function to window close event

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
                cell_text = f"c:{col-1},r:{row-1}\n"
                cell = tk.Label(self.frame, text=cell_text, borderwidth=self.borderwidth, relief=self.relief, width=self.cell_width, height=self.cell_height, bg=self.bg_color, highlightbackground=self.highlight_color)
                cell.grid(row=row, column=col)
                cell.bind("<Button-1>", self.toggle_highlight)  # Ensure left-click event is bound to toggle_highlight

    def toggle_highlight(self, event):
        focused_widget = self.root.focus_get()
        key = event.char if isinstance(focused_widget, tk.Entry) else None
        current_color = event.widget.cget("bg")
        cell_info = event.widget.grid_info()
        cell_position = f"{cell_info['row'] - 1},{cell_info['column'] - 1}"

        if cell_position in self.highlighted_cells:
            print(f"Mouse clicked in highlighted cell at position: {cell_position}")
            ref_number = self.highlighted_cells[cell_position]["ref"]
            self.append_to_sequence_file(cell_position, ref_number)  # Append node to sequence file
        else:
            print(f"Mouse click ignored in non-highlighted cell at position: {cell_position}")
            # Ignore clicks in non-highlighted cells

    def append_to_sequence_file(self, cell_position, ref_number):
        row, col = map(int, cell_position.split(','))
        node = {
            "r": ref_number,
            "x": row,
            "y": col,
            "lu": 30,  # Default value
            "s": 0.25,  # Default value
            "w": 0.25   # Default value
        }
        self.sequence.append(node)  # Add the node to the in-memory sequence

        try:
            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequence, f, indent=4)  # Save the updated sequence to the file
        except IOError as e:
            print(f"Error saving to {self.sequence_file}: {e}")

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
                    cell_text = f"c:{col},r:{row}\nref:{cell_data['ref']}\nmod:{cell_data['mod']}"
                    for widget in self.frame.grid_slaves():
                        if widget.grid_info()['row'] == row + 1 and widget.grid_info()['column'] == col + 1:
                            widget.configure(bg=self.highlighted_color, text=cell_text)
                            widget.unbind("<Button-1>")  # Disable left-click interaction for read-only cells
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
            while next_sequence in sequence_numbers and next_sequence <= 15:
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
        except (FileNotFoundError, json.JSONDecodeError):  # Handle missing or invalid file
            self.sequence = []  # Initialize an empty sequence if the file doesn't exist or is invalid
            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequence, f, indent=4)

    def on_close(self):
        # Save the sequence to the file before closing
        with open(self.sequence_file, 'w') as f:
            json.dump(self.sequence, f, indent=4)
        self.root.destroy()  # Close the application

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    root = tk.Tk()
    root.title("LED Positions")
    app = GridApp(root, config)
    root.mainloop()
