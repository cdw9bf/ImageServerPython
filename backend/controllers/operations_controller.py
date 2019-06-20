from flask import Blueprint, Response, request
from flask import current_app as app
from members.models import Image
from members import db

operations_page = Blueprint('operations_page', __name__, template_folder='templates')


@operations_page.route('/thumbnails', methods=['GET'])
def get_list_of_thumbnails():
    # TODO: Make filter happen on DB Call
    has_thumbnails = Image.query.all()
    resp = Response([str(i) for i in has_thumbnails if i.thumb_nail_path is not None])
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/missing', methods=['GET'])
def get_list_of_missing_thumbnails():
    needs_thumbnails = Image.query.filter(thumb_nail_path=None).all()
    resp = Response([str(i) for i in needs_thumbnails])
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/generate', methods=['POST'])
def generate_thumb_nail():
    data = request.json()
    print(data)
    resp = Response()
    resp.status_code = 204
    return resp
