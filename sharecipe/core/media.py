import os
from PIL import Image, UnidentifiedImageError
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage

class UnsupportedMediaError(Exception):
    pass

def delete_media(filename):
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

def upload_media(picture: FileStorage, max_size=1080) -> str:
    filename = "{}.{}".format(str(uuid.uuid4()), picture.filename.split('.')[-1])

    picture = _resize_image(picture.stream, max_size)
    if picture is None:
        raise UnsupportedMediaError

    picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    return filename

def _resize_image(stream, size):
    try:
        img = Image.open(stream)

        if img.size[0] <= size and img.size[1] <= size:
            return img

        if img.size[0] > img.size[1]:
            return img.resize((size, int((size / img.size[0]) * img.size[1])))
        else:
            return img.resize((int((size / img.size[1]) * img.size[0]), size))
    except UnidentifiedImageError:
        return None