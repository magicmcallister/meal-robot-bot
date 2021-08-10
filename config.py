import sys
import os
import configparser


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        self.config_folder = os.path.abspath("")
        self.config_path = os.path.join(self.config_folder, self.config_file)

    def load(self):
        if not os.path.isfile(self.config_path):
            self.config_folder = os.path.dirname(os.path.abspath(""))
            self.config_path = os.path.join(self.config_folder, self.config_file)
        try:
            self.config.read(self.config_path)
        except Exception:
            print("Error: wrong or missing 'config.ini' file")

    def get(self, section, parameter):
        if self.config.has_option(section, parameter):
            value = self.config.get(section, parameter)
        else:
            value = os.getenv("_".join([section.upper(), parameter.upper()]))
        return value
