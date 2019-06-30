from members.json_helpers import JsonRequest


class GenerateThumbnailRequest(JsonRequest):
    """
    Thumbnail Data Class
    """
    MODEL = {
        "id": str,
    }

    def __init__(self, id=None):
        self.id = id
