# lesion_counter.py

class LesionCounter:
    def __init__(self, filename='lesion_count.txt'):
        self.filename = filename

    def set_lesion_count(self, lesion_count):
        with open(self.filename, 'w') as file:
            file.write(str(lesion_count))

    def get_lesion_count(self):
        try:
            with open(self.filename, 'r') as file:
                return int(file.read())
        except FileNotFoundError:
            # If the file doesn't exist yet, return 0
            return 0

    def reset_lesion_count(self):
        self.set_lesion_count(0)

    def increment_lesion_count(self):
        current_count = self.get_lesion_count()
        self.set_lesion_count(current_count + 1)

    def decrement_lesion_count(self):
        current_count = self.get_lesion_count()
        # Ensure count doesn't go below 0
        new_count = max(0, current_count - 1)
        self.set_lesion_count(new_count)