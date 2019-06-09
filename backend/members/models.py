from . import db
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    date = db.Column(db.DateTime())
    save_path = db.Column(db.String(240))
    thumb_nail_path = db.Column(db.String(240))

    def __init__(self, file, file_name, tags, date, save_path, thumb_nail_path, id=None):
        self.id = id if id is not None else uuid.uuid4()
        self.file = file
        self.file_name = file_name
        self.tags = tags
        self.date = date
        self.save_path = save_path
        self.thumb_nail_path = thumb_nail_path

