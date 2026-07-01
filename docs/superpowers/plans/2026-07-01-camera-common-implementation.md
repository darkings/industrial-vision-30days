# 相机公共模块 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 Day08 中已经验证过的海康 MVS 抓图流程和图像统计函数整理到 `week02-camera\camera_common`，让 Day10 以及后续练习可以统一导入调用。

**Architecture:** `camera_common.hik_mvs` 负责 SDK 路径、设备枚举、相机生命周期、抓帧、曝光设置；`camera_common.image_stats` 负责纯图像统计。Day08 脚本保留为学习记录，新建 Day10 验证脚本调用公共模块。

**Tech Stack:** Python 3.12、Hikvision MVS Python SDK、ctypes、numpy、OpenCV、pytest。

---

## 文件结构

- 修改：`D:\Projects\industrial-vision-30days\week02-camera\camera_common\__init__.py`
  - 导出公共模块说明，保持轻量。
- 修改：`D:\Projects\industrial-vision-30days\week02-camera\camera_common\image_stats.py`
  - 提供 `calculate_gray_stats(image)`，不依赖相机。
- 修改：`D:\Projects\industrial-vision-30days\week02-camera\camera_common\hik_mvs.py`
  - 从 Day08 已验证代码整理 SDK 加载、设备打印、打开相机、抓帧、释放资源、曝光设置。
- 新建：`D:\Projects\industrial-vision-30days\week02-camera\camera_common\test_image_stats.py`
  - 离线测试图像统计函数，不连接相机。
- 新建：`D:\Projects\industrial-vision-30days\week02-camera\day10\test01_grab_one_frame_with_common.py`
  - Day10 第 2 节验证脚本：调用 `camera_common` 抓一帧、保存、打印统计。

---

### Task 1: 图像统计公共函数

**Files:**
- Modify: `D:\Projects\industrial-vision-30days\week02-camera\camera_common\image_stats.py`
- Create: `D:\Projects\industrial-vision-30days\week02-camera\camera_common\test_image_stats.py`

- [ ] **Step 1: 写离线测试**

```python
import numpy as np

from image_stats import calculate_gray_stats


def test_calculate_gray_stats_counts_saturated_pixels():
    image = np.array(
        [
            [0, 128, 255],
            [255, 64, 32],
        ],
        dtype=np.uint8,
    )

    stats = calculate_gray_stats(image)

    assert stats["width"] == 3
    assert stats["height"] == 2
    assert stats["mean_gray"] == 122.33
    assert stats["min_gray"] == 0
    assert stats["max_gray"] == 255
    assert stats["overexposed_pixels"] == 2
    assert stats["overexposed_ratio"] == 33.33
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
& D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe -m pytest D:\Projects\industrial-vision-30days\week02-camera\camera_common\test_image_stats.py -v
```

Expected: FAIL，原因是 `calculate_gray_stats` 还没有实现。

- [ ] **Step 3: 实现 `calculate_gray_stats`**

```python
from __future__ import annotations


def calculate_gray_stats(image):
    """
    统计灰度或 BGR 图像的基础亮度信息。
    """

    import numpy as np

    if image.ndim == 3:
        import cv2

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    height, width = gray.shape[:2]
    pixel_count = width * height
    overexposed_pixels = int(np.count_nonzero(gray == 255))

    return {
        "width": width,
        "height": height,
        "mean_gray": round(float(np.mean(gray)), 2),
        "min_gray": int(np.min(gray)),
        "max_gray": int(np.max(gray)),
        "overexposed_pixels": overexposed_pixels,
        "overexposed_ratio": round(overexposed_pixels / pixel_count * 100, 2),
    }
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
& D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe -m pytest D:\Projects\industrial-vision-30days\week02-camera\camera_common\test_image_stats.py -v
```

Expected: PASS。

---

### Task 2: 海康 MVS 公共抓帧模块

**Files:**
- Modify: `D:\Projects\industrial-vision-30days\week02-camera\camera_common\hik_mvs.py`
- Modify: `D:\Projects\industrial-vision-30days\week02-camera\camera_common\__init__.py`

- [ ] **Step 1: 从 Day08 整理 SDK 基础函数**

在 `hik_mvs.py` 中放入这些函数：

```python
from __future__ import annotations

import importlib
import os
import sys
from ctypes import POINTER, byref, c_ubyte, cast, memset, sizeof
from pathlib import Path


MVS_INSTALL_DIR = Path(r"C:\Program Files (x86)\MVS")


def find_mvimport_dir() -> Path:
    env_development_dir = os.getenv("MVCAM_COMMON_RUNENV")
    candidate_dirs = []

    if env_development_dir:
        candidate_dirs.append(
            Path(env_development_dir) / "Samples" / "Python" / "MvImport"
        )

    candidate_dirs.append(
        MVS_INSTALL_DIR / "Development" / "Samples" / "Python" / "MvImport"
    )

    for mvimport_dir in candidate_dirs:
        if (mvimport_dir / "MvCameraControl_class.py").exists():
            return mvimport_dir

    raise FileNotFoundError(
        "没有找到 MvCameraControl_class.py。请确认 MVS 已安装，"
        "并检查 MVCAM_COMMON_RUNENV 环境变量或 MVS_INSTALL_DIR。"
    )


def load_hik_sdk():
    mvimport_dir = find_mvimport_dir()
    if str(mvimport_dir) not in sys.path:
        sys.path.insert(0, str(mvimport_dir))
    return importlib.import_module("MvCameraControl_class")


def check_sdk_ret(ret: int, action: str) -> None:
    if ret != 0:
        raise RuntimeError(f"{action}失败，错误码 ret[0x{ret:x}]")
```

- [ ] **Step 2: 整理设备信息和像素转换函数**

继续在 `hik_mvs.py` 中放入：

```python
def decode_ctypes_string(ctypes_char_array) -> str:
    raw_bytes = memoryview(ctypes_char_array).tobytes()
    raw_bytes = raw_bytes.split(b"\x00", 1)[0]

    for encoding in ("gbk", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("latin-1", errors="replace")


def is_mono_pixel_format(sdk, pixel_type: int) -> bool:
    mono_formats = (
        sdk.PixelType_Gvsp_Mono8,
        sdk.PixelType_Gvsp_Mono10,
        sdk.PixelType_Gvsp_Mono10_Packed,
        sdk.PixelType_Gvsp_Mono12,
        sdk.PixelType_Gvsp_Mono12_Packed,
        sdk.PixelType_Gvsp_Mono14,
        sdk.PixelType_Gvsp_Mono16,
    )
    return pixel_type in mono_formats


def print_device_list(sdk, device_list) -> None:
    print(f"发现设备数量：{device_list.nDeviceNum}")

    for index in range(device_list.nDeviceNum):
        device_info = cast(
            device_list.pDeviceInfo[index],
            POINTER(sdk.MV_CC_DEVICE_INFO),
        ).contents

        if device_info.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            gige_info = device_info.SpecialInfo.stGigEInfo
            model_name = decode_ctypes_string(gige_info.chModelName)
            serial_number = decode_ctypes_string(gige_info.chSerialNumber)
            ip1 = (gige_info.nCurrentIp & 0xFF000000) >> 24
            ip2 = (gige_info.nCurrentIp & 0x00FF0000) >> 16
            ip3 = (gige_info.nCurrentIp & 0x0000FF00) >> 8
            ip4 = gige_info.nCurrentIp & 0x000000FF

            print(f"[{index}] GigE 相机")
            print(f"    型号：{model_name}")
            print(f"    序列号：{serial_number}")
            print(f"    当前 IP：{ip1}.{ip2}.{ip3}.{ip4}")
        else:
            print(f"[{index}] 非 GigE 设备，传输层类型：{device_info.nTLayerType}")
```

- [ ] **Step 3: 整理抓帧和曝光函数**

继续在 `hik_mvs.py` 中放入：

```python
def convert_frame_to_numpy(sdk, cam, frame_out):
    import cv2
    import numpy as np

    frame_info = frame_out.stFrameInfo
    width = frame_info.nWidth
    height = frame_info.nHeight
    src_pixel_type = frame_info.enPixelType

    if is_mono_pixel_format(sdk, src_pixel_type):
        dst_pixel_type = sdk.PixelType_Gvsp_Mono8
        channel_count = 1
    else:
        dst_pixel_type = sdk.PixelType_Gvsp_RGB8_Packed
        channel_count = 3

    dst_buffer_size = width * height * channel_count
    dst_buffer = (c_ubyte * dst_buffer_size)()

    convert_param = sdk.MV_CC_PIXEL_CONVERT_PARAM_EX()
    memset(byref(convert_param), 0, sizeof(convert_param))
    convert_param.nWidth = width
    convert_param.nHeight = height
    convert_param.pSrcData = frame_out.pBufAddr
    convert_param.nSrcDataLen = frame_info.nFrameLen
    convert_param.enSrcPixelType = src_pixel_type
    convert_param.enDstPixelType = dst_pixel_type
    convert_param.pDstBuffer = dst_buffer
    convert_param.nDstBufferSize = dst_buffer_size

    ret = cam.MV_CC_ConvertPixelTypeEx(convert_param)
    check_sdk_ret(ret, "转换像素格式")

    image = np.frombuffer(dst_buffer, dtype=np.uint8, count=dst_buffer_size)

    if channel_count == 1:
        return image.reshape((height, width)).copy()

    image = image.reshape((height, width, 3))
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def set_manual_exposure(cam, exposure_time_us: float) -> None:
    ret = cam.MV_CC_SetEnumValue("ExposureAuto", 0)
    check_sdk_ret(ret, "关闭自动曝光")

    ret = cam.MV_CC_SetFloatValue("ExposureTime", float(exposure_time_us))
    check_sdk_ret(ret, f"设置曝光时间 {exposure_time_us} us")


def get_current_exposure_time(sdk, cam) -> float:
    exposure_value = sdk.MVCC_FLOATVALUE()
    memset(byref(exposure_value), 0, sizeof(exposure_value))

    ret = cam.MV_CC_GetFloatValue("ExposureTime", exposure_value)
    check_sdk_ret(ret, "读取当前曝光时间")

    return float(exposure_value.fCurValue)


def grab_one_frame_from_open_camera(sdk, cam, timeout_ms: int = 1000):
    frame_out = sdk.MV_FRAME_OUT()
    memset(byref(frame_out), 0, sizeof(frame_out))

    ret = cam.MV_CC_GetImageBuffer(frame_out, timeout_ms)
    check_sdk_ret(ret, "抓取一帧")

    try:
        return convert_frame_to_numpy(sdk, cam, frame_out)
    finally:
        cam.MV_CC_FreeImageBuffer(frame_out)
```

- [ ] **Step 4: 实现高级函数 `grab_one_frame`**

继续在 `hik_mvs.py` 中放入：

```python
def grab_one_frame(device_index: int = 0, exposure_time_us: float | None = None):
    sdk = load_hik_sdk()
    cam = None
    is_sdk_initialized = False
    is_handle_created = False
    is_device_opened = False
    is_grabbing = False

    try:
        sdk.MvCamera.MV_CC_Initialize()
        is_sdk_initialized = True

        device_list = sdk.MV_CC_DEVICE_INFO_LIST()
        tlayer_type = (
            sdk.MV_GIGE_DEVICE
            | sdk.MV_USB_DEVICE
            | sdk.MV_GENTL_CAMERALINK_DEVICE
            | sdk.MV_GENTL_CXP_DEVICE
            | sdk.MV_GENTL_XOF_DEVICE
        )

        ret = sdk.MvCamera.MV_CC_EnumDevices(tlayer_type, device_list)
        check_sdk_ret(ret, "枚举设备")

        if device_list.nDeviceNum == 0:
            raise RuntimeError("没有发现相机。请先确认 MVS 能预览，且网卡和相机在同一网段。")

        print_device_list(sdk, device_list)

        if device_index >= device_list.nDeviceNum:
            raise ValueError(f"设备序号 {device_index} 不存在。")

        cam = sdk.MvCamera()
        selected_device = cast(
            device_list.pDeviceInfo[device_index],
            POINTER(sdk.MV_CC_DEVICE_INFO),
        ).contents

        ret = cam.MV_CC_CreateHandle(selected_device)
        check_sdk_ret(ret, "创建相机句柄")
        is_handle_created = True

        ret = cam.MV_CC_OpenDevice(sdk.MV_ACCESS_Exclusive, 0)
        check_sdk_ret(ret, "打开设备")
        is_device_opened = True

        if selected_device.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            packet_size = cam.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    print(f"警告：设置 GigE 包大小失败 ret[0x{ret:x}]")

        ret = cam.MV_CC_SetEnumValue("TriggerMode", sdk.MV_TRIGGER_MODE_OFF)
        check_sdk_ret(ret, "关闭触发模式")

        if exposure_time_us is not None:
            set_manual_exposure(cam, exposure_time_us)

        ret = cam.MV_CC_StartGrabbing()
        check_sdk_ret(ret, "开始取流")
        is_grabbing = True

        return grab_one_frame_from_open_camera(sdk, cam)

    finally:
        if cam is not None and is_grabbing:
            cam.MV_CC_StopGrabbing()
        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()
        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()
        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()
```

- [ ] **Step 5: 更新 `__init__.py`**

```python
"""
week02-camera 的相机公共工具。
"""
```

---

### Task 3: Day10 公共模块验证脚本

**Files:**
- Create: `D:\Projects\industrial-vision-30days\week02-camera\day10\test01_grab_one_frame_with_common.py`

- [ ] **Step 1: 编写验证脚本**

```python
# -- coding: utf-8 --
"""
Day10 第 2 节：使用 camera_common 抓取一帧。
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
WEEK02_DIR = BASE_DIR.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "common_grab_one_frame"
OUTPUT_IMAGE_PATH = OUTPUT_DIR / "day10_common_grab_one_frame.png"

if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import grab_one_frame
from camera_common.image_stats import calculate_gray_stats


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image = grab_one_frame(device_index=0, exposure_time_us=1000.0)
    stats = calculate_gray_stats(image)

    saved = cv2.imwrite(str(OUTPUT_IMAGE_PATH), image)
    if not saved:
        raise RuntimeError(f"保存图片失败：{OUTPUT_IMAGE_PATH}")

    print("=== Day10 公共模块抓图验证 ===")
    print(f"图像 shape：{image.shape}")
    print(
        f"宽={stats['width']} 高={stats['height']} "
        f"mean={stats['mean_gray']:.2f} "
        f"min={stats['min_gray']} max={stats['max_gray']} "
        f"overexposed={stats['overexposed_ratio']:.2f}%"
    )
    print(f"保存路径：{OUTPUT_IMAGE_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行 Day10 验证脚本**

Run:

```powershell
& D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe D:\Projects\industrial-vision-30days\week02-camera\day10\test01_grab_one_frame_with_common.py
```

Expected: 控制台能打印相机设备信息、图像 shape、灰度统计值、保存路径；输出目录中生成 `day10_common_grab_one_frame.png`。

---

### Task 4: 回归检查和提交

**Files:**
- Check: `D:\Projects\industrial-vision-30days\week02-camera\camera_common\*.py`
- Check: `D:\Projects\industrial-vision-30days\week02-camera\day10\test01_grab_one_frame_with_common.py`

- [ ] **Step 1: 运行离线测试**

Run:

```powershell
& D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe -m pytest D:\Projects\industrial-vision-30days\week02-camera\camera_common\test_image_stats.py -v
```

Expected: PASS。

- [ ] **Step 2: 运行相机验证脚本**

Run:

```powershell
& D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe D:\Projects\industrial-vision-30days\week02-camera\day10\test01_grab_one_frame_with_common.py
```

Expected: 成功抓图并保存到 Day10 输出目录。

- [ ] **Step 3: 查看工作区变更**

Run:

```powershell
git status --short
```

Expected: 只提交公共模块、Day10 验证脚本和计划文档；不提交用户实验图片变更。

- [ ] **Step 4: 提交实现**

Run:

```powershell
git add docs/superpowers/plans/2026-07-01-camera-common-implementation.md week02-camera/camera_common/__init__.py week02-camera/camera_common/image_stats.py week02-camera/camera_common/hik_mvs.py week02-camera/camera_common/test_image_stats.py week02-camera/day10/test01_grab_one_frame_with_common.py
git commit -m "feat: add shared camera helpers"
```

Expected: 生成一次只包含本次公共模块实现的提交。

---

## 自检

- 设计文档中的模块位置已覆盖：`week02-camera\camera_common`。
- 设计文档中的两个模块职责已覆盖：`hik_mvs.py` 和 `image_stats.py`。
- Day08 作为学习记录保留，没有计划改写。
- Day10 起调用公共模块已覆盖：新增 Day10 验证脚本。
- 离线测试和相机实拍验证均有明确命令。
