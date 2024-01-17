# annotation_vars.py
# All variables to be used in PageFunctionality Class

class PageVariables:
    def __init__(self):
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

        # List to store rectangle coordinates
        self.rectangle_coordinates = []
        self.rectangle_coordinate = None
        self.rect_pen_colour = 'Green'
        self.rect_type = 'Highlight'

        # List to store arrow coordinates
        self.arrows = []
        self.arrow_coordinates = []
        self.arrow_colour = 'blue'
        self.arrow_coordinate = None

        # Initialise dashed line drawing mode variables
        self.dashed_lines = []
        self.dashed_line_coordinates = []
        self.dashed_line_coordinate = None
        self.dashed_lines_plus = []
        self.local_dashed_lines_Plus = []
        self.dashed_lines_num_txt = []
        self.dashed_line_mode = False
        self.dashed_line_drawing = False
        self.dash_line_count = 0

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
