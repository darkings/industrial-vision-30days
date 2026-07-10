def convert_to_yolo_labels(image_width, image_height, x1, y1, x2, y2, class_id):
  """
  将像素坐标转换为YOLO标签
  """
  x_center = (x1 + x2) / 2
  y_center = (y1 + y2) / 2
  w = x2 - x1
  h = y2 - y1

  x_norm = x_center / image_width
  y_norm = y_center / image_height
  w_norm = w / image_width
  h_norm = h / image_height

  return f"{class_id} {x_norm:6f} {y_norm:6f} {w_norm:6f} {h_norm:6f}"


def main():
  image_width = 1280
  image_height = 1024
  x1 = 396
  y1 = 72
  x2 = 765
  y2 = 668
  class_id = 0
  label = convert_to_yolo_labels(image_width, image_height, x1, y1, x2, y2, class_id)
  print(label)


if __name__ == "__main__":
  main()
