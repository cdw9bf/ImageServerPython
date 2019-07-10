from flask import Blueprint, Response, request
from flask import current_app as app

from werkzeug.datastructures import FileStorage
from typing import Dict, AnyStr
from members.models import Image, MasterRecord
from members import db
import json
import os
import errno

from utils.creators import create_image, create_master_record
from utils.encoder import DateTimeEncoder

upload_page = Blueprint('upload_page', __name__, template_folder='templates')
ACCEPTED_FILES = {'png', 'jpeg', 'jpg', 'nef'}


def is_accepted_file(file_name):
    if file_name.split(".")[-1].lower() in ACCEPTED_FILES:
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

    resp = Response(json.dumps(image.to_json(), cls=DateTimeEncoder))
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
    master_record = create_master_record(byte_stream=file.stream, file_name=file.filename)
    image = create_image(image_id=master_record.uuid,
                         image_size='original',
                         date_taken=master_record.date_taken,
                         file_name=file.filename,
                         config=config)
    db.session.add(master_record)
    db.session.add(image)

    try:
        os.makedirs(os.path.dirname(image.path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

    file.save(image.path)
    db.session.commit()
    return image

