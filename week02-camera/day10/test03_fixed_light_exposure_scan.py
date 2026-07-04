from pathlib import Path
import sys

import cv2


BASE_DIR = Path(__file__).resolve().parent
WEEK02_DIR = BASE_DIR.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "fixed_light_exposure_scan"
EXPOSURE_TIMES = [800, 1000, 1200, 1500]


if str(WEEK02_DIR) not in sys.path:
  sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import HikCamera
from camera_common.image_stats import calculate_gray_stats


def main():
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  with HikCamera(device_index=0) as camera:
    for exposure_time in EXPOSURE_TIMES:
      camera.set_exposure_time(exposure_time)
      camera.discard_frames(3)
      print(f"\n=== ExposureTime = {exposure_time} us ===")
      for index in range(5):
        image = camera.grab_one_frame()
        stats = calculate_gray_stats(image)
        path = OUTPUT_DIR / f"exposure_{exposure_time}us_frame_{index + 1:02d}.png"
        saved = cv2.imwrite(str(path), image)

        if not saved:
          raise RuntimeError(f"图片保存失败：{path}")

        print(
          f"exposure={exposure_time}us | "
          f"frame={index + 1:02d} \n"
          f"宽={stats['width']} 高={stats['height']} "
          f"mean={stats['mean_gray']:.2f} "
          f"min={stats['min_gray']} max={stats['max_gray']} "
          f"overexposed={stats['overexposed_ratio']:.2f}%"
        )


if __name__ == "__main__":
  main()
