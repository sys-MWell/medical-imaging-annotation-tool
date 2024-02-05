class UserCache:
    def __init__(self, user_type, user_id, image_id, image_location):
        self.user_type = user_type
        self.user_id = user_id
        self.image_id = image_id
        self.image_location = image_location

    def save_to_file(self):
        with open('usercache.txt', 'w') as file:
            file.write(f'user_type: {self.user_type}\n')
            file.write(f'user_id: {self.user_id}\n')
            file.write(f'image_id: {self.image_id}\n')
            file.write(f'image_location: {self.image_location}\n')

    def read_from_file(self):
        with open('usercache.txt', 'r') as file:
            lines = file.readlines()
            # Check if lines list has at least 4 elements
            if len(lines) >= 4:
                self.user_type = lines[0].split(': ')[1].strip()
                self.user_id = lines[1].split(': ')[1].strip()
                self.image_id = lines[2].split(': ')[1].strip()
                self.image_location = lines[3].split(': ')[1].strip()
            else:
                # Handle the case where the file doesn't have enough lines
                print("Error: Not enough lines in the file.")

