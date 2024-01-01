import copy
import os
import shutil
import uuid
import matplotlib
import numpy as np
from PIL import ImageTk, Image
from matplotlib import backend_bases, patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as mlines
import tkinter as tk
from tkinter import Scale
from tkinter import filedialog
from tkinter import ttk, font
import tkinter.messagebox as messagebox
import json

matplotlib.use("TkAgg")

LARGE_FONT = ("Verdana", 12)
MASTER_COLOUR = "#c9c9c9"
BACKGROUND_COLOUR = "#d7d7d9"
FRAME_BACKGROUND_COLOUR = "#edeef0"
SECONDARY_COLOUR = "#f0f0f0"

PEN_TYPE = 'Line'
LESION_COUNT = 0
IMAGE_SELECTED = False

class ImageInfo:
    def __init__(self, image_id, image_location):
        self.image_id = image_id
        self.image_location = image_location


class UserCache:
    def __init__(self, user_id, image_id, image_location):
        self.user_id = user_id
        self.image_id = image_id
        self.image_location = image_location

    def save_to_file(self):
        with open('usercache.txt', 'w') as file:
            file.write(f'user_id: {self.user_id}\n')
            file.write(f'image_id: {self.image_id}\n')
            file.write(f'image_location: {self.image_location}\n')

    def read_from_file(self):
        with open('usercache.txt', 'r') as file:
            lines = file.readlines()
            self.user_id = lines[0].split(': ')[1].strip()
            self.image_id = lines[1].split(': ')[1].strip()
            self.image_location = lines[2].split(': ')[1].strip()


class AnnotationTool(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Set the window size to 720p
        self.geometry("1280x720")

        # Set window position to top-left corner
        self.geometry("+0+0")

        # Set the minimum window size
        self.minsize(1620, 920)

        tk.Tk.iconbitmap(self, default="./img/logo.ico")
        tk.Tk.wm_title(self, "Medical Annotation Tool")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (HomePage, AnnotationPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # Set background colour

        # Create and place an image/logo
        self.img = Image.open('./img/logo.png')
        self.logo = ImageTk.PhotoImage(self.img)
        self.logo_label = tk.Label(self, image=self.logo, bg='#ffffff')
        self.logo_label.pack(pady=10, expand=True)  # Use expand=True to occupy extra space
        # Center the logo
        self.logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # Bind the function to the <Configure> event of the window
        self.bind('<Configure>', self.resize_image)

        # Create a font object
        custom_font = font.Font(family="Helvetica", size=24, weight="bold")

        # Styling for the buttons
        style = ttk.Style()

        # Configure the styling for the custom button
        style.configure("Custom.TButton", font=('Helvetica', 14), background="#eeeeee", foreground="#333333")
        style.map("Custom.TButton",
                  background=[('active', '#dddddd'), ('pressed', '!disabled', '#999999')],
                  foreground=[('pressed', '#333333')])

        # Create and place stylish buttons
        button_frame = tk.Frame(self, bg='#ffffff')
        button_frame.pack(pady=10, expand=True)  # Use expand=True to occupy extra space

        # Set shading effects
        controller.option_add("*TCombobox*Listbox*Background", '#ffffff')
        controller.option_add("*TCombobox*Listbox*Foreground", '#333333')

        # Configure grid weights to make the widgets expand with the window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Initially clear RADS JSON
        try:
            # Check if the 'rads.JSON' file exists
            if os.path.exists('rads.JSON'):
                # Remove the existing 'rads.JSON' file
                os.remove('rads.JSON')
                print("Cleared existing rads.JSON file")
        except Exception as e:
            print(e)

        # Time delay for image logo loading screen
        self.after(0000, lambda: controller.show_frame(AnnotationPage))

    def resize_image(self, event):
        # Get the current window size
        width = event.width
        height = event.height

        # Calculate the maximum width and height for the image
        max_width = int(width * 0.55)  # Change the factor as needed
        max_height = int(height * 0.55)  # Change the factor as needed

        # Calculate the aspect ratio of the original image
        aspect_ratio = self.img.width / self.img.height

        # Calculate the new size for the image while keeping the original aspect ratio
        if max_width / max_height > aspect_ratio:
            new_width = int(max_height * aspect_ratio)
            new_height = max_height
        else:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)

        # Resize the image and update the label
        resized_img = self.img.resize((new_width, new_height))
        self.logo = ImageTk.PhotoImage(resized_img)
        self.logo_label.config(image=self.logo)


class PageFunctionality(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create a list to store the images
        self.graph_frame = None
        self.upload_frame = None
        self.images = []
        self.images_save = []
        self.image_info = []

        # Disable upload functionality condition
        self.upload_condition = False

        # Assigning class variables
        self.lines = []
        self.line_coordinates = []
        self.line_coordinates_save = []
        self.line_coordinates_clear = []
        # Add a list to store rectangle coordinates
        self.rectangle_coordinates = []
        self.rectangle_coordinate = None
        self.pen_type_handler = False

        # Dictionary to store lesion data
        self.lesion_data_dict = {}

        # Undo and redo
        # Master object store - all objects
        self.added_objects = []
        self.removed_objects = []

        # Default ID variables and image locaiton
        self.user_id = "2013"
        self.image_id = None
        self.image_location = './img/blank.png'

        self.annotation_status = False
        self.display_annotation_opts_status = False

        # User input variables for RADS -> When JSON file is loaded
        self.shape_combobox = None
        self.orientation_combobox = None
        self.margin_pattern_var = None
        self.echo_pattern_var = None
        self.posterior_var = None
        self.additional_notes = None

        # Canvas variables
        self.a = None
        self.f = None

        self.combined_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bg=BACKGROUND_COLOUR)
        self.combined_frame.pack(fill="both", padx=10, pady=10, expand=True,
                                 anchor='center')  # Use pack with fill and expand options

        self.upload_functionality()
        self.annotation_functionality()

    # Upload image section functionality
    def upload_functionality(self):
        # Create a frame for the matplotlib graph and toolbar
        self.upload_frame = tk.Frame(self.combined_frame, bg=FRAME_BACKGROUND_COLOUR, width=250, height=680)
        self.upload_frame.pack(side="left", fill="both", expand=False)  # Use pack with fill and expand options

        # Set background color
        self.configure(bg=MASTER_COLOUR)

        label = tk.Label(self.upload_frame, text="Image Upload and Selection", font=("Helvetica", 16),
                         bg=SECONDARY_COLOUR)
        label.pack(pady=10, padx=10)

        # Create a button to upload images with a modern style
        upload_button = ttk.Button(self.upload_frame, text="Upload Images", command=self.upload_images,
                                   style="Custom.TButton")
        upload_button.pack(pady=10)

        # Please select image label
        select_img_label = tk.Label(self.upload_frame, text="Please select an image...", font=("Helvetica", 12),
                                    bg=SECONDARY_COLOUR)
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

        label = tk.Label(self.annotation_frame, text="Image Annotation", font=("Helvetica", 16), bg=SECONDARY_COLOUR)
        label.pack(side="top", anchor='n', pady=10, padx=10)

        self.graph_frame = tk.Frame(self.annotation_frame)
        self.graph_frame.pack(anchor="n", fill="both", expand=True,
                              pady=0, padx=20)  # Use pack with fill and expand options

        # Radio btns frame
        self.radio_btn_frame = tk.Frame(self.graph_frame, highlightbackground="black", highlightthickness=1)
        self.radio_btn_frame.pack(side="top", pady=0, padx=10)
        self.radio_ultrasound_type_var = tk.StringVar(value="")

        # Ultra sound type radio button selection
        if self.upload_condition:
            # Ultra sound Type Radio Button
            # Configure the style for the Radiobuttons
            style_upload = ttk.Style()
            style_upload.configure("Custom.TRadiobutton", background=FRAME_BACKGROUND_COLOUR,
                                   foreground="black", padding=10, borderwidth=1, relief="solid")

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
            global IMAGE_SELECTED
            IMAGE_SELECTED = True
            # Load the image and resize it
            home_img = Image.open("./img/restart.png")
            home_img = home_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            home_button_image = ImageTk.PhotoImage(home_img)
            # Create the ttk.Button with the resized image and custom style
            home_button = tk.Button(matplotlib_btn_frame, image=home_button_image, compound="top",
                                    command=self.home_action, width=50, height=50, bg=self.btn_colour)
            home_button.image = home_button_image  # Store the image as an attribute of the button
            home_button.pack(side="left", padx=5)  # Pack the button to the left with padding
            # Bind events to show and hide tooltips

            # Load the image and resize it
            pan_img = Image.open("./img/move.png")
            pan_img = pan_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            pan_button_image = ImageTk.PhotoImage(pan_img)
            # Create the ttk.Button with the resized image and custom style
            pan_button = tk.Button(matplotlib_btn_frame, image=pan_button_image, compound="top",
                                   command=self.pan_action, width=50, height=50, bg=self.btn_colour)
            pan_button.image = pan_button_image  # Store the image as an attribute of the button
            pan_button.pack(side="left", padx=5)  # Pack the button to the left with padding
            # Bind events to show and hide tooltips

            # Load the image and resize it
            zoom_img = Image.open("./img/zoom.png")
            zoom_img = zoom_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            zoom_button_image = ImageTk.PhotoImage(zoom_img)
            # Create the ttk.Button with the resized image and custom style
            zoom_button = tk.Button(matplotlib_btn_frame, image=zoom_button_image, compound="top",
                                    command=self.zoom_action, width=50, height=50, bg=self.btn_colour)
            zoom_button.image = zoom_button_image  # Store the image as an attribute of the button
            zoom_button.pack(side="left", padx=5)  # Pack the button to the left with padding

            separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
            separator_label.pack(side="left", padx=5)

            # Load the image and resize it
            options_img = Image.open("./img/options.png")
            options_img = options_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            options_button_image = ImageTk.PhotoImage(options_img)
            # Create the ttk.Button with the resized image and custom style
            options_button = tk.Button(matplotlib_btn_frame, image=options_button_image, compound="top",
                                       command=lambda: self.display_annotations(), width=50, height=50,
                                       bg=self.btn_colour)
            options_button.image = options_button_image  # Store the image as an attribute of the button
            options_button.pack(side="left", padx=5)  # Pack the button to the left with padding

            clear_img = Image.open("./img/clear.png")
            clear_img = clear_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            clear_button_image = ImageTk.PhotoImage(clear_img)
            # Create the ttk.Button with the resized image and custom style
            clear_button = tk.Button(matplotlib_btn_frame, image=clear_button_image, compound="top",
                                     command=lambda: self.clear_lines(), width=50, height=50,
                                     bg=self.btn_colour)
            clear_button.image = clear_button_image  # Store the image as an attribute of the button
            clear_button.pack(side="left", padx=5)  # Pack the button to the left with padding

            save_img = Image.open("./img/save.png")
            save_img = save_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            save_button_image = ImageTk.PhotoImage(save_img)
            # Create the ttk.Button with the resized image and custom style
            save_button = tk.Button(matplotlib_btn_frame, image=save_button_image, compound="top",
                                    command=lambda: self.save_confirmation(), width=50, height=50,
                                    bg=self.btn_colour)
            save_button.image = save_button_image  # Store the image as an attribute of the button
            save_button.pack(side="left", padx=5)  # Pack the button to the left with padding

            # Add a separator
            separator_label = tk.Label(matplotlib_btn_frame, text="|", font=("Helvetica", 8), fg="black")
            separator_label.pack(side="left", padx=5)

            undo_img = Image.open("./img/undo.png")
            undo_img = undo_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            undo_button_image = ImageTk.PhotoImage(undo_img)
            # Create the ttk.Button with the resized image and custom style
            undo_button = tk.Button(matplotlib_btn_frame, image=undo_button_image, compound="top",
                                    command=lambda: self.undo_object(), width=50, height=50,
                                    bg=self.btn_colour)
            undo_button.image = undo_button_image  # Store the image as an attribute of the button
            undo_button.pack(side="left", padx=5)  # Pack the button to the left with padding

            redo_img = Image.open("./img/redo.png")
            redo_img = redo_img.resize((50, 50))  # Resize the image to 50x50 pixels
            # Convert the image to a format compatible with tkinter
            redo_button_image = ImageTk.PhotoImage(redo_img)
            # Create the ttk.Button with the resized image and custom style
            redo_button = tk.Button(matplotlib_btn_frame, image=redo_button_image, compound="top",
                                    command=lambda: self.redo_object(), width=50, height=50,
                                    bg=self.btn_colour)
            redo_button.image = redo_button_image  # Store the image as an attribute of the button
            redo_button.pack(side="left", padx=5)  # Pack the button to the left with padding

        self.display_annotation_opts(self.options_frame)

        self.generate_matplotlib(self.image_location)

    # Undo button functionality
    def undo_object(self):
        global LESION_COUNT
        if self.added_objects:
            last_object = self.added_objects.pop()
            if 'line_obj' in last_object:
                line_obj = last_object['line_obj']
                last_object_line = self.line_coordinates.pop()
                self.line_coordinates_save.pop()
                self.line_coordinates_clear.pop()
                last_object_line["line_obj"].remove()
                self.removed_objects.append(last_object_line)
                LESION_COUNT -= 1
            elif 'rectangle_obj' in last_object:
                rectangle_obj = last_object['rectangle_obj']
                last_object_rect = self.rectangle_coordinates.pop()
                last_object_rect["rectangle_obj"].remove()
                self.removed_objects.append(last_object_rect)
            else:
                print("Unknown object type")
            self.f.canvas.draw()

    # Redo button functionality
    def redo_object(self):
        global LESION_COUNT
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
                LESION_COUNT += 1
            elif 'rectangle_obj' in restored_object:
                rectangle_obj = restored_object['rectangle_obj']
                self.a.add_patch(rectangle_obj)
                self.added_objects.append(restored_object)
                self.rectangle_coordinates.append(restored_object)
        self.f.canvas.draw()

    # Matplotlib canvas
    def generate_matplotlib(self, image_location):
        # Add image to Matplotlib
        img_arr = mpimg.imread(image_location)
        # Figure
        f = Figure(figsize=(10, 8), dpi=100, facecolor=SECONDARY_COLOUR)
        # Axis
        a = f.add_subplot()
        a.margins(0)
        a.imshow(img_arr)
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

        # Reduce the padding between the canvas and the toolbar
        canvas.get_tk_widget().pack_configure(pady=0)

        if self.annotation_status:
            # Connect the 'button_press_event' to the 'pressed' function
            canvas.mpl_connect('button_press_event', self.pressed)

            self.move = None
            # Connect the 'motion_notify_event' to the 'moved' functions
            canvas.mpl_connect('motion_notify_event', self.moved)

            self.focus_set()  # Set the focus to the graph frame
            self.bind('<KeyPress-p>',
                      self.key_press_handler)  # Bind the key press event to the key_press_handler function
            self.update_variable()

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

        # Create a Combobox widget for colour selection
        self.colour_selection = ttk.Combobox(self.button_frame, values=['red', 'green', 'blue', 'yellow'])
        self.colour_selection.set('red')
        self.colour_selection.pack(side="left", padx=5, pady=5)  # Pack the combobox to the left with padding
        self.colour_selection.bind("<<ComboboxSelected>>",
                                   lambda event: self.change_colour())  # Bind the selection event to change_colour

        # Create a Combobox widget for line width selection
        self.width_scale = ttk.Combobox(self.button_frame, values=list(range(1, 11)), state="readonly")
        self.width_scale.set(2)
        self.width_scale.pack(side="left", padx=5, pady=5)  # Pack the combobox to the left with padding

        # Create a button to load and display the saved coordinates
        button_load = ttk.Button(self.button_frame, text="Load Lines", command=self.load)
        button_load.pack(side="left", padx=5, pady=5)  # Pack the button to the left with padding

        self.pen_type_lbl = tk.Label(self.button_frame, text="Pen type: Line", fg="red")
        self.pen_type_lbl.pack(side="bottom", padx=5, pady=5)

        # Initialize rectangle drawing mode variable
        self.rectangle_mode = False
        self.rectangle_drawing = False

    # If mouse is clicked on canvas, drawing lesions
    def pressed(self, event):
        global LESION_COUNT
        self.focus_set()  # Set the focus to the graph frame
        self.bind('<KeyPress-p>',
                  self.key_press_handler)  # Bind the key press event to the key_press_handler function
        if PEN_TYPE == 'Rect':
            self.pen_type_lbl.configure(text="Pen type: Irregular", fg="green")
            self.rectangle_mode = True
        else:
            self.pen_type_lbl.configure(text="Pen type: Line", fg="red")
            # LINE BELOW CONTROLS THE LOOP FOR RECTANGLE MODE, CHANGING IT TO TRUE KEEPS MAKING RECTS
            self.rectangle_mode = False
            # Connect the 'motion_notify_event' to the 'moved' function
            self.move = self.f.canvas.mpl_connect('motion_notify_event', self.moved)

        state = self.toolbar.mode
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
                        # Create a green rectangle
                        try:
                            self.rect = patches.Rectangle((event.xdata, event.ydata), 0, 0, linewidth=2, edgecolor='g',
                                                          facecolor='none')
                            self.a.add_patch(self.rect)
                        except:
                            pass
                        # Set the rectangle drawing flag to True
                        self.rectangle_drawing = True
                        self.cid = self.f.canvas.mpl_connect('motion_notify_event', self.draw_rectangle)
                else:
                    # Check if left mouse button is pressed
                    if event.button == 1:
                        LESION_COUNT += 1
                        # Clear redo
                        self.removed_objects = []
                        # Create a new line object and store it in the lines list
                        line = self.a.plot([], [], color=self.colour, linewidth=2)
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

    # If pen for drawing lesions is moved
    def moved(self, event):
        state = self.toolbar.mode
        if state == '':
            # Check if left mouse button is pressed and lines list is not empty
            if event.button == 1 and self.lines:
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

    # Draw irregular lesion identifier
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
                                                             "height": height}}
            else:
                self.f.canvas.mpl_disconnect(self.cid)
                self.rectangle_mode = False
                self.rectangle_drawing = False

    # Handle P key press
    def key_press_handler(self, event):
        global PEN_TYPE
        if PEN_TYPE == 'Line':
            if self.pen_type_handler:
                PEN_TYPE = "Rect"
                self.pen_type_lbl.configure(text="Pen type: Irregular", fg="green")
        elif PEN_TYPE == 'Rect':
            self.pen_type_handler = True
            PEN_TYPE = "Line"
            self.pen_type_lbl.configure(text="Pen type: Line", fg="red")

    # Update pen type text
    def update_variable(self):
        try:
            global PEN_TYPE
            if PEN_TYPE == 'Line':
                self.pen_type_lbl.configure(text="Pen type: Line", fg="red")
            elif PEN_TYPE == 'Rect':
                self.pen_type_lbl.configure(text="Pen type: Irregular", fg="green")
            # Call the function again after a delay (in milliseconds)
            self.after(1000, self.update_variable)
        except:
            pass

    # Change pen colour
    def change_colour(self):
        # Get the selected colour from the combobox
        new_colour = self.colour_selection.get()
        # Update the line colour and line width for new drawings
        self.colour = new_colour
        self.width = self.width_scale.get()

        # Connect the 'button_press_event' to the 'pressed' function
        self.f.canvas.mpl_disconnect(self.cid)
        self.cid = self.f.canvas.mpl_connect('button_press_event', self.pressed)

        self.lines = []  # Clear the existing lines list
        self.line_coordinates = []  # Clear the existing line_coordinates list

        # Redraw the canvas to update the plot
        self.f.canvas.draw()

    # Clear all canvas drawings functionality
    def clear_lines(self):
        global LESION_COUNT
        # Clear all lines drawn on the matplotlib image
        for line_info in self.line_coordinates_clear:
            line = line_info["line_obj"]
            line.remove()  # Remove the line object

        for rect in self.a.patches:
            rect.remove()  # Remove the rectangle patch

        self.added_objects = []
        self.removed_objects = []
        LESION_COUNT = 0

        self.lines = []  # Clear the lines list
        self.line_coordinates = []  # Clear the line_coordinates list
        self.line_coordinates_save = []  # Clear the line_coordinates_save list
        self.line_coordinates_clear = []  # Clear the line_coordinates_clear list
        self.rectangle_coordinates = []
        self.f.canvas.draw()  # Redraw the canvas to update the plot

    # Message box, confirming save
    def save_confirmation(self):
        response = messagebox.askyesno("Save",
                                       "Are you sure you want to save?")
        if response:
            # Save functionality
            self.save()
        else:
            # Do nothing
            pass

    # Save ALL to JSON - main save for annotation ultrasound and RADS
    def save(self):
        print(self.radio_ultrasound_type_var.get())
        self.load_rads_data()
        if self.lines and (self.line_coordinates_save or self.rectangle_coordinates):
            # Convert rectangle coordinates to desired format
            converted_rectangles = []
            for rectangle_info in self.rectangle_coordinates:
                rectangle_obj = rectangle_info["rectangle_obj"]
                if rectangle_obj is not None:  # Add a check for None
                    rectangle = {
                        "x": rectangle_info["coordinates"]["x"],
                        "y": rectangle_info["coordinates"]["y"],
                        "width": rectangle_obj.get_width(),
                        "height": rectangle_obj.get_height()
                    }
                    converted_rectangles.append(rectangle)

            # Initialize the list to store all annotations
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
                "user_id": self.user_id,
                "coordinates": [],
                "irregular": converted_rectangles,  # Use the converted_rectangles
                "rads:": lesions
            }

            unique_lines = set()
            for line_info in self.line_coordinates_save:
                line_obj = line_info["line_obj"]
                if line_obj not in unique_lines:
                    unique_lines.add(line_obj)
                    line_data = {
                        "lesions": [],
                        "width": line_obj.get_linewidth(),
                        "colour": line_obj.get_color()
                    }
                    coordinates = line_info["coordinates"]
                    if coordinates:
                        for coord_list in coordinates:
                            line_data["lesions"].append(f"{coord_list}")
                        annotation["coordinates"].append(line_data)

            try:
                with open("annotations.json", "r") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {"images": []}

            # Check if the image_id already exists in the data
            image_exists = False
            for image in data["images"]:
                if image["image_id"] == self.image_id:
                    image_exists = True
                    image["ultra_sound"] = self.radio_ultrasound_type_var.get()
                    image["annotations"] = [annotation]  # Override existing annotations
                    break

            if not image_exists:
                image_data = {
                    "image_id": self.image_id,
                    "ultra_sound": self.radio_ultrasound_type_var.get(),
                    "annotations": [annotation]
                }
                data["images"].append(image_data)

            with open("annotations.json", "w") as file:
                json.dump(data, file, indent=2)

    # Load JSON file -> Coordinates and RADS
    def load(self):
        self.clear_lines()
        try:
            with open("annotations.json", "r") as file:
                data = json.load(file)
                for image in data["images"]:
                    if image["image_id"] == self.image_id:
                        for annotation in image["annotations"]:
                            # Redraw the rectangles
                            if "irregular" in annotation:
                                rect_data_list = annotation["irregular"]
                                for rect_data in rect_data_list:
                                    x = rect_data["x"]
                                    y = rect_data["y"]
                                    width = rect_data["width"]
                                    height = rect_data["height"]

                                    # Create a Rectangle object from the loaded data
                                    rect_obj = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='g',
                                                                 facecolor='none')

                                    # Store the rectangle object along with its coordinates
                                    rect_info = {"rectangle_obj": rect_obj, "coordinates": rect_data}

                                    # Append to the rectangle_coordinates list
                                    self.rectangle_coordinates.append(rect_info)
                                    # Add the rectangle patch to the Axes object
                                    self.a.add_patch(rect_obj)
                            for line_data in annotation["coordinates"]:
                                line = line_data["lesions"]
                                color = line_data["colour"]
                                width = line_data["width"]
                                line_info = {"line_obj": None, "coordinates": []}
                                for coord_list in line:
                                    coords = eval(coord_list)  # Convert the string back to a tuple
                                    if coords is None:
                                        continue  # Skip if coords is None
                                    x_coords = [x for x, _ in coords]
                                    y_coords = [y for _, y in coords]
                                    line_obj = mlines.Line2D(x_coords, y_coords, color=color, linewidth=width)
                                    self.a.add_line(line_obj)
                                    line_info["line_obj"] = line_obj
                                    line_info["coordinates"].append(coords)
                                self.line_coordinates.append(line_info)
                                self.line_coordinates_save.append(line_info)
                                self.line_coordinates_clear.append(line_info)
                        self.f.canvas.draw()
                        break
        except FileNotFoundError:
            # Handle the case when the file is not found
            pass

    # Load rads data from JSON
    def load_rads_data(self):
        # Clear dictionary
        self.lesion_data_dict = {}
        # Retrieve lesion data from rads.JSON
        try:
            with open('rads.JSON', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        for lesion_key, lesion_data in data.items():
            # Extract information for each lesion
            shape_combobox = lesion_data.get("masses", {}).get("shape", "")
            orientation_combobox = lesion_data.get("masses", {}).get("Orientation", "")
            margin_selection = lesion_data.get("masses", {}).get("Margin", "")
            margin_pattern_var = lesion_data.get("masses", {}).get("Margin options", "")
            echo_pattern_var = lesion_data.get("masses", {}).get("Echo pattern", "")
            posterior_var = lesion_data.get("masses", {}).get("Posterior features", "")
            additional_notes = lesion_data.get("masses", {}).get("Additional notes", "")

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

            # Debug print
            # print(f"Lesion {lesion_key}:")
            # print(shape_combobox)
            # print(orientation_combobox)
            # print(margin_selection)
            # print(margin_pattern_var)
            # print(echo_pattern_var)
            # print(posterior_var)
            # print(additional_notes)

    # Upload images functionality
    def upload_images(self):
        try:
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
            # Create a list to store the image data
            images_data = []
            for image in self.images_save:
                # Assign a unique ID to each image
                image_id = str(uuid.uuid4())
                # New file name with the unique ID
                new_filename = f"medical_images/{image_id}.png"
                # Move the image to the "medical_images" directory with the new file name
                os.rename(image["image_location"], new_filename)
                # Append the image data to the list
                images_data.append({"image_id": image_id, "image_location": new_filename})

            # Create a dictionary with the list of images
            data = {"images": images_data}

            # Save the data to a JSON file
            with open("images.json", "w") as file:
                json.dump(data, file, indent=2)
        except Exception as ex:
            print(ex)

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
            print(ex)
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
        global LESION_COUNT
        if LESION_COUNT >= 1:
            # Check upload functionality status
            if not self.upload_condition:
                self.load_image()
            else:
                # Popup dialog functionality
                response = messagebox.askyesno("Load New Image",
                                               "Any unsaved work will be lost. Do you want to load a new image?")
                if response:
                    LESION_COUNT = 0
                    # Load new image functionality
                    self.load_image()
                else:
                    # Do nothing
                    pass
        else:
            LESION_COUNT = 0
            self.load_image()

    # Load image
    def load_image(self):
        self.clear_lines()
        self.annotation_frame.destroy()
        # User cache
        saveCache = UserCache(self.user_id, self.image_id, self.image_location)
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

# Rads page functionality
class RadsFunctionality(tk.Frame):
    def __init__(self, parent=None, controller=None):
        tk.Frame.__init__(self, parent, bg=MASTER_COLOUR)

        self.margin_vars = {}
        self.posterior_vars = {}
        self.controller = controller

        style = ttk.Style()
        style.configure("Custom.TCombobox", font=('Helvetica', 12), padding=5, background="white",
                        fieldbackground="white")
        style.configure("Custom.TRadiobutton", font=('Helvetica', 12), background=MASTER_COLOUR)
        style.configure("Custom.TCheckbutton", font=('Helvetica', 12), background=MASTER_COLOUR)

        # Declare variables
        self.user_id = ''
        self.image_id = ''
        self.image_location = ''
        self.additional_notes = ''

        self.rads_load_status = False
        self.image_upload_status = False
        self.initial_load = False
        self.unlock_rads()
        self.num_notebooks = 1
        self.masses_frames = []
        # Initialize the list to store removed notebook states
        self.removed_notebooks = []
        self.page_data = {}

        self.lesions = 0

        # Checkbox option variables
        self.echo_pattern_var = tk.StringVar()
        self.margin_pattern_var = tk.StringVar()

        self.master_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.master_frame.pack(pady=10, padx=10, fill="both", expand=1)

        # Prevent the frame from growing beyond a certain width
        self.master_frame.pack_propagate(False)
        self.master_frame.config(width=350)  # Set the maximum width
        # Bind the <Configure> event to a function that will update the size of the content_frame when the window is resized

        # Set the title label
        title_label = ttk.Label(self.master_frame, text="RADS", font=("Helvetica", 16))
        title_label.pack(pady=10)

        # Create frame for form
        form_frame = ttk.Frame(self.master_frame)
        form_frame.pack(pady=10, padx=10, fill="both", expand=1)
        self.form_frame = form_frame

        #tk.Button(form_frame, text="Undo", command=self.undo_remove).pack()

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
            last_page_index = self.notebook.index("end") - 1
            self.notebook.forget(last_page_index)
            self.num_notebooks -= 1
            # Delete entry from rads.JSON
            page_num = int(self.notebook.index('end') +1)
            #print(f"Remove page: {page_num}")
            self.delete_entry_from_json(self.notebook.index("end") +1)
            if page_num in self.page_data:
                self.page_data.pop(page_num)
                #print(f"Page {page_num} deleted from self.page_data")
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

        # Store variables associated with the current page
        self.page_data[page_num] = {
            "shape_combobox": tk.StringVar(),
            "orientation_combobox": tk.StringVar(),
            "margin_pattern_var": tk.StringVar(),
            "echo_pattern_var": tk.StringVar(),
            "posterior_var": tk.StringVar(),
            "additional_notes": tk.StringVar(),
            "margin_pattern_selected": [],
            "echo_pattern_selected": []
        }

        # Subsection: Shape
        shape_label = ttk.Label(masses_frame, text="Shape")
        shape_label.grid(row=1, column=0, sticky="w")
        shape_options = ["Oval", "Round", "Irregular"]
        self.shape_combobox = ttk.Combobox(masses_frame, values=shape_options, state="readonly",
                                           textvariable=self.page_data[page_num]["shape_combobox"])
        self.shape_combobox.grid(row=1, column=1, pady=3)
        # Bind the function to the combobox selection event
        self.shape_combobox.bind("<<ComboboxSelected>>", lambda event: self.on_shape_select(event, page_num))

        # Subsection: Orientation
        orientation_label = ttk.Label(masses_frame, text="Orientation")
        orientation_label.grid(row=2, column=0, sticky="w")
        orientation_options = ["Parallel", "Not Parallel"]
        self.orientation_combobox = ttk.Combobox(masses_frame, values=orientation_options, state="readonly",
                                                 textvariable=self.page_data[page_num]["orientation_combobox"])
        self.orientation_combobox.grid(row=2, column=1, pady=3)
        self.orientation_combobox.bind("<<ComboboxSelected>>", self.save_to_json(page_num))

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

        # Initially disable update_not_circumscribed_options until selection has been made
        self.update_not_circumscribed_options(page_num)

        # Store the reference to margin_var along with the page_num
        self.margin_vars[page_num] = self.margin_var  # Store the margin_var in a dictionary

        # Subsection: Echo Pattern
        echo_pattern_label = ttk.Label(masses_frame, text="Echo Pattern")
        echo_pattern_label.grid(row=10, column=0, sticky="w")
        echo_pattern_options = ["Anechoic", "Hyperechoic", "Complex cystic and solid", "Hypoechoic", "Isoechoic",
                                "Heterogeneous"]
        for i, option in enumerate(echo_pattern_options):
            check = tk.Checkbutton(masses_frame, text=option,
                                   command=lambda option=option: self.select_option_echo(page_num, option))
            check.grid(row=10 + i, column=1, sticky="w", pady=2)

        # Subsection: Posterior Features
        self.posterior_var = tk.StringVar()
        posterior_features_label = ttk.Label(masses_frame, text="Posterior Features")
        posterior_features_label.grid(row=17, column=0, sticky="w")
        posterior_features_options = ["No posterior features", "Enhancement", "Shadowing", "Combined patterns"]
        for i, option in enumerate(posterior_features_options):
            radio = ttk.Radiobutton(masses_frame, text=option, variable=self.posterior_var, value=option,
                                    command=lambda: self.save_to_json(page_num))
            radio.grid(row=17 + i, column=1, sticky="w", pady=2)

        # Store posterior data for page
        self.posterior_vars[page_num] = self.posterior_var  # Store the margin_var in a dictionary

        # Additional frame entry box
        # Create a scrollable text input box
        text_box = tk.Text(additional_frame, width=40)
        text_box.pack(pady=5, padx=5)
        text_box.bind("<KeyRelease>", lambda event: self.text_box_handler(page_num, event))

        # Return at end
        return masses_frame

    def on_margin_selected(self, page_num):
        selected_value = self.margin_var.get()
        # Clear check buttons if Circumscribed is selected
        if selected_value == "Circumscribed":
            for check_button in self.not_circumscribed_checkbuttons:
                check_button.deselect()

        # This function is a wrapper that calls both functions
        self.save_to_json(page_num)
        self.update_not_circumscribed_options(page_num)

    # Margin option selections
    def select_option_margin(self, page_num, option):
        # Organises non circumscribed options
        if option in self.page_data[page_num]["margin_pattern_selected"]:
            self.page_data[page_num]["margin_pattern_selected"].remove(option)
        else:
            self.page_data[page_num]["margin_pattern_selected"].append(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["margin_pattern_var"].set(", ".join(self.page_data[page_num]["margin_pattern_selected"]))
        self.save_to_json(page_num)

    # Echo option selections
    def select_option_echo(self, page_num, option):
        # Organises echo options
        if option in self.page_data[page_num]["echo_pattern_selected"]:
            self.page_data[page_num]["echo_pattern_selected"].remove(option)
        else:
            self.page_data[page_num]["echo_pattern_selected"].append(option)

        # Update the StringVar to reflect the selected options
        self.page_data[page_num]["echo_pattern_var"].set(", ".join(self.page_data[page_num]["echo_pattern_selected"]))
        self.save_to_json(page_num)

    # Word limit for text_box
    def text_box_handler(self, page_num, event):
        self.additional_notes = event.widget.get("1.0", "end-1c")
        text = event.widget.get("1.0", "end-1c")  # Get the text content
        words = text.split()  # Split the text into words
        if len(words) > 100:  # Check if the word limit is exceeded
            event.widget.delete("end-2c")  # Remove the extra words
        self.page_data[page_num]["additional_notes"].set(self.additional_notes)
        self.save_to_json(page_num)

    # Function to handle shape selection
    def on_shape_select(self, event, page_num):
        if self.shape_combobox.get() == "Irregular":
            # Add your logic here for when "Irregular" is selected
            global PEN_TYPE
            PEN_TYPE = 'Rect'
            messagebox.showinfo("Pen change",
                                "Highlighting irregular lesions.\nPress 'P' key to "
                                "activate/deactivate")  # Display message for type of pen
        else:
            PEN_TYPE = 'Line'
            messagebox.showinfo("Pen change",
                                "Drawing lesions")  # Display message for type of pen
        self.save_to_json(page_num)

    # Function to update the state of not_circumscribed_options based on the selected radio button
    def update_not_circumscribed_options(self, page_num):
        try:
            margin_var = self.margin_vars.get(page_num)

            if margin_var and margin_var.get() == "Not Circumscribed":
                state = "normal"  # Enable the checkboxes
            else:
                state = "disabled"  # Disable the checkboxes

            # Convert page_num to string
            page_str = str(page_num)

            # Print debug information
            #print("Searching for page:", page_str)
            #print("Masses frames:", self.masses_frames)

            # Get the masses_frame for the specific page_num
            # masses_frame_dict = next(item for item in self.masses_frames if page_str in item)

            # Array starts at 0, minus 1 to get correct order
            # Debug
            #print("Masses frames dict:", self.masses_frames[page_num-1])
            masses_frame = self.masses_frames[page_num-1]

            # Loop through the not_circumscribed_options checkboxes and set their state
            for child in masses_frame.winfo_children():
                if child.cget("text") in self.not_circumscribed_options:
                    child.configure(state=state)
        except Exception as e:
            print(e)
            pass

    # Unlock rads functionality
    def unlock_rads(self):
        user_cache = UserCache(None, None, None)  # Initialize with default values
        user_cache.read_from_file()
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

    # Disable frame -> Input functions disabled
    def disable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Text, tk.Checkbutton, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton,
                                  tk.Radiobutton, ttk.Radiobutton,
                                  tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='disabled')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.disable_frame(child)

    # Enable frame -> Input functions enabled
    def enable_frame(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Text, tk.Checkbutton, tk.Button, ttk.Button, ttk.Combobox, tk.Checkbutton,
                                  tk.Radiobutton, ttk.Radiobutton,
                                  tk.Listbox, tk.Spinbox, tk.Text, Scale)):
                child.configure(state='normal')
            elif isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.enable_frame(child)

    # Save RADS details to JSON -> Every input saved
    def save_to_json(self, page_num):
        # Check page data options - debug
        # try:
        #     print(f"Selected Shape Option: {self.page_data[page_num]['shape_combobox'].get()}")
        #     print(f"Selected Orientation Option: {self.page_data[page_num]['orientation_combobox'].get()}")
        #     margin_var = self.margin_vars.get(page_num)
        #     print(f"Selected Margin Option: {margin_var.get()}")
        #     print(f"Selected Not Circumscribed Option: {self.page_data[page_num]['margin_pattern_var'].get()}")
        #     print(f"Selected Echo Option: {self.page_data[page_num]['echo_pattern_var'].get()}")
        #     posterior_var = self.posterior_vars.get(page_num)
        #     print(f"Selected Posterior Option: {posterior_var.get()}")
        # except Exception as e:
        #     print(e)

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
                    page_entry = {
                        "masses": {
                            "shape": page_data["shape_combobox"].get(),
                            "Orientation": page_data["orientation_combobox"].get(),
                            "Margin": margin_var.get(),
                            "Margin options": page_data["margin_pattern_var"].get(),
                            "Echo pattern": page_data["echo_pattern_var"].get(),
                            "Posterior features": posterior_var.get(),
                            "Additional notes": page_data["additional_notes"].get()
                        }
                    }

                    # Add the page entry to the data dictionary
                    data[f"Lesion_{page_num}"] = page_entry

                # Save the updated data to the JSON file
                with open('rads.JSON', 'w') as file:
                    json.dump(data, file, indent=4)

                # Debug
                #print("Data saved to rads.JSON")
            except Exception as e:
                pass
                #print(f"Here? {e}")
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
            #print(f"Entry {entry_key} deleted from rads.JSON")
        except Exception as e:
            # Print any exceptions that may occur during the process
            print(e)

    # Check annotation variables -> If image loaded, how many lesions
    def image_checks(self):
        try:
            global LESION_COUNT
            global IMAGE_SELECTED
            if (LESION_COUNT > 0):
                if not self.initial_load:
                    self.enable_rads()
                    self.initial_load = True
                if LESION_COUNT != self.notebook.index("end"):
                    if LESION_COUNT > self.notebook.index("end"):
                        # print("add")
                        # print(self.notebook.index("end"))
                        self.add_new_page()
                    if LESION_COUNT < self.notebook.index("end"):
                        ''' If lesion is less then count of notebooks (pages) then one page needs removed (has been
                        removed)'''
                        self.remove_notebook()
            else:
                if LESION_COUNT == 0:
                    # Disable RADS form)
                    self.disable_frame(self.rads_massses_frame)
                    self.disable_frame(self.rads_additional_frame)
                    self.initial_load = False
                    #print(f"num notebooks: {self.num_notebooks}")
                    self.remove_all_notebooks()

            if (IMAGE_SELECTED == True):
                if not self.image_upload_status:
                    self.image_upload_status = True
                    for child in self.masses_frame.winfo_children():
                        if child.cget("text") in self.not_circumscribed_options:
                            child.configure(state="disabled")
            else:
                self.image_upload_status = False
                self.disable_frame(self.masses_frame)
                self.disable_frame(self.additional_frame)
            self.after(500, self.image_checks)
        except:
            pass

# Annotation page display
class AnnotationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')

        # Create a frame to hold the combined functionalities
        combined_frame = tk.Frame(self, highlightbackground="black", highlightthickness=2)
        combined_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Use pack with fill and expand options

        # Add upload/annotation functionality to the left of the combined page
        page_one = PageFunctionality(combined_frame, controller)
        page_one.pack(side="left", fill="both", expand=True)  # Use pack with fill and expand options

        # Add RADS functionality to the right of the combined page
        page_two = RadsFunctionality(combined_frame, controller)
        page_two.pack(side="right", fill="both", expand=False)  # Use pack with fill and expand options

        # Bind the <Configure> event to a function that will update the size of the pages when the window is resized
        combined_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        # Update the size of the pages when the window is resized
        self.update_idletasks()

# Load application
app = AnnotationTool()
plt.margins(x=0)
app.mainloop()
