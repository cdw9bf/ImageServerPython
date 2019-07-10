from flask import Blueprint, Response, request
from datetime import datetime
from members.json_helpers import DataFormatMisMatch
from members.models import Image, MasterRecord
from sqlalchemy import and_
import re
from utils.encoder import DateTimeEncoder
import json
from constants import FULL, THUMBNAIL, ORIGINAL


image_page = Blueprint('image_page', __name__, template_folder='templates')


@image_page.route('/<img_id>/thumbnail', methods=['GET'])
def get_thumbnail_image(img_id):
    image = Image.query.filter(and_(Image.uuid == img_id, Image.size == THUMBNAIL)).first_or_404()
    resp = Response(open(image.path, "rb"))
    resp.headers.set('Content-Type', 'image/jpeg')
    return resp


@image_page.route('/<img_id>/full-size', methods=['GET'])
def get_full_size_image(img_id):
    image = Image.query.filter(and_(Image.uuid == img_id, Image.size == FULL)).first_or_404()
    resp = Response(open(image.path, "rb"))
    resp.headers.set('Content-Type', 'image/jpeg')
    return resp


@image_page.route('/<img_id>/original', methods=['GET'])
def get_original_image(img_id):
    image = Image.query.filter(and_(Image.uuid == img_id, Image.size == ORIGINAL)).first_or_404()
    resp = Response(open(image.path, "rb"))
    resp.headers.set('Content-Type', 'image/{0}'.format(image.image_type.lower()))
    return resp


@image_page.route('/<img_id>/metadata', methods=['GET'])
def get_image_metadata(img_id):
    image = MasterRecord.query.filter(MasterRecord.uuid == img_id).first_or_404()
    resp = Response(json.dumps(image.to_json(), cls=DateTimeEncoder))
    resp.headers.set('Content-Type', 'application/json')
    return resp


@image_page.route('', methods=['GET'])
def get_images():
    begin_time = parse_time(request.args.get('begin-time', '1980-01-01'))
    end_time = parse_time(request.args.get('end-time', '2099-01-01'))

    images = MasterRecord.query.filter(MasterRecord.date_taken.between(begin_time, end_time)).all()
    resp = Response(json.dumps({"ids": [i.uuid for i in images]}, cls=DateTimeEncoder))
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

