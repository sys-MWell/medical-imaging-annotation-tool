# rads_loaded_status.py

class RadsLoadStatus:
    def __init__(self, filename='rads_loaded.txt'):
        self.filename = filename

    def set_rads_load_status(self, status):
        with open(self.filename, 'w') as file:
            file.write(str(status))

    def get_rads_load_status(self):
        try:
            with open(self.filename, 'r') as file:
                return str(file.read())
        except FileNotFoundError:
            # If the file doesn't exist yet, return 0
            return 0
