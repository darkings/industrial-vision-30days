from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def read_local_image(path):
  """
  读取本地图片路径
  """
  import cv2

  validation_suffixes = [".jpg", ".png"]
  if not path.exists():
    raise RuntimeError(f"文件路径不存在:{path}")
  if path.suffix.lower() not in validation_suffixes:
    raise RuntimeError("当前读取的文件不是指定图片文件")

  image = cv2.imread(str(path))
  if image is None:
    raise RuntimeError("图片读取失败")
  return image


def convert_to_grayscale(image):
  """
  转化灰度图
  """
  import cv2

  if len(image.shape) == 3:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  return image
