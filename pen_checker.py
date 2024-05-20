# pen_checker.py

class PenTypeFileManager:
    def __init__(self):
        self.filename = "pen_type.txt"

    def save_pen_line(self, word):
        try:
            second = self.read_type_line()
            with open(self.filename, 'w') as file:
                file.seek(0)
                file.write(word + '\n' + second)
        except Exception as e:
            return e

    def set_type_line(self, content):
        try:
            with open(self.filename, 'r+') as file:
                # Read the first line
                first_line = file.readline().strip()

                # Skip the second line
                file.readline()

                # Go back to the beginning of the file
                file.seek(0)

                # Write the first line
                file.write(first_line + '\n')

                # Write the new content to the second line
                file.write(content + '\n')

                # Truncate the file to the current position
                file.truncate()
        except Exception as e:
            return e

    def clear_file(self):
        try:
            with open(self.filename, 'w') as file:
                file.truncate(0)
        except Exception as e:
            return e

    def read_pen_line(self):
        try:
            with open(self.filename, 'r') as file:
                first_line = file.readline().strip()
            return first_line
        except Exception as e:
            return e

    def read_type_line(self):
        try:
            with open(self.filename, 'r') as file:
                # Skip the first line
                file.readline()
                second_line = file.readline().strip()
            return second_line
        except Exception as e:
            return e
