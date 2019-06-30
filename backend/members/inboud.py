from members.json_helpers import JsonRequest


class GenerateThumbnailRequest(JsonRequest):
    """
    Thumbnail Data Class
    """
    MODEL = {
        "ids": list,
    }

    def __init__(self, ids=None):
        self.ids = ids
