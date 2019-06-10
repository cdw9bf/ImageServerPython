from flask import Blueprint, Response, request


image_page = Blueprint('simple_page', __name__, template_folder='templates')
