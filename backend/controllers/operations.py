from flask import Blueprint, Response, request
from flask import current_app as app
from utils.encoder import DateTimeEncoder
from members.models import Image, db
from members.inboud import GenerateThumbnailRequest, GenerateFullSizeRequest
from processors.resize import create_thumbnail, create_fullsize

import json

operations_page = Blueprint('operations_page', __name__, template_folder='templates')


@operations_page.route('/thumbnails', methods=['GET'])
def get_list_of_thumbnails():
    has_thumbnails = Image.query.filter(Image.thumb_nail_path.isnot(None)).all()
    resp = Response(json.dumps(has_thumbnails, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/missing', methods=['GET'])
def get_list_of_missing_thumbnails():
    needs_thumbnails = Image.query.filter(Image.thumb_nail_path.is_(None)).all()
    resp = Response(json.dumps(needs_thumbnails, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/generate', methods=['POST'])
def generate_thumb_nail():
    # Model
    #
    thumbnail_request = GenerateThumbnailRequest()
    thumbnail_request.from_json(input_json=request.get_json())
    image = Image.query.filter(Image.id == thumbnail_request.id).first_or_404()
    image.thumb_nail_path = image.original_path.replace("/original/", "/thumbnail/").replace(".{ext}".format(ext=image.image_type), ".jpg")
    create_thumbnail(image, image.thumb_nail_path)
    db.session.commit()
    return "", 204


@operations_page.route('/full-size', methods=['GET'])
def get_list_of_full_size():
    has_viewables = Image.query.filter(Image.fullsize_viewable_path.isnot(None)).all()
    resp = Response(json.dumps(has_viewables, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/full-size/missing', methods=['GET'])
def get_list_of_missing_full_size():
    needs_viewables = Image.query.filter(Image.fullsize_viewable_path.is_(None)).all()
    resp = Response(json.dumps(needs_viewables, cls=DateTimeEncoder))
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/full-size/generate', methods=['POST'])
def generate_full_size():
    fullsize_request = GenerateFullSizeRequest()
    fullsize_request.from_json(input_json=request.get_json())
    image = Image.query.filter(Image.id == fullsize_request.id).first_or_404()
    image.fullsize_viewable_path = image.original_path.replace("/original/", "/full_size/").replace(".{ext}".format(ext=image.image_type), ".jpg")
    create_fullsize(image, image.fullsize_viewable_path)
    db.session.commit()
    return "", 204




