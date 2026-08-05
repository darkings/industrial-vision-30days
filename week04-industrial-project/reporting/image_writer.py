from pathlib import Path

import cv2
import numpy as np
from core import ImageWriteError


def write_image(path: Path, image: np.ndarray):
    """写入图片"""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        success = cv2.imwrite(str(path), image)
        if not success:
            raise ImageWriteError(path)
        return path
    except ImageWriteError:
        raise
    except (OSError, cv2.error, TypeError, ValueError) as exc:
        raise ImageWriteError(path, message=f"图片写入错误 路径:{path} 错误：{exc}")
