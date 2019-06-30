from flask import Blueprint, Response, request
from members.models import Image

image_page = Blueprint('image_page', __name__, template_folder='templates')


@image_page.route('/images/<img_id>/original', methods=['GET'])
def get_original_image(img_id):
    image = Image.query.filter(id=img_id).get()


