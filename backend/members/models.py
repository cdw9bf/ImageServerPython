from . import db
import uuid
from werkzeug.datastructures import FileStorage
from sqlalchemy.dialects.postgresql import UUID
from typing import Dict
from datetime import datetime


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    original_path = db.Column(db.String(240), nullable=False)
    fullsize_viewable_path = db.Column(db.String(240))
    thumb_nail_path = db.Column(db.String(240))

    def __init__(self, image: FileStorage, file_name: str, tags: Dict, date: datetime, save_path: str, fullsize_viewable_path: str=None, thumb_nail_path: str = None, id=None):
        self.id = id if id is not None else uuid.uuid4()
        self.file = image
        self.file_name = file_name
        self.tags = tags
        self.date = date
        self.original_path = save_path
        self.thumb_nail_path = thumb_nail_path
        self.fullsize_viewable_path = fullsize_viewable_path
        self.img_type = save_path.rsplit(".", 1)[-1]

