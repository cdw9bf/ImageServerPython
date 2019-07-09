from flask import Blueprint, Response, request
from datetime import datetime
from members.json_helpers import DataFormatMisMatch
from members.models import Image
import re
from utils.encoder import DateTimeEncoder
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


@image_page.route('/<img_id>/original', methods=['GET'])
def get_original_image(img_id):
    image = Image.query.filter(Image.id == img_id).first_or_404()
    resp = Response(open(image.original_path, "rb"))
    resp.headers.set('Content-Type', 'image/{0}'.format(image.image_type.lower()))
    return resp


@image_page.route('/<img_id>/metadata', methods=['GET'])
def get_image_metadata(img_id):
    image = Image.query.filter(Image.id == img_id).first_or_404()
    resp = Response(json.dumps(image.to_json(), cls=DateTimeEncoder))
    resp.headers.set('Content-Type', 'application/json')
    return resp


@image_page.route('', methods=['GET'])
def get_images():
    begin_time = request.args.get('begin-time')
    end_time = request.args.get('end-time')

    images = Image.query.filter(Image.date_taken.between('2018-01-01', '2019-03-15')).all()
    resp = Response(json.dumps(images, cls=DateTimeEncoder))
    resp.headers.set('Content-Type', 'application/json')
    return resp


def parse_time(time: str) -> datetime:
    no_time = "(?:19|20)\d{2}-(?:0|1)\d{1}-(?:[0-3])\d{1}"
    with_time = no_time + " (?:[0-2]\d{1}):(?:[0-5]\d{1}):(?:[0-5]\d{1})"
    if len(re.findall(with_time, time)) == 1:
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    elif len(re.findall(no_time, time)) == 1:
        return datetime.strptime(time, "%Y-%m-%d")
    else:
        raise DataFormatMisMatch(
            message="Invalid time passed in search query, should be of format `YYYY-MM-DD [hh-mm-ss]` but was {0}"
                    .format(time))

