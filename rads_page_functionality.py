# rads_page_functionality.py
import tkinter
import webbrowser

from imports import *
from rads_vars import PageVariables
from lesion_counter import LesionCounter


# Rads page functionality
class RadsFunctionality(tk.Frame):
    def __init__(self, parent=None, controller=None):
        tk.Frame.__init__(self, parent, bg=MASTER_COLOUR)

        # Initialise the variables from PageVariables
        PageVariables.__init__(self)

        self.controller = controller

        # If rads loaded from annotations.json
        self.rads_status = RadsLoadStatus()

        # Pen checker
        self.pen_check = PenTypeFileManager()

        # Load RADS data from JSON
        self.load_rads_data = LoadRadsData()
        # Lesion RADS data dictionary
        self.lesion_data_dict = {}
        self.page_data = {}
        self.masses_frames = []
        self.additional_frames = []

        # Unlock rads function
        self.unlock_rads()
        self.lesion_counter = LesionCounter()
        self.lesion_counter.reset_lesion_count()

        style = ttk.Style()
        style.configure("Custom.TCombobox", font=('Helvetica', 12), padding=5, background="white",
                        fieldbackground="white")
        style.configure("Custom.TRadiobutton", font=('Helvetica', 12), background=MASTER_COLOUR)
        style.configure("Custom.TCheckbutton", font=('Helvetica', 12), background=MASTER_COLOUR)

        # Checkbox option variables
        self.echo_pattern_var = tk.StringVar()
        self.margin_selection_var = tk.StringVar()
        self.posterior_var = tk.StringVar()

        self.master_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.master_frame.pack(pady=10, padx=10, fill="both", expand=1)

        # Prevent the frame from growing beyond a certain width
        self.master_frame.pack_propagate(False)
        self.master_frame.config(width=350)  # Set the maximum width
        # Bind the <Configure> event to a function that will update the size of the content_frame when the window is resized

        # Set the title label
        title_label = ttk.Label(self.master_frame, text="ACR BI-RADS", font=("Helvetica", 16))
        title_label.pack(pady=10)

        # Create frame for form
        form_frame = ttk.Frame(self.master_frame)
        form_frame.pack(pady=10, padx=10, fill="both", expand=1)
        self.form_frame = form_frame

        # Create the notebook
        self.notebook = ttk.Notebook(form_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create the first page
        masses_frame = self.create_page("Lesion 1", 1)
        self.masses_frames.append(masses_frame)

        self.rads_massses_frame = self.masses_frame
        self.rads_additional_frame = self.additional_frame

        self.disable_frame(self.masses_frame)
        self.disable_frame(self.additional_frame)
        self.image_checks()

    def add_new_page(self):
        # Get the number of existing pages
        num_pages = self.notebook.index("end")

        # Create a new page with a unique name
        new_page_name = f"Lesion {num_pages + 1}"
        self.num_notebooks = self.num_notebooks + 1
        num_pages = num_pages + 1

        # Create the new page and store a reference to the masses_frame
        masses_frame = self.create_page(new_page_name, num_pages)
        self.masses_frames.append(masses_frame)

    def remove_all_notebooks(self):
        while self.num_notebooks > 1:
            self.remove_notebook()

    def remove_notebook(self):
        if self.num_notebooks > 0:
            self.masses_frames.pop()
            self.additional_frames.pop()
            last_page_index = self.notebook.index("end") - 1
            self.notebook.forget(last_page_index)
            self.num_notebooks -= 1
            # Delete entry from rads.JSON
            page_num = int(self.notebook.index('end') + 1)
            # print(f"Remove page: {page_num}")
            self.delete_entry_from_json(self.notebook.index("end") + 1)
            if page_num in self.page_data:
                self.page_data.pop(page_num)
                # print(f"Page {page_num} deleted from self.page_data")
            else:
                print(f"Page {page_num} not found in self.page_data")

    def create_page(self, page_name, page_num):
        # Create the frame for masses
        rads_frame = ttk.Frame(self.form_frame)
        rads_frame.pack(fill="both", expand=1)
        self.rads_frame = rads_frame

        # Pack the frames into the notebook
        self.notebook.add(rads_frame, text=page_name)
        self.notebook.pack(fill="both", expand=True)

        # Create the frame for masses
        masses_frame = ttk.LabelFrame(rads_frame, text="Masses")
        masses_frame.pack(pady=10, padx=10, fill="both", expand=1)
        self.masses_frame = masses_frame

        # Create the frame for additional
        additional_frame = ttk.LabelFrame(rads_frame, text="Additional notes")
        additional_frame.pack(pady=10, padx=10, fill="both", expand=1)
        self.additional_frame = additional_frame

        # Pack the frames within the rads_frame
        masses_frame.pack(pady=10, padx=10, fill="both", expand=1)
        additional_frame.pack(pady=10, padx=10, fill="both", expand=1)

        # Get page data dictionary
        self.page_data_call(page_num)

        # Subsection: Shape
        shape_label = ttk.Label(masses_frame, text="Shape")
        shape_label.grid(row=1, column=0, sticky="w")
        shape_options = ["Oval", "Round", "Irregular"]
        self.shape_combobox = ttk.Combobox(masses_frame, values=shape_options, state="readonly")
        self.shape_combobox.grid(row=1, column=1, pady=3)
        # Bind the function to the combobox selection event
        self.shape_combobox.bind("<<ComboboxSelected>>", lambda event: self.on_shape_select(event, page_num))
        # Bind key events to prevent typing in the combobox
        self.shape_combobox.bind("<Key>", lambda event: "break")

        # Subsection: Orientation
        orientation_label = ttk.Label(masses_frame, text="Orientation")
        orientation_label.grid(row=2, column=0, sticky="w")
        orientation_options = ["Parallel", "Not Parallel"]
        self.orientation_combobox = ttk.Combobox(masses_frame, values=orientation_options, state="readonly")
        self.orientation_combobox.grid(row=2, column=1, pady=3)
        self.orientation_combobox.bind("<<ComboboxSelected>>",
                                       lambda event: self.on_orientation_select(event, page_num))
        # Bind key events to prevent typing in the combobox
        self.orientation_combobox.bind("<Key>", lambda event: "break")

        # Subsection: Margin
        margin_label = ttk.Label(masses_frame, text="Margin")
        margin_label.grid(row=3, column=0, sticky="w")
        self.margin_var = tk.StringVar()
        margin_circumscribed_radio = ttk.Radiobutton(masses_frame, text="Circumscribed", variable=self.margin_var,
                                                     value="Circumscribed",
                                                     command=lambda: self.on_margin_selected(page_num))
        margin_circumscribed_radio.grid(row=3, column=1, sticky="w", pady=3)
        margin_not_circumscribed_radio = ttk.Radiobutton(masses_frame, text="Not Circumscribed",
                                                         variable=self.margin_var, value="Not Circumscribed",
                                                         command=lambda: self.on_margin_selected(page_num))
        margin_not_circumscribed_radio.grid(row=5, column=1, sticky="w", pady=3)
        self.not_circumscribed_checkbuttons = []
        self.not_circumscribed_options = ["Indistinct", "Angular", "Microlobulated", "Spiculated"]
        for i, option in enumerate(self.not_circumscribed_options):
            check = tk.Checkbutton(masses_frame, text=option, state='disabled',
                                   command=lambda option=option: self.select_option_margin(page_num, option))
            check.grid(row=6 + i, column=1, sticky="w", padx=8, pady=2)
            self.not_circumscribed_checkbuttons.append(check)
            if page_num == 1:
                self.checkboxes.append(check)
        # Initially disable update_not_circumscribed_options until selection has been made
        self.update_not_circumscribed_options(page_num)
        # Store the reference to margin_var along with the page_num
        self.margin_vars[page_num] = self.margin_var  # Store the margin_var in a dictionary

        # Subsection: Echo Pattern
        echo_pattern_label = ttk.Label(masses_frame, text="Echo Pattern")
        echo_pattern_label.grid(row=10, column=0, sticky="w")
        self.echo_pattern_options = ["Anechoic", "Hyperechoic", "Complex cystic and solid", "Hypoechoic", "Isoechoic",
                                     "Heterogeneous"]
        # Create a dictionary to store the check buttons
        self.check_buttons = {}
        for i, option in enumerate(self.echo_pattern_options):
            check = tk.Checkbutton(masses_frame, text=option,
                                   command=lambda option=option: self.select_option_echo(page_num, option))
            check.grid(row=10 + i, column=1, sticky="w", pady=2)
            if page_num == 1:
                self.checkboxes.append(check)

        # Subsection: Posterior Features
        # Radio buttons options:
        posterior_radio_label = ttk.Label(masses_frame, text="Posterior Features")
        posterior_radio_label.grid(row=17, column=0, sticky="w")
        self.posterior_var = tk.StringVar()
        no_posterior_features_radio = ttk.Radiobutton(masses_frame, text="No Posterior Features",
                                                     variable=self.posterior_var,
                                                     value="No posterior",
                                                     command=lambda: self.posterior_radio_selected(page_num))
        no_posterior_features_radio.grid(row=17, column=1, sticky="w", pady=3)
        posterior_features_radio = ttk.Radiobutton(masses_frame, text="Posterior Features",
                                                         variable=self.posterior_var, value="Posterior",
                                                         command=lambda: self.posterior_radio_selected(page_num))
        posterior_features_radio.grid(row=18, column=1, sticky="w", pady=3)
        # Check buttons options:
        self.posterior_features_options = ["Enhancement", "Shadowing"]
        for i, option in enumerate(self.posterior_features_options):
            check = tk.Checkbutton(masses_frame, text=option,
                                   command=lambda option=option: self.select_option_posterior(page_num, option))
            check.grid(row=19 + i, column=1, sticky="w", padx=8, pady=2)
            if page_num == 1:
                self.checkboxes.append(check)

        # Subsection: Calcification
        calcification_label = ttk.Label(masses_frame, text="Calcification")
        calcification_label.grid(row=21, column=0, sticky="w")
        self.calcification_var = tk.StringVar()
        calcification_present_radio = ttk.Radiobutton(masses_frame, text="Calcification Not Present",
                                                     variable=self.calcification_var,
                                                     value="Not present",
                                                     command=lambda: self.on_calcification_selected(page_num))
        calcification_present_radio.grid(row=21, column=1, sticky="w", pady=3)
        calcification_not_present_radio = ttk.Radiobutton(masses_frame, text="Calcification Present",
                                                         variable=self.calcification_var, value="Present",
                                                         command=lambda: self.on_calcification_selected(page_num))
        calcification_not_present_radio.grid(row=22, column=1, sticky="w", pady=3)
        # Check buttons options:
        self.not_calcification_checkbuttons = []
        self.not_calcification_options = ["Micro-calcification", "Macro-calcification"]
        for i, option in enumerate(self.not_calcification_options):
            check = tk.Checkbutton(masses_frame, text=option, state='disabled',
                                   command=lambda option=option: self.select_option_calcification(page_num, option))
            check.grid(row=23 + i, column=1, sticky="w", padx=8, pady=2)
            self.not_calcification_checkbuttons.append(check)
            if page_num == 1:
                self.checkboxes.append(check)

        # Subsection: BI-RADS URL - Defining the text and URL link for BI-RADS reporting URL
        rads_reporting_text = "BI-RADS Reporting"
        rads_reporting_url = "https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems/Bi-Rads"

        # BI-RADS reporting text widget
        rads_reporting_widget = tk.Label(masses_frame, text=rads_reporting_text, fg="blue", cursor="hand2")
        rads_reporting_widget.bind("<Button-1>", lambda event: self.open_url(rads_reporting_url))
        rads_reporting_widget.grid(row=25, column=1, sticky="w")

        # Initially disable update_not_calcification_options until selection has been made
        self.update_not_calcification_options(page_num)
        # Store the reference to calcification_var along with the page_num
        self.posterior_vars[page_num] = self.posterior_var  # Store the posterior_var in a dictionary
        self.calcification_vars[page_num] = self.calcification_var  # Store the calcification_var in a dictionary

        # Additional frame entry box
        # Create a scrollable text input box
        self.text_box = tk.Text(additional_frame, width=40, wrap="word")  # Set wrap to "word"
        self.text_box.pack(pady=5, padx=5)
        self.text_box.bind("<KeyRelease>", lambda event: self.text_box_handler(page_num, event))

        if page_num == 1:
            self.margin_var1 = self.margin_var
            self.posterior_var1 = self.posterior_var
            self.calcification_var1 = self.calcification_var
            self.shape_combobox1 = self.shape_combobox
            self.orientation_combobox1 = self.orientation_combobox
            self.text_box1 = self.text_box

        # Return at end
        self.additional_frames.append(additional_frame)
        return masses_frame

    # Create page data dictionary for each lesion
    def page_data_call(self, page_num):
        # Store variables associated with the current page
        self.page_data[page_num] = {
            "shape_combobox": tk.StringVar(),
            "orientation_combobox": tk.StringVar(),
            "margin_selection_var": tk.StringVar(),
            "margin_selection_selected": [],
            "echo_pattern_var": tk.StringVar(),
            "echo_pattern_selected": [],
            "posterior_var": tk.StringVar(),
            "posterior_selected": [],
            "additional_notes": tk.StringVar(),
            "calcification_var": tk.StringVar(),
            "calcification_selected": []
        }

    # URL open
    def open_url(self, url):
        webbrowser.open_new(url)

    # Function to handle shape selection
    def on_shape_select(self, event, page_num):
        self.page_data[page_num]["shape_combobox"] = event.widget
        self.save_to_json(page_num)

    def on_orientation_select(self, event, page_num):
        self.page_data[page_num]["orientation_combobox"] = event.widget
        self.save_to_json(page_num)

    def on_margin_selected(self, page_num):
        selected_value = self.margin_var.get()
        masses_frame = self.masses_frames[page_num - 1]
        # Clear check buttons if Circumscribed is selected
        for child in masses_frame.winfo_children():
            if isinstance(child, tk.Checkbutton) and child.cget("text") in self.not_circumscribed_options:
                child.deselect()
                self.page_data[page_num]["margin_selection_selected"] = []
                self.page_data[page_num]["margin_selection_var"].set("")

        # This function is a wrapper that calls both functions
        self.save_to_json(page_num)
        self.update_not_circumscribed_options(page_num)

    # Margin option selections
    def select_option_margin(self, page_num, option):
        # Organises non circumscribed options
        if option in self.page_data[page_num]["margin_selection_selected"]:
            self.page_data[page_num]["margin_selection_selected"].remove(option)
        else:
            self.page_data[page_num]["margin_selection_selected"].append(option)
            # Save pen option
            self.save_pen_option(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["margin_selection_var"].set(
            ", ".join(self.page_data[page_num]["margin_selection_selected"]))
        self.save_to_json(page_num)

    # Function to update the state of not_circumscribed_options based on the selected radio button
    def update_not_circumscribed_options(self, page_num):
        try:
            margin_var = self.margin_vars.get(page_num)

            if margin_var and margin_var.get() == "Not Circumscribed":
                state = "normal"  # Enable the checkboxes
            else:
                state = "disabled"  # Disable the checkboxes

            masses_frame = self.masses_frames[page_num - 1]

            # Loop through the not_circumscribed_options checkboxes and set their state
            for child in masses_frame.winfo_children():
                if child.cget("text") in self.not_circumscribed_options:
                    child.configure(state=state)
        except Exception as e:
            # print(e)
            pass

    # Echo option selections
    def select_option_echo(self, page_num, option):
        # Organises echo options
        if option in self.page_data[page_num]["echo_pattern_selected"]:
            self.page_data[page_num]["echo_pattern_selected"].remove(option)
        else:
            self.page_data[page_num]["echo_pattern_selected"].append(option)
            # Save pen option
            self.save_pen_option(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["echo_pattern_var"].set(", ".join(self.page_data[page_num]["echo_pattern_selected"]))
        self.save_to_json(page_num)

    # Posterior radio selection
    def posterior_radio_selected(self, page_num):
        selected_value = self.posterior_var.get()
        masses_frame = self.masses_frames[page_num - 1]
        # Clear check buttons if calcification is selected
        for child in masses_frame.winfo_children():
            if isinstance(child, tk.Checkbutton) and child.cget("text") in self.posterior_features_options:
                child.deselect()
                self.page_data[page_num]["posterior_selected"] = []
                self.page_data[page_num]["posterior_var"].set("")

        # This function is a wrapper that calls both functions
        self.save_to_json(page_num)
        self.update_posterior_options(page_num)

    # Posterior option selections
    def select_option_posterior(self, page_num, option):
        # Organises posterior selection
        if option in self.page_data[page_num]["posterior_selected"]:
            self.page_data[page_num]["posterior_selected"].remove(option)
        else:
            self.page_data[page_num]["posterior_selected"].append(option)
            # Save pen option
            expected_values = {'Shadowing', 'Enhancement'}
            if set(self.page_data[page_num]["posterior_selected"]) == expected_values:
                option = 'Combined pattern'
            self.save_pen_option(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["posterior_var"].set(", ".join(self.page_data[page_num]["posterior_selected"]))
        self.save_to_json(page_num)

    def update_posterior_options(self, page_num):
        try:
            posterior_var = self.posterior_vars.get(page_num)
            if posterior_var and posterior_var.get() == "Posterior":
                state = "normal"  # Enable the checkboxes
            else:
                state = "disabled"  # Disable the checkboxes

            masses_frame = self.masses_frames[page_num - 1]

            # Loop through the not_circumscribed_options checkboxes and set their state
            for child in masses_frame.winfo_children():
                if child.cget("text") in self.posterior_features_options:
                    child.configure(state=state)
        except Exception as e:
            pass

    def on_calcification_selected(self, page_num):
        selected_value = self.calcification_var.get()
        masses_frame = self.masses_frames[page_num - 1]
        # Clear check buttons if calcification is selected
        for child in masses_frame.winfo_children():
            if isinstance(child, tk.Checkbutton) and child.cget("text") in self.not_calcification_options:
                child.deselect()
                self.page_data[page_num]["calcification_selected"] = []
                self.page_data[page_num]["calcification_var"].set("")

        # This function is a wrapper that calls both functions
        self.save_to_json(page_num)
        self.update_not_calcification_options(page_num)

    def select_option_calcification(self, page_num, option):
        # Organises non present calcification options
        if option in self.page_data[page_num]["calcification_selected"]:
            self.page_data[page_num]["calcification_selected"].remove(option)
        else:
            self.page_data[page_num]["calcification_selected"].append(option)
            # Save pen option
            self.save_pen_plus_option(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["calcification_var"].set(
            ", ".join(self.page_data[page_num]["calcification_selected"]))
        self.save_to_json(page_num)

    def update_not_calcification_options(self, page_num):
        try:
            calcification_var = self.calcification_vars.get(page_num)
            if calcification_var and calcification_var.get() == "Present":
                state = "normal"  # Enable the checkboxes
            else:
                state = "disabled"  # Disable the checkboxes

            masses_frame = self.masses_frames[page_num - 1]

            # Loop through the not_circumscribed_options checkboxes and set their state
            for child in masses_frame.winfo_children():
                if child.cget("text") in self.not_calcification_options:
                    child.configure(state=state)
        except Exception as e:
            pass

    # Word limit for text_box
    def text_box_handler(self, page_num, event):
        self.additional_notes = event.widget.get("1.0", "end-1c")
        text = event.widget.get("1.0", "end-1c")  # Get the text content
        words = text.split()  # Split the text into words
        if len(words) > 100:  # Check if the word limit is exceeded
            event.widget.delete("end-2c")  # Remove the extra words
        self.page_data[page_num]["additional_notes"].set(self.additional_notes)
        self.save_to_json(page_num)

    def save_pen_option(self, option):
        # Set pen in txt file
        self.pen_check.save_pen_line('Rect')
        self.pen_check.set_type_line(option)

    # Save calcification type
    def save_pen_plus_option(self, option):
        self.pen_check.save_pen_line('Plus')
        self.pen_check.set_type_line(option)

    # Unlock rads functionality
    def unlock_rads(self):
        # Initialise with default values
        user_cache = UserCache(None, None, None, None)
        user_cache.read_from_file()
        self.user_type = user_cache.user_type
        self.user_id = user_cache.user_id
        self.image_id = user_cache.image_id
        self.image_location = user_cache.image_location
        self.rads_load_status = True

    # Enable rads functionality
    def enable_rads(self):
        self.enable_frame(self.rads_massses_frame)
        self.enable_frame(self.rads_additional_frame)
        masses_frame = self.masses_frames[0]

        # Make initial lesion, lesion 1 not circumscribed options disabled.
        for child in masses_frame.winfo_children():
            if child.cget("text") in self.not_circumscribed_options:
                child.configure(state='disabled')

        # Make initial lesion, lesion 1 posterior features options disabled.
        for child in masses_frame.winfo_children():
            if child.cget("text") in self.posterior_features_options:
                child.configure(state='disabled')

        # Make initial lesion, lesion 1 not calcification options disabled.
        for child in masses_frame.winfo_children():
            if child.cget("text") in self.not_calcification_options:
                child.configure(state='disabled')

    # Disable frame -> Input functions disabled
    def disable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child,
                          (tk.Entry, tk.Text, tk.Checkbutton, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton,
                           tk.Radiobutton, ttk.Radiobutton,
                           tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='disabled')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.disable_frame(child)

    # Enable frame -> Input functions enabled
    def enable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child,
                          (tk.Entry, tk.Text, tk.Checkbutton, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton,
                           tk.Radiobutton, ttk.Radiobutton,
                           tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='normal')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.enable_frame(child)

    def clear_lesion_inputs(self):
        # Clear lesion 1 inputs when no lesion exists
        self.margin_var = tk.StringVar()
        self.posterior_var = tk.StringVar()
        self.calcification_var = tk.StringVar()
        self.canvas = tk.StringVar()
        self.not_circumscribed_checkbuttons = []
        self.not_calcification_checkbuttons = []
        self.margin_var1.set("")
        self.posterior_var1.set("")
        self.calcification_var1.set("")
        self.shape_combobox1.set('')  # Clear the selected option
        self.orientation_combobox1.set('')
        self.text_box1.delete("1.0", tk.END)
        # Deselect all checkboxes
        for checkbox in self.checkboxes:
            checkbox.deselect()

    # Load lesion/rads data and add data back to rads form
    def load_data(self):
        lesion_count = self.lesion_counter.get_lesion_count()
        if lesion_count > 0:
            for index, (lesion_key, lesion_data) in enumerate(self.lesion_data_dict.items(), start=0):
                try:
                    self.enable_rads()
                    # Reset variables for multi-selection
                    self.page_data[index + 1]["echo_pattern_var"].set("")
                    self.page_data[index + 1]["margin_selection_var"].set("")
                    self.page_data[index + 1]["posterior_var"].set("")
                    self.page_data_call(index + 1)
                    # Get masses frame for notebook page
                    masses_frame = self.masses_frames[index]
                    additional_frame = self.additional_frames[index]

                    # Deselect all - Incase previous still selected
                    for child in masses_frame.winfo_children():
                        if isinstance(child, tk.Checkbutton):
                            child.deselect()

                    # -- Shape --
                    for child in masses_frame.winfo_children():
                        shape_option = "Oval", "Round", "Irregular"
                        if isinstance(child, ttk.Combobox) and child.cget("values") == shape_option:
                            # Check if the child is a Combobox and has the correct values
                            if child.cget("values") == shape_option:
                                # Assuming "Shape" is the label text associated with the Combobox
                                child.set(lesion_data["shape_combobox"])
                    self.page_data[index + 1]["shape_combobox"].set(lesion_data["shape_combobox"])
                    # -----

                    # -- Orientation --
                    for child in masses_frame.winfo_children():
                        shape_option = "Parallel", "Not Parallel"
                        if isinstance(child, ttk.Combobox) and child.cget("values") == shape_option:
                            # Check if the child is a Combobox and has the correct values
                            if child.cget("values") == shape_option:
                                # Assuming "Shape" is the label text associated with the Combobox
                                child.set(lesion_data["orientation_combobox"])
                    self.page_data[index + 1]["orientation_combobox"].set(lesion_data["orientation_combobox"])
                    # -----

                    # -- Margins --
                    margin_selection = lesion_data["margin_selection"]
                    for child in masses_frame.winfo_children():
                        if isinstance(child, ttk.Radiobutton) and child.cget("value") == lesion_data["margin_selection"]:
                            if child.cget("value") == lesion_data["margin_selection"]:
                                # Select the radio button
                                child.invoke()
                    self.margin_var.set(margin_selection)
                    self.margin_vars[index + 1].set(lesion_data["margin_selection"])
                    not_circumscribed_options = lesion_data["margin_notcircumscribed_options"]
                    # Split the string into a list of words
                    options_list = not_circumscribed_options.split(', ')
                    # Loop through the margin options
                    for option in options_list:
                        self.page_data[index + 1]["margin_selection_selected"].append(option)
                        self.page_data[index + 1]["margin_selection_var"].set(
                            ", ".join(self.page_data[index + 1]["margin_selection_selected"]))
                    # Loop through the not_circumscribed_options checkboxes and set their state
                    for child in masses_frame.winfo_children():
                        if isinstance(child, tk.Checkbutton) and child.cget("text") in options_list:
                            child.select()
                    # -----

                    # -- Echo --
                    echo_options = lesion_data["echo_pattern"]
                    # Split the string into a list of words
                    options_list_echo = echo_options.split(', ')

                    for option in options_list_echo:
                        self.page_data[index + 1]["echo_pattern_selected"].append(option)
                        self.page_data[index + 1]["echo_pattern_var"].set(
                            ", ".join(self.page_data[index + 1]["echo_pattern_selected"]))

                    for child in masses_frame.winfo_children():
                        if isinstance(child, tk.Checkbutton) and child.cget("text") in options_list_echo:
                            child.select()
                    # -----

                    # -- Posterior --
                    posterior_selection = lesion_data["posterior"]
                    self.posterior_var.set(posterior_selection)
                    self.posterior_vars[index + 1].set(posterior_selection)
                    for child in masses_frame.winfo_children():
                        if isinstance(child, ttk.Radiobutton) and child.cget("value") == posterior_selection:
                            if child.cget("value") == posterior_selection:
                                # Select the radio button
                                child.invoke()
                    # -
                    posterior_options = lesion_data["posterior_features"]
                    # Split the string into a list of words
                    options_list_posterior = posterior_options.split(', ')
                    for option in options_list_posterior:
                        self.page_data[index + 1]["posterior_selected"].append(option)
                        self.page_data[index + 1]["posterior_var"].set(
                                ", ".join(self.page_data[index + 1]["posterior_selected"]))
                    for child in masses_frame.winfo_children():
                        if isinstance(child, tk.Checkbutton) and child.cget("text") in options_list_posterior:
                            child.select()
                    # -----

                    # -- Calcification
                    calcification_selection = lesion_data["calcification"]
                    for child in masses_frame.winfo_children():
                        if isinstance(child, ttk.Radiobutton) and child.cget("value") == lesion_data["calcification"]:
                            if child.cget("value") == lesion_data["calcification"]:
                                # Select the radio button
                                child.invoke()
                    self.calcification_var.set(calcification_selection)
                    self.calcification_vars[index + 1].set(lesion_data["calcification"])
                    # -
                    calcification_options = lesion_data["calcification_options"]
                    # Split the string into a list of words
                    options_list = calcification_options.split(', ')
                    # Loop through the calcification options
                    for option in options_list:
                        self.page_data[index + 1]["calcification_selected"].append(option)
                        self.page_data[index + 1]["calcification_var"].set(
                            ", ".join(self.page_data[index + 1]["calcification_selected"]))
                    # Loop through the calcification_options checkboxes and set their state
                    for child in masses_frame.winfo_children():
                        if isinstance(child, tk.Checkbutton) and child.cget("text") in options_list:
                            child.select()
                    # -----

                    # -- Additional --
                    # Iterate through children of masses_frame
                    for child in additional_frame.winfo_children():
                        if isinstance(child, tk.Text):
                            child.configure(state='normal')
                            child.delete(1.0, tk.END)
                            # Insert text with word wrapping enabled
                            child.insert(tk.END, lesion_data["additional_notes"], "word_wrap")
                            child.tag_configure("word_wrap", wrap="word")  # Configure tag for word wrapping
                            # If medical professionals user
                            if self.user_type != "1":
                                child.configure(state='disable')
                    self.page_data[index + 1]["additional_notes"].set(str(lesion_data["additional_notes"]))
                    # -----

                    self.save_to_json(index + 1)
                except Exception as e:
                    print(e)

    # Save RADS details to JSON -> Every input saved
    def save_to_json(self, page_num):
        if self.rads_load_status:
            try:
                # Load existing data from the JSON file, if any
                try:
                    with open('rads.JSON', 'r') as file:
                        data = json.load(file)
                except FileNotFoundError:
                    data = {}

                # Iterate through the pages and create entries for each
                for page_num, page_data in self.page_data.items():
                    margin_var = self.margin_vars.get(page_num)
                    posterior_var = self.posterior_vars.get(page_num)
                    calcification_var = self.calcification_vars.get(page_num)
                    # Check and remove ", " from margin pattern and echo pattern for the first 3 characters
                    margin_selection = page_data["margin_selection_var"].get()
                    echo_pattern = page_data["echo_pattern_var"].get()
                    posterior_selection = page_data["posterior_var"].get()
                    calcification_selection = page_data["calcification_var"].get()
                    # Remove "," from the start of the string
                    if margin_selection.startswith(", "):
                        margin_selection = margin_selection[2:]
                    if echo_pattern.startswith(", "):
                        echo_pattern = echo_pattern[2:]
                    if posterior_selection.startswith(", "):
                        posterior_selection = posterior_selection[2:]
                    if calcification_selection.startswith(", "):
                        calcification_selection = calcification_selection[2:]

                    page_entry = {
                        "masses": {
                            "Shape": page_data["shape_combobox"].get(),
                            "Orientation": page_data["orientation_combobox"].get(),
                            "Margin": margin_var.get(),
                            "Margin options": margin_selection,
                            "Echo pattern": echo_pattern,
                            "Posterior": posterior_var.get(),
                            "Posterior features": posterior_selection,
                            "Calcification": calcification_var.get(),
                            "Calcification options": calcification_selection,
                            "Additional notes": page_data["additional_notes"].get()
                        }
                    }

                    # Add the page entry to the data dictionary
                    data[f"Lesion_{page_num}"] = page_entry

                # Save the updated data to the JSON file
                with open('rads.JSON', 'w') as file:
                    json.dump(data, file, indent=4)

                # Debug
                # print("Data saved to rads.JSON")
            except Exception as e:
                pass
                # Error 'NoneType' object has no attribute 'get'
                # Error list index out of range

    # UPDATE RADS details from JSON
    def delete_entry_from_json(self, page_num):
        try:
            # Load existing data from the JSON file, if any
            try:
                with open('rads.JSON', 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}

            # Delete the entry associated with the specified Lesion page_num
            entry_key = f"Lesion_{page_num}"
            if entry_key in data:
                data.pop(entry_key)

            # Save the updated data to the JSON file
            with open('rads.JSON', 'w') as file:
                json.dump(data, file, indent=4)

            # Print a message indicating successful deletion
            # print(f"Entry {entry_key} deleted from rads.JSON")
        except Exception as e:
            # Print any exceptions that may occur during the process
            print(f"{e}")

    # Check annotation variables -> If image loaded, how many lesions
    def image_checks(self):
        try:
            LESION_COUNT = self.lesion_counter.get_lesion_count()
            rads_load_status = str(self.rads_status.get_rads_load_status())
            if (LESION_COUNT > 0):
                if rads_load_status == "True":
                    if not self.initial_load:
                        self.initial_load = True
                        # If medical professionals user
                        if self.user_type == "1":
                            self.enable_rads()
                    if LESION_COUNT == self.notebook.index("end"):
                        # If user loads image
                        self.lesion_data_dict = self.load_rads_data.load_rads_data()
                        self.rads_status.set_rads_load_status("False")
                        self.load_data()
                        self.zero_lesions = True
                if LESION_COUNT != self.notebook.index("end"):
                    if LESION_COUNT < self.notebook.index("end"):
                        ''' If lesion is less then count of notebooks (pages) then one page needs removed (has been
                        removed)'''
                        self.remove_notebook()
            else:
                if LESION_COUNT == 0:
                    if self.zero_lesions:
                        self.zero_lesions = False
                        self.initial_load = False
                        # print(f"num notebooks: {self.num_notebooks}")
                        self.clear_lesion_inputs()
                        self.remove_all_notebooks()
                        # Disable RADS form)
                        self.disable_frame(self.rads_massses_frame)
                        self.disable_frame(self.rads_additional_frame)
                        # Refresh page_data for page 1
                        self.page_data_call(1)
                        self.save_to_json(0)

            if (self.image_selected == True):
                if not self.image_upload_status:
                    self.image_upload_status = True
                    for child in self.masses_frame.winfo_children():
                        if child.cget("text") in self.not_circumscribed_options:
                            child.configure(state="disabled")
            else:
                self.image_upload_status = False
                self.disable_frame(self.masses_frame)
                self.disable_frame(self.additional_frame)

            self.after(200, self.image_checks)
        except Exception as ex:
            print(f"error: {ex}")
            pass
