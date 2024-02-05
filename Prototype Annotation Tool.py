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

        for F in (HomePage, AccountPage, AnnotationPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

        # Load AnnotationPage only when specified
        if cont == AnnotationPage:
            frame.load_content()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')  # Set background colour

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
        self.after(3000, lambda: controller.show_frame(AccountPage))

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


class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')  # Set background color

        # Logo
        self.img = Image.open('./img/logo.png')
        self.logo = ImageTk.PhotoImage(self.img)
        self.logo_label = tk.Label(self, image=self.logo, bg='#ffffff')
        self.logo_label.pack(pady=10, expand=True)  # Use expand=True to occupy extra space

        # Title Label
        title_label = tk.Label(self, text="Select Account Type", font=("Helvetica", 24, "bold"), bg='#ffffff')
        title_label.pack(side="top", anchor="n", pady=2)  # Reduced the vertical padding

        # Frame for Buttons
        button_frame = tk.Frame(self, bg='#ffffff')
        button_frame.pack(side="top", anchor="n", expand=True)

        # Styling for the buttons specific to this page
        account_button_style = ttk.Style()
        account_button_style.configure("AccountPage.TButton", font=('Helvetica', 18, 'bold'),
                                       background="#f2f2f2", foreground="#333333",
                                       width=20, padding=(15, 15), bordercolor="#999999",
                                       lightcolor="#999999", darkcolor="#999999")

        account_button_style.map("AccountPage.TButton",
                                background=[('active', '#d9d9d9'), ('pressed', '!disabled', '#cccccc')],
                                foreground=[('pressed', '#333333')])

        # Doctor Button
        doctor_button = ttk.Button(button_frame, text="Doctor", style="AccountPage.TButton",
                                   command=lambda: self.on_button_click(controller, "Doctor"))
        doctor_button.grid(row=0, column=0, padx=10, pady=5)  # Reduced vertical padding

        # AI Researcher Button
        ai_researcher_button = ttk.Button(button_frame, text="AI Researcher", style="AccountPage.TButton",
                                          command=lambda: self.on_button_click(controller, "AI Researcher"))
        ai_researcher_button.grid(row=0, column=1, padx=10, pady=5)  # Reduced vertical padding

        # Configure grid weights to make the widgets expand with the window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

    def on_button_click(self, controller, account_type):
        # Handle button click event
        if account_type == "Doctor":
            saveCache = UserCache("1", "", "", "")
        elif account_type == "AI Researcher":
            saveCache = UserCache("2", "", "", "")
        else:
            pass

        # Save user cache credentials and load Annotation Page
        saveCache.save_to_file()
        controller.show_frame(AnnotationPage)


# Annotation page display
class AnnotationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')

        # Set a flag to track whether content is loaded
        self.content_loaded = False

        # Bind the <Configure> event to a function that will update the size of the pages when the window is resized
        self.bind("<Configure>", self.on_frame_configure)

        self.controller = controller

    def on_frame_configure(self, event):
        # Update the size of the pages when the window is resized
        self.update_idletasks()

    def load_content(self):
        # Check if content is already loaded
        if not self.content_loaded:
            # Create a frame to hold the combined functionalities
            combined_frame = tk.Frame(self, highlightbackground="black", highlightthickness=2)
            combined_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Use pack with fill and expand options

            # Add upload/annotation functionality to the left of the combined page
            page_one = PageFunctionality(combined_frame, self.controller)
            page_one.pack(side="left", fill="both", expand=True)  # Use pack with fill and expand options

            # Add RADS functionality to the right of the combined page
            page_two = RadsFunctionality(combined_frame, self.controller)
            page_two.pack(side="right", fill="both", expand=False)  # Use pack with fill and expand options

            # Set the flag to True after content is loaded
            self.content_loaded = True

# Load application
app = AnnotationTool()
plt.margins(x=0)
app.mainloop()