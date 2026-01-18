import os
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

from .models import Badge, BadgeRow, LeatherBand


class Engine:
    def __init__(self, band: LeatherBand):
        self.__name: str = ""
        self.__name_image: Optional[Image.Image] = None
        self.__name_image_bbox: Optional[tuple[int, int, int, int]] = None
        self.__name_image_mask: Image.Image = Image.new("L", (1, 1), 0)
        self.__background_image: Optional[Image.Image] = None
        self.__band: LeatherBand = band

        # font_path = os.path.join(os.path.dirname(__file__), "font", "PixelOperator.ttf")
        # font_path = os.path.join(os.path.dirname(__file__), "font", "W95FA.otf")
        font_path = os.path.join(os.path.dirname(__file__), "font", "PIXEARG_.TTF")
        self.font_size = 8
        self.font = ImageFont.truetype(font_path, self.font_size)

    def set_band(self, band: LeatherBand):
        self.__band = band
        self.update_background()

    def set_name(self, name: str):
        if self.__name != name:
            self.__name = name
            self.__generate_name_image()

    def update_background(
        self,
    ):
        self.__background_image = self.__band.get_image()
        self.__generate_name_image_mask()
        self.__generate_name_image()

    def __generate_name_image_mask(self):
        if self.__background_image is None:
            self.__name_image_bbox = None
            return None

        gray_img = self.__background_image.convert("L")
        img_array = np.array(gray_img)

        # 2. Threshold to ensure we only have pure white (255) vs the rest
        # If your "white" isn't perfect, you can adjust the threshold value
        _, binary = cv2.threshold(img_array, 254, 255, cv2.THRESH_BINARY)

        # 3. Find connected components
        # connectivity=8 includes diagonals; connectivity=4 does not
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        # If only background is found (num_labels = 1), return None
        if num_labels < 2:
            return None

        # 4. Filter out the background label (always index 0) and find the largest area
        # stats[label, cv2.CC_STAT_AREA] gives the pixel count
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

        # 5. Extract bounding box coordinates for the largest label
        # stats contains [left, top, width, height, area]
        x = stats[largest_label, cv2.CC_STAT_LEFT]
        y = stats[largest_label, cv2.CC_STAT_TOP]
        w = stats[largest_label, cv2.CC_STAT_WIDTH]
        h = stats[largest_label, cv2.CC_STAT_HEIGHT]
        self.__name_image_bbox = (x, y, w + x, h + y)

        bg_crop = self.__background_image.crop(self.__name_image_bbox)
        self.__name_image_mask = bg_crop.convert("L").point(
            lambda p: 255 if p > 254 else 0  # pyright: ignore[reportOperatorIssue]
        )

    def __generate_name_image(self):
        if (
            self.__name_image_bbox is None
            or self.__background_image is None
            or self.__name_image_mask is None
            or self.__name == ""
        ):
            self.__name_image = None
            return

        w, h = (
            self.__name_image_bbox[2] - self.__name_image_bbox[0],
            self.__name_image_bbox[3] - self.__name_image_bbox[1],
        )

        rotate = False
        if h > w:
            rotate = True
            w, h = h, w

        name_image = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(name_image)
        draw.fontmode = "1"

        # Draw the name text on the name image
        bbox = draw.textbbox((20, 20), self.__name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_y = (h - self.font_size) // 2
        text_x = max((w - text_width) // 2, 1)
        draw.text((text_x, text_y), self.__name, font=self.font, fill=(0, 0, 0, 255))

        # Rotate the name image if necessary
        if rotate:
            name_image = name_image.rotate(90, expand=True)

        # Ensure mask is the same size as name_image (should be guaranteed by logic, but good for safety)
        a = name_image.split()[3]
        new_a = ImageChops.multiply(a, self.__name_image_mask)
        name_image.putalpha(new_a)

        self.__name_image = name_image

    def __create_badge_row_image(self, badge_row: BadgeRow):
        images = []
        width = 0
        max_height = 0

        for index, badge in enumerate(badge_row.badges):
            image = badge.get_image()
            if image is None:
                print(f"Warning: Badge image not found: {badge.image_path}")
                continue
            if index == 0:
                image = image.crop((0, 0, image.width - 1, image.height))
            elif index == len(badge_row.badges) - 1:
                image = image.crop((1, 0, image.width, image.height))
            else:
                image = image.crop((1, 0, image.width - 1, image.height))
            images.append(image)
            width += image.width
            max_height = max(max_height, image.height)

        new_image = Image.new("RGBA", (width, max_height), color=(255, 255, 255, 0))
        x = 0
        for image in images:
            new_image.paste(image, (x, 0))
            x += image.width

        return new_image

    def create_band_image(self) -> Optional[Image.Image]:
        if self.__band is None or self.__background_image is None:
            return None

        background = self.__background_image.copy()

        if self.__name_image is not None and self.__name_image_bbox is not None:
            background.alpha_composite(
                self.__name_image,
                (self.__name_image_bbox[0], self.__name_image_bbox[1]),
            )

        bg_width, bg_height = background.size

        current_y = bg_height

        for badge in self.__band.badges:
            image = None
            if isinstance(badge, Badge):
                image = badge.get_image()
            elif isinstance(badge, BadgeRow):
                image = self.__create_badge_row_image(badge)

            if image is None:
                continue

            b_width, b_height = image.size

            # scale the image to fit the background width
            scale = bg_width / b_width
            image = image.resize(
                (int(b_width * scale), int(b_height * scale)),
                resample=Image.Resampling.LANCZOS,
            )

            b_width, b_height = image.size

            # center horizontally
            x_pos = (bg_width - b_width) // 2

            # place directly above the previous item (or bottom edge)
            # The bottom of the badge should be at current_y
            # So top of the badge is current_y - b_height
            top_y = current_y - b_height

            # Composite the badge
            # We use the badge itself as the mask for transparency
            background.alpha_composite(image, (x_pos, top_y))

            # Update current_y for the next badge, applying margin
            current_y = top_y - self.__band.margin

        return background
