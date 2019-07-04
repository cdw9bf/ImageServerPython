from members.models import Image
import cv2
from typing import AnyStr
import os
import errno
import rawpy


def create_fullsize(image: Image, dst: AnyStr):
    """
    Creates Full Size Jpeg of original image. Undergoes slight compression
    :param image: Image db object
    :param dst: Destination path
    :return: None
    """
    img_arr = load_img(image.original_path, image.image_type)
    ratio = img_arr.shape[0:2][::-1]
    resized = cv2.resize(src=img_arr, dsize=ratio, interpolation=cv2.INTER_AREA)
    save_image(image=resized, destination=dst)


def create_thumbnail(image: Image, dst: AnyStr, size: int=300):
    """
    Creates small thumbnail image
    :param image: Image db object
    :param dst: Destination file path
    :param size: Horizontal size in px
    :return: None
    """
    img_arr = load_img(image.original_path, image.image_type)
    ratio = img_arr.shape[0:2][::-1]

    # Height will be 300 for now
    # Width will be whatever maintains aspect ratio
    asp = ratio[0] / ratio[1]
    target_size = (int(asp * size), size)

    resized = resize(img_arr, target_size)
    save_image(image=resized, destination=dst)


def resize(img, target_size):
    """
    Executes resize function
    :param img: Image numpy array
    :param target_size: Tuple of target dimensions
    :return: numpy array of resized image
    """
    return cv2.resize(src=img, dsize=target_size, interpolation=cv2.INTER_AREA)


def load_img(path: AnyStr, img_type: AnyStr):
    """
    Loads image from disk to array
    :param path: Path on disk
    :param img_type: extension of file
    :return: numpy array of image
    """
    if img_type.lower() in ['jpeg', 'jpg']:
        return cv2.imread(path)
    elif img_type.lower() in ['nef']:
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess()
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    else:
        raise ValueError("Not yet Implemented")


def save_image(image, destination):
    """
    Saves jpeg image to disk
    :param image: Numpy array of image
    :param destination: File path for saving image
    :return: None
    """
    try:
        os.makedirs(os.path.dirname(destination))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
    cv2.imwrite(destination, image)
