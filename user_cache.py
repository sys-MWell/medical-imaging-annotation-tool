class UserCache:
    def __init__(self, user_id, image_id, image_location):
        self.user_id = user_id
        self.image_id = image_id
        self.image_location = image_location

    def save_to_file(self):
        with open('usercache.txt', 'w') as file:
            file.write(f'user_id: {self.user_id}\n')
            file.write(f'image_id: {self.image_id}\n')
            file.write(f'image_location: {self.image_location}\n')

    def read_from_file(self):
        with open('usercache.txt', 'r') as file:
            lines = file.readlines()
            self.user_id = lines[0].split(': ')[1].strip()
            self.image_id = lines[1].split(': ')[1].strip()
            self.image_location = lines[2].split(': ')[1].strip()