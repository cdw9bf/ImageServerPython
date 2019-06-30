from members.models import Image
import cv2
import numpy as np
import os
import errno


def create_thumbnail(image: Image):
    if image.file is None:
        pass
    npimg = np.fromfile(image.file.stream, np.uint8)
    #
    print(npimg)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    try:
        os.makedirs(os.path.dirname(image.fullsize_viewable_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
    cv2.imwrite(image.fullsize_viewable_path, img)

