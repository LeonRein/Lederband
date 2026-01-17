from typing import Optional

from PIL import Image

from .models import Badge, BadgeRow, LeatherBand


def create_badge_row_image(badge_row: BadgeRow):
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


def create_band_image(band: LeatherBand) -> Optional[Image.Image]:
    background = band.get_image()
    if background is None:
        return None

    bg_width, bg_height = background.size

    current_y = bg_height

    for badge in band.badges:
        image = None
        if isinstance(badge, Badge):
            image = badge.get_image()
        elif isinstance(badge, BadgeRow):
            image = create_badge_row_image(badge)

        if image is None:
            continue

        try:
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
            current_y = top_y - band.margin

        except Exception as e:
            print(f"Error processing badge {badge.name}: {e}")
            continue

    return background
