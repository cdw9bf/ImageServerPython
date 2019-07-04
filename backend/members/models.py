from . import db
import uuid
import json
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import UUID
from typing import Dict
from datetime import datetime


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    date_taken = db.Column(db.DateTime(), nullable=True)
    date_uploaded = db.Column(db.DateTime(), nullable=False)
    original_path = db.Column(db.String(240), nullable=False)
    fullsize_viewable_path = db.Column(db.String(240), nullable=True)
    thumb_nail_path = db.Column(db.String(240), nullable=True)
    tags = db.Column(JSON, nullable=True)
    image_type = db.Column(db.String(10), nullable=False)

    def __init__(self, date_uploaded: datetime, ,save_path: str, date_taken: datetime=None,tags: Dict=None, fullsize_viewable_path: str=None, thumb_nail_path: str = None, id=None):
        self.id = id if id is not None else uuid.uuid4()
        self.date_uploaded = date_uploaded
        self.date_taken = date_taken
        self.original_path = save_path
        self.fullsize_viewable_path = fullsize_viewable_path
        self.thumb_nail_path = thumb_nail_path
        self.tags = tags
        self.image_type = save_path.rsplit(".", 1)[-1]

    def __repr__(self):
        d = {
            "id": str(self.id),
            "date": str(self.date),
            "img_type": self.image_type
        }
        return json.dumps(d)

    def to_json(self):
        return {
            "name": self.original_path.split("/")[-1],
            "id": str(self.id),
            "date": str(self.date),
            "tags": self.tags,
            "img_type": self.image_type
        }
