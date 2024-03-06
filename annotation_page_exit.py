# annotation_page_exit.py

from imports import *


class ExitOperation:
    def __init__(self, page_functionality):
        self.page_functionality = page_functionality
        self.controller = self.page_functionality.controller
        self.account_page = None

    def exit_confirmation(self, page):
        self.account_page = page
        # Check if lesions have been drawn
        # Check lesion count
        lesion_count = self.page_functionality.lesion_counter.get_lesion_count()
        if (lesion_count >= 1 or (len(self.page_functionality.dashed_line_coordinates) >= 1) or (
                len(self.page_functionality.rectangle_coordinates) >= 1)):
            # If lesions drawn display dialog box
            self.exit_dialog(page)
        else:
            # Else exit page
            self.controller.show_frame(self.account_page)

    def exit_dialog(self, page):
        # Create a custom dialog window
        dialog = tk.Toplevel(self.controller)
        dialog.title("Exit options")

        # Set the window as transient to prevent minimising
        dialog.transient(self.controller)

        # Disable the close button
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        # Calculate the center position for the dialog
        x = self.controller.winfo_x() + (self.controller.winfo_width() - 450) // 2
        y = self.controller.winfo_y() + (self.controller.winfo_height() - dialog.winfo_reqheight()) // 2

        # Set the position of the dialog
        dialog.geometry(f"+{x}+{y}")

        # Set a fixed size for the dialog
        dialog.resizable(width=False, height=False)
        dialog.geometry("450x200")  # Keep the width as 450

        # Create a label with the message
        message_label = tk.Label(dialog, text="Please select an exit option:", padx=20, pady=20, font=("Helvetica", 14))
        message_label.pack()

        # Configure style for fixed-size buttons
        style = ttk.Style()
        style.configure("FixedSize.TButton", font=("Helvetica", 12), padding=10,
                        relief='raised', background='#424242', foreground='#212121', width=10, height=2)

        # Create "exit" and "close" buttons
        exit_button = ttk.Button(dialog, text="Exit",
                                      command=lambda: self.on_button_click("1", dialog),
                                      style="FixedSize.TButton")
        cancel_button = ttk.Button(dialog, text="Cancel", command=lambda: self.on_button_click("2", dialog),
                                  style="FixedSize.TButton")

        # Create a frame for the buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(side="bottom", anchor="center")

        # Add buttons to the frame
        exit_button.pack(side=tk.LEFT, padx=(96, 10))
        cancel_button.pack(side=tk.LEFT, padx=10)

        # Run the dialog using wait_window on the Tk instance
        self.controller.wm_attributes("-disabled", True)

        # Manually update the Tkinter event loop to keep the main window responsive
        while dialog.winfo_exists():
            self.controller.update_idletasks()
            self.controller.update()

        # Enable main window
        self.controller.wm_attributes("-disabled", False)


    def on_button_click(self, button_text, dialog):
        if button_text != "2":
            # Exit page
            self.controller.show_frame(self.account_page)

        # Set focus to the main window
        self.controller.focus_set()

        # Destroy the dialog window
        dialog.destroy()

        # Release the grab
        self.controller.grab_release()

        # Update the main window to ensure it stays on top
        self.controller.attributes("-topmost", True)
        self.controller.attributes("-topmost", False)