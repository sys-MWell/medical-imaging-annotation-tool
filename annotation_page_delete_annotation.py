# annotation_page_delete_annotation.py

from imports import *


class DeleteOperations:
    def __init__(self, page_functionality):
        self.page_functionality = page_functionality
        self.controller = self.page_functionality.controller

    def delete_dialog(self):
        dialog = tk.Toplevel(self.controller)
        dialog.title("Delete options")

        # Set the window as transient to prevent minimising
        dialog.transient(self.controller)

        # Disable the close button
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        x = self.controller.winfo_x() + (self.controller.winfo_width() - 450) // 2
        y = self.controller.winfo_y() + (self.controller.winfo_height() - 220) // 2

        # Set the position and size of the dialog
        dialog.geometry(f"450x{220}+{x}+{y}")

        # Set a fixed size for the dialog
        dialog.resizable(width=False, height=False)

        # Create a label with the message
        message_label = tk.Label(dialog, text="Choose delete option:", padx=20, pady=20, font=("Helvetica", 14))
        message_label.pack()

        # Configure style for fixed-size buttons
        style = ttk.Style()
        style.configure("FixedSize.TButton", font=("Helvetica", 12), padding=10,
                        relief='raised', background='#424242', foreground='#212121', width=10, height=2)

        # Create "Confirm" and "Close" buttons
        new_save_button = ttk.Button(dialog, text="Confirm", command=lambda: self.on_rgb_button_click("1", dialog),
                                     style="FixedSize.TButton")
        close_button = ttk.Button(dialog, text="Close", command=lambda: self.on_rgb_button_click("2", dialog),
                                  style="FixedSize.TButton")

        # Create a frame for the buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(side="bottom", anchor="center")

        # Add buttons to the frame
        new_save_button.pack(side=tk.LEFT, padx=(100, 0), pady=(0, 10))
        close_button.pack(side=tk.RIGHT, padx=(0, 100), pady=(0, 10))

        # Run the dialog using wait_window on the Tk instance
        self.controller.wm_attributes("-disabled", True)

        # Manually update the Tkinter event loop to keep the main window responsive
        while dialog.winfo_exists():
            self.controller.update_idletasks()
            self.controller.update()

        self.controller.wm_attributes("-disabled", False)

    def on_rgb_button_click(self, option, dialog):
        if option == "1":
            self.delete_annotation()
            self.rgb_cancel(dialog)
        elif option == "2":
            self.rgb_cancel(dialog)

    def rgb_cancel(self, dialog):
        # Set focus to the main window
        self.controller.focus_set()

        # Destroy the dialog window
        dialog.destroy()

        # Release the grab
        self.controller.grab_release()

        # Update the main window to ensure it stays on top
        self.controller.attributes("-topmost", True)
        self.controller.attributes("-topmost", False)

    def delete_annotation(self):
        # Load the JSON data
        with open("annotations.json", "r") as file:
            annotations_data = json.load(file)

        # Iterate through images
        for image in annotations_data["images"]:
            # Iterate through annotations
            for annotation in image["annotations"]:
                # Check if annotation_id matches the one to delete
                if annotation["annotation_id"] == self.page_functionality.annotation_id:
                    # Remove the annotation
                    image["annotations"].remove(annotation)
                    self.page_functionality.clear_lines()
                    break
        else:
            pass

        # Save the updated JSON data
        with open("annotations.json", "w") as file:
            json.dump(annotations_data, file, indent=2)