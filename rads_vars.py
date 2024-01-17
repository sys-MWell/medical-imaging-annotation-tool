# rads_vars.py
# All variables to be used in RadsFunctionality Class

class PageVariables:
    def __init__(self):

        self.margin_vars = {}
        self.posterior_vars = {}

        # Declare variables
        self.user_id = ''
        self.image_id = ''
        self.image_location = ''
        self.additional_notes = ''

        self.rads_load_status = False
        self.image_upload_status = False
        self.initial_load = False
        self.num_notebooks = 1
        self.masses_frames = []

        # Initialize the list to store removed notebook states
        self.removed_notebooks = []
        self.page_data = {}

        self.lesions = 0
        self.checkboxes = []
        self.image_selected = True
