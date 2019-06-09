from flask import Blueprint, Response
import json

# What do I want to do?
#
# 1. Upload full size image
# 2. Save Image to disk
# 3. Create Entries in DB
# 4. Create Thumbnail for serving image in the future

simple_page = Blueprint('simple_page', __name__, template_folder='templates')

@simple_page.route('/show')
def blueprint_route():
    resp = Response(json.dumps({"Status": "Healthy"}))
    resp.headers['Content-Type'] = "application/json"
    return resp

