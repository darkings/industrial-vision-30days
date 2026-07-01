# 工业机器视觉 30 天学习项目

这是一个面向工业落地的高强度学习项目，目标是在 1 个月内完成可展示的工业视觉作品。

最后更新：2026-06-29

主学习路线：

```text
OpenCV -> YOLO -> PaddleOCR -> 缺陷检测 -> 工业视觉项目整合
```

## 当前学习状态

| 日期  | 课程                       | 状态   | 主要成果                                                   |
| ----- | -------------------------- | ------ | ---------------------------------------------------------- |
| Day 1 | OpenCV 图像基础            | 已完成 | 读图、shape、像素、灰度图、缩放、ROI、图片保存             |
| Day 2 | OpenCV 图像预处理          | 已完成 | 画框、文字、批处理、滤波、亮度/对比度、直方图、CLAHE、锐化 |
| Day 3 | 阈值分割与形态学           | 已完成 | 固定阈值、OTSU、自适应阈值、腐蚀、膨胀、开闭运算           |
| Day 4 | 边缘检测与轮廓分析         | 已完成 | Canny、轮廓查找、面积周长、外接矩形、OK/NG 规则            |
| Day 5 | 几何特征与尺寸测量基础     | 已完成 | 轮廓中心、旋转矩形、像素距离与尺寸标定基础                 |
| Day 6 | OpenCV 几何测量综合检测    | 已完成 | 检测流水线、目标识别、尺寸 OK/NG、检测报告图               |
| Day 7 | 相机、镜头、光源、标定基础 | 已完成 | FOV、像素精度、焦距、景深、光源选择、标定风险              |
| Day 8 | 工业相机与 GigE 接入预研   | 已完成 | 海康 SDK 枚举设备、抓帧、参数查询、曝光对比实验             |
| Day 9 | 相机抓帧接入 OpenCV 检测流程 | 已完成 | 完成真实图像分析、多阈值、OTSU、形态学和 frame 分析封装    |
| Day 10 | 稳定成像系统搭建           | 待开始 | 支架、环形光源、光源控制器到货后，先固定成像系统           |

当前已完成的主要练习：

```text
week01-opencv/day01/test03_read_imgs.py
week01-opencv/day01/test04_gray_img.py
week01-opencv/day01/test05_roi_img.py

week01-opencv/day02/test01_draw_rectangle.py
week01-opencv/day02/test02_batch_mark_images.py
week01-opencv/day02/test03_image_filters.py
week01-opencv/day02/test04_brightness_contrast.py
week01-opencv/day02/test05_histogram_equalization.py
week01-opencv/day02/test06_image_sharpening.py

week01-opencv/day03/test01_fixed_threshold.py
week01-opencv/day03/test02_threshold_comparison.py
week01-opencv/day03/test03_otsu_threshold.py
week01-opencv/day03/test04_otsu_gaussian_comparison.py
week01-opencv/day03/test05_adaptive_threshold.py
week01-opencv/day03/test06_erode_dilate.py
week01-opencv/day03/test07_open_close.py
week01-opencv/day03/test08_comprehensive.py

week01-opencv/day04/test01_canny_basics.py
week01-opencv/day04/test02_canny_threshold_comparison.py
week01-opencv/day04/test03_find_draw_contours.py
week01-opencv/day04/test04_contour_area_perimeter.py
week01-opencv/day04/test05_bounding_rect.py
week01-opencv/day04/test06_comprehensive.py

week01-opencv/day05/test01_contour_center.py
week01-opencv/day05/test02_min_area_rect.py
week01-opencv/day05/test03_pixel_measurement.py

week01-opencv/day06/test01_pipeline_preview.py
week01-opencv/day06/test02_part_identification.py
week01-opencv/day06/test03_size_ok_ng.py
week01-opencv/day06/test04_detection_report.py

week02-camera/day08/test01_hik_sdk_grab_one_frame.py
week02-camera/day08/test02_hik_sdk_structure_notes.py
week02-camera/day08/test03_hik_camera_params_query.py
week02-camera/day08/test04_hik_exposure_comparison.py
week02-camera/day08/test04_exposure_image_stats_test.py

week02-camera/day09/test01_camera_image_analysis.py
week02-camera/day09/test02_camera_image_analysis.py
week02-camera/day09/test03_threshold_comparison.py
week02-camera/day09/test04_otsu_comparison.py
week02-camera/day09/test05_morphology_cleanup.py
week02-camera/day09/test06_frame_analysis_function.py
```

## 从这里继续

每次开始学习前，先阅读：

1. `LEARNING_PROGRESS.md`：当前学习进度、下一课内容和教学方法。
2. `LEARNING_ERRORS.md`：整个学习过程中持续积累的错误、根因和正确写法。
3. 对应日期目录中的练习代码。
4. Obsidian 中当天的理论笔记。

当前下一课：

```text
Day 10
稳定成像系统搭建
下一步：先做硬件安装与安全检查，确认支架、相机、镜头、环形光源和光源控制器连接稳定。
```

## 当前换到 Windows 继续学习提示

当前准备从 macOS 切换到 Windows 电脑继续学习。

Windows 继续入口：

```text
Day10 第 1 节：硬件安装与安全检查
```

当前状态：

```text
Day01-Day09 已完成。
Day10 理论笔记已完成并检查。
当前不要继续调 Day09 旧图像阈值。
下一步应先在 Windows 上确认硬件、MVS、SDK、相机连接和稳定成像系统。
```

Windows 项目目录：

```text
D:\Projects\industrial-vision-30days
```

Windows Obsidian 笔记目录：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

Windows 继续前先做：

```text
1. 拉取或同步项目源码。
2. 根据 requirements.txt 重新创建 .venv，不复制 macOS 的 .venv。
3. 安装并打开 MVS / 海康 SDK。
4. 确认 GigE 相机能在 MVS 中枚举并预览。
5. 确认 Python 能调用 SDK 抓到一帧。
6. 再开始 Day10 第 1 节硬件安装与安全检查。
```

Day10 的学习边界：

```text
先固定支架、相机、镜头、环形光源和光源控制器。
先让图像稳定，再重新选择曝光、阈值和检测规则。
暂不做正式 OK/NG、尺寸标定、YOLO、OCR 或复杂触发联动。
```

## 当前工业相机实测状态

2026-06-27 已确认当前设备可以作为入门实操相机继续使用。

设备信息：

```text
相机接口：GigE 网口
MVS 识别型号：MV-13MG-E
厂商显示：Machine Vision
序列号：7A050E5PAK00046
物理地址：24:52:6A:8F:E7:6C
相机 IP：169.254.184.253
子网掩码：255.255.255.0
网关：169.254.184.254
分辨率：1280 x 1024
采集帧率：约 75 fps
镜头：8mm 1:1.4
```

已完成验证：

```text
1. MVS 可以识别并打开该 GigE 相机。
2. MVS 可以实时预览画面。
3. 台式机上已使用 Python 调用海康 SDK 完整打开相机并抓到一帧。
4. 已查询 ExposureTime、Gain、TriggerMode、PixelFormat 等相机参数。
5. 已完成 800 us、1000 us、1500 us 等曝光时间对比实验。
```

当前硬件状态：

```text
GigE 工业相机：已到位
镜头：已到位
相机固定支架：已到位
环形光源：已到位
光源控制器：已到位
```

因此 Day09 先完成固定图片下的阈值理解；Day10 开始搭建稳定成像系统。正式尺寸测量、标定和 OK/NG 结论必须等支架、光源、曝光和连续抓图稳定性验证后再做。

换电脑继续时优先检查：

```text
1. 安装 MVS / 海康 SDK。
2. 网口相机和电脑网卡处在可通信网段。
3. MVS 能枚举设备并预览。
4. Python 能调用 SDK 打开设备并抓一帧。
5. 将抓到的一帧转换为 OpenCV 可处理的 numpy.ndarray。
6. 再接入 Day06 的检测流程。
```

## 每课完成后的同步规则

每一课通过代码、输出和理论验收后，必须同步更新：

1. `README.md`
   - 修改最后更新时间。
   - 更新课程状态表。
   - 更新已完成练习。
   - 更新“当前下一课”。
2. `LEARNING_PROGRESS.md`
   - 记录已掌握内容、完成文件、验证结果和下一课。
3. `LEARNING_ERRORS.md`
   - 只记录有学习价值的概念、API、控制流、数据处理和工程逻辑问题。
4. Obsidian 当天笔记
   - 检查知识、代码、Markdown 可读性和工业实践补充。

任何一项没有同步，都不算该课完整收尾。

## 项目位置

### macOS

```text
/Users/jie/Projects.localized/industrial-vision-30days
```

macOS Obsidian 工业视觉笔记目录：

```text
/Users/jie/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain/learning/IndustrialVision
```

### Windows

```text
D:\Projects\industrial-vision-30days
```

Windows Obsidian 工业视觉笔记目录：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

不同电脑的操作系统、用户名、Python 版本和绝对路径可以不同。项目源码通过 Git 同步，`.venv` 必须在每台电脑上根据 `requirements.txt` 单独创建；不要把某一台电脑的绝对路径用于程序代码。

Obsidian 笔记通过 iCloud 同步。macOS 使用 macOS 路径，Windows 使用 Windows 路径。

Day 3 笔记：

macOS：

```text
/Users/jie/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain/learning/IndustrialVision/Day03_阈值分割与形态学.md
```

Windows：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision\Day03_阈值分割与形态学.md
```

## 在另一台电脑恢复环境

本项目只使用一个位于项目根目录的虚拟环境：

```text
industrial-vision-30days/.venv
```

不按天或按周创建虚拟环境。Day 1、Day 2、YOLO、PaddleOCR 和最终综合项目优先共用根环境。

只有出现无法兼容的 PyTorch、CUDA 或 PaddlePaddle 依赖冲突时，才创建专用环境，并在 README 中记录原因和用途。

不要复制或继续使用另一台电脑中的 `.venv`。虚拟环境包含本机解释器和路径，应在新电脑重新创建。

在 macOS 中执行：

```bash
cd /Users/jie/Projects.localized/industrial-vision-30days

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

在 Windows PowerShell 中执行：

```powershell
cd D:\Projects\industrial-vision-30days

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

检查环境：

macOS：

```bash
python --version
python -c "import cv2, numpy, matplotlib; print(cv2.__version__)"
```

Windows PowerShell：

```powershell
python --version
python -c "import cv2, numpy, matplotlib; print(cv2.__version__)"
```

日常进入项目后激活环境：

macOS：

```bash
cd /Users/jie/Projects.localized/industrial-vision-30days
source .venv/bin/activate
```

Windows PowerShell：

```powershell
cd D:\Projects\industrial-vision-30days
.\.venv\Scripts\Activate.ps1
```

激活后，终端通常会显示 `(.venv)`。可以通过以下命令确认当前解释器来自项目根目录：

macOS：

```bash
which python
python --version
```

Windows PowerShell：

```powershell
where.exe python
python --version
```

预期 Python 路径：

macOS：

```text
/Users/jie/Projects.localized/industrial-vision-30days/.venv/bin/python
```

Windows：

```text
D:\Projects\industrial-vision-30days\.venv\Scripts\python.exe
```

## Git 与虚拟环境

项目第一次提交曾误跟踪 `week01-opencv/day01/.venv`。

2026-06-18 已完成迁移：

- 根环境 `.venv` 已安装并验证依赖。
- 旧的 `week01-opencv/day01/.venv` 已删除。
- Git 索引中的 4518 个旧环境文件已取消跟踪。
- `.gitignore` 已忽略所有 `.venv/` 和 Python 缓存。

虚拟环境不进入 Git。跨电脑同步时只同步：

```text
requirements.txt
源码
配置
必要的数据说明
```

## 学习成果标准

学习不是以“看完课程”为完成标准，而是以以下成果为标准：

- 能解释代码为什么这样写。
- 能独立修改参数并观察结果。
- 能使用自己的图片完成练习。
- 能记录成功结果和失败案例。
- 每周至少完成一个可以运行和展示的小项目。
