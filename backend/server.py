from flask import Flask, request, jsonify, send_from_directory, Response
import json
from upload.controller import simple_page
app = Flask(__name__)
app.register_blueprint(simple_page, url_prefix="/upload")


@app.route('/healthcheck', methods=["GET"])
def serve_health_check():
    resp = Response(json.dumps({"Status": "Healthy"}))
    resp.headers['Content-Type'] = "application/json"
    return resp



if __name__ == "__main__":
    app.run()
