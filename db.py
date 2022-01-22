import json
import os

class Database:
    def __init__(self, path="data.json"):
        self.path = path
        self.data = {}

    def load_from_file(self):
        if os.path.isfile(self.path):
            with open(self.path, "r") as f:
                self.data = json.load(f)

    def save_to_file(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f)
