from . import db
import uuid as uuid_gen
import json
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import UUID
from typing import Dict
from datetime import datetime

#
# class Image(db.Model):
#     __tablename__ = 'images'
#     id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
#     date_taken = db.Column(db.DateTime(), nullable=True)
#     date_uploaded = db.Column(db.DateTime(), nullable=False)
#     original_path = db.Column(db.String(240), nullable=False)
#     fullsize_viewable_path = db.Column(db.String(240), nullable=True)
#     thumb_nail_path = db.Column(db.String(240), nullable=True)
#     tags = db.Column(JSON, nullable=True)
#     image_type = db.Column(db.String(10), nullable=False)
#
#     def __init__(self, date_uploaded: datetime, save_path: str, date_taken: datetime=None,tags: Dict=None, fullsize_viewable_path: str=None, thumb_nail_path: str = None, id=None):
#         self.id = id if id is not None else uuid_gen.uuid4()
#         self.date_uploaded = date_uploaded
#         self.date_taken = date_taken
#         self.original_path = save_path
#         self.fullsize_viewable_path = fullsize_viewable_path
#         self.thumb_nail_path = thumb_nail_path
#         self.tags = tags
#         self.image_type = save_path.rsplit(".", 1)[-1]
#
#     def __repr__(self):
#         d = {
#             "id": str(self.id),
#             "date_taken": str(self.date_taken),
#             "date_uploaded": str(self.date_uploaded),
#             "img_type": self.image_type
#         }
#         return json.dumps(d)
#
#     def to_json(self):
#         return {
#             "name": self.original_path.split("/")[-1],
#             "id": str(self.id),
#             "date_taken": self.date_taken,
#             "date_uploaded": self.date_uploaded,
#             "tags": self.tags,
#             "img_type": self.image_type
#         }


class Image(db.Model):
    __tablename__ = 'images'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True)
    size = db.Column(db.String(10), nullable=False, primary_key=True)
    date_uploaded = db.Column(db.DateTime(), nullable=False)
    path = db.Column(db.String(240), nullable=False)
    image_format = db.Column(db.String(10), nullable=False)

    def __init__(self, img_id, date_uploaded: datetime, path: str, size: str):
        self.uuid = img_id
        self.date_uploaded = date_uploaded
        self.path = path
        self.size = size
        self.image_format = path.rsplit(".", 1)[-1]

    def __repr__(self):
        d = {
            "name": self.path.split("/")[-1],
            "uuid": str(self.uuid),
            "date_uploaded": str(self.date_uploaded),
            "image_size": self.size,
            "image_format": self.image_format
        }
        return json.dumps(d)

    def to_json(self):
        return {
            "name": self.path.split("/")[-1],
            "uuid": str(self.uuid),
            "date_uploaded": self.date_uploaded,
            "image_size": self.size,
            "image_format": self.image_format
        }

#
# | uuid             | date_taken | date_added         | tags |
# | :--------------: | :--------: | :----------------: | :--: |
# | UUID PRIMARY KEY | TIMESTAMP  | TIMESTAMP NOT NULL | JSON |
#
#
# | uuid             | path          | image_format  | size             | date_uploaded      |
# | :--------------: | :-----------: | :-----------: | :--------------: | :----------------: |
# | UUID PRIMARY KEY | TEXT NOT NULL | TEXT NOT NULL | TEXT PRIMARY KEY | TIMESTAMP NOT NULL |


class MasterRecord(db.Model):
    __tablename__ = 'master_records'
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    date_taken = db.Column(db.DateTime(), nullable=True)
    date_added = db.Column(db.DateTime(), nullable=False)
    tags = db.Column(JSON, nullable=True)

    def __init__(self, date_added: datetime, img_id: str = None, date_taken: datetime = None, tags: Dict = None):
        self.uuid = img_id if img_id is not None else uuid_gen.uuid4()
        self.date_added = date_added
        self.date_taken = date_taken
        self.tags = tags

    def to_json(self):
        return {
            'uuid': str(self.uuid),
            'date_added': self.date_added,
            'date_taken': self.date_taken,
            'tags': self.tags
        }

    def __repr__(self):
        return json.dumps({
            'uuid': str(self.uuid),
            'date_added': str(self.date_added),
            'date_taken': str(self.date_taken),
            'tags': self.tags
        })


