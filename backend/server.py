from flask import Flask, Response
import json
from controllers.upload_controller import upload_page
from controllers.image_controller import image_page
from controllers.operations_controller import operations_page
from members import db
from members.json_helpers import DataFormatMisMatch, InvalidInputJson

app = Flask(__name__)
app.register_blueprint(upload_page, url_prefix="/upload")
app.register_blueprint(image_page, url_prefix="/images")
app.register_blueprint(operations_page, url_prefix="/operations")


@app.route('/healthcheck', methods=["GET"])
def serve_health_check():
    resp = Response(json.dumps({"Status": "Healthy"}))
    resp.headers['Content-Type'] = "application/json"
    return resp


@app.errorhandler(DataFormatMisMatch)
def handle_invalid_usage(error):
    """
    Error Handler for DataFormatMisMatch error. Returns a 400 code to requester from any thrown DataFormatMisMatch Exception
    :param error: DataFormatMisMatch Exception
    :return:
    """
    resp = Response(json.dumps(error.to_dict()))
    resp.status_code = error.status_code
    return resp


@app.errorhandler(InvalidInputJson)
def handle_invalid_usage(error):
    """
    Error Handler for InvalidInputJson error. Returns a 400 code to requester from any thrown InvalidInputJson Exception
    :param error: InvalidInputJson Exception
    :return:
    """
    resp = Response(json.dumps(error.to_dict()))
    resp.status_code = error.status_code
    return resp


if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = "/tmp/"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/image_server'
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    app.run()
