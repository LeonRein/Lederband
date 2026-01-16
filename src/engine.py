from typing import Optional

from PIL import Image

from .models import LeatherBand


def create_band_image(band: LeatherBand) -> Optional[Image.Image]:
    background = band.get_image()
    if background is None:
        print(f"Warning: Background image not found: {band.image_path}")
        return None

    bg_width, bg_height = background.size

    current_y = bg_height

    for badge in band.badges:
        badge_image = badge.get_image()
        if badge_image is None:
            print(f"Warning: Badge image not found: {badge.image_path}")
            continue

        try:
            b_width, b_height = badge_image.size

            # center horizontally
            x_pos = (bg_width - b_width) // 2

            # place directly above the previous item (or bottom edge)
            # The bottom of the badge should be at current_y
            # So top of the badge is current_y - b_height
            top_y = current_y - b_height

            # Composite the badge
            # We use the badge itself as the mask for transparency
            background.alpha_composite(badge_image, (x_pos, top_y))

            # Update current_y for the next badge, applying margin
            current_y = top_y - band.margin

        except Exception as e:
            print(f"Error processing badge {badge.name}: {e}")
            continue

    return background
