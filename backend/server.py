from flask import Flask, Response
import json
from controllers.upload_controller import upload_page
from controllers.image_controller import image_page
from controllers.operations_controller import operations_page


from members import db
app = Flask(__name__)
app.register_blueprint(upload_page, url_prefix="/upload")
app.register_blueprint(image_page, url_prefix="/images")
app.register_blueprint(operations_page, url_prefix="/operations")




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
