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


def generate_clahe_image(clipLimit=2, tileGridSize=(8, 8), image=None):
  """
  生成CLAHE图像
  """
  import cv2

  if image is None:
    raise RuntimeError("输入的图像为空")

  clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
  return clahe.apply(image)


def generate_morphology_image(morph_type="tophat", image=None, kernel=None):
  """
  生成TopHat/BlackHat图
  """
  import cv2

  if morph_type == "tophat":
    morph_mode = cv2.MORPH_TOPHAT
  elif morph_type == "blackhat":
    morph_mode = cv2.MORPH_BLACKHAT
  else:
    raise RuntimeError(f"未知的形态学类型:{morph_type}")
  if image is None:
    raise RuntimeError("输入的图像为空")
  if kernel is None:
    raise RuntimeError("输入的核数据为空")
  return cv2.morphologyEx(image, morph_mode, kernel)


def save_image(path, image):
  """
  保存单张图片
  """
  import cv2

  if image is None:
    raise RuntimeError(f"保存的图片为空：{path}")
  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_outputs(outputs_dir, gray_image, clahe_image, morph_images):
  """
  在输出目录保存文件
  """
  outputs_dir.mkdir(parents=True, exist_ok=True)
  gray_image_path = outputs_dir / "gray.png"
  clahe_image_path = outputs_dir / "clahe.png"
  save_image(gray_image_path, gray_image)
  save_image(clahe_image_path, clahe_image)
  for item in morph_images:
    tophat_image_path = outputs_dir / f"tophat_{item['ksize']}.png"
    blackhat_image_path = outputs_dir / f"blackhat_{item['ksize']}.png"
    save_image(tophat_image_path, item["tophat"])
    save_image(blackhat_image_path, item["blackhat"])


def main():
  import cv2

  inputs_dir = BASE_DIR / "inputs"
  outputs_dir = BASE_DIR / "outputs" / "local_contrast"
  image_file_path = inputs_dir / "defect.png"
  ksizes = [7, 15, 31]

  image = read_local_image(image_file_path)
  gray_image = convert_to_grayscale(image)
  clahe_image = generate_clahe_image(image=gray_image)
  morph_images = []
  for ksize in ksizes:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    tophat_image = generate_morphology_image(
      morph_type="tophat", image=gray_image, kernel=kernel
    )
    blackhat_image = generate_morphology_image(
      morph_type="blackhat", image=gray_image, kernel=kernel
    )
    morph_images.append(
      {"ksize": ksize, "tophat": tophat_image, "blackhat": blackhat_image}
    )
  save_outputs(outputs_dir, gray_image, clahe_image, morph_images)


if __name__ == "__main__":
  main()
