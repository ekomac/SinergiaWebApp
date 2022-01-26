import os


def is_image_size_valid(img_url, mb_limit):
    image_size = os.path.getsize(img_url)
    if image_size > mb_limit:
        return False
    return True
