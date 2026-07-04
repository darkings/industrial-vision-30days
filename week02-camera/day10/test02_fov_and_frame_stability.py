"""
练习目标：
  1.使用 camera_common 连续抓取多帧
  2.保存每一帧图片
  3.统计每一帧的亮度信息
  4.观察画面是否稳定
"""

from pathlib import Path
import sys

import cv2


BASE_DIR = Path(__file__).resolve().parent
WEEK02_DIR = BASE_DIR.parent

OUTPUT_DIR = BASE_DIR / "outputs" / "fov_stability"


if str(WEEK02_DIR) not in sys.path:
  sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import HikCamera
from camera_common.image_stats import calculate_gray_stats


def main():
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  with HikCamera(device_index=0, exposure_time_us=1000.0) as camera:
    camera.discard_frames(3)
    for index in range(5):
      image = camera.grab_one_frame()
      stats = calculate_gray_stats(image)
      saved_path = OUTPUT_DIR / f"frame_{index + 1:02d}.png"
      saved = cv2.imwrite(str(saved_path), image)
      if not saved:
        raise RuntimeError(f"图片保存失败：{saved_path}")
      print(f"图像 shape：{image.shape}")
      print(
        f"宽={stats['width']} 高={stats['height']} "
        f"mean={stats['mean_gray']:.2f} "
        f"min={stats['min_gray']} max={stats['max_gray']} "
        f"overexposed={stats['overexposed_ratio']:.2f}%"
      )
      # print(f"保存路径：{saved_path}")


if __name__ == "__main__":
  main()
