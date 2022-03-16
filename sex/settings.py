import os
import json

from PySide2.QtGui import QIcon
       
def get_plugin_icon(filename: str) -> QIcon:
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "icons", filename)
    return QIcon(path)

class PluginSettings:
    def __init__(self):
        self._json_defaults = \
        """
{
    "window_size": [
        1463,
        952
    ],
    "font": "Courier New",    
    "editor_font_size": 11,
    "console_font_size": 10,
    "tab_font_size": 11,
    "tab_spaces": 4,
    "align_max_nodes": 50,
    "use_snippet_object": false,
    "window_pos": [
        233,
        229
    ]
}        
        """
        path = os.path.dirname(os.path.abspath(__file__))
        self.settings_file_path = os.path.join(path, "..", "settings.json")
        self.settings = {}
        self.defaults = json.loads(self._json_defaults)
        self.load()
       
    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        elif key in self.defaults:
            return self.defaults[key]
        else:
            raise KeyError(f"No setting [{key}]!")

    def __setitem__(self, key, value):
        self.settings[key] = value

    def load(self):
        settings_file_exists = os.path.isfile(self.settings_file_path)
        if settings_file_exists:
            with open(self.settings_file_path) as settings_file:
                self.settings = json.load(settings_file)

    def save(self):
        settings_to_save = self.defaults.copy()
        settings_to_save.update(self.settings)
        with open(self.settings_file_path, "w") as settings_file:
            json.dump(settings_to_save, settings_file, indent=4)