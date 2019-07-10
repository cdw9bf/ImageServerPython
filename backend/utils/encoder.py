import json
from members.models import Image, MasterRecord
from datetime import date, datetime
from uuid import UUID


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        elif isinstance(o, Image):
            return o.to_json()
        elif isinstance(o, MasterRecord):
            return o.to_json()
        elif isinstance(o, UUID):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)

