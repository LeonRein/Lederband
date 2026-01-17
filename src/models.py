import dataclasses
import os
import pathlib
from dataclasses import dataclass
from typing import List

from dataclasses_json import config, dataclass_json
from PIL import Image


@dataclass_json
@dataclass
class Badge:
    """Class representing a single badge."""

    @property
    def name(self):
        path = pathlib.Path(self.image_path)
        return path.stem

    def get_image(self):
        if not self.image_path or not os.path.exists(os.path.abspath(self.image_path)):
            raise FileNotFoundError(f"Badge image not found: {self.image_path}")
        return Image.open(os.path.abspath(self.image_path)).convert("RGBA")

    image_path: str = ""


@dataclass_json
@dataclass
class BadgeRow:
    """Class representing a row of badges."""

    badges: List[Badge]

    @classmethod
    def from_paths(cls, *args):
        badges = [Badge(arg) for arg in args]
        return cls(badges)


def union_decoder(data):
    results = []
    for item in data:
        # Try to parse as A first
        if "badges" in item:
            results.append(BadgeRow.from_dict(item))
        # Then try B
        else:
            results.append(Badge.from_dict(item))
    return results


@dataclass_json
@dataclass
class LeatherBand:
    """Class representing the entire leather band configuration."""

    image_path: str = ""
    margin: int = 6
    badges: List[Badge | BadgeRow] = dataclasses.field(
        default_factory=list, metadata=config(decoder=union_decoder)
    )

    def get_image(self):
        if not self.image_path or not os.path.exists(os.path.abspath(self.image_path)):
            raise FileNotFoundError(f"Background image not found: {self.image_path}")
        return Image.open(os.path.abspath(self.image_path)).convert("RGBA")

    def save_to_file(self, filepath: str):
        with open(filepath, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filepath: str) -> "LeatherBand":
        with open(filepath, "r") as f:
            return cls.from_json(f.read())
