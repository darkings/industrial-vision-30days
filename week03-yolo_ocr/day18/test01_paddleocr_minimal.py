from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "inputs" / "image.png"


def verify_paddleocr(image_path):
  """
  PaddleOCR 验证
  """
  import cv2
  from paddleocr import PaddleOCR

  # 初始化ocr
  ocr = PaddleOCR(
    use_textline_orientation=True,
    enable_mkldnn=False,
    lang="ch",
  )

  # 读取图片
  image = cv2.imread(str(image_path))
  if image is None:
    raise RuntimeError(f"图片读取失败:{image_path}")

  # OCR识别
  results = ocr.predict(image)

  # 打印读取结果
  for result in results:
    if result is None:
      continue
    texts = result.get("rec_texts", [])
    scores = result.get("rec_scores", [])
    # 获取检测框坐标，通常为4个点的多边形
    boxes = result.get("dt_polys", [])

    # 确保三个列表长度一致后排序
    # 排序是为了能正确的输出文本的顺序
    if len(texts) == len(scores) == len(boxes):
      # 将文本、置信度、检测框坐标打包
      combined = zip(boxes, texts, scores)

      # 判断读取引擎图像的真实翻转状态
      is_y_inverted = False
      # 检查整图是否被翻转了 180 度 (导致全局 Y 坐标倒置)
      doc_angle = result.get("doc_preprocessor_res", {}).get("angle")
      # 检查文本行是否普遍被判定为 180 度 (作为备用特征)
      line_angles = result.get("textline_orientation_angles", [])
      # 综合判定逻辑 (根据 Paddle 的输出，角度通常是 int 或 str)
      if str(doc_angle) == "180" or doc_angle == 180:
        is_y_inverted = True
      elif line_angles:
        # 如果没有整图角度，但超过半数的文本行被判定为 180 度，也视同倒置
        inverted_count = sum(1 for a in line_angles if str(a) == "180" or a == 180)
        if inverted_count > len(line_angles) / 2:
          is_y_inverted = True
      print(f"[Debug] 坐标系倒置状态: {is_y_inverted} (doc_angle: {doc_angle})")

      # 按照检测框动态排序
      # 如果倒置 (Y轴从下往上递增) -> 降序 reverse=True
      # 如果正常 (Y轴从上往下递增) -> 升序 reverse=False
      # item[0] 为每个boxes
      # point 每个boxes 循环坐标点
      # point[1] 每个坐标点的y坐标
      sorted_combined = sorted(
        combined,
        key=lambda item: min(point[1] for point in item[0]),
        reverse=is_y_inverted,
      )
      for _, text, confidence in sorted_combined:
        print(f"文本：{text} (置信度{confidence:.3f})")
    else:
      # 如果没有dt_polys 直接输出文本
      for text, confidence in zip(texts, scores):
        print(f"文本：{text} (置信度{confidence:.3f})")


def main():
  verify_paddleocr(IMAGE_FILE_PATH)


if __name__ == "__main__":
  main()
