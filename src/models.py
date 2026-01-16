import dataclasses
import os
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from PIL import Image


@dataclass_json
@dataclass
class Badge:
    """Class representing a single badge."""

    @property
    def name(self):
        return os.path.basename(self.filename)

    def get_image(self):
        if not self.image_path or not os.path.exists(self.image_path):
            return None
        return Image.open(self.background_path).convert("RGBA")

    image_path: str


@dataclass_json
@dataclass
class LeatherBand:
    """Class representing the entire leather band configuration."""

    image_path: str
    margin: int
    badges: List[Badge] = dataclasses.field(default_factory=list)

    def get_image(self):
        if not self.image_path or not os.path.exists(self.image_path):
            return None
        return Image.open(self.image_path).convert("RGBA")

    def save_to_file(self, filepath: str):
        with open(filepath, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filepath: str) -> "LeatherBand":
        with open(filepath, "r") as f:
            return cls.from_json(f.read())
