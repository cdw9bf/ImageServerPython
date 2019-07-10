from datetime import datetime

from sqlalchemy import exists

from flask import Blueprint, Response, request
from utils.encoder import DateTimeEncoder
from members.models import Image, db, MasterRecord
from members.inboud import GenerateThumbnailRequest, GenerateFullSizeRequest
from processors.resize import create_thumbnail, create_fullsize
from constants import FULL, THUMBNAIL

import json

operations_page = Blueprint('operations_page', __name__, template_folder='templates')


@operations_page.route('/thumbnails', methods=['GET'])
def get_list_of_thumbnails():
    has_thumbnails = Image.query.filter(Image.size == THUMBNAIL).all()
    resp = Response(json.dumps({"ids": [i.uuid for i in has_thumbnails]}, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/missing', methods=['GET'])
def get_list_of_missing_thumbnails():
    needs_viewables = db.session.query(MasterRecord)\
        .filter(MasterRecord.uuid == Image.uuid)\
        .filter(~exists().where(Image.size == THUMBNAIL))\
        .all()
    resp = Response(json.dumps({"ids": [i.uuid for i in needs_viewables]}, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/generate', methods=['POST'])
def generate_thumb_nail():
    thumbnail_request = GenerateThumbnailRequest()
    thumbnail_request.from_json(input_json=request.get_json())
    if already_created(thumbnail_request.id, THUMBNAIL):
        return "Already Created\n", 400

    thumbnail_image = process_new_image(thumbnail_request.id, size=THUMBNAIL, create_function=create_thumbnail)

    db.session.add(thumbnail_image)
    db.session.commit()
    return "", 204


@operations_page.route('/full-size', methods=['GET'])
def get_list_of_full_size():
    has_viewables = Image.query.filter(Image.size == FULL).all()
    resp = Response(json.dumps({"ids": [i.uuid for i in has_viewables]}, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/full-size/missing', methods=['GET'])
def get_list_of_missing_full_size():
    needs_viewables = db.session.query(MasterRecord)\
        .filter(MasterRecord.uuid == Image.uuid)\
        .filter(~exists().where(Image.size == FULL))\
        .all()
    resp = Response(json.dumps({"ids": [i.uuid for i in needs_viewables]}, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/full-size/generate', methods=['POST'])
def generate_full_size():
    fullsize_request = GenerateFullSizeRequest()
    fullsize_request.from_json(input_json=request.get_json())
    if already_created(fullsize_request.id, FULL):
        return "Already Created\n", 400

    full_size_image = process_new_image(fullsize_request.id, size=FULL, create_function=create_fullsize)

    db.session.add(full_size_image)
    db.session.commit()
    return "", 204


def already_created(img_id, size) -> bool:
    """
    Checks to see if image has already been created
    :param img_id: UUID of Image
    :param size: Target format size
    :return: true or false
    """
    img = Image.query.filter(Image.uuid == img_id).filter(Image.size == size).all()
    print(img)
    if len(img) != 0:
        return True
    return False


def process_new_image(uuid, size, create_function) -> Image:
    """
    Wrapper function for creating a new image. Makes it easy to add new types in the future
    :param uuid: Image UUID
    :param size: Target format size (thumbnail, fullsize)
    :param create_function: function used to create new image
    :return: New Image object
    """
    orig_image = db.session.query(Image)\
        .filter(Image.uuid == uuid)\
        .filter(Image.size == "original")\
        .first_or_404()

    new_img = Image(
        img_id=orig_image.uuid,
        date_uploaded=datetime.utcnow(),
        path=orig_image.path.replace("/original/", "/{size}/".format(size=size))
                            .replace(".{ext}".format(ext=orig_image.image_format), ".jpg"),
        size=size
    )

    create_function(image=orig_image, dst=new_img.path)
    return new_img

