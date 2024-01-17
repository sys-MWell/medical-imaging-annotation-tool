from imports import *


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
        style.configure("Custom.TButton", font=('Helvetica', 14), background="#eeeeee",
                        foreground=UPLOAD_IMG_BTN_COLOUR)
        style.map("Custom.TButton",
                  background=[('active', '#dddddd'), ('pressed', '!disabled', '#999999')],
                  foreground=[('pressed', UPLOAD_IMG_BTN_COLOUR)])

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