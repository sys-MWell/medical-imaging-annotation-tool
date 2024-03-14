# ai_researcher_view.py
# Import all
from imports import *

class AIResearcherView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.ai_researcher_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bg=BACKGROUND_COLOUR)
        self.ai_researcher_frame.pack(fill="both", padx=10, pady=10, expand=True,
                                 anchor='center')  # Use pack with fill and expand options

        # Create a frame for the matplotlib graph and toolbar
        self.researcher_content_frame = tk.Frame(self.ai_researcher_frame, bg=FRAME_BACKGROUND_COLOUR)
        self.researcher_content_frame.pack(side="right", fill="both", expand=True, pady=0)

        label = tk.Label(self.researcher_content_frame, text="Image Annotation", font=("Helvetica", 26)
                         , bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
        label.pack(side="top", anchor='n', pady=10, padx=10)

        self.selected_image_id = None

        self.treeview_setup_frames()

    def treeview_setup_frames(self):
        # Left panel for Image IDs
        self.image_id_frame = tk.Frame(self.researcher_content_frame, bg=FRAME_BACKGROUND_COLOUR)
        self.image_id_frame.pack(side="left", fill="y", padx=10, pady=10, expand=False)

        # Right panel for details
        self.details_frame = tk.Frame(self.researcher_content_frame, bg=FRAME_BACKGROUND_COLOUR)
        self.details_frame.pack(side="right", fill="both", padx=(0, 10), pady=10, expand=True)

        # Add a label for image_id_tree row count
        self.image_id_row_count_label = tk.Label(self.image_id_frame, text="Rows: 0", bg=FRAME_BACKGROUND_COLOUR)
        self.image_id_row_count_label.pack(side="bottom", fill="x", anchor="w")
        self.image_id_row_count_label.config(anchor='w')

        # Add a label for details_tree row count
        self.details_row_count_label = tk.Label(self.details_frame, text="Rows: 0", bg=FRAME_BACKGROUND_COLOUR)
        self.details_row_count_label.pack(side="bottom", fill="x", anchor="w")
        self.details_row_count_label.config(anchor='w')

        # Setup TreeView for Image IDs
        self.setup_image_id_treeview()

        # Setup TreeView for annotation details
        self.setup_details_treeview()

    def setup_image_id_treeview(self):
        # Adjust setup to include 'Image ID' as a regular column
        self.image_id_tree = ttk.Treeview(self.image_id_frame, columns=('image_id',), show='headings')
        # Configure the 'Image ID' column
        self.image_id_tree.heading('image_id', text='Image ID')
        self.image_id_tree.column('image_id', anchor='w', width=100)

        # Create a Scrollbar and associate it with self.image_id_tree
        scrollbar = ttk.Scrollbar(self.image_id_frame, orient="vertical", command=self.image_id_tree.yview)
        self.image_id_tree.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar to the right of the Treeview
        scrollbar.pack(side="right", fill="y")

        # Pack the Treeview to fill the remaining space
        self.image_id_tree.pack(side="left", fill="both", expand=True)

        # Bind the selection event
        self.image_id_tree.bind("<<TreeviewSelect>>", self.on_image_id_select)
        self.image_id_tree.bind("<Double-1>", self.on_image_id_double_click)

        # Load and insert Image IDs
        self.insert_image_ids()

    def insert_image_ids(self):
        with open('annotations.json', 'r') as file:
            data = json.load(file)

        max_length = 0
        for image in data['images']:
            image_id = image['image_id']
            max_length = max(max_length, len(image_id))
            self.image_id_tree.insert('', tk.END, values=(image_id,))

        self.image_id_tree.column('image_id', width=max_length * 7)

        # Update the row count label
        row_count = len(data['images'])
        self.image_id_row_count_label.config(text=f"Rows: {row_count}")

    def setup_details_treeview(self):
        columns = ('annotation_id', 'user_id', 'lesion_details', 'highlight_details', 'bi-rads_details')
        self.details_tree = ttk.Treeview(self.details_frame, columns=columns, show='headings')

        # Define headings and columns for the details view
        self.details_tree.heading('annotation_id', text='Annotation ID')
        self.details_tree.heading('user_id', text='User ID')
        self.details_tree.heading('lesion_details', text='Lesion Details')
        self.details_tree.heading('highlight_details', text='Highlight Details')
        self.details_tree.heading('bi-rads_details', text='BI-RADS Details')

        # Create a Scrollbar and set it to vertical
        scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=self.details_tree.yview)
        # Configure the Treeview to be scrollable with the scrollbar
        self.details_tree.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar to the right of the Treeview
        scrollbar.pack(side="right", fill="y")
        # Pack the Treeview to fill the available space, leaving space for the scrollbar
        self.details_tree.pack(side="left", fill="both", expand=True)

        # Update the column width
        self.details_tree.column('annotation_id', width=300)
        self.details_tree.column('user_id', width=10)

        # Bind double-click
        self.details_tree.bind("<Double-1>", self.on_annotation_id_double_click)

    def on_image_id_select(self, event):
        selected_items = self.image_id_tree.selection()
        if selected_items:  # Check if anything is selected
            # Get the first selected item
            item = selected_items[0]
            # Retrieve the item's values, which is a tuple
            self.selected_image_id = self.image_id_tree.item(item, 'values')[0]
            self.update_details_view(self.selected_image_id)

    def update_details_view(self, image_id):
        # Clear previous items
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)

        # Load and insert details for selected Image ID
        with open('annotations.json', 'r') as file:
            data = json.load(file)

        for image in data['images']:
            if image['image_id'] == image_id:
                for annotation in image['annotations']:
                    annotation_id = annotation['annotation_id']

                    # Your existing logic to extract and insert details
                    self.details_tree.insert('', tk.END, values=(
                        annotation_id,
                        annotation['user_id'],
                        '...',  # Replace with your extraction logic
                        '...',  # Replace with your extraction logic
                        '...',  # Replace with your extraction logic
                    ))

        # After updating details_tree, refresh the row count label
        children = self.details_tree.get_children()
        row_count = len(children)
        self.details_row_count_label.config(text=f"Rows: {row_count}")

    def on_image_id_double_click(self, event):
        # Get the item that was clicked
        item_id = self.image_id_tree.selection()[0]
        image_id = self.image_id_tree.item(item_id, 'values')[0]
        image_path = f"./medical_images/{image_id}.png"

        # Check if the image file exists
        if not os.path.exists(image_path):
            # Display an error popup if the image does not exist
            error_popup = tk.Toplevel(self)
            error_popup.title("Error")
            error_popup.geometry("300x100")
            error_popup.resizable(False, False)
            tk.Label(error_popup, text="No image available for this ID.").pack(pady=20)

            # Centre the error popup
            error_popup_x = self.winfo_rootx() + (self.winfo_width() - 300) // 2
            error_popup_y = self.winfo_rooty() + (self.winfo_height() - 100) // 2
            error_popup.geometry(f"+{error_popup_x}+{error_popup_y}")

            error_popup.transient(self.controller)
            error_popup.grab_set()  # Disables the main window until the error popup is closed
            return

        # Proceed with loading and displaying the image if it exists
        img = Image.open(image_path)
        img_width, img_height = img.size

        popup = tk.Toplevel(self)
        popup.title(f"Image: {image_id}")
        popup.geometry(f"{img_width}x{img_height}")
        popup.resizable(False, False)

        main_window_x = self.winfo_rootx()
        main_window_y = self.winfo_rooty()
        popup_x = main_window_x + (self.winfo_width() - img_width) // 2
        popup_y = main_window_y + (self.winfo_height() - img_height) // 2
        popup.geometry(f"+{popup_x}+{popup_y}")

        img_photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(popup, image=img_photo)
        img_label.image = img_photo
        img_label.pack()

        popup.transient(self.controller)
        popup.grab_set()

    def on_annotation_id_double_click(self, event):
        if not hasattr(self, 'selected_image_id') or not self.selected_image_id:
            self.show_error_popup("Please select an Image ID first.")
            return

        region = event.widget.identify("region", event.x, event.y)
        column = event.widget.identify_column(event.x)

        # Ensure that the double-click was on the cell of the 'annotation_id' column
        if region == "cell" and self.details_tree.heading(column, "text") == "Annotation ID":
            selected_item = self.details_tree.selection()[0]
            annotation_id = self.details_tree.item(selected_item, 'values')[0]

            annotated_image_path = f"./annotations/{self.selected_image_id}_{annotation_id}.png"

            if not os.path.exists(annotated_image_path):
                self.show_error_popup("No annotated image available for this ID.")
                return

            # Display the image
            img = Image.open(annotated_image_path)
            img_width, img_height = img.size
            popup = tk.Toplevel(self)
            popup.title(f"Annotated Image: {self.selected_image_id}_{annotation_id}")
            popup.resizable(False, False)
            main_window_x = self.winfo_rootx()
            main_window_y = self.winfo_rooty()
            popup_x = main_window_x + (self.winfo_width() - img_width) // 2
            popup_y = main_window_y + (self.winfo_height() - img_height) // 2
            popup.geometry(f"+{popup_x}+{popup_y}")
            img_photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(popup, image=img_photo)
            img_label.image = img_photo
            img_label.pack()
            popup.transient(self.controller)
            popup.grab_set()

    def show_error_popup(self, message):
        error_popup = tk.Toplevel(self)
        error_popup.title("Error")
        error_popup.geometry("300x100")
        error_popup.resizable(False, False)
        tk.Label(error_popup, text=message).pack(pady=20)
        # Centre the error popup
        error_popup_x = self.winfo_rootx() + (self.winfo_width() - 300) // 2
        error_popup_y = self.winfo_rooty() + (self.winfo_height() - 100) // 2
        error_popup.geometry(f"+{error_popup_x}+{error_popup_y}")
        error_popup.transient(self.controller)
        error_popup.grab_set()  # Disables the main window until the error popup is closed