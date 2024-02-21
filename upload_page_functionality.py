# upload_page_functionality.py

from imports import *


class UploadFunctionality:
    def __init__(self, page_functionality):
        self.page_functionality = page_functionality
        self.controller = self.page_functionality.controller

# Upload image section functionality
    def upload_functionality(self):
        # Create a frame for the matplotlib graph and toolbar
        self.upload_frame = tk.Frame(self.page_functionality.combined_frame, bg=FRAME_BACKGROUND_COLOUR, width=250)
        self.upload_frame.pack(side="left", fill="both", expand=False)  # Use pack with fill and expand options

        # Set background color
        self.page_functionality.configure(bg=MASTER_COLOUR)

        # Adjust upload button visibility based on user type
        if self.page_functionality.user_type == "1":
            label = tk.Label(self.upload_frame, text="Image Upload and Selection", font=("Helvetica", 16),
                             bg=SECONDARY_COLOUR, fg=MASTER_FONT_COLOUR)
            label.pack(pady=10, padx=10)

            # Create a button to upload images with a modern style
            upload_button = ttk.Button(self.upload_frame, text="Upload Images",
                                       command=self.upload_images,
                                       style="Custom.TButton")
            upload_button.pack(pady=10)
        elif self.page_functionality.user_type == "2":
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
                                    highlightbackground="black", highlightthickness=1, width=250)
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
        self.canvas = tk.Canvas(self.image_frame, bg=SECONDARY_COLOUR, width=250)
        self.scrollbar = ttk.Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview,
                                       style="Custom.Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=SECONDARY_COLOUR, padx=0)

        # Scrollbar functionality
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"), width=250, height=2000
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the scrollbar style
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", gripcount=20,
                        background="gray")  # Set the background color and grip count as needed

        # Load all images from JSON
        self.load_images_from_json()

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
        self.page_functionality.image_id = self.image_info[index].image_id
        self.page_functionality.image_location = self.image_info[index].image_location
        lesion_count = self.page_functionality.lesion_counter.get_lesion_count()
        if (lesion_count >= 1 or (len(self.page_functionality.dashed_line_coordinates) >= 1) or (
                len(self.page_functionality.rectangle_coordinates) >= 1)):
            # Check upload functionality status
            # If medical professional user
            if self.page_functionality.user_type == "1":
                if not self.page_functionality.upload_condition:
                    self.load_image()
                else:
                    # Popup dialog functionality
                    response = messagebox.askyesno("Load New Image",
                                                   "Any unsaved work will be lost. Do you want to load a new image?")
                    if response:
                        self.page_functionality.lesion_counter.reset_lesion_count()
                        # Load new image functionality
                        self.load_image()
                    else:
                        # Do nothing
                        pass
            else:
                self.load_image()
        else:
            self.page_functionality.lesion_counter.reset_lesion_count()
            self.load_image()

    # Load image
    def load_image(self):
        self.page_functionality.clear_lines()
        self.page_functionality.annotation_frame.destroy()
        # User cache
        saveCache = UserCache(self.page_functionality.user_type, self.page_functionality.user_id,
                              self.page_functionality.image_id, self.page_functionality.image_location)
        saveCache.save_to_file()
        # Disable upload functionality
        self.page_functionality.upload_condition = True
        self.page_functionality.annotation_status = True
        self.page_functionality.annotation_functionality()

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