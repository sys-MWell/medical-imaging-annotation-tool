# annotation_page_save_operations.py

from imports import *


class SaveOperations:
    def __init__(self, page_functionality):
        self.page_functionality = page_functionality
        self.controller = self.page_functionality.controller

    # Message box, confirming save
    def save_confirmation(self):
        lesion_count = self.page_functionality.lesion_counter.get_lesion_count()
        if ((self.page_functionality.lines and (self.page_functionality.line_coordinates_save or
                                                self.page_functionality.rectangle_coordinates)) or
                (int(lesion_count) > 0) or (len(self.page_functionality.dashed_line_coordinates) > 0)):
            found_annotation = False
            if self.page_functionality.annotation_id == '':
                response = messagebox.askyesno("Save", "Are you sure you want to save?")
                if response:
                    # Save functionality
                    self.save('2')
            else:
                # Load the JSON data from the file
                with open("annotations.json", "r") as file:
                    json_data = json.load(file)
                # Check image ID and annotation ID exist in JSON
                for image in json_data["images"]:
                    if "image_id" in image and image["image_id"] == self.page_functionality.image_id:
                        for annotation in image["annotations"]:
                            if ("annotation_id" in annotation and annotation["annotation_id"] ==
                                    self.page_functionality.annotation_id):
                                found_annotation = True

            if found_annotation:
                self.save_dialog()
        else:
            messagebox.showinfo("Information", "Unable to save. A lesion must be highlighted.")

    def save_dialog(self):
        # Create a custom dialog window
        dialog = tk.Toplevel(self.controller)
        dialog.title("Save options")

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
        message_label = tk.Label(dialog, text="Choose a save option:", padx=20, pady=20, font=("Helvetica", 14))
        message_label.pack()

        # Configure style for fixed-size buttons
        style = ttk.Style()
        style.configure("FixedSize.TButton", font=("Helvetica", 12), padding=10,
                        relief='raised', background='#424242', foreground='#212121', width=10, height=2)

        # Create "Overwrite," "New Save," and "Close" buttons
        overwrite_button = ttk.Button(dialog, text="Overwrite",
                                      command=lambda: self.on_button_click("1", dialog),
                                      style="FixedSize.TButton")
        new_save_button = ttk.Button(dialog, text="New Save", command=lambda: self.on_button_click("2", dialog),
                                     style="FixedSize.TButton")
        close_button = ttk.Button(dialog, text="Close", command=lambda: self.on_button_click("3", dialog),
                                  style="FixedSize.TButton")

        # Create a frame for the buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(side="bottom", anchor="center")

        # Add buttons to the frame
        overwrite_button.pack(side=tk.LEFT, padx=(28, 10))
        new_save_button.pack(side=tk.LEFT, padx=10)
        close_button.pack(side=tk.LEFT, padx=10)

        # Run the dialog using wait_window on the Tk instance
        self.controller.wm_attributes("-disabled", True)

        # Manually update the Tkinter event loop to keep the main window responsive
        while dialog.winfo_exists():
            self.controller.update_idletasks()
            self.controller.update()

        # Enable main window
        self.controller.wm_attributes("-disabled", False)

    def on_button_click(self, button_text, dialog):

        if button_text != "3":
            # Save annotation
            self.save(button_text)

        # Set focus to the main window
        self.controller.focus_set()

        # Destroy the dialog window
        dialog.destroy()

        # Release the grab
        self.controller.grab_release()

        # Update the main window to ensure it stays on top
        self.controller.attributes("-topmost", True)
        self.controller.attributes("-topmost", False)

    # Save ALL to JSON - main save for annotation ultrasound and RADS
    def save(self, save_type):
        timestamp = int(time.time() * 1000)  # Convert seconds to milliseconds
        if save_type == "1":
            unique_annotation_id = self.page_functionality.annotation_id
        else:
            unique_annotation_id = f"{timestamp}_{uuid.uuid4()}"  # Unique annotation ID with timestamp
            self.page_functionality.annotation_id = unique_annotation_id

        self.lesion_data_dict = self.page_functionality.load_rads_data.load_rads_data()
        lesion_count = self.page_functionality.lesion_counter.get_lesion_count()
        if ((self.page_functionality.lines and (self.page_functionality.line_coordinates_save or
                                                self.page_functionality.rectangle_coordinates)) or
                (int(lesion_count) > 0) or (len(self.page_functionality.dashed_line_coordinates) > 0)):
            # Convert rectangle coordinates to desired format
            converted_rectangles = []
            for rectangle_info in self.page_functionality.rectangle_coordinates:
                rectangle_obj = rectangle_info["rectangle_obj"]
                if rectangle_obj is not None:  # Check for none
                    rectangle = {
                        "x": rectangle_info["coordinates"]["x"],
                        "y": rectangle_info["coordinates"]["y"],
                        "width": rectangle_obj.get_width(),
                        "height": rectangle_obj.get_height(),
                        "colour": rectangle_info["coordinates"]["colour"],
                        "type": rectangle_info["coordinates"]["type"]
                    }
                    # Check if "rgb_rect" exists in rectangle_info
                    if "rgb_value" in rectangle_info["coordinates"]:
                        rectangle["rgb_value"] = rectangle_info["coordinates"]["rgb_value"]
                    converted_rectangles.append(rectangle)

            # Save echo/arrow objects to JSON
            converted_arrows = []
            for arrow_info in self.page_functionality.arrow_coordinates:
                arrow_obj = arrow_info["arrow_obj"]
                if arrow_obj is not None:  # Check for none
                    arrow = {
                        "start_x": arrow_info["coordinates"]["start_x"],
                        "start_y": arrow_info["coordinates"]["start_y"],
                        "point_x": arrow_info["coordinates"]["point_x"],
                        "point_y": arrow_info["coordinates"]["point_y"]
                    }
                    converted_arrows.append(arrow)

            # Save orientation/dashed-line objects to JSON
            converted_dashedlines = []
            for dashedline_info in self.page_functionality.dashed_line_coordinates:
                dashedline_obj = dashedline_info["dashedline_obj"]
                if dashedline_obj is not None:  # Check for none
                    dashedline = {
                        "start_x": dashedline_info["coordinates"]["start_x"],
                        "end_x": dashedline_info["coordinates"]["end_x"],
                        "start_y": dashedline_info["coordinates"]["start_y"],
                        "end_y": dashedline_info["coordinates"]["end_y"],
                        "txt": str(dashedline_info["dashedlinetext"])
                    }
                    converted_dashedlines.append(dashedline)

            # Save calcification/plus objects to JSON
            converted_plus = []
            for plus_info in self.page_functionality.plus_coordinates:
                plus_obj = plus_info["plus_obj"]
                if plus_obj is not None:
                    plus = {
                        "x": plus_info["coordinates"]["x"],
                        "y": plus_info["coordinates"]["y"],
                        "type": plus_info["coordinates"]["type"]
                    }
                    converted_plus.append(plus)

            # Initialise the list to store all annotations
            lesions = []
            # Loop through each entry in self.lesion_data_dict
            for lesion_key, lesion_data in self.lesion_data_dict.items():
                rads_entry = {
                    f"{lesion_key}": {
                        "masses": {
                            "Shape": lesion_data["shape_combobox"],
                            "Orientation": lesion_data["orientation_combobox"],
                            "Margin": lesion_data["margin_selection"],
                            "Margin selection": lesion_data["margin_notcircumscribed_options"],
                            "Echo pattern": lesion_data["echo_pattern"],
                            "Posterior features": lesion_data["posterior"],
                            "Calcification": lesion_data["calcification"],
                            "Calcification selection": lesion_data["calcification_options"],
                            "Additional_notes": lesion_data["additional_notes"]
                        }
                    }
                }
                lesions.append(rads_entry)

            annotation = {
                "annotation_id": unique_annotation_id,
                "user_id": self.page_functionality.user_id,
                "ultrasound_type": self.page_functionality.radio_ultrasound_type_var.get(),
                "coordinates": [],
                "highlight": converted_rectangles,  # Use the converted_rectangles
                "echo": converted_arrows,  # Arrow objects saved
                "orientation": converted_dashedlines,  # Dashed-line objects saved
                "calcification": converted_plus,
                "rads": lesions
            }

            # Save lesion lines
            unique_lines = set()
            count = 1

            line_data = {
                "lesions": [],  # This will be a flat list of all coordinates
                "width": None,  # Update this with the desired value
                "colour": None  # Update this with the desired value
            }

            coordinate_strings = []  # New list to store coordinate strings
            for line_info in self.page_functionality.line_coordinates_save:
                line_obj = line_info["line_obj"]

                if line_obj not in unique_lines:
                    unique_lines.add(line_obj)
                    coordinates = line_info["coordinates"]

                    if coordinates:
                        # Flatten the list of coordinates and convert them to strings
                        flat_coordinates = [f"({coord[0]}, {coord[1]})" for sublist in coordinates for coord in sublist]

                        # Join the flat coordinates into a single string
                        coordinate_string = f"[{', '.join(flat_coordinates)}]"
                        coordinate_strings.append(coordinate_string)
                    count += 1

            # Add the line_data to annotation with the desired width and colour
            line_data["width"] = line_info["line_obj"].get_linewidth() if self.page_functionality.line_coordinates_save\
                else None
            line_data["colour"] = line_info["line_obj"].get_color() if self.page_functionality.line_coordinates_save\
                else None

            # Append the list of coordinate strings to the "lesions" field
            line_data["lesions"].extend(coordinate_strings)
            annotation["coordinates"].append(line_data)

            try:
                with open("annotations.json", "r") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {"images": []}

            # Check if the image_id and annotation_id already exist in the data
            image_exists = False
            if save_type == "1":
                for image in data["images"]:
                    if image["image_id"] == self.page_functionality.image_id:
                        for i, existing_annotation in enumerate(image["annotations"]):
                            if self.page_functionality.annotation_id == existing_annotation["annotation_id"]:
                                # Update existing annotation data
                                image_exists = True
                                image["annotations"][i] = annotation  # Update only the specific annotation
                                break
            elif save_type == "2":
                # Check if the image_id already exists in the data
                for image in data["images"]:
                    if image["image_id"] == self.page_functionality.image_id:
                        image_exists = True
                        image["annotations"].append(annotation)  # Override existing annotations
                        break

            if not image_exists:
                image_data = {
                    "image_id": self.page_functionality.image_id,
                    "annotations": [annotation]
                }
                data["images"].append(image_data)

            with open("annotations.json", "w") as file:
                json.dump(data, file, indent=2)
        else:
            messagebox.showinfo("Information", "Unable to save. An error has occurred.")

        self.page_functionality.upload_functionality.display_images()
        # Toolbar save functionality
        self.save_figure()

    def save_figure(self):
        # Saving canvas/annotated ultrasound image
        # Saving to folder annotations
        filename = f"./annotations/{self.page_functionality.image_id}_{self.page_functionality.annotation_id}.png"
        self.page_functionality.f.savefig(filename, bbox_inches='tight', pad_inches=0)