import json
from members.models import Image
from datetime import date, datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Image):
            return o.to_json()
        return json.JSONEncoder.default(self, o)

