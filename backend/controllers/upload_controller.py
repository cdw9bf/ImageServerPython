from flask import Blueprint, Response, request
from flask import current_app as app
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
    file = request.files['file']
    if not is_accepted_file(file.filename):
        resp = Response(
            json.dumps(
                {"error": "invalid file extension. Expecting {0} was {1}".format(ACCEPTED_FILES,
                                                                                 file.filename.split(".")[-1])}),
            status=400)
        resp.headers['Content-Type'] = "application/json"
        return resp

    process_file(file, app.config)

    resp = Response(json.dumps({"Status": "Success"}))
    resp.headers['Content-Type'] = "application/json"
    return resp


def process_file(file, config: Dict):
    # Grab metadata
    # Insert into DB
    # Save to path (by???)
    # Create jpg thumbnail
    image = create_image_object(file, config)
    db.session.add(image)

    try:
        os.makedirs(os.path.dirname(image.original_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
    image.file.save(image.original_path)
    db.session.commit()


def read_image_metadata(file) -> Dict[AnyStr, AnyStr]:
    tags = {}
    extension = file.filename.split(".")[-1]
    if extension in ['jpg', 'jpeg']:
        exif_format = exifread.process_file(file)
        # Format the dict to be String - String mapping
        for key in exif_format.__iter__():
            # print(exif_format[key])
            if type(exif_format[key]) == bytes:
                continue
            tags[key] = exif_format[key].values
    else:
        raise ValueError("Extension {0} is not yet implemented".format(extension))
    return tags


def create_file_save_path(date: datetime, file_name, config, dir_appendage) -> AnyStr:
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


def extract_date_taken(tags):
    # TODO: Look at better ways of getting datetime, could be fragile
    if 'Image DateTime' in tags:
        return datetime.strptime(tags['Image DateTime'], "%Y:%m:%d %H:%M:%S")
    else:
        raise ValueError("'Image DateTime' not in Tags dictionary!")


def create_image_object(file, config) -> Image:
    filename = secure_filename(file.filename)

    tags = read_image_metadata(file)
    date_taken = extract_date_taken(tags)
    original_path = create_file_save_path(date=date_taken,
                                          file_name=filename,
                                          config=config,
                                          dir_appendage="original")
    # fullsize_viewable_path = original_path.replace("/original/", "/viewable/")
    # fullsize_viewable_path = ".".join(fullsize_viewable_path.rsplit(".", 1)[:-1]) + ".jpg"

    return Image(
        image=file,
        tags=tags,
        date=date_taken,
        save_path=original_path
    )



