import os
import shutil
from pathlib import Path

import yaml

VIEW_DISTANCE = 1

EPISODE_FILE = 'episode.jsonl'
SETTINGS_FILE = 'settings.yaml'


class ExperimentSettings:
    def __init__(self, path, show_weights=False):
        self.path = path
        root_path = Path(__file__).resolve().parent.parent / SETTINGS_FILE
        if path:
            settings_file = Path(path) / SETTINGS_FILE
            if not os.path.isdir(path):
                os.mkdir(path)
                shutil.copyfile(root_path, settings_file)
        else:
            settings_file = root_path
        with open(settings_file) as fin:
            self.settings = yaml.load(fin)
        self.show_weights = show_weights

    def __getattr__(self, item):
        if item in self.settings:
            return self.settings[item]
        raise AttributeError(f'{item} is not found in settings')

    def get_path(self, filename):
        if self.path:
            return os.path.join(self.path, filename)
        return None
