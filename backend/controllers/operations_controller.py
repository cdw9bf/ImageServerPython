from flask import Blueprint, Response, request
from flask import current_app as app
from members.models import Image
from members.inboud import GenerateThumbnailRequest

operations_page = Blueprint('operations_page', __name__, template_folder='templates')


@operations_page.route('/thumbnails', methods=['GET'])
def get_list_of_thumbnails():
    has_thumbnails = Image.query.filter(Image.thumb_nail_path.isnot(None)).all()
    resp = Response([str(i) for i in has_thumbnails])
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/missing', methods=['GET'])
def get_list_of_missing_thumbnails():
    needs_thumbnails = Image.query.filter(Image.thumb_nail_path.is_(None)).all()
    resp = Response([str(i) for i in needs_thumbnails])
    resp.headers['Content-Type'] = "application/json"
    return resp


@operations_page.route('/thumbnails/generate', methods=['POST'])
def generate_thumb_nail():
    # Model
    #
    thumbnail_request = GenerateThumbnailRequest()
    thumbnail_request.from_json(input_json=request.get_json())
    image = Image.query.filter(Image.id == thumbnail_request.id).first_or_404()
    print(image.file)
    return "", 204

