from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "IMG_9859.png"
OUTPUTS_FILE_PATH = BASE_DIR / "outputs" / "erode_dilate"
OUTPUTS_FILE_PATH.mkdir(parents=True, exist_ok=True)
# 图片保存路径
image_name = IMAGE_FILE_PATH.stem
gray_path = OUTPUTS_FILE_PATH / f"{image_name}_gray.png"
binary_inv_path = OUTPUTS_FILE_PATH / f"{image_name}_binary_inv.png"
eroded_path = OUTPUTS_FILE_PATH / f"{image_name}_eroded.png"
dilated_path = OUTPUTS_FILE_PATH / f"{image_name}_dilated.png"
# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片加载失败")
# 转化为灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# OTSU 反二值化
used_threshold, binary_inv_image = cv2.threshold(
    gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
)
print(f"自动阈值为：{used_threshold}")

# 3x3 矩形结构元素
kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,  # 矩形结构元素
    (3, 3),  # 3x3 的核
)

# 腐蚀一次
eroded_image = cv2.erode(
    binary_inv_image,  # 单通道二值图
    kernel,  # 3x3的矩形结构元素
    iterations=1,  # 腐蚀一次
)

# 膨胀一次
dilated_image = cv2.dilate(
    binary_inv_image,  # 单通道二值图
    kernel,  # 3x3的矩形结构元素
    iterations=1,  # 膨胀一次
)

# 保存比较结果
saved_gray = cv2.imwrite(str(gray_path), gray_image)
saved_binary_inv = cv2.imwrite(str(binary_inv_path), binary_inv_image)
saved_eroded = cv2.imwrite(str(eroded_path), eroded_image)
saved_dilated = cv2.imwrite(str(dilated_path), dilated_image)

# 统计3张图白色像素数量
binary_inv_white_pixels = cv2.countNonZero(binary_inv_image)
eroded_white_pixels = cv2.countNonZero(eroded_image)
dilated_white_pixels = cv2.countNonZero(dilated_image)

# 结果
results = [
    [saved_gray, gray_path, 0],
    [saved_binary_inv, binary_inv_path, binary_inv_white_pixels],
    [saved_eroded, eroded_path, eroded_white_pixels],
    [saved_dilated, dilated_path, dilated_white_pixels],
]

# 打印
for saved, path, pixels in results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败！")
    if pixels != 0:
        print(f"{path.name} 白色像素数量为：{pixels}")
    else:
        continue
