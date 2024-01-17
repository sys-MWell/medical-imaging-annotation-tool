# load_rads_data.py
from imports import *


# Load rads data from JSON
class LoadRadsData:
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

        return self.lesion_data_dict
