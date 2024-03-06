# annotation_page_data_loader.py

from imports import *


class DataLoader:
    def __init__(self, page_functionality):
        self.page_functionality = page_functionality
        self.controller = self.page_functionality.controller

    # Message box, confirming load
    def load_confirmation(self):
        annotations = []
        annotation_count = 0
        # Load the JSON data from the file
        try:
            with open("annotations.json", "r") as file:
                json_data = json.load(file)

            # Check image ID and annotation ID exist in JSON
            for image in json_data["images"]:
                if "image_id" in image and image["image_id"] == self.page_functionality.image_id:
                    for annotation in image["annotations"]:
                        annotations.append(annotation["annotation_id"])
                        annotation_count += 1

            if annotation_count > 0:
                self.load_dialog(annotation_count, annotations)
            else:
                messagebox.showinfo("Information", "No saved data found.")

        except FileNotFoundError:
            # Handle the error if the file is not found
            messagebox.showinfo("Information", "No saved data found.")

    def load_dialog(self, annotation_count, annotations):
        # Create a custom dialog window for load option
        dialog = tk.Toplevel(self.controller)
        dialog.title("Load options")

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
        dialog.geometry("450x200")

        # Combobox styling
        combobox_style = ttk.Style()
        # Configure the combobox style to customize its appearance
        combobox_style.configure('Custom.TCombobox', fieldbackground='white')

        # Combobox with save selection
        combobox_values = [f"Save {i}" for i in range(1, annotation_count + 1)]
        selected_value = tk.StringVar()
        combobox = ttk.Combobox(dialog, values=combobox_values, textvariable=selected_value, font=("Helvetica", 14),
                                state="readonly", style='Custom.TCombobox')
        combobox.set("Select an option")  # Initial option
        combobox.pack(pady=15)

        # Create a style object
        style = ttk.Style()

        # Style for the buttons
        style.configure('Load.TButton', font=('Helvetica', 12), padding=5, relief='raised', background='#424242',
                        foreground='#212121', width=10, height=2)

        # Create an "OK" button
        ok_button = ttk.Button(dialog, text="OK",
                               command=lambda: self.load_select(selected_value.get(), dialog, annotations),
                               style='Load.TButton')
        ok_button.pack(pady=10)

        # Create a "Cancel" button
        cancel_button = ttk.Button(dialog, text="Cancel", command=lambda: self.load_cancel(dialog),
                                   style='Load.TButton')
        cancel_button.pack(pady=10)

        # Set the focus on the combobox
        combobox.focus_set()

        # Run the dialog using wait_window on the Tk instance
        self.controller.wm_attributes("-disabled", True)

        # Manually update the Tkinter event loop to keep the main window responsive
        while dialog.winfo_exists():
            self.controller.update_idletasks()
            self.controller.update()

        self.controller.wm_attributes("-disabled", False)

    def load_select(self, value, dialog, annotations):
        # Split the string by space
        split_parts = value.split()

        # Get the last part of the split string (assuming the number is the last part)
        last_part = split_parts[-1]

        # Check if the last part is a digit
        if last_part.isdigit():
            # Convert the digit to an integer
            number = int(last_part)
            self.annotation_id = str(annotations[number - 1])
            self.load()

            # Set focus to the main window
            self.controller.focus_set()

            # Destroy the dialog window
            dialog.destroy()

            # Release the grab
            self.controller.grab_release()

            # Update the main window to ensure it stays on top
            self.controller.attributes("-topmost", True)
            self.controller.attributes("-topmost", False)

    def load_cancel(self, dialog):
        # Set focus to the main window
        self.controller.focus_set()

        # Destroy the dialog window
        dialog.destroy()

        # Release the grab
        self.controller.grab_release()

        # Update the main window to ensure it stays on top
        self.controller.attributes("-topmost", True)
        self.controller.attributes("-topmost", False)

    # Load JSON file -> Coordinates and RADS
    def load(self):
        annotation_id = self.annotation_id
        self.page_functionality.clear_lines()
        self.page_functionality.lesion_data_dict = {}
        try:
            with open("annotations.json", "r") as file:
                data = json.load(file)
                for image in data["images"]:
                    if image["image_id"] == self.page_functionality.image_id:
                        for annotation in image["annotations"]:
                            if annotation["annotation_id"] == annotation_id:
                                self.page_functionality.set_cancer_type_radio_buttons_state("normal")
                                self.page_functionality.image_id = image["image_id"]
                                self.page_functionality.annotation_id = annotation["annotation_id"]
                                self.page_functionality.user_id = annotation["user_id"]
                                ultra_sound_type = annotation["ultra_sound_type"]
                                self.page_functionality.radio_ultrasound_type_var.set(ultra_sound_type)

                                # Load lesion lines
                                for line_data in annotation["coordinates"]:
                                    self.page_functionality.lesion_counter.increment_lesion_count()
                                    lines = line_data["lesions"]  # lines is now a list of coordinate strings

                                    for coord_string in lines:
                                        coords = eval(coord_string)  # Convert the string back to a list of tuples
                                        if coords is None:
                                            continue  # Skip if coords is None

                                        x_coords = [x for x, _ in coords]
                                        y_coords = [y for _, y in coords]
                                        line_obj = mlines.Line2D(x_coords, y_coords, color=line_data["colour"],
                                                                 linewidth=line_data["width"])
                                        self.page_functionality.a.add_line(line_obj)

                                        line_info = {"line_obj": line_obj, "coordinates": [coords]}
                                        self.page_functionality.line_coordinates.append(line_info)
                                        self.page_functionality.line_coordinates_save.append(line_info)
                                        self.page_functionality.line_coordinates_clear.append(line_info)

                                # Redraw the rectangles
                                if "highlight" in annotation:
                                    rect_data_list = annotation["highlight"]
                                    for rect_data in rect_data_list:
                                        x = rect_data["x"]
                                        y = rect_data["y"]
                                        width = rect_data["width"]
                                        height = rect_data["height"]
                                        colour = rect_data["colour"]
                                        # Create a Rectangle object from the loaded data
                                        rect_obj = patches.Rectangle((x, y), width, height, linewidth=2,
                                                                     edgecolor=colour,
                                                                     facecolor='none')
                                        # Store the rectangle object along with its coordinates
                                        rect_info = {"rectangle_obj": rect_obj, "coordinates": rect_data}

                                        # RGB pixel check
                                        if "rgb_value" in rect_data:
                                            # Access the RGB values if they exist
                                            rgb_1 = rect_data["rgb_value"]["rgb_1"]
                                            rgb_2 = rect_data["rgb_value"]["rgb_2"]
                                            coordinates = rect_info["coordinates"]
                                            self.page_functionality.get_pixel_rgb_values(coordinates,
                                                                                         rgb_1, rgb_2)

                                        # Append to the rectangle_coordinates list
                                        self.page_functionality.rectangle_coordinates.append(rect_info)
                                        # Add the rectangle patch to the Axes object
                                        self.page_functionality.a.add_patch(rect_obj)

                                # Redraw arrows/echo pointers
                                if "echo" in annotation:
                                    arrow_data_list = annotation["echo"]
                                    for arrow_data in arrow_data_list:
                                        start_x = arrow_data["start_x"]
                                        start_y = arrow_data["start_y"]
                                        point_x = arrow_data["point_x"]
                                        point_y = arrow_data["point_y"]

                                        start_point = (start_x, start_y)
                                        end_point = (point_x, point_y)

                                        # Calculate the arrow dimensions
                                        dx = end_point[0] - start_point[0]
                                        dy = end_point[1] - start_point[1]

                                        # Create the arrow object
                                        arrow_obj = FancyArrow(start_point[0], start_point[1], dx, dy,
                                                               color='blue', width=2, head_width=10)

                                        # Store the rectangle object along with its coordinates
                                        arrow_info = {"arrow_obj": arrow_obj, "coordinates": arrow_data}

                                        # Append to the arrow_coordinates list
                                        self.page_functionality.arrow_coordinates.append(arrow_info)

                                        # Add the arrow to the plot
                                        self.page_functionality.a.add_patch(arrow_obj)

                                # Redraw orientation lines
                                if "orientation" in annotation:
                                    dashedline_data_list = annotation["orientation"]
                                    for dashedline_data in dashedline_data_list:
                                        start_x = dashedline_data["start_x"]
                                        end_x = dashedline_data["end_x"]
                                        start_y = dashedline_data["start_y"]
                                        end_y = dashedline_data["end_y"]
                                        txt = dashedline_data["txt"]
                                        colour = "#ffc61c"

                                        line_obj = mlines.Line2D([start_x, end_x], [start_y, end_y],
                                                                 color=colour, linewidth=2, linestyle='dashed')
                                        self.page_functionality.a.add_line(line_obj)
                                        self.page_functionality.dashed_lines.append(line_obj)

                                        plus1 = self.page_functionality.a.plot(start_x, start_y, marker='+',
                                                                               markersize=10, markeredgewidth=2,
                                                                               color=colour)
                                        self.page_functionality.dashed_lines_plus.append(plus1[0])
                                        plus2 = self.page_functionality.a.plot(end_x, end_y, marker='+', markersize=10,
                                                                               markeredgewidth=2,
                                                                               color=colour)
                                        self.page_functionality.dashed_lines_plus.append(plus2[0])

                                        # Remove the 'Text(' and ')' parts
                                        cleaned_string = txt.replace('Text(', '').replace(')', '')
                                        # Split the string into a list using commas as separators - Convert the elements to
                                        # appropriate types (float for coordinates, and strip quotes for text)
                                        elements = cleaned_string.split(', ')
                                        x_coordinate = float(elements[0])
                                        y_coordinate = float(elements[1])
                                        text_content = elements[2].strip("'")
                                        text = self.page_functionality.a.text(x_coordinate, y_coordinate, text_content,
                                                                              color=colour,
                                                                              fontsize=15, verticalalignment='center',
                                                                              horizontalalignment='right')
                                        self.page_functionality.dashed_lines_num_txt.append(text)

                                        # Store dashed line object information
                                        dashedline_info = {"dashedline_obj": line_obj,
                                                           "coordinates": dashedline_data,
                                                           "dashedlinestart_obj": plus1,
                                                           "dashedlineend_obj": plus2,
                                                           "dashedlinetext": text}

                                        # Append to dashedline list
                                        self.page_functionality.dashed_line_coordinates.append(dashedline_info)

                                if 'calcification' in annotation:
                                    plus_list = annotation["calcification"]
                                    for plus_data in plus_list:
                                        x = plus_data["x"]
                                        y = plus_data["y"]
                                        # Redraw a "+" plus shape at the given coordinates
                                        plus = self.page_functionality.a.plot(x, y, marker='+', markersize=10, markeredgewidth=2,
                                                           color='#ff5100')
                                        plus_info = {"plus_obj": plus, "coordinates": plus_data}
                                        self.page_functionality.plus_coordinates.append(plus_info)
                                        print(f"TEST: {self.page_functionality.plus_coordinates}")

                                # Load RADS
                                for rad_data in annotation["rads"]:
                                    # Iterate over the dictionary keys
                                    for lesion_key, lesion_data in rad_data.items():
                                        # Extract information for each lesion
                                        masses_data = lesion_data.get("masses", {})
                                        shape_combobox = masses_data.get("shape", "")
                                        orientation_combobox = masses_data.get("Orientation", "")
                                        margin_selection = masses_data.get("Margin", "")
                                        margin_pattern_var = masses_data.get("Margin selection", "")
                                        echo_pattern_var = masses_data.get("Echo pattern", "")
                                        posterior_var = masses_data.get("Posterior features", "")
                                        calcification_var = masses_data.get("Calcification", "")
                                        calcification_selected = masses_data.get("Calcification selection", "")
                                        additional_notes = masses_data.get("additional_notes", "")

                                        # Store the lesion data in the dictionary using lesion_key as the index
                                        self.page_functionality.lesion_data_dict[lesion_key] = {
                                            "shape_combobox": shape_combobox,
                                            "orientation_combobox": orientation_combobox,
                                            "margin_selection": margin_selection,
                                            "margin_notcircumscribed_options": margin_pattern_var,
                                            "echo_pattern": echo_pattern_var,
                                            "posterior": posterior_var,
                                            "calcification": calcification_var,
                                            "calcification_options": calcification_selected,
                                            "additional_notes": additional_notes
                                        }
                                break
                        if self.page_functionality.user_type != "1":
                            self.page_functionality.set_cancer_type_radio_buttons_state("disabled")
                        self.page_functionality.f.canvas.draw()
                        break
            self.page_functionality.save_to_json()
        except FileNotFoundError:
            # Handle the case when the file is not found
            pass
