from flask import Blueprint, Response
from members.models import Image
from utils.json_helpers import DateTimeEncoder
import json

image_page = Blueprint('image_page', __name__, template_folder='templates')


@image_page.route('/<img_id>/thumbnail', methods=['GET'])
def get_thumbnail_image(img_id):
    image = Image.query.filter(Image.id == img_id).first_or_404()
    if image.thumb_nail_path is None:
        return "No Thumbnail Path", 400
    resp = Response(open(image.thumb_nail_path, "rb"))
    resp.headers.set('Content-Type', 'image/jpeg')
    return resp


@image_page.route('/<img_id>/full-size', methods=['GET'])
def get_full_size_image(img_id):
    image = Image.query.filter(Image.id == img_id).first_or_404()
    if image.fullsize_viewable_path is None:
        return "No Full Size Path", 400
    resp = Response(open(image.fullsize_viewable_path, "rb"))
    resp.headers.set('Content-Type', 'image/jpeg')
    return resp


@image_page.route('/<img_id>/metadata', methods=['GET'])
def get_image_metadata(img_id):
    image = Image.query.filter(Image.id == img_id).first_or_404()
    if image.fullsize_viewable_path is None:
        return "No Full Size Path", 400
    resp = Response(json.dumps(image.to_json(), cls=DateTimeEncoder))
    resp.headers.set('Content-Type', 'application/json')
    return resp

