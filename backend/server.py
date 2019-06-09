from flask import Flask, request, jsonify, send_from_directory, Response
import json
from upload_controller import simple_page
from members import db
app = Flask(__name__)
app.register_blueprint(simple_page, url_prefix="/upload")


@app.route('/healthcheck', methods=["GET"])
def serve_health_check():
    resp = Response(json.dumps({"Status": "Healthy"}))
    resp.headers['Content-Type'] = "application/json"
    return resp


if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = "/tmp/"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/image_server'
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    app.run()
