import io
import os
from datetime import datetime
from typing import AnyStr, Dict

import exifread
from werkzeug.utils import secure_filename

from members.models import Image, MasterRecord


def create_master_record(byte_stream, file_name: AnyStr) -> MasterRecord:
    """
    Creates the Master Record Database Object
    :param byte_stream: Input bytesteam of image
    :param file_name: Name of Image file Uploaded
    :return: New Image Object for uploaded image
    """
    file_name = secure_filename(file_name)

    tags = read_image_metadata(byte_stream, extension=file_name.split(".")[-1])
    date_taken = extract_date_taken(tags)

    return MasterRecord(
        tags=tags,
        date_taken=date_taken,
        date_added=datetime.utcnow()
    )


def create_image(image_id: AnyStr, image_size: AnyStr, date_taken: datetime, file_name: AnyStr, config: Dict) -> Image:
    """
    Creates the Image Object database Record
    :param image_id: Uuid of Image
    :param image_size: Type of image, (original, thumbnail, fullsize)
    :param date_taken: Date image was taken or created
    :param file_name: Name of file uploaded
    :param config: App config params
    :return: Image Database Object
    """
    path = create_file_save_path(date=date_taken,
                                 file_name=file_name,
                                 config=config,
                                 dir_appendage=image_size)
    return Image(
        img_id=image_id,
        date_uploaded=datetime.utcnow(),
        path=path,
        size=image_size
    )


def create_file_save_path(date: datetime, file_name, config, dir_appendage) -> AnyStr:
    """
    Creates the path to save the image on the system.
    :param date: Date that the image was taken
    :param file_name: Name of the Image File
    :param config: App config that contains the UPLOAD_FOLDER field
    :param dir_appendage: type of file that's being saved
    :return: Full path to save image at. Should be unique barring a race condition
    """
    path = "{y}/{m}/{d}/".format(y=date.year, m=date.month, d=date.day)
    full_path = os.path.join(config['UPLOAD_FOLDER'], dir_appendage, path + file_name)
    if os.path.exists(full_path):
        i = 0
        name_split = file_name.rsplit(".", 1)
        # Todo: Remove this race condition if two images are uploaded at the same time with the same name
        while os.path.exists(full_path):
            new_name = name_split[0:-1] + ["{0}".format(i)] + name_split[-1::]
            new_name = ".".join(new_name)
            full_path = os.path.join(config['UPLOAD_FOLDER'], dir_appendage, path + new_name)
            i += 1
    return full_path


def extract_date_taken(tags) -> datetime:
    """
    Extracts the date the photo was taken from the image. If none found, it defaults to 2000
    :param tags: Dictionary of Image Tags
    :return: Datetime object
    """
    # TODO: Look at better ways of getting datetime, could be fragile
    if 'Image DateTime' in tags:
        return datetime.strptime(tags['Image DateTime'], "%Y:%m:%d %H:%M:%S")
    else:
        print("No Datetime Found!")
        return datetime.strptime("2000:01:01 00:00:00", "%Y:%m:%d %H:%M:%S")


def read_image_metadata(bytes_io: io.BytesIO, extension: AnyStr) -> Dict[AnyStr, AnyStr]:
    """
    Main image metadata processing. Reads EXIFs information then returns it in a dictionary format.
    Strips out fields that are not needed / full of junk that's not meaningful.
    :param bytes_io: BytesIo object of image
    :param extension: type of file being processed
    :return: Dictionary of Tags
    """
    tags = {}
    if extension.lower() in ['jpg', 'jpeg', 'nef']:
        exif_format = exifread.process_file(bytes_io)
        # Format the dict to be String - String mapping
        for key in exif_format.__iter__():
            if type(exif_format[key]) == bytes:
                continue

            # Filter out lots of Nikon Specific tags that don't mean anything
            if key.startswith("MakerNote") and key not in ["MakerNote Quality", "MakerNote FocusMode", "MakerNote TotalShutterReleases"]:
                continue

            # Filter out some exif tags
            if key == "EXIF MakerNote":
                continue

            # if it's in the exifread.utils.Ratio format make it into a string
            if type(exif_format[key].values) == list \
                    and len(exif_format[key].values) > 0 \
                    and type(exif_format[key].values[0]) == exifread.utils.Ratio:
                tags[key] = [i.__repr__() for i in exif_format[key].values]
            else:
                tags[key] = exif_format[key].values
    else:
        raise ValueError("Extension {0} is not yet implemented".format(extension))
    # Reset to beginning of bytestream for future consumption
    bytes_io.seek(0)
    return tags
