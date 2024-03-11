from imports import *
from annotation_page_quit import QuitOperation


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

        for F in (HomePage, AccountPage, AnnotationPage, LoginPage):
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
        self.controller = controller

        self.controller.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.quit_operation = QuitOperation(self)

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


    # Quit application
    def on_closing(self):
        # Quit application dialog
        self.quit()
        pass

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
        self.controller = controller

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

        # Create the close button
        close_button = ttk.Button(button_frame, text="Quit", style="AccountPage.TButton"
                                  , command=lambda: self.on_button_click(controller, "Exit"))
        close_button.grid(row=1, column=0, columnspan=2)  # Place the button below the existing buttons

        # Configure grid weights to make the widgets expand with the window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

    def on_button_click(self, controller, account_type):
        # Handle button click event
        if account_type == "Doctor":
            saveCache = UserCache("1", "", "", "")
            # Save user cache credentials and load Annotation Page
            saveCache.save_to_file()
            # Load login page
            #controller.show_frame(AnnotationPage)
            controller.show_frame(LoginPage)
        elif account_type == "AI Researcher":
            saveCache = UserCache("2", "", "", "")
        elif account_type == "Exit":
            self.quit()
        else:
            pass

# Annotation page display
class AnnotationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')

        # Set a flag to track whether content is loaded
        self.content_loaded = False
        self.page_functionality = None
        self.rads_functionality = None
        self.combined_frame = None

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
            self.combined_frame = combined_frame

            # Add upload/annotation functionality to the left of the combined page
            page_one = PageFunctionality(combined_frame, self.controller, AccountPage)
            page_one.pack(side="left", fill="both", expand=True)  # Use pack with fill and expand options
            self.page_functionality = page_one

            # Add RADS functionality to the right of the combined page
            page_two = RadsFunctionality(combined_frame, self.controller)
            page_two.pack(side="right", fill="both", expand=False)  # Use pack with fill and expand options
            self.rads_functionality = page_two

            # Set the flag to True after content is loaded
            self.content_loaded = True
        else:
            # If page already loaded
            self.destroy_all_functionalities()
            self.content_loaded = False
            self.load_content()

    def destroy_page_functionality(self):
        if self.page_functionality:
            self.page_functionality.destroy()
            self.page_functionality = None

    def destroy_rads_functionality(self):
        if self.rads_functionality:
            self.rads_functionality.destroy()
            self.rads_functionality = None

    def destroy_all_functionalities(self):
        # Destroy all previously loaded pages
        self.destroy_page_functionality()
        self.destroy_rads_functionality()
        self.combined_frame.destroy()


# Login page display
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffffff')  # Set background color
        self.controller = controller

        # Frame for login elements
        login_frame = tk.Frame(self, bg='#ffffff')
        login_frame.pack(padx=20, pady=20)

        # Logo
        self.img = Image.open('./img/logo.png')
        self.logo = ImageTk.PhotoImage(self.img)
        self.logo_label = tk.Label(login_frame, image=self.logo, bg='#ffffff')
        self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)

        login_button_style = ttk.Style()
        login_button_style.configure("LoginPage.TButton", font=('Helvetica', 18, 'bold'),
                                     background="#f2f2f2", foreground="#333333",
                                     width=20, padding=(15, 15), bordercolor="#999999",
                                     lightcolor="#999999", darkcolor="#999999")

        # Title
        title_label = tk.Label(login_frame, text="Login details: ", font=("Helvetica", 28, "bold"), bg='#ffffff')
        title_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Create a combobox for the ID number
        id_label = tk.Label(login_frame, text="Username:", font=("Helvetica", 26), bg='#ffffff')
        id_label.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)  # Align the label to the east (right) and add padding
        self.id_var = tk.StringVar()
        self.id_combobox = ttk.Combobox(login_frame, textvariable=self.id_var, font=("Helvetica", 22),
                                        width=14)  # Decreased width
        self.id_combobox.grid(row=2, column=1, sticky="w", pady=5)  # Align the combobox to the west (left)

        # Create an entry for the password
        password_label = tk.Label(login_frame, text="Password:", font=("Helvetica", 26), bg='#ffffff')
        password_label.grid(row=3, column=0, sticky="e",
                            padx=(0, 10), pady=5)  # Align the label to the east (right) and add padding
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(login_frame, textvariable=self.password_var, show="*", font=("Helvetica", 22),
                                       width=15)  # Decreased width
        self.password_entry.grid(row=3, column=1, sticky="w", pady=5)  # Align the entry to the west (left)

        # Checkbox to show/hide password
        self.show_password_var = tk.IntVar()
        self.show_password_checkbox = tk.Checkbutton(login_frame, text="Show Password", variable=self.show_password_var,
                                                     font=("Helvetica", 12), bg="#ffffff",
                                                     command=self.toggle_password_visibility)
        self.show_password_checkbox.grid(row=4, column=0, columnspan=2, sticky="nsew")  # Centered in two columns

        # Populate the combobox with IDs from the credentials file
        self.populate_ids()

        # Create a login button with custom styling
        self.login_button = ttk.Button(login_frame, text="Login", command=self.verify_credentials, style="LoginPage.TButton")
        self.login_button.grid(row=5, column=1, pady=15, padx=5)

        # Create a back button
        self.back_button = ttk.Button(login_frame, text="Back", command=lambda: controller.show_frame(AccountPage),
                                       style="LoginPage.TButton")
        self.back_button.grid(row=5, column=0, pady=15, padx=5)

        # Add shadow border to the password entry
        self.password_entry.config(highlightbackground="#dddddd", highlightthickness=1)

    # Display user IDs within combobox
    def populate_ids(self):
        ids = []
        with open('credentials.txt', 'r') as file:
            for line in file:
                id, _ = line.strip().split()
                ids.append(id)
        self.id_combobox['values'] = ids

    # Verify login details
    def verify_credentials(self):
        entered_id = self.id_var.get()
        entered_password = self.password_var.get()

        with open('credentials.txt', 'r') as file:
            for line in file:
                id, password = line.strip().split()
                if id == entered_id and password == entered_password:
                    self.login_function()
                    return

    # If login details are correct, load the AnnotationPage
    def login_function(self):
        self.controller.protocol("WM_DELETE_WINDOW", "")
        saveCache = UserCache("1", self.id_var.get(), "", "")
        # Save user cache credentials and load Annotation Page
        saveCache.save_to_file()
        # Clear entries
        self.id_combobox.set('')
        self.password_entry.delete(0, 'end')
        self.controller.show_frame(AnnotationPage)

    # Toggle password visibility
    def toggle_password_visibility(self):
        if self.show_password_var.get() == 1:
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")


# Load application
app = AnnotationTool()
plt.margins(x=0)
app.mainloop()