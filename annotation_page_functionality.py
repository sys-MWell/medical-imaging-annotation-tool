# annotation_page_functionality.py
from collections import Counter

from imports import *
from annotation_vars import PageVariables
from lesion_counter import LesionCounter
from annotation_page_data_loader import DataLoader
from annotation_page_save_operations import SaveOperations
from upload_page_functionality import UploadFunctionality
from annotation_page_exit import ExitOperation
from annotation_page_rgb_slider import DoubleSlider
from annotation_page_delete_annotation import DeleteOperations
from annotation_page_quit import QuitOperation


class PageFunctionality(tk.Frame):
    def __init__(self, parent, controller, account_page):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Initialise the variables from PageVariables
        PageVariables.__init__(self)

        # Disable the old function
        self.controller.protocol("WM_DELETE_WINDOW", "")
        # Close window
        self.controller.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Account page
        self.account_page = account_page

        # Lesion Counter
        self.lesion_counter = LesionCounter()
        self.lesion_counter.reset_lesion_count()

        # If rads loaded from annotations.json
        self.rads_load_status = RadsLoadStatus()
        self.rads_load_status.set_rads_load_status('False')

        # Load Data from annotation_page_data_loader.py
        self.data_loader = DataLoader(self)

        # Save data from annotation_page_save_operations.py
        self.save_operations = SaveOperations(self)

        # Upload image functionality page upload_page_functionality.py
        self.upload_functionality = UploadFunctionality(self)

        # Exit functionality
        self.exit_operation = ExitOperation(self)

        # Delete operations annotation_page_delete_annotation.py
        self.delete_operations = DeleteOperations(self)

        # Quit functionality
        self.quit_operation = QuitOperation(self)

        # Load RADS data from JSON
        self.load_rads_data = LoadRadsData()
        # Lesion RADS data dictionary
        self.lesion_data_dict = {}

        # Random colour generator
        self.colour_generator = RandomColourGenerator()

        # Pen checker
        self.pen_check = PenTypeFileManager()
        self.pen_check.clear_file()
        self.pen_check.save_pen_line('Line')
        self.colour_rads_check()

        self.combined_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bg=BACKGROUND_COLOUR)
        self.combined_frame.pack(fill="both", padx=10, pady=10, expand=True,
                                 anchor='center')  # Use pack with fill and expand options

        # Initialise with default values
        user_cache = UserCache(None, None, None, None)
        user_cache.read_from_file()
        self.user_type = user_cache.user_type

        self.upload_functionality.upload_functionality()
        self.annotation_functionality()


    # Annotation functionality
    def annotation_functionality(self):
        # Create a frame for the matplotlib graph and toolbar
        self.annotation_frame = tk.Frame(self.combined_frame, bg=FRAME_BACKGROUND_COLOUR)
        self.annotation_frame.pack(side="right", fill="both", expand=True,
                                   pady=0, padx=20)  # Use pack with fill and expand opt

        label = tk.Label(self.annotation_frame, text="Image Annotation", font=("Helvetica", 26), bg=SECONDARY_COLOUR,
                         fg=MASTER_FONT_COLOUR)
        label.pack(side="top", anchor='n', pady=10, padx=10)

        self.graph_frame = tk.Frame(self.annotation_frame)
        self.graph_frame.pack(anchor="n", fill="both", expand=True,
                              pady=0, padx=20)  # Use pack with fill and expand options

        # Radio btns frame
        self.radio_btn_frame = tk.Frame(self.graph_frame, highlightbackground=MASTER_BORDER_COLOUR
                                        , highlightthickness=1)
        self.radio_btn_frame.pack(side="top", pady=0, padx=10)
        self.radio_ultrasound_type_var = tk.StringVar(value="")

        # Ultrasound type radio button selection
        if self.upload_condition:
            # Ultrasound Type Radio Button
            # Configure the style for the Radiobuttons
            style_upload = ttk.Style()
            style_upload.configure("Custom.TRadiobutton", background=FRAME_BACKGROUND_COLOUR,
                                   foreground=MASTER_FONT_COLOUR, padding=10, borderwidth=1, relief="solid")

            # Benign
            benign_radio = ttk.Radiobutton(self.radio_btn_frame,
                                           variable=self.radio_ultrasound_type_var, text="Benign", value="Benign",
                                           style="Custom.TRadiobutton")
            benign_radio.pack(side="left", padx=5)

            # Malignant
            malignant_radio = ttk.Radiobutton(self.radio_btn_frame,
                                              variable=self.radio_ultrasound_type_var, text="Malignant",
                                              value="Malignant", style="Custom.TRadiobutton")
            malignant_radio.pack(side="left", padx=5)

            # Normal
            normal_radio = ttk.Radiobutton(self.radio_btn_frame,
                                           variable=self.radio_ultrasound_type_var, text="Normal", value="Normal",
                                           style="Custom.TRadiobutton")
            normal_radio.pack(side="left", padx=5)

        matplotlib_btn_frame = tk.Frame(self.graph_frame)
        matplotlib_btn_frame.pack(side="top", padx=10, pady=20)

        self.matplotlib_frame = tk.Frame(self.graph_frame)
        self.matplotlib_frame.pack(side="left", pady=0, padx=10)

        # Initialize the colour variable
        self.colour = 'red'

        self.btn_colour = "#c2bbb8"

        self.cid = None  # Variable to store the connection id for the event handler

        # Create a new frame for the buttons
        self.options_frame = tk.Frame(self.graph_frame)
        self.options_frame.pack(anchor="n", side="bottom", pady=5, expand=True)

        # Page buttons for annotation tool
        if self.upload_condition:
            # Generate button toolbar
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/restart.png", self.home_action,
                               "Set canvas to original position")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/move.png", self.pan_action, "Canvas pan")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/zoom.png", self.zoom_action, "Canvas zoom")

            separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
            separator_label.pack(side="left", padx=5)
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/options.png",
                               lambda: self.display_annotations(),
                               "Hide/Show pen toolbar")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/clear.png", lambda: self.clear_lines(),
                               "Canvas clear")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/save.png",
                               lambda: self.save_operations.save_confirmation(),
                               "Save annotation")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/load.png",
                               lambda: self.data_loader.load_confirmation(),
                               "Load existing image annotations")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/trash.png",
                               lambda: self.delete_operations.delete_confirmation(),
                               "Delete annotation save")
            separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
            separator_label.pack(side="left", padx=5)
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/undo.png", lambda: self.undo_object(),
                               "Undo annotation")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/redo.png", lambda: self.redo_object(),
                               "Redo annotation")
            separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
            separator_label.pack(side="left", padx=5)
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/exit.png", self.exit, "Exit")

        self.display_annotation_opts(self.options_frame)
        self.generate_matplotlib(self.image_location)

    def set_cancer_type_radio_buttons_state(self, state):
        for radio_button in self.radio_btn_frame.winfo_children():
            radio_button.configure(state=state)

    # User exit - back to homepage
    def exit(self):

        self.exit_operation.exit_confirmation(self.account_page)

    # Create function buttons
    def create_button(self, frame, width, height, image_path, command, tooltip):
        # Load the image and resize it
        img = Image.open(image_path)
        img = img.resize((width, height))  # Resize the image to 50x50 pixels
        # Convert the image to a format compatible with tkinter
        button_image = ImageTk.PhotoImage(img)
        # Create the ttk.Button with the resized image and custom style
        button = tk.Button(frame, image=button_image, compound="top", command=command, width=width, height=height,
                           bg=self.btn_colour)
        button.image = button_image  # Store the image as an attribute of the button
        button.pack(side="left", padx=5)  # Pack the button to the left with padding
        # Bind events to show and hide tooltips
        CreateToolTip(button, tooltip)

    # Undo button functionality
    def undo_object(self):
        if self.added_objects:
            last_object = self.added_objects.pop()
            if 'line_obj' in last_object:
                line_obj = last_object['line_obj']
                last_object_line = self.line_coordinates.pop()
                self.line_coordinates_save.pop()
                self.line_coordinates_clear.pop()
                last_object_line["line_obj"].remove()
                self.removed_objects.append(last_object_line)
                self.lesion_counter.decrement_lesion_count()
            elif 'rectangle_obj' in last_object:
                rectangle_obj = last_object['rectangle_obj']
                last_object_rect = self.rectangle_coordinates.pop()
                last_object_rect["rectangle_obj"].remove()
                rect_coords = last_object['coordinates']
                rect_type = rect_coords['type']
                for type in self.echo_patterns:
                    if type == rect_type:
                        last_object = self.added_objects[-1]
                        if 'rgb_highlight_obj' in last_object:
                            self.added_objects.pop()
                            last_object_rgb = self.rgb_coordinates.pop()
                            self.removed_objects.append(last_object_rgb)
                            if len(self.rgb_coordinates) < 1:
                                if self.rgb_original is not None:
                                    self.rgb_redo_history.append(self.rgb_history.pop())
                                    self.img_arr = np.copy(self.rgb_original)
                            else:
                                # When more than 0 echo drawn
                                # Remove the last changes from the history and store in redo_history
                                self.rgb_redo_history.append(self.rgb_history.pop())
                                # Restore the previous state of the image
                                self.img_arr = self.rgb_history[-1].copy() if self.rgb_history else None
                            # Remove the image from the axes
                            for im in self.a.images:
                                im.remove()
                            self.a.imshow(self.img_arr)
                            self.f.canvas.draw()
                self.removed_objects.append(last_object_rect)
            elif 'arrow_obj' in last_object:
                arrow_obj = last_object['arrow_obj']
                last_object_arrow = self.arrow_coordinates.pop()
                last_object_arrow["arrow_obj"].remove()
                self.arrows.pop()
                self.removed_objects.append(last_object_arrow)
                try:
                    self.preview_arrow.remove()
                except:
                    pass
            elif 'dashedline_obj' in last_object:
                dashedline_obj = last_object['dashedline_obj']
                last_object_dashedline = self.dashed_line_coordinates.pop()
                if 'dashedline_obj' in last_object_dashedline:
                    dashedline_obj_list = last_object_dashedline['dashedline_obj']
                    for line2d_obj in dashedline_obj_list:
                        line2d_obj.remove()
                last_object_dashedline["dashedlinestart_obj"].remove()
                last_object_dashedline["dashedlineend_obj"].remove()
                last_object_dashedline["dashedlinetext"].remove()
                self.dashed_lines.pop()
                self.dashed_lines_num_txt.pop()
                # Remove the last two elements using slicing
                self.dashed_lines_plus = self.dashed_lines_plus[:-2]
                self.removed_objects.append(last_object_dashedline)
            elif 'plus_obj' in last_object:
                self.removed_objects.append(last_object)
                last_object_plus = self.plus_coordinates.pop()
                # Pop the last item from the list
                last_object_plus_item = last_object_plus["plus_obj"][-1]
                # Remove the object stored in "plus_obj"
                last_object_plus_item.remove()
            else:
                print("Unknown object type")
            self.f.canvas.draw()

    # Redo button functionality
    def redo_object(self):
        if self.removed_objects:
            # Restore the last removed object
            restored_object = self.removed_objects.pop()
            if 'line_obj' in restored_object:
                line_obj = restored_object["line_obj"]
                self.a.add_line(line_obj)
                self.added_objects.append(restored_object)
                self.line_coordinates.append(restored_object)
                self.line_coordinates_save.append(restored_object)
                self.line_coordinates_clear.append(restored_object)
                self.lesion_counter.increment_lesion_count()
            elif 'rectangle_obj' in restored_object:
                rectangle_obj = restored_object['rectangle_obj']
                self.a.add_patch(rectangle_obj)
                self.rectangle_coordinates.append(restored_object)
                # RGB rectangle pixel
                rect_coords = restored_object['coordinates']
                rect_type = rect_coords['type']
                for type in self.echo_patterns:
                    if type == rect_type:
                        if len(self.removed_objects) > 0:
                            last_object = self.removed_objects[-1]
                            if 'rgb_highlight_obj' in last_object:
                                # Add RGB pixel back to added objects
                                restored_rgb_object = self.removed_objects.pop()
                                restored_rgb_value = restored_rgb_object['rgb_value']
                                # Restore RGB pixels
                                self.get_pixel_rgb_values(rect_coords, restored_rgb_value[0], restored_rgb_value[1])
                self.added_objects.append(restored_object)
            elif 'arrow_obj' in restored_object:
                arrow_obj = restored_object['arrow_obj']
                self.arrows.append(arrow_obj)
                self.a.add_patch(arrow_obj)
                self.added_objects.append(restored_object)
                self.arrow_coordinates.append(restored_object)
            elif 'dashedline_obj' in restored_object:
                if 'dashedline_obj' in restored_object:
                    dashedline_obj_list = restored_object['dashedline_obj']
                    for line2d_obj in dashedline_obj_list:
                        self.a.add_line(line2d_obj)
                        self.dashed_lines.append(line2d_obj)
                    self.dashed_line_coordinates.append(restored_object)
                if 'dashedlinestart_obj' in restored_object:
                    dashedline_obj_list = restored_object['dashedlinestart_obj']
                    self.a.add_line(dashedline_obj_list)
                    self.dashed_lines_plus.append(dashedline_obj_list)
                if 'dashedlineend_obj' in restored_object:
                    dashedline_obj_list = restored_object['dashedlineend_obj']
                    self.a.add_line(dashedline_obj_list)
                    self.dashed_lines_plus.append(dashedline_obj_list)
                if 'dashedlinetext' in restored_object:
                    dashedline_obj_list = restored_object['dashedlinetext']
                    self.a.add_artist(dashedline_obj_list)
                    self.dashed_lines_num_txt.append(dashedline_obj_list)
                self.added_objects.append(restored_object)
            elif 'plus_obj' in restored_object:
                plus_obj = restored_object["plus_obj"][0]
                self.a.add_line(plus_obj)
                self.plus_coordinates.append(restored_object)
                self.added_objects.append(restored_object)
        self.f.canvas.draw()

    # Matplotlib canvas
    def generate_matplotlib(self, image_location):
        # Add image to Matplotlib
        self.img_arr = mpimg.imread(image_location)
        # Original image_arr
        self.rgb_original = np.copy(self.img_arr)
        # Figure
        f = Figure(dpi=100, facecolor=SECONDARY_COLOUR)
        # Axis
        a = f.add_subplot()
        a.margins(0)
        a.imshow(self.img_arr)
        a.set_position([0, 0, 1, 1])
        a.axis('off')  # Hide axis

        self.f = f
        self.a = a

        # Create Canvas
        canvas = FigureCanvasTkAgg(f, self.graph_frame)
        canvas.draw()

        # Set canvas size
        # Set the desired width and height
        canvas.get_tk_widget().config(width=831, height=1208)
        canvas.get_tk_widget().configure(background=SECONDARY_COLOUR)  # Change 'black' to the color of your choice
        # Set canvas size dynamically
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=10)

        # Matplotlib toolbar
        backend_bases.NavigationToolbar2.toolitems = []
        toolbar = NavigationToolbar2Tk(canvas, self.graph_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X,
                     anchor="center")  # Position the toolbar at the bottom and fill it horizontally
        self.toolbar = toolbar

        # Create a label to display the coordinates
        self.coord_lbl = tk.Label(self.graph_frame, text="", fg="black")
        # Place the coord_label to the right of pen_type_lbl
        self.coord_lbl.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)

        if not self.upload_condition:
            toolbar.destroy()
        else:
            # Enable radio buttons
            self.set_cancer_type_radio_buttons_state("disabled")

        if self.annotation_status:
            # Connect the 'button_press_event' to the 'pressed' function
            canvas.mpl_connect('button_press_event', self.pressed)

            self.move = None
            # Connect the 'motion_notify_event' to the 'moved' functions
            canvas.mpl_connect('motion_notify_event', self.moved)
            # Connect the 'leave_event' to the 'update_coord_label_leave' function
            canvas.mpl_connect('figure_leave_event', self.update_coord_label_leave)
            canvas.mpl_connect('button_release_event', self.release)
            canvas.mpl_connect('motion_notify_event', self.update_coordinates)

        # Hide button frame
        else:
            self.button_frame.pack_forget()

    def update_coordinates(self, event):
        # Check if the mouse pointer is over the image
        self.coord_lbl.config(text=f"Coordinates: (0, 0)")
        if event.inaxes == self.a:
            # Get the coordinates of the mouse pointer
            x = int(event.xdata)
            y = int(event.ydata)
            # Update the label with the coordinates
            self.coord_lbl.config(text=f"Coordinates: ({x}, {y})")

    # Function to update coordinate label when mouse leaves the canvas
    def update_coord_label_leave(self, event):
        # When mouse leaves canvas, set label to (0, 0)
        self.coord_lbl.config(text=f"Coordinates: (0, 0)")

    def display_annotations(self):
        # Hide/unhide button frame
        if self.display_annotation_opts_status:
            self.display_annotation_opts_status = False
            self.button_frame.pack()
        elif not self.display_annotation_opts_status:
            self.display_annotation_opts_status = True
            self.button_frame.pack_forget()

    # Display pen functions
    def display_annotation_opts(self, options_frame):
        # Frame for buttons
        self.button_frame = tk.Frame(options_frame)
        self.button_frame.pack(side="bottom", expand=True)  # Pack the frame at the top with padding

        # Lesion select button
        self.create_button(self.button_frame, 25, 25, "./img/pen.png",
                           self.set_lesion_tool, "Lesion/Pen Draw")

        # Rectangle select button
        self.create_button(self.button_frame, 25, 25, "./img/square.png",
                           self.set_highlight_tool, "Rectangle Draw")

        # Arrow select button
        self.create_button(self.button_frame, 25, 25, "./img/left-down.png",
                           self.set_arrow_tool, "Arrow Draw")

        # Dashed-line / Orientation select button
        self.create_button(self.button_frame, 25, 25, "./img/dashed-line.png",
                           self.set_orientation_tool, "Orientation/Dashed-line Draw")

        # Calcification / 'plus' select button
        self.create_button(self.button_frame, 25, 25, "./img/plus.png",
                           self.plus_tool_select, "Calcification/Plus Draw")

        # Create a Combobox widget for line width selection
        self.width_scale = ttk.Combobox(self.button_frame, values=list(range(1, 11)), state="readonly")
        self.width_scale.set(2)
        self.width_scale.pack(side="left", padx=5, pady=5)  # Pack the combobox to the left with padding

        self.pen_type_lbl = tk.Label(self.button_frame, text="Pen type: Lesion", fg="red")
        self.pen_type_lbl.pack(side="bottom", padx=5, pady=5)

        # Pen/lesion drawing mode
        self.pen_mode = True

        # Initialise rectangle drawing mode variable
        self.rectangle_mode = False
        self.rectangle_drawing = False

        # Initialise arrow drawing mode variable
        self.arrow_mode = False
        self.arrow_start = None
        self.arrow = None

        # Initialise plus drawing mode variable
        self.plus_mode = False

    # Matplotlib button functionalities
    def home_action(self):
        self.toolbar.home()
        self.disable_matplotlib_action()

    def pan_action(self):
        if self.toolbar.mode != self.toolbar.mode.PAN:
            self.toolbar.pan()
            self.pen_type_lbl.configure(text="Canvas toolbar: Pan/Move", fg="black")
        else:
            self.define_pen_type()

    def zoom_action(self):
        if self.toolbar.mode != self.toolbar.mode.ZOOM:
            self.toolbar.zoom()
            self.pen_type_lbl.configure(text="Canvas toolbar: Zoom", fg="black")
        else:
            self.define_pen_type()

    def define_pen_type(self):
        line = self.pen_check.read_pen_line()
        type = self.pen_check.read_type_line()
        if line == "Line":
            self.set_lesion_tool()
        elif line == "Rect":
            self.set_highlight_type(type)
        elif line == "Arrow":
            self.set_arrow_tool()
        elif line == "Dashed-line":
            self.set_orientation_tool()

    def disable_matplotlib_action(self):
        self.toolbar.mode = self.toolbar.mode.NONE

    def set_lesion_tool(self):
        self.disable_matplotlib_action()
        self.pen_check.save_pen_line('Line')
        self.rect_type = ''
        self.rect_pen_colour = 'Green'
        self.pen_type_lbl.configure(text="Pen type: Lesion", fg="red")
        self.pen_mode = True
        self.rectangle_mode = False
        self.arrow_mode = False
        self.dashed_line_mode = False
        self.plus_mode = False
        self.canvas_connect()

    def set_highlight_type(self, rect_type):
        self.set_highlight_tool_start()
        self.toolbar.mode = self.toolbar.mode.NONE
        colour = self.colour_generator.predefined_colour(rect_type)
        self.rect_pen_colour = colour
        self.rect_type = type
        self.pen_type_lbl.configure(text=f"Pen type: {rect_type}", fg=colour)
        if rect_type == '':
            self.set_highlight_tool()

    def set_highlight_tool(self):
        self.rect_pen_colour = 'green'
        self.pen_check.clear_file()
        self.pen_check.save_pen_line('Rect')
        self.pen_type_lbl.configure(text="Pen type: Highlight", fg="green")
        self.set_highlight_tool_start()

    def set_highlight_tool_start(self):
        self.disable_matplotlib_action()
        self.pen_mode = False
        self.rectangle_mode = True
        self.arrow_mode = False
        self.dashed_line_mode = False
        self.plus_mode = False
        self.canvas_connect()

    def set_arrow_tool(self):
        self.disable_matplotlib_action()
        self.pen_check.save_pen_line('Arrow')
        self.pen_type_lbl.configure(text="Pen type: Arrow point", fg="purple")
        self.pen_mode = False
        self.rectangle_mode = False
        self.dashed_line_mode = False
        self.arrow_mode = True
        self.arrow_start = None
        self.preview_arrow = None
        self.plus_mode = False
        self.canvas_connect()

    def set_orientation_tool(self):
        self.disable_matplotlib_action()
        self.pen_check.save_pen_line('Dashed-line')
        self.pen_type_lbl.configure(text="Pen type: Orientation", fg="#d6a615")
        self.dashed_line_mode = True
        self.pen_mode = False
        self.rectangle_mode = False
        self.arrow_mode = False
        self.plus_mode = False

    # If calcification / Plus button clicked
    def plus_tool_select(self):
        self.plus_type = ''
        self.pen_type_lbl.configure(text="Pen type: Calcification", fg="#ff5100")
        self.pen_check.clear_file()
        self.set_calcification_tool()

    # If Calcification BI-RADS selected
    def set_plus_tool(self, plus_type):
        self.plus_type = plus_type
        self.pen_type_lbl.configure(text=f"Pen type: {plus_type}", fg="#ff5100")
        self.set_calcification_tool()

    # set Calcification functionality
    def set_calcification_tool(self):
        self.disable_matplotlib_action()
        self.pen_check.save_pen_line('Plus')
        self.plus_mode = True
        self.dashed_line_mode = False
        self.pen_mode = False
        self.rectangle_mode = False
        self.arrow_mode = False

    # Debugger function
    def print_echo(self):
        for arrow in self.arrows:
            self.a.add_patch(arrow)
        self.f.canvas.draw()

    def canvas_connect(self):
        # Connect the 'motion_notify_event' to the 'moved' function
        self.move = self.f.canvas.mpl_connect('motion_notify_event', self.moved)

    # If mouse is clicked on canvas, drawing lesions
    def pressed(self, event):
        self.update_coordinates(event)
        self.move = self.f.canvas.mpl_connect('motion_notify_event', self.moved)
        state = self.toolbar.mode
        # If highlight goes out of bounds, refresh
        line = self.pen_check.read_pen_line()
        if state == '':
            # Check if left mouse button is pressed
            if event.button == 1:
                if self.rectangle_mode:
                    self.f.canvas.mpl_disconnect(self.move)
                    # Check if rectangle drawing is in progress
                    if self.rectangle_drawing:
                        # Finish rectangle drawing
                        # Get RGB values of pixels within the drawn rectangle
                        # Check if last rectangle drawn is echo type
                        for type in self.echo_patterns:
                            if type == self.pen_check.read_type_line():
                                self.rgb_pixel_confirm(self.rectangle_coordinate["coordinates"])
                                # Appending to rectangle coordinate if rgb is changed
                                self.rectangle_coordinate["coordinates"]["rgb_value"] = {
                                    "rgb_1": self.rgb_value1,
                                    "rgb_2": self.rgb_value2
                                }
                        # Master object store - all objects
                        self.added_objects.append(self.rectangle_coordinate)
                        self.rectangle_coordinates.append(self.rectangle_coordinate)
                        self.f.canvas.mpl_disconnect(self.cid)
                        self.rectangle_drawing = False
                    else:
                        # Start new rectangle drawing
                        try:
                            self.rect = patches.Rectangle((event.xdata, event.ydata), 0, 0,
                                                          linewidth=2, edgecolor=self.rect_pen_colour,
                                                          facecolor='none')
                            self.a.add_patch(self.rect)
                        except:
                            pass
                        # Set the rectangle drawing flag to True
                        self.rectangle_drawing = True
                        self.cid = self.f.canvas.mpl_connect('motion_notify_event', self.draw_rectangle)

                elif self.arrow_mode:
                    if self.arrow_start:
                        # If arrow_start is not None, finalise the arrow
                        dx = event.xdata - self.arrow_start[0]
                        dy = event.ydata - self.arrow_start[1]

                        # Create the final arrow
                        arrow = FancyArrow(self.arrow_start[0], self.arrow_start[1], dx, dy,
                                           color=self.arrow_colour, width=2, head_width=10)
                        self.arrows.append(arrow)

                        self.arrow_coordinate = {"arrow_obj": arrow,
                                                 "coordinates": {"start_x": self.arrow_start[0],
                                                                 "start_y": self.arrow_start[1],
                                                                 "point_x": event.xdata, "point_y": event.ydata}}

                        self.arrow_coordinates.append(self.arrow_coordinate)
                        self.added_objects.append(self.arrow_coordinate)
                        self.removed_objects = []

                        # Add the final arrow to the plot
                        self.a.add_patch(arrow)
                        # Reset arrow_start
                        self.arrow_start = None
                        # Redraw the canvas to update the plot
                        self.f.canvas.draw()
                    else:
                        # Start a new arrow
                        self.arrow_start = (event.xdata, event.ydata)

                elif self.dashed_line_mode:
                    # Check if dashed line drawing is in progress
                    if self.dashed_line_drawing:
                        # Finish dashed line drawing
                        self.f.canvas.mpl_disconnect(self.cid)
                        self.dashed_line_drawing = False
                    else:
                        # Start new dashed line drawing
                        x, y = event.xdata, event.ydata
                        self.dashed_line_drawing = True
                        self.cid = self.f.canvas.mpl_connect('button_press_event',
                                                             lambda e: self.draw_dashed_line(e, x, y))
                elif self.plus_mode:
                    if event.button == 1:
                        # Start new plus draw
                        x, y = event.xdata, event.ydata
                        self.draw_plus(event, x, y)

                else:
                    # Check if left mouse button is pressed
                    if event.button == 1:
                        if self.lesion_counter.get_lesion_count() < 15:
                            # Clear redo
                            self.removed_objects = []

                            self.colour = '#ef0567'

                            # Create a new line object and store it in the lines list
                            line = self.a.plot([], [], color=self.colour, linewidth=self.width_scale.get())
                            self.lines.append(line[0])

                            # Create a dictionary for the line coordinates and add it to the line_coordinates list
                            line_info = {"line_obj": line[0], "coordinates": []}
                            # Master object store - all objects
                            self.added_objects.append(line_info)
                            self.line_coordinates.append(line_info)
                            self.line_coordinates_save.append(line_info)
                            self.line_coordinates_clear.append(line_info)

                            # Store the new line coordinates as a separate list within the line_info
                            line_info["coordinates"].append([])

                            # Store the current mouse position for reference in moved
                            self.move = (event.xdata, event.ydata)

    # If pen for drawing lesions is moved
    def moved(self, event):
        self.update_coordinates(event)
        state = self.toolbar.mode
        if state == '':
            # Check if left mouse button is pressed and lines list is not empty
            if event.button == 1 and self.lines and self.pen_mode and self.move is not None:
                if self.lesion_counter.get_lesion_count() < 15:
                    # Get the last line from the lines list
                    line = self.lines[-1]

                    # Get the corresponding line info from the line_coordinates list
                    line_info = self.line_coordinates[-1]

                    # Get the last line coordinates list from line_info
                    line_coords = line_info["coordinates"][-1]

                    # Append the new mouse coordinates to the line's existing data
                    x = np.append(line.get_xdata(), event.xdata)
                    y = np.append(line.get_ydata(), event.ydata)
                    line.set_data(x, y)

                    # Append the coordinates to the line_coords
                    line_coords.append((event.xdata, event.ydata))

                    # Redraw the canvas to update the plot
                    self.f.canvas.draw()
            elif self.arrow_mode and self.arrow_start:
                # Remove the preview arrow before drawing a new one
                try:
                    if self.preview_arrow:
                        self.preview_arrow.remove()
                except:
                    pass
                try:
                    # Calculate the arrow dimensions for the preview
                    dx = event.xdata - self.arrow_start[0]
                    dy = event.ydata - self.arrow_start[1]

                    # Draw the preview arrow
                    self.preview_arrow = FancyArrow(self.arrow_start[0], self.arrow_start[1], dx, dy,
                                                    color=self.arrow_colour, width=2, head_width=10)
                    self.a.add_patch(self.preview_arrow)
                    self.f.canvas.draw()
                except:
                    pass

    def release(self, event):
        try:
            element = self.added_objects[-1] if self.added_objects else None
            if len(element['coordinates'][0]) == 0:
                self.lines.pop()
                self.added_objects.pop()
                self.line_coordinates.pop()
                self.line_coordinates_save.pop()
                self.line_coordinates_clear.pop()
            else:
                if self.pen_mode:
                    state = self.toolbar.mode
                    if state == '':
                        if self.lesion_counter.get_lesion_count() < 15:
                            self.rads_load_status.set_rads_load_status('True')
                            self.lesion_counter.increment_lesion_count()
        except:
            pass

    # Draw highlight lesion identifier
    def draw_rectangle(self, event):
        if self.rectangle_drawing:
            if event.inaxes == self.a:
                width = event.xdata - self.rect.get_x()
                height = event.ydata - self.rect.get_y()
                self.rect.set_width(width)
                self.rect.set_height(height)
                # Fill the rectangle with the most common pixel colour - if rect_type is echo
                # Store the coordinates of the drawn rectangle
                self.rectangle_coordinate = {"rectangle_obj": self.rect,
                                             "coordinates": {"x": self.rect.get_x(), "y": self.rect.get_y(),
                                                             "width": width,
                                                             "height": height,
                                                             "colour": self.rect_pen_colour,
                                                             "type": self.rect_type}}
                self.f.canvas.draw()

    def rgb_pixel_confirm(self, coordinates):
        dialog = tk.Toplevel(self.controller)
        dialog.title("RGB options")

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
        message_label = tk.Label(dialog, text="Choose RGB colour parameters:", padx=20, pady=20, font=("Helvetica", 14))
        message_label.pack()

        # Configure style for fixed-size buttons
        style = ttk.Style()
        style.configure("FixedSize.TButton", font=("Helvetica", 12), padding=10,
                        relief='raised', background='#424242', foreground='#212121', width=10, height=2)

        # Create "Confirm" and "Close" buttons
        new_save_button = ttk.Button(dialog, text="Confirm", command=lambda: self.on_rgb_button_click("1"
                                                                                                      , dialog
                                                                                                      , coordinates),
                                     style="FixedSize.TButton")
        close_button = ttk.Button(dialog, text="Close", command=lambda: self.on_rgb_button_click("2"
                                                                                                 , dialog
                                                                                                 , coordinates),
                                  style="FixedSize.TButton")

        # Create DoubleSlider instance
        slider_frame = DoubleSlider(dialog, self)
        slider_frame.pack(expand=True, fill=tk.BOTH)

        # Redraw sliders after the canvas has been created
        slider_frame.redraw_sliders()

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

    def on_rgb_button_click(self, option, dialog, coordinates):
        if option == "1":
            self.get_pixel_rgb_values(coordinates, self.rgb_value1, self.rgb_value2)
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

    # Check RGB pixels of echo
    def get_pixel_rgb_values(self, coordinates, rgb_value1, rgb_value2):
        x1 = int(coordinates["x"])
        y1 = int(coordinates["y"])
        x2 = int(coordinates["x"] + coordinates["width"])
        y2 = int(coordinates["y"] + coordinates["height"])

        # Clip x and y values
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # RGB values from slider
        self.min_rgb_value = rgb_value1
        self.max_rgb_value = rgb_value2

        # Debug purposes
        coordinates_save = set()

        # Create overlay dots for pixels within the specified RGB range
        for y in range(y1, y2):
            for x in range(x1, x2):
                try:
                    pixel_rgb = (self.img_arr[y, x] * 255).astype(int)
                    clipped_rgb = np.clip(pixel_rgb, 0, 255)  # Clip RGB values to [0, 255] range
                    if (self.min_rgb_value <= clipped_rgb[0] <= self.max_rgb_value
                            and self.min_rgb_value <= clipped_rgb[1] <= self.max_rgb_value
                            and self.min_rgb_value <= clipped_rgb[2] <= self.max_rgb_value):
                        # Check if pixel coordinates are within the rectangle boundary
                        if x1 <= x < x2 and y1 <= y < y2:
                            # Create overlay square with adjusted coordinates
                            self.img_arr[y, x] = [255, 0, 0]  # Set to red
                            coordinates_save.add((x, y))  # Use a tuple instead of a dictionary
                except Exception as e:
                    pass

        self.rgb_coordinate = {"rgb_highlight_obj": self.img_arr,
                               "coordinates": coordinates_save,  # Use the set directly
                               "rgb_value": [rgb_value1, rgb_value2],
                               "colour": 'red'}
        self.added_objects.append(self.rgb_coordinate)
        self.rgb_coordinates.append(self.rgb_coordinate)

        # Remove the image from the axes
        for im in self.a.images:
            im.remove()

        # Save the changes to the history
        self.rgb_history.append(self.img_arr.copy())

        # Plot the image with modified pixels
        self.a.imshow(self.img_arr)

        # Redraw the canvas
        self.f.canvas.draw()

    # Draw dashed lines
    def draw_dashed_line(self, event, start_x, start_y):
        if event.inaxes and event.button == 1:
            end_x, end_y = event.xdata, event.ydata
            colour = "#ffc61c"

            self.local_dashed_lines_plus = []

            count = len(self.dashed_line_coordinates)
            if count % 2 == 0:
                self.dash_line_count = 1
            else:
                self.dash_line_count = 2

            # Draw "+" plus shapes at the starting and ending coordinates
            self.draw_plus_shape(colour, start_x, start_y)
            self.draw_plus_shape(colour, end_x, end_y, label=f'{self.dash_line_count}', padding=15)

            line = self.a.plot([start_x, end_x], [start_y, end_y], linestyle='dashed', color=colour, linewidth=2)
            self.dashed_lines.append(line[0])

            self.dashed_line_coordinate = {"dashedline_obj": line,
                                           "coordinates": {"start_x": start_x,
                                                           "end_x": end_x,
                                                           "start_y": start_y,
                                                           "end_y": end_y},
                                           "dashedlinestart_obj": self.local_dashed_lines_plus[0],
                                           "dashedlineend_obj": self.local_dashed_lines_plus[1],
                                           "dashedlinetext": self.dashed_lines_num_txt[-1]}
            # Add to added objects array for UNDO and REDO
            self.dashed_line_coordinates.append(self.dashed_line_coordinate)
            self.added_objects.append(self.dashed_line_coordinate)

            # Redraw the canvas to update the plot
            self.f.canvas.draw()
            self.dashed_line_drawing = False
            self.f.canvas.mpl_disconnect(self.cid)

    def draw_plus_shape(self, colour, x, y, label=None, padding=0):
        # Draw a "+" plus shape at the given coordinates
        plus = self.a.plot(x, y, marker='+', markersize=10, markeredgewidth=2, color=colour)
        self.dashed_lines_plus.append(plus[0])
        self.local_dashed_lines_plus.append(plus[0])

        # Add label text with padding next to the "+" plus shape
        if label is not None:
            x_label = x + padding
            y_label = y + padding
            text = self.a.text(x_label, y_label, label, color=colour, fontsize=15, verticalalignment='center',
                               horizontalalignment='right')
            self.dashed_lines_num_txt.append(text)

    def draw_plus(self, event, x, y):
        if event.inaxes and event.button == 1:
            # Draw a "+" plus shape at the given coordinates
            plus = self.a.plot(x, y, marker='+', markersize=10, markeredgewidth=2, color='#ff5100')
            self.plus_coordinate = {"plus_obj": plus,
                                    "coordinates": {"x": x,
                                                    "y": y,
                                                    "type": self.plus_type}}
            self.plus_coordinates.append(self.plus_coordinate)
            self.added_objects.append(self.plus_coordinate)
            # Redraw the canvas to update the plot
            self.f.canvas.draw()

    # Clear all canvas drawings functionality
    def clear_lines(self):
        # Clear all lines drawn on the matplotlib image
        for line_info in self.line_coordinates_clear:
            line = line_info["line_obj"]
            line.remove()  # Remove the line object

        for rect in self.a.patches:
            rect.remove()  # Remove the rectangle patch

        try:
            for dashed_line in self.dashed_lines:
                dashed_line.remove()  # Remove dashed-lines
        except:
            pass
        try:
            for dashed_line_plus in self.dashed_lines_plus:
                dashed_line_plus.remove()
        except Exception as ex:
            pass
        try:
            for dashed_line_num_txt in self.dashed_lines_num_txt:
                dashed_line_num_txt.remove()
        except:
            pass
        try:
            for plus in self.plus_coordinates:
                plus_object = plus["plus_obj"][-1]
                plus_object.remove()
        except Exception as e:
            print(e)

        # RGB
        self.img_arr = np.copy(self.rgb_original)
        # Remove the image from the axes
        for im in self.a.images:
            im.remove()
        self.a.imshow(self.img_arr)
        self.rgb_history = []
        self.rgb_redo_history = []
        self.rgb_coordinates = []

        # Clear image type
        self.radio_ultrasound_type_var.set("")

        # Clear annotation_id
        self.annotation_id = ''

        # When cleared default to lesion draw
        self.set_lesion_tool()

        self.added_objects = []
        self.removed_objects = []

        # Reset lesion counter
        self.lesion_counter.reset_lesion_count()

        # Reset arrow_start
        self.arrow_start = None
        self.lines = []  # Clear the lines list
        self.line_coordinates = []  # Clear the line_coordinates list
        self.line_coordinates_save = []  # Clear the line_coordinates_save list
        self.line_coordinates_clear = []  # Clear the line_coordinates_clear list
        self.rectangle_coordinates = []  # Clear rectangle array
        self.arrows = []  # Clear arrow arrays
        self.arrow_coordinates = []
        self.dashed_lines = []  # Clear dashed-line arrays
        self.dashed_lines_plus = []
        self.dashed_line_coordinates = []
        self.dashed_lines_num_txt = []
        self.plus_coordinates = []
        self.f.canvas.draw()  # Redraw the canvas to update the plot

    # Save RADS details to JSON -> Every input saved
    def save_to_json(self):
        try:
            # Load existing data from the JSON file, if any
            try:
                with open('rads.JSON', 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}

            # Iterate through the pages and create entries for each
            for page_num, rads_data in self.lesion_data_dict.items():
                page_entry = {
                    "masses": {
                        "Shape": rads_data["shape_combobox"],
                        "Orientation": rads_data["orientation_combobox"],
                        "Margin": rads_data["margin_selection"],
                        "Margin options": rads_data["margin_notcircumscribed_options"],
                        "Echo pattern": rads_data["echo_pattern"],
                        "Posterior features": rads_data["posterior"],
                        "Calcification": rads_data["calcification"],
                        "Calcification options": rads_data["calcification_options"],
                        "Additional notes": rads_data["additional_notes"]
                    }
                }
                # Add the page entry to the data dictionary
                data[f"{page_num}"] = page_entry
                self.rads_load_status.set_rads_load_status('True')

            # Save the updated data to the JSON file
            with open('rads.JSON', 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            print(e)
            pass

    # Disable frame functionality
    def disable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton, tk.Radiobutton,
                                  tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='disabled')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.disable_frame(child)

    # Enable frame functionality
    def enable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton, tk.Radiobutton,
                                  tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='enabled')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.disable_frame(child)

        # Quit application

    def on_closing(self):
        # Quit application dialog
        self.quit_operation.quit_confirmation()
        pass

    # Check RADS margin and echo selection
    def colour_rads_check(self):
        line = self.pen_check.read_pen_line()
        type = self.pen_check.read_type_line()
        if self.rect_type != type:
            if line == "Rect":
                self.set_highlight_type(type)
            if line == "Plus":
                self.set_plus_tool(type)
        self.after(200, self.colour_rads_check)