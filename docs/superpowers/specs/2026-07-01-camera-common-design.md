# Camera Common Design

## Goal

Unify repeated camera capture code into one shared learning module so Day10 and later exercises can import the same Hikvision MVS helper functions instead of copying SDK setup and frame grabbing code into every script.

## Location

Use this project-local path:

```text
D:\Projects\industrial-vision-30days\week02-camera\camera_common\
```

This keeps camera acquisition code inside `week02-camera`, while leaving `week01-opencv` focused on OpenCV image basics.

## Module Layout

```text
week02-camera/
  camera_common/
    __init__.py
    hik_mvs.py
    image_stats.py
```

`hik_mvs.py` owns camera acquisition concerns:

- load the Hikvision MVS SDK from the installed Windows path
- initialize and finalize the SDK
- enumerate devices
- create, open, close, and destroy camera handles
- set common camera parameters such as exposure, gain, trigger mode, and pixel format
- grab one frame and convert it to `numpy.ndarray`
- release SDK image buffers correctly

`image_stats.py` owns image measurement helpers:

- calculate width and height
- calculate mean, min, max
- calculate overexposed pixel ratio
- later extension points: ROI stats, histogram summary, sharpness score

## Import Style

Because the parent folder is named `week02-camera` and contains a hyphen, scripts should add the `week02-camera` directory to `sys.path`, then import `camera_common` as a normal package.

Example:

```python
from pathlib import Path
import sys

WEEK02_DIR = Path(__file__).resolve().parents[1]
if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import grab_one_frame
from camera_common.image_stats import calculate_gray_stats
```

## Learning Policy

Keep Day08 scripts as learning records. They show the full SDK lifecycle step by step and should not be rewritten immediately.

From Day10 onward, new exercises should import from `camera_common` so each lesson can focus on the current topic:

- Day10: stable imaging, FOV, fixed exposure, repeated capture
- Day11: batch capture and dataset folder rules
- Later days: triggering, calibration, measurement, detection

## Initial Implementation Scope

The first implementation should stay small:

- expose a reusable one-frame capture function
- expose simple grayscale statistics
- add one Day10 practice script that imports these helpers

Do not build a large framework yet. The module should grow only when repeated exercises need the same behavior.

## Validation

Validate the shared module by running a Day10 script that:

- imports `camera_common`
- grabs one frame from the MV-13MG-E camera
- computes image statistics
- saves the frame to a Day10 output folder
- prints the camera parameters and saved image path
