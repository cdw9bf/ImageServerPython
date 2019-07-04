from flask import Blueprint, Response, request
from flask import current_app as app

from werkzeug.datastructures import FileStorage
import io
import shutil
from typing import Dict, AnyStr
from datetime import datetime
from members.models import Image
from members import db
import json
import os
import exifread
from werkzeug.utils import secure_filename
import errno


# What do I want to do?
#
# 1. Upload full size image
# 2. Save Image to disk
# 3. Create Entries in DB

upload_page = Blueprint('upload_page', __name__, template_folder='templates')
ACCEPTED_FILES = {'png', 'jpeg', 'jpg', 'NEF'}


def is_accepted_file(file_name):
    if file_name.split(".")[-1] in ACCEPTED_FILES:
        return True
    else:
        return False


@upload_page.route('/', methods=['POST'])
def upload_image():
    """
    Upload Image method. Takes image stream as a form parameter of the request, saves it, and creates an entry in the DB
    :return: Created Image Object
    """
    file = request.files['file']
    if not is_accepted_file(file.filename):
        resp = Response(
            json.dumps(
                {"error": "invalid file extension. Expecting {0} was {1}".format(ACCEPTED_FILES,
                                                                                 file.filename.split(".")[-1])}),
            status=400)
        resp.headers['Content-Type'] = "application/json"
        return resp

    image = process_file(file, app.config)

    resp = Response(str(image))
    resp.headers['Content-Type'] = "application/json"
    return resp


def process_file(file: FileStorage, config: Dict) -> Image:
    """
    Takes byte stream, creates image object, saves file to location and commits entry to db
    :param file: FileStorage object from Request
    :param config: Configuration Dictionary from main app
    :return: Created Image Object
    """
    # Grab metadata
    # Insert into DB
    # Save to path
    image = create_image_object(byte_stream=file.stream, file_name=file.filename, config=config)
    db.session.add(image)

    try:
        os.makedirs(os.path.dirname(image.original_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

    file.save(image.original_path)
    db.session.commit()
    return image


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


def create_image_object(byte_stream, file_name: AnyStr, config) -> Image:
    """
    Creates the Image Database Object
    :param byte_stream: Input bytesteam of image
    :param file_name: Name of Image file Uploaded
    :param config: App config
    :return: New Image Object for uploaded image
    """
    file_name = secure_filename(file_name)

    tags = read_image_metadata(byte_stream, extension=file_name.split(".")[-1])
    date_taken = extract_date_taken(tags)
    original_path = create_file_save_path(date=date_taken,
                                          file_name=file_name,
                                          config=config,
                                          dir_appendage="original")

    return Image(
        tags=tags,
        date_uploaded=datetime.now(),
        date_taken=date_taken,
        save_path=original_path
    )



