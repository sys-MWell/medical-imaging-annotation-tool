# annotation_page_functionality.py
import time
from collections import Counter

from imports import *
from annotation_vars import PageVariables
from lesion_counter import LesionCounter


class PageFunctionality(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Initialise the variables from PageVariables
        PageVariables.__init__(self)

        # Lesion Counter
        self.lesion_counter = LesionCounter()
        self.lesion_counter.reset_lesion_count()

        # If rads loaded from annotations.json
        self.rads_load_status = RadsLoadStatus()
        self.rads_load_status.set_rads_load_status('False')

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

        self.upload_functionality()
        self.annotation_functionality()

    # Upload image section functionality
    def upload_functionality(self):
        # Create a frame for the matplotlib graph and toolbar
        self.upload_frame = tk.Frame(self.combined_frame, bg=FRAME_BACKGROUND_COLOUR, width=250, height=680)
        self.upload_frame.pack(side="left", fill="both", expand=False)  # Use pack with fill and expand options

        # Set background color
        self.configure(bg=MASTER_COLOUR)

        # Adjust upload button visability based on user type
        if self.user_type == "1":
            label = tk.Label(self.upload_frame, text="Image Upload and Selection", font=("Helvetica", 16),
                             bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
            label.pack(pady=10, padx=10)

            # Create a button to upload images with a modern style
            upload_button = ttk.Button(self.upload_frame, text="Upload Images", command=self.upload_images,
                                       style="Custom.TButton")
            upload_button.pack(pady=10)
        elif self.user_type == "2":
            label = tk.Label(self.upload_frame, text="Annotation Selection", font=("Helvetica", 16),
                             bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
            label.pack(pady=10, padx=10)

        # Please select image label
        select_img_label = tk.Label(self.upload_frame, text="Please select an image...", font=("Helvetica", 12),
                                    bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
        select_img_label.pack(pady=2, padx=10)

        # Error display - No Images Uploaded
        self.error_display_img_label = tk.Label(self.upload_frame, text="No images uploaded\n"
                                                                        "please upload images",
                                                font=("Helvetica", 12),
                                                bg=SECONDARY_COLOUR, fg='red')
        self.error_display_img_label.pack(pady=2, padx=10, anchor='center', side='top')

        # Create a frame to display the images with a light background
        self.image_frame = tk.Frame(self.upload_frame, bg=SECONDARY_COLOUR,
                                    highlightbackground="black", highlightthickness=1, width=250, height=680)
        self.image_frame.pack(pady=10, padx=10)

        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", gripcount=0,
                        background="red")  # Set the background color as needed
        style.layout("Custom.Vertical.TScrollbar",
                     [('Vertical.Scrollbar.trough', {'children':
                                                         [('Vertical.Scrollbar.thumb',
                                                           {'expand': '1', 'unit': '1', 'children': [
                                                               ('Vertical.Scrollbar.grip', {'sticky': 'ns'})]})]})])

        # Create a canvas with a scrollbar for displaying the images
        self.canvas = tk.Canvas(self.image_frame, bg=SECONDARY_COLOUR, width=250, height=680)
        self.scrollbar = ttk.Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview,
                                       style="Custom.Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=SECONDARY_COLOUR, padx=0)

        # Scrollbar functionality
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                height=680, width=250
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the scrollbar style
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", gripcount=10,
                        background="gray")  # Set the background color and grip count as needed

        # Load all images from JSON
        self.load_images_from_json()

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

        # Ultra sound type radio button selection
        if self.upload_condition:
            # Ultra sound Type Radio Button
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
        self.options_frame.pack(anchor="n", side="bottom", expand=True)  # Pack the frame at the top with padding

        # Page buttons for annotation tool
        if self.upload_condition:
            # Generate button toolbar
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/restart.png", self.home_action,
                               "Set canvas to original position")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/move.png", self.pan_action, "Canvas pan")
            self.create_button(matplotlib_btn_frame, 50, 50, "./img/zoom.png", self.zoom_action, "Canvas Zoom")

            # If Medical Professional User
            if self.user_type == "1":
                separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
                separator_label.pack(side="left", padx=5)
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/options.png",
                                   lambda: self.display_annotations(),
                                   "Hide/Show pen toolbar")
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/clear.png", lambda: self.clear_lines(),
                                   "Canvas clear")
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/save.png", lambda: self.save_confirmation(),
                                   "Save annotation")
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/load.png", lambda: self.load_confirmation(),
                                   "Load existing image annotations")
                separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
                separator_label.pack(side="left", padx=5)
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/undo.png", lambda: self.undo_object(),
                                   "Undo annotation")
                self.create_button(matplotlib_btn_frame, 50, 50, "./img/redo.png", lambda: self.redo_object(),
                                   "Redo annotation")

        self.display_annotation_opts(self.options_frame)
        self.generate_matplotlib(self.image_location)

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
                self.added_objects.append(restored_object)
                self.rectangle_coordinates.append(restored_object)
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
        self.f.canvas.draw()

    # Matplotlib canvas
    def generate_matplotlib(self, image_location):
        # Add image to Matplotlib
        self.img_arr = mpimg.imread(image_location)
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
        canvas.get_tk_widget().config(width=800, height=600)  # Set the desired width and height
        canvas.get_tk_widget().configure(background=SECONDARY_COLOUR)  # Change 'black' to the color of your choice
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0)

        # Matplotlib toolbar
        backend_bases.NavigationToolbar2.toolitems = []
        toolbar = NavigationToolbar2Tk(canvas, self.graph_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X,
                     anchor="center")  # Position the toolbar at the bottom and fill it horizontally
        self.toolbar = toolbar

        if not self.upload_condition:
            toolbar.destroy()

        # If Medical Professional User
        if self.user_type == "1":
            if self.annotation_status:
                # Connect the 'button_press_event' to the 'pressed' function
                canvas.mpl_connect('button_press_event', self.pressed)

                self.move = None
                # Connect the 'motion_notify_event' to the 'moved' functions
                canvas.mpl_connect('motion_notify_event', self.moved)

                canvas.mpl_connect('button_release_event', self.release)

            # Hide button frame
            else:
                self.button_frame.pack_forget()

    # Matplotlib button functionalities
    def home_action(self):
        self.toolbar.home()

    def pan_action(self):
        self.toolbar.pan()

    def zoom_action(self):
        self.toolbar.zoom()

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

        # If Medical Professional User
        if self.user_type == "1":
            # Lesion select button
            self.create_button(self.button_frame, 25, 25, "./img/pen.png",
                               self.set_lesion_tool, "Lesion/Pen Draw")

            # Rectangle select button
            self.create_button(self.button_frame, 25, 25, "./img/square.png",
                               self.set_highlight_tool, "Rectangle Draw")

            # Arrow select button
            self.create_button(self.button_frame, 25, 25, "./img/left-down.png",
                               self.set_echo_tool, "Arrow Draw")

            # Dashed-line / Orientation select button
            self.create_button(self.button_frame, 25, 25, "./img/dashed-line.png",
                               self.set_orientation_tool, "Orientation/Dashed-line Draw")

            # Create a Combobox widget for line width selection
            self.width_scale = ttk.Combobox(self.button_frame, values=list(range(1, 11)), state="readonly")
            self.width_scale.set(2)
            self.width_scale.pack(side="left", padx=5, pady=5)  # Pack the combobox to the left with padding

            self.pen_type_lbl = tk.Label(self.button_frame, text="Pen type: Lesion", fg="blue")
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

    def set_lesion_tool(self):
        self.pen_check.save_pen_line('Line')
        self.rect_type = ''
        self.rect_pen_colour = 'Green'
        self.pen_type_lbl.configure(text="Pen type: Lesion", fg="blue")
        self.pen_mode = True
        self.rectangle_mode = False
        self.arrow_mode = False
        self.dashed_line_mode = False
        self.canvas_connect()

    def set_highlight_tool(self):
        self.rect_pen_colour = 'green'
        self.pen_check.clear_file()
        self.pen_check.save_pen_line('Rect')
        self.pen_type_lbl.configure(text="Pen type: Highlight", fg="green")
        self.set_highlight_tool_start()

    def set_highlight_tool_start(self):
        self.pen_mode = False
        self.rectangle_mode = True
        self.arrow_mode = False
        self.dashed_line_mode = False
        self.canvas_connect()

    def set_echo_tool(self):
        self.pen_check.save_pen_line('Arrow')
        self.pen_type_lbl.configure(text="Pen type: Echo", fg="purple")
        self.pen_mode = False
        self.rectangle_mode = False
        self.dashed_line_mode = False
        self.arrow_mode = True
        self.arrow_start = None
        self.preview_arrow = None
        self.canvas_connect()

    def set_orientation_tool(self):
        self.pen_check.save_pen_line('Dashed-line')
        self.pen_type_lbl.configure(text="Pen type: Orientation", fg="red")
        self.dashed_line_mode = True
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
                            self.lesion_counter.increment_lesion_count()
        except:
            # If rectangle (Highlight)
            pass

    # Draw highlight lesion identifier
    def draw_rectangle(self, event):
        if self.rectangle_drawing:
            if event.inaxes == self.a:
                width = event.xdata - self.rect.get_x()
                height = event.ydata - self.rect.get_y()
                self.rect.set_width(width)
                self.rect.set_height(height)
                self.f.canvas.draw()
                # Store the coordinates of the drawn rectangle
                self.rectangle_coordinate = {"rectangle_obj": self.rect,
                                             "coordinates": {"x": self.rect.get_x(), "y": self.rect.get_y(),
                                                             "width": width,
                                                             "height": height,
                                                             "colour": self.rect_pen_colour,
                                                             "type": self.rect_type}}
                # Fill the rectangle with the most common pixel colour - if rect_type is echo
                if self.rect_type in self.echo_patterns:
                    most_common_colour = self.calculate_most_common_colour(self.rect)
                    self.rect.set_facecolor(most_common_colour)
                    self.f.canvas.draw()
            else:
                self.finalise_rectangle(event)

    def finalise_rectangle(self, event):
        if self.rectangle_drawing:
            # Finish rectangle drawing
            # Master object store - all objects
            self.added_objects.append(self.rectangle_coordinate)
            self.rectangle_coordinates.append(self.rectangle_coordinate)
            self.f.canvas.mpl_disconnect(self.cid)
            self.rectangle_drawing = False

    def calculate_most_common_colour(self, rectangle, num_clusters=5):
        x1 = int(rectangle.get_x())
        y1 = int(rectangle.get_y())
        x2 = int(rectangle.get_x() + rectangle.get_width())
        y2 = int(rectangle.get_y() + rectangle.get_height())

        # Ensure x1 is less than x2 and y1 is less than y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Check if the rectangle dimensions are greater than zero
        if x2 - x1 <= 0 or y2 - y1 <= 0:
            return None  # Return None if the rectangle has zero dimensions

        # Adjust coordinates to ensure they are within image bounds
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.img_arr.shape[1])
        y2 = min(y2, self.img_arr.shape[0])

        # Get the pixels within the adjusted rectangle bounds
        pixels = self.img_arr[y1:y2, x1:x2]

        # Reshape the pixel array
        flattened_pixels = pixels.reshape(-1, pixels.shape[-1])

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(flattened_pixels)

        # Find the cluster with the largest number of pixels
        cluster_labels = kmeans.predict(flattened_pixels)
        most_common_cluster_label = Counter(cluster_labels).most_common(1)[0][0]

        # Get the representative colour of the most common cluster
        most_common_colour = kmeans.cluster_centers_[most_common_cluster_label]

        # Return colour that is most common
        return most_common_colour

    def draw_dashed_line(self, event, start_x, start_y):
        if event.inaxes and event.button == 1:
            end_x, end_y = event.xdata, event.ydata

            self.local_dashed_lines_plus = []

            count = len(self.dashed_line_coordinates)
            if count % 2 == 0:
                self.dash_line_count = 1
            else:
                self.dash_line_count = 2

            # Draw "+" plus shapes at the starting and ending coordinates
            self.draw_plus_shape(start_x, start_y)
            self.draw_plus_shape(end_x, end_y, label=f'{self.dash_line_count}', padding=15)

            line = self.a.plot([start_x, end_x], [start_y, end_y], linestyle='dashed', color='red', linewidth=2)
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

    def draw_plus_shape(self, x, y, label=None, padding=0):
        # Draw a "+" plus shape at the given coordinates
        plus = self.a.plot(x, y, marker='+', markersize=10, markeredgewidth=2, color='red')
        self.dashed_lines_plus.append(plus[0])
        self.local_dashed_lines_plus.append(plus[0])

        # Add label text with padding next to the "+" plus shape
        if label is not None:
            x_label = x + padding
            y_label = y + padding
            text = self.a.text(x_label, y_label, label, color='red', fontsize=10, verticalalignment='center',
                               horizontalalignment='right')
            self.dashed_lines_num_txt.append(text)

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
        self.f.canvas.draw()  # Redraw the canvas to update the plot

    # Message box, confirming save
    def save_confirmation(self):
        found_annotation = False
        if self.annotation_id == '':
            response = messagebox.askyesno("Save", "Are you sure you want to save?")
        else:
            # Load the JSON data from the file
            with open("annotations.json", "r") as file:
                json_data = json.load(file)
            # Check image ID and annotation ID exist in JSON
            for image in json_data["images"]:
                if "image_id" in image and image["image_id"] == self.image_id:
                    for annotation in image["annotations"]:
                        if "annotation_id" in annotation and annotation["annotation_id"] == self.annotation_id:
                            found_annotation = True

        if found_annotation:
            self.save_dialog()
        else:
            if response:
                # Save functionality
                self.save('2')
            else:
                # Do nothing
                pass

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
        overwrite_button = ttk.Button(dialog, text="Overwrite", command=lambda: self.on_button_click("1", dialog),
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
            unique_annotation_id = self.annotation_id
        else:
            unique_annotation_id = f"{timestamp}_{uuid.uuid4()}"  # Unique annotation ID with timestamp
            self.annotation_id = unique_annotation_id

        self.lesion_data_dict = self.load_rads_data.load_rads_data()
        lesion_count = self.lesion_counter.get_lesion_count()
        if ((self.lines and (self.line_coordinates_save or self.rectangle_coordinates)) or
                (int(lesion_count) > 0) or (len(self.dashed_line_coordinates) > 0)):
            # Convert rectangle coordinates to desired format
            converted_rectangles = []
            for rectangle_info in self.rectangle_coordinates:
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
                    converted_rectangles.append(rectangle)

            # Save echo/arrow objects to JSON
            converted_arrows = []
            for arrow_info in self.arrow_coordinates:
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
            for dashedline_info in self.dashed_line_coordinates:
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

            # Initialise the list to store all annotations
            lesions = []
            # Loop through each entry in self.lesion_data_dict
            for lesion_key, lesion_data in self.lesion_data_dict.items():
                rads_entry = {
                    f"{lesion_key}": {
                        "masses": {
                            "shape": lesion_data["shape_combobox"],
                            "Orientation": lesion_data["orientation_combobox"],
                            "Margin": lesion_data["margin_selection"],
                            "Margin not circumscribed options": lesion_data["margin_notcircumscribed_options"],
                            "Echo pattern": lesion_data["echo_pattern"],
                            "Posterior features": lesion_data["posterior"],
                            "additional_notes": lesion_data["additional_notes"]
                        }
                    }
                }
                lesions.append(rads_entry)

            annotation = {
                "annotation_id": unique_annotation_id,
                "user_id": self.user_id,
                "ultra_sound_type": self.radio_ultrasound_type_var.get(),
                "coordinates": [],
                "highlight": converted_rectangles,  # Use the converted_rectangles
                "echo": converted_arrows,  # Arrow objects saved
                "orientation": converted_dashedlines,  # Dashed-line objects saved
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
            for line_info in self.line_coordinates_save:
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
            line_data["width"] = line_info["line_obj"].get_linewidth() if self.line_coordinates_save else None
            line_data["colour"] = line_info["line_obj"].get_color() if self.line_coordinates_save else None

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
                    if image["image_id"] == self.image_id:
                        for i, existing_annotation in enumerate(image["annotations"]):
                            if self.annotation_id == existing_annotation["annotation_id"]:
                                # Update existing annotation data
                                image_exists = True
                                image["annotations"][i] = annotation  # Update only the specific annotation
                                break
            elif save_type == "2":
                # Check if the image_id already exists in the data
                for image in data["images"]:
                    if image["image_id"] == self.image_id:
                        image_exists = True
                        image["annotations"].append(annotation)  # Override existing annotations
                        break

            if not image_exists:
                image_data = {
                    "image_id": self.image_id,
                    "annotations": [annotation]
                }
                data["images"].append(image_data)

            with open("annotations.json", "w") as file:
                json.dump(data, file, indent=2)

        # Toolbar save functionality
        self.save_figure()

    def save_figure(self):
        # Saving canvas/annotated ultrasound image
        # Saving to folder annotations
        filename = f"./annotations/{self.image_id}_{self.annotation_id}.png"
        self.f.savefig(filename, bbox_inches='tight', pad_inches=0)

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
                        "shape": rads_data["shape_combobox"],
                        "Orientation": rads_data["orientation_combobox"],
                        "Margin": rads_data["margin_selection"],
                        "Margin options": rads_data["margin_notcircumscribed_options"],
                        "Echo pattern": rads_data["echo_pattern"],
                        "Posterior features": rads_data["posterior"],
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

    # Message box, confirming load
    def load_confirmation(self):
        annotations = []
        annotation_count = 0
        # Load the JSON data from the file
        with open("annotations.json", "r") as file:
            json_data = json.load(file)
        # Check image ID and annotation ID exist in JSON
        for image in json_data["images"]:
            if "image_id" in image and image["image_id"] == self.image_id:
                for annotation in image["annotations"]:
                    annotations.append(annotation["annotation_id"])
                    annotation_count += 1

        if annotation_count > 0:
            self.load_dialog(annotation_count, annotations)
        else:
            messagebox.showinfo("No Saves Found", "No saved data found.")

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
            self.annotation_id = str(annotations[number-1])
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
        self.clear_lines()
        self.lesion_data_dict = {}
        try:
            with open("annotations.json", "r") as file:
                data = json.load(file)
                for image in data["images"]:
                    if image["image_id"] == self.image_id:
                        for annotation in image["annotations"]:
                            if annotation["annotation_id"] == annotation_id:
                                self.image_id = image["image_id"]
                                self.annotation_id = annotation["annotation_id"]
                                self.user_id = annotation["user_id"]
                                ultra_sound_type = annotation["ultra_sound_type"]
                                self.radio_ultrasound_type_var.set(ultra_sound_type)
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
                                        rect_obj = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor=colour,
                                                                     facecolor='none')
                                        # Store the rectangle object along with its coordinates
                                        rect_info = {"rectangle_obj": rect_obj, "coordinates": rect_data}
                                        # Append to the rectangle_coordinates list
                                        self.rectangle_coordinates.append(rect_info)
                                        # Add the rectangle patch to the Axes object
                                        self.a.add_patch(rect_obj)

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
                                        self.arrow_coordinates.append(arrow_info)

                                        # Add the arrow to the plot
                                        self.a.add_patch(arrow_obj)

                                if "orientation" in annotation:
                                    dashedline_data_list = annotation["orientation"]
                                    for dashedline_data in dashedline_data_list:
                                        start_x = dashedline_data["start_x"]
                                        end_x = dashedline_data["end_x"]
                                        start_y = dashedline_data["start_y"]
                                        end_y = dashedline_data["end_y"]
                                        txt = dashedline_data["txt"]

                                        line_obj = mlines.Line2D([start_x, end_x], [start_y, end_y],
                                                                 color='red', linewidth=2, linestyle='dashed')
                                        self.a.add_line(line_obj)
                                        self.dashed_lines.append(line_obj)

                                        plus1 = self.a.plot(start_x, start_y, marker='+', markersize=10, markeredgewidth=2,
                                                            color='red')
                                        self.dashed_lines_plus.append(plus1[0])
                                        plus2 = self.a.plot(end_x, end_y, marker='+', markersize=10, markeredgewidth=2,
                                                            color='red')
                                        self.dashed_lines_plus.append(plus2[0])

                                        # Remove the 'Text(' and ')' parts
                                        cleaned_string = txt.replace('Text(', '').replace(')', '')
                                        # Split the string into a list using commas as separators - Convert the elements to
                                        # appropriate types (float for coordinates, and strip quotes for text)
                                        elements = cleaned_string.split(', ')
                                        x_coordinate = float(elements[0])
                                        y_coordinate = float(elements[1])
                                        text_content = elements[2].strip("'")
                                        text = self.a.text(x_coordinate, y_coordinate, text_content, color='red',
                                                           fontsize=10, verticalalignment='center',
                                                           horizontalalignment='right')
                                        self.dashed_lines_num_txt.append(text)

                                        # Store dashed line object information
                                        dashedline_info = {"rectangle_obj": line_obj, "coordinates": dashedline_data}

                                        # Append to dashedline list
                                        self.dashed_line_coordinates.append(dashedline_info)

                                # Load lesion lines
                                for line_data in annotation["coordinates"]:
                                    self.lesion_counter.increment_lesion_count()
                                    lines = line_data["lesions"]  # lines is now a list of coordinate strings

                                    for coord_string in lines:
                                        coords = eval(coord_string)  # Convert the string back to a list of tuples
                                        if coords is None:
                                            continue  # Skip if coords is None

                                        x_coords = [x for x, _ in coords]
                                        y_coords = [y for _, y in coords]
                                        line_obj = mlines.Line2D(x_coords, y_coords, color=line_data["colour"],
                                                                 linewidth=line_data["width"])
                                        self.a.add_line(line_obj)

                                        line_info = {"line_obj": line_obj, "coordinates": [coords]}
                                        self.line_coordinates.append(line_info)
                                        self.line_coordinates_save.append(line_info)
                                        self.line_coordinates_clear.append(line_info)

                                for rad_data in annotation["rads"]:
                                    # Iterate over the dictionary keys
                                    for lesion_key, lesion_data in rad_data.items():
                                        # Extract information for each lesion
                                        masses_data = lesion_data.get("masses", {})
                                        shape_combobox = masses_data.get("shape", "")
                                        orientation_combobox = masses_data.get("Orientation", "")
                                        margin_selection = masses_data.get("Margin", "")
                                        margin_pattern_var = masses_data.get("Margin not circumscribed options", "")
                                        echo_pattern_var = masses_data.get("Echo pattern", "")
                                        posterior_var = masses_data.get("Posterior features", "")
                                        additional_notes = masses_data.get("additional_notes", "")

                                        # Store the lesion data in the dictionary using lesion_key as the index
                                        self.lesion_data_dict[lesion_key] = {
                                            "shape_combobox": shape_combobox,
                                            "orientation_combobox": orientation_combobox,
                                            "margin_selection": margin_selection,
                                            "margin_notcircumscribed_options": margin_pattern_var,
                                            "echo_pattern": echo_pattern_var,
                                            "posterior": posterior_var,
                                            "additional_notes": additional_notes
                                        }
                                break
                        self.f.canvas.draw()
                        break
            self.save_to_json()
        except FileNotFoundError:
            # Handle the case when the file is not found
            pass

    # Upload images functionality
    def upload_images(self):
        try:
            self.uploaded_image = ''
            self.images_save = []
            # Browse and select image files
            filetypes = [('Image Files', '*.jpg *.jpeg *.png')]
            filenames = filedialog.askopenfilenames(filetypes=filetypes)

            # Check if the user has selected file(s)
            if filenames:
                # Load and resize the images
                for filename in filenames:
                    img = Image.open(filename)
                    imgTk = ImageTk.PhotoImage(img)
                    # Assign a unique ID to each image
                    image_id = str(uuid.uuid4())
                    # Save the image and its ID to a dictionary
                    image_data = {"image_id": image_id, "image_location": filename}
                    self.uploaded_image = filename
                    self.images.append(imgTk)
                    self.images_save.append(image_data)
                    self.image_info = []

                # Save images to JSON
                self.save_images_to_json()
                # Display the images
                self.load_images_from_json()
            else:
                # Handle the case where no file is selected
                pass
        except:
            pass

    # Save image details to JSON
    def save_images_to_json(self):
        try:
            # Read existing data from the file, if it exists
            existing_data = {}
            if os.path.exists("images.json"):
                with open("images.json", "r") as file:
                    existing_data = json.load(file)

            # Create a list to store the image data
            images_data = []

            if self.uploaded_image != '':
                for image in self.images_save:
                    # Assign a unique ID to each image
                    image_id = str(uuid.uuid4())
                    # New file name with the unique ID
                    new_filename = f"medical_images/{image_id}.png"
                    # Move the image to the "medical_images" directory with the new file name
                    os.rename(image["image_location"], new_filename)
                    # Append the image data to the list
                    images_data.append({"image_id": image_id, "image_location": new_filename})

            # Append new data to the existing data
            existing_data.setdefault("images", []).extend(images_data)

            # Save the combined data to the JSON file
            with open("images.json", "w") as file:
                json.dump(existing_data, file, indent=2)

        except Exception as ex:
            # Handle the exception
            pass

    # Load images from JSON file
    def load_images_from_json(self):
        # Open the images.json file and load the image data
        try:
            with open("images.json", "r") as file:
                data = json.load(file)

            # Clear the current images
            self.images = []
            self.images_save = []
            self.image_info = []

            # Load the images from the image_location in the JSON
            for image_info in data["images"]:
                image_id = image_info["image_id"]
                image_location = image_info["image_location"]
                img = Image.open(image_location)
                img = img.resize((100, 100))
                img = ImageTk.PhotoImage(img)
                self.images.append(img)
                self.images_save.append(image_info)
                image_info_save = ImageInfo(image_id, image_location)
                self.image_info.append(image_info_save)

            self.error_display_img_label.destroy()
            # Display the loaded images
            self.display_images()
        except Exception as ex:
            # print(ex)
            return

    # Display images loaded from JSON
    def display_images(self):
        # Clear the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Display the images in rows of 2
        for i in range(len(self.images)):
            img_label = tk.Label(self.scrollable_frame, image=self.images[i],
                                 highlightbackground="black", highlightthickness=1)
            img_label.grid(row=i // 2, column=i % 2, padx=(10, 0), pady=10, sticky="n")

            # Bind the click event to the image
            img_label.bind("<Button-1>", lambda event, index=i: self.on_image_click(index))

        # Update the scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # On displayed image click
    def on_image_click(self, index):
        # Update image_id and image_locations
        self.image_id = self.image_info[index].image_id
        self.image_location = self.image_info[index].image_location
        lesion_count = self.lesion_counter.get_lesion_count()
        if (lesion_count >= 1 or (len(self.dashed_line_coordinates) >= 1) or (len(self.rectangle_coordinates) >= 1)):
            # Check upload functionality status
            if not self.upload_condition:
                self.load_image()
            else:
                # Popup dialog functionality
                response = messagebox.askyesno("Load New Image",
                                               "Any unsaved work will be lost. Do you want to load a new image?")
                if response:
                    self.lesion_counter.reset_lesion_count()
                    # Load new image functionality
                    self.load_image()
                else:
                    # Do nothing
                    pass
        else:
            self.lesion_counter.reset_lesion_count()
            self.load_image()

    # Load image
    def load_image(self):
        self.clear_lines()
        self.annotation_frame.destroy()
        # User cache
        saveCache = UserCache(self.user_type, self.user_id, self.image_id, self.image_location)
        saveCache.save_to_file()
        # Disable upload functionality
        self.upload_condition = True
        self.annotation_status = True
        self.annotation_functionality()

    # Delete image functionality -> Not used at the moment
    def delete_image(self, i):
        # Remove the image from the list
        deleted_image = self.images_save.pop(i)
        self.images.pop(i)

        # Remove the image from its file location
        image_location = deleted_image["image_location"]
        if os.path.exists(image_location):
            os.remove(image_location)

        # Remove the image data from images.json
        self.remove_image_from_json(deleted_image)

    # Remove image from JSON part of delete image functionality -> Not used at the moment
    def remove_image_from_json(self, deleted_image):
        # Open the images.json file and load the image data
        with open("images.json", "r") as file:
            data = json.load(file)

        # Remove the deleted image from the loaded data
        data["images"] = [image for image in data["images"] if image != deleted_image]

        # Save the updated data to the JSON file
        with open("images.json", "w") as file:
            json.dump(data, file, indent=2)

        # Display the remaining images
        self.display_images()

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

    # Check RADS margin and echo selection
    def colour_rads_check(self):
        line = self.pen_check.read_pen_line()
        type = self.pen_check.read_type_line()
        if self.rect_type != type:
            if line == "Rect":
                self.set_highlight_tool_start()
                colour = self.colour_generator.predefined_colour(type)
                self.rect_pen_colour = colour
                self.rect_type = type
                self.pen_type_lbl.configure(text=f"Pen type: {type}", fg=colour)
                if type == '':
                    self.set_highlight_tool()
        self.after(500, self.colour_rads_check)
