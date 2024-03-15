# ai_researcher_view.py
# Import all
from imports import *

class AIResearcherView(tk.Frame):
    def __init__(self, parent, controller, account_page):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Account page
        self.account_page = account_page

        self.ai_researcher_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bg=BACKGROUND_COLOUR)
        self.ai_researcher_frame.pack(fill="both", padx=10, pady=10, expand=True,
                                 anchor='center')  # Use pack with fill and expand options

        # Create a frame for the matplotlib graph and toolbar
        self.researcher_content_frame = tk.Frame(self.ai_researcher_frame, bg=FRAME_BACKGROUND_COLOUR)
        self.researcher_content_frame.pack(side="right", fill="both", expand=True, pady=0)

        label = tk.Label(self.researcher_content_frame, text="AI Researcher View", font=("Helvetica", 26)
                         , bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
        label.pack(side="top", anchor='n', pady=10, padx=10)

        # AI researcher buttons frame
        self.ai_researcher_btn_frame = tk.Frame(self.researcher_content_frame)
        self.ai_researcher_btn_frame.pack(side="top", padx=10, pady=1)

        self.selected_image_id = None

        self.btn_setup()

        self.treeview_setup_frames()

    def btn_setup(self):
        self.create_button(self.ai_researcher_btn_frame, 50, 50, "./img/download.png"
                           , self.download_dataset,
                           "Download entire dataset")

        self.create_button(self.ai_researcher_btn_frame, 50, 50, "./img/info.png"
                           , self.page_guide,
                           "Page Guide")

        separator_label = tk.Label(self.ai_researcher_btn_frame, text="|", font=("Helvetica", 8), fg="black")
        separator_label.pack(side="left", padx=5)

        self.create_button(self.ai_researcher_btn_frame, 50, 50, "./img/exit.png"
                           , self.back_to_homepage, "Back to homepage")

    def download_dataset(self):
        # Define the path to the source file (the original annotations.json)
        source_file_path = 'annotations.json'  # Adjust if the path is different

        # Check if the source file exists to avoid errors
        if not os.path.exists(source_file_path):
            self.show_error_popup("Source file does not exist.")
            return

        # Ask the user to select a directory where they want to save the copy
        save_directory = filedialog.askdirectory(title="Select Folder to Save Annotations")

        # If the user cancels the directory selection, the returned string will be empty
        if not save_directory:
            return  # User cancelled the operation

        # Define the path where the copy will be saved
        destination_file_path = os.path.join(save_directory, 'annotations.json')

        # Copy the file to the selected directory
        try:
            shutil.copy(source_file_path, destination_file_path)
            # Optionally, inform the user that the file was successfully copied
            self.show_info_popup("File successfully saved to selected directory.")
        except Exception as e:
            # Handle any errors during the copy process
            self.show_error_popup(f"Failed to save file: {e}")

    def show_info_popup(self, message):
        info_popup = tk.Toplevel(self)
        info_popup.title("Info")
        info_popup.geometry("300x100")
        info_popup.resizable(False, False)

        tk.Label(info_popup, text=message).pack(pady=20, padx=20)

        def close_popup():
            info_popup.destroy()

        ok_button = tk.Button(info_popup, text="OK", command=close_popup)
        ok_button.pack(pady=(0, 20))

        # Center the popup relative to the main application window
        window_x = self.winfo_rootx() + self.winfo_width() // 2 - 150
        window_y = self.winfo_rooty() + self.winfo_height() // 2 - 50
        info_popup.geometry(f"+{window_x}+{window_y}")

        info_popup.transient(self.controller)  # Make the popup a transient window of the main application window
        info_popup.grab_set()  # Grab the focus to the popup until it is dismissed

    def back_to_homepage(self):
        self.controller.show_frame(self.account_page)

    def create_button(self, frame, width, height, image_path, command, tooltip):
        # Load the image and resize it
        img = Image.open(image_path)
        img = img.resize((width, height))  # Resize the image to 50x50 pixels
        # Convert the image to a format compatible with tkinter
        button_image = ImageTk.PhotoImage(img)
        # Create the ttk.Button with the resized image and custom style
        button = tk.Button(frame, image=button_image, compound="top", command=command, width=width, height=height,
                           bg="#c2bbb8")
        button.image = button_image  # Store the image as an attribute of the button
        button.pack(side="left", padx=5)  # Pack the button to the left with padding
        # Bind events to show and hide tooltips
        CreateToolTip(button, tooltip)

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
        columns = ('annotation_id', 'user_id', 'ultrasound_result', 'lesion_details'
                   , 'bi-rads_details')
        self.details_tree = ttk.Treeview(self.details_frame, columns=columns, show='headings')

        # Define headings and columns for the details view
        self.details_tree.heading('annotation_id', text='Annotation ID')
        self.details_tree.heading('user_id', text='User ID')
        self.details_tree.heading('ultrasound_result', text='Ultrasound Result')
        self.details_tree.heading('lesion_details', text='Lesion Details and Highlights')
        self.details_tree.heading('bi-rads_details', text='BI-RADS Details')

        # Create a Scrollbar and set it to vertical
        scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=self.details_tree.yview)
        # Configure the Treeview to be scrollable with the scrollbar
        self.details_tree.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar to the right of the Treeview
        scrollbar.pack(side="right", fill="y")
        # Pack the Treeview to fill the available space, leaving space for the scrollbar
        self.details_tree.pack(side="left", fill="both", expand=True)

        # Configure the column widths and weight
        self.details_tree.column('annotation_id', width=310, stretch=tk.NO)  # This column won't stretch
        self.details_tree.column('user_id', width=70, stretch=tk.NO)
        self.details_tree.column('ultrasound_result', width=120, stretch=tk.NO)
        self.details_tree.column('lesion_details', width=200, stretch=tk.YES)  # This column will expand

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
                    ultrasound_result = annotation['ultrasound_type'] if annotation['ultrasound_type'] else "N/A"

                    # Initialise variables to hold other details including BI-RADS data
                    details_status = "N/A"
                    bi_rads_details_list = []

                    # Check for BI-RADS data and ensure it's not empty
                    if annotation.get('rads'):
                        for rad in annotation['rads']:
                            for lesion_details in rad.values():
                                masses = lesion_details.get('masses', {})
                                for key, value in masses.items():
                                    if value.strip():  # Check if the field is not empty and add the field name to the list
                                        bi_rads_details_list.append(key.capitalize())

                    # Format the BI-RADS details or "N/A" if the list is empty
                    bi_rads_details = ", ".join(bi_rads_details_list) if bi_rads_details_list else "N/A"

                    # Update details_status based on available information
                    if bi_rads_details_list or ultrasound_result != "N/A":
                        details_status = "Details available"

                    # Inserting gathered data into the treeview
                    self.details_tree.insert('', tk.END, values=(
                        annotation_id,
                        annotation['user_id'],
                        ultrasound_result,
                        details_status,  # Using the updated status
                        bi_rads_details,  # Insert the formatted BI-RADS details or "N/A"
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

            # Check if the double-click was on the lesion_details column
        elif region == "cell" and self.details_tree.heading(column, "text") == "Lesion Details and Highlights":
            selected_item = self.details_tree.selection()[0]
            annotation_id = self.details_tree.item(selected_item, 'values')[0]

            # Find the annotation details by annotation_id
            with open('annotations.json', 'r') as file:
                data = json.load(file)

            details = None
            for image in data['images']:
                for annotation in image['annotations']:
                    if annotation['annotation_id'] == annotation_id:
                        details = annotation
                        break
                if details:
                    break

            if not details:
                self.show_error_popup("Details not found.")
                return

            # Prepare the details string
            details_str = f"Annotation ID: {annotation_id}\n\n"

            # Use json.dumps to format the highlights section in a readable, JSON-like format
            if 'coordinates' in details:
                coordinates_str = json.dumps(details['coordinates'], indent=2)
                details_str += f"Lesion:\n{coordinates_str}\n\n"
            else:
                details_str += "Lesion: N/A\n\n"

            highlight_details = details.get('highlight')
            if highlight_details:
                highlight_str = json.dumps(details['highlight'], indent=2)
            else:
                highlight_str = "N/A"
            details_str += f"Highlight:\n{highlight_str}\n\n"

            echo_details = details.get('echo')
            if echo_details:
                echo_str = json.dumps(echo_details, indent=2)
            else:
                echo_str = "N/A"
            details_str += f"Echo:\n{echo_str}\n\n"

            orientation_details = details.get('orientation')
            if orientation_details:
                orientation_str = json.dumps(orientation_details, indent=2)
            else:
                orientation_str = "N/A"
            details_str += f"Orientation:\n{orientation_str}\n\n"

            calcification_details = details.get('calcification')
            if calcification_details:
                calcification_str = json.dumps(calcification_details, indent=2)
            else:
                calcification_str = "N/A"
            details_str += f"Calcification:\n{calcification_str}"

            # Display details in a popup
            self.show_details_popup(details_str)

        elif region == "cell" and self.details_tree.heading(column, "text") == "BI-RADS Details":
            selected_item = self.details_tree.selection()[0]
            annotation_id = self.details_tree.item(selected_item, 'values')[0]
            bi_rads_str = "N/A"

            # Find the annotation details by annotation_id
            with open('annotations.json', 'r') as file:
                data = json.load(file)

            for image in data['images']:
                for annotation in image['annotations']:
                    if annotation['annotation_id'] == annotation_id:
                        rads_data = annotation.get('rads', [])
                        if rads_data:
                            # Prepare BI-RADS data for popup display
                            bi_rads_str = json.dumps(rads_data, indent=2)
                        else:
                            break
                        break

            self.show_details_popup(bi_rads_str)

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

    def show_details_popup(self, details):
        popup = tk.Toplevel(self)
        popup.title("Annotation Details")
        popup.geometry("600x500")  # Set a fixed size
        popup.resizable(False, False)  # Prevent resizing the window

        # Create a frame to contain the Text widget and the Scrollbar
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create the Scrollbar
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Text widget and attach the Scrollbar to it
        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the Scrollbar's command to scroll the Text widget
        scrollbar.config(command=text_widget.yview)

        text_widget.insert(tk.END, details)
        text_widget.configure(state='disabled')  # Make text read-only

        # Create an OK button to allow closing the popup
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=5)

        # Update centering calculation based on the new popup size
        window_x = self.winfo_rootx() + (self.winfo_width() // 2) - (600 // 2)
        window_y = self.winfo_rooty() + (self.winfo_height() // 2) - (500 // 2)
        popup.geometry(f"+{window_x}+{window_y}")

        # Make the popup modal
        popup.grab_set()

        # Make the popup a transient window of the main application window
        popup.transient(self.controller)

        # Block interaction with the main window until the popup is closed
        popup.wait_window()

    def page_guide(self):
        popup = tk.Toplevel(self)
        popup.title("MEDISCANAI AI-Researcher Quick Guide")
        popup.geometry("600x400")  # Adjust size as needed
        popup.resizable(False, False)

        # Use a Text widget for better text formatting and readability
        guide_text_widget = tk.Text(popup, wrap=tk.WORD, height=25, width=80, padx=10, pady=10)
        guide_text_widget.pack(expand=True, fill=tk.BOTH)

        # Inserting formatted guide text
        guide_text = """
    MEDISCANAI AI-Researcher Quick Guide
    ------------------------------------

    - Click an Image ID from the Image ID column to load details relating to that ultrasound image. This includes all 
    annotations from that image, the users who created the annotations, ultrasound results, lesion details, 
    and BI-RADS details.

    - Double left-click on an Image ID column cell to display the image in a popup.

    - Double left-click on an Annotation ID column row cell to display the image in a popup containing the drawn 
    annotations.

    - Double left-click on a Lesion Details and Highlight column row cell to display the JSON data for that 
    annotation. This includes lesion coordinates, highlight, echo, orientation, and calcification details.

    - Double left-click on a BI-RADS Details column row cell to display the BI-RADS JSON data for that annotation.
    """
        guide_text_widget.insert(tk.END, guide_text)
        guide_text_widget.configure(state='disabled')  # Make the text read-only

        # OK Button to close the popup
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

        # Center the popup relative to the main application window
        window_x = self.winfo_rootx() + self.winfo_width() // 2 - 300
        window_y = self.winfo_rooty() + self.winfo_height() // 2 - 200
        popup.geometry(f"+{window_x}+{window_y}")

        # Make the popup modal
        popup.grab_set()

        # Make the popup a transient window of the main application window
        popup.transient(self.controller)

        # This will block interaction with the main window until the popup is closed
        popup.wait_window()
