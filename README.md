# 工业机器视觉 30 天学习项目

这是一个面向工业落地的高强度学习项目，目标是在 1 个月内完成可展示的工业视觉作品。

最后更新：2026-06-22

主学习路线：

```text
OpenCV -> YOLO -> PaddleOCR -> 缺陷检测 -> 工业视觉项目整合
```

## 当前学习状态

| 日期 | 课程 | 状态 | 主要成果 |
|---|---|---|---|
| Day 1 | OpenCV 图像基础 | 已完成 | 读图、shape、像素、灰度图、缩放、ROI、图片保存 |
| Day 2 | OpenCV 图像预处理 | 已完成 | 画框、文字、批处理、滤波、亮度/对比度、直方图、CLAHE、锐化 |
| Day 3 | 阈值分割与形态学 | 已完成 | 固定阈值、OTSU、自适应阈值、腐蚀、膨胀、开闭运算 |
| Day 4 | 边缘检测与轮廓分析 | 已完成 | Canny、轮廓查找、面积周长、外接矩形、OK/NG 规则 |
| Day 5 | 几何特征与尺寸测量基础 | 待开始 | 轮廓中心、旋转矩形、像素距离与尺寸标定基础 |

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
```

## 从这里继续

每次开始学习前，先阅读：

1. `LEARNING_PROGRESS.md`：当前学习进度、下一课内容和教学方法。
2. `LEARNING_ERRORS.md`：整个学习过程中持续积累的错误、根因和正确写法。
3. 对应日期目录中的练习代码。
4. Obsidian 中当天的理论笔记。

当前下一课：

```text
Day 5
第 1 部分：轮廓中心与图像矩
第 2 部分：旋转外接矩形
第 3 部分：像素距离与尺寸标定基础
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

当前 Obsidian 知识库中的工业视觉笔记目录：

```text
/Users/jie/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain/learning/IndustrialVision
```

### Ubuntu/WSL

```text
/home/jie/Projects/industrial-vision-30days
```

Windows 访问 WSL 项目的路径：

```text
\\wsl.localhost\Ubuntu\home\jie\Projects\industrial-vision-30days
```

不同电脑的操作系统、用户名、Python 版本和绝对路径可以不同。项目源码通过 Git 同步，`.venv` 必须在每台电脑上根据 `requirements.txt` 单独创建；不要把某一台电脑的绝对路径用于程序代码。

Obsidian 笔记通过 iCloud 同步时，各系统上的本地绝对路径也可能不同。当前 macOS 使用上方记录的目录。

Day 3 笔记：

```text
/Users/jie/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain/learning/IndustrialVision/Day03.md
```

## 在另一台电脑恢复环境

本项目只使用一个位于项目根目录的虚拟环境：

```text
industrial-vision-30days/.venv
```

不按天或按周创建虚拟环境。Day 1、Day 2、YOLO、PaddleOCR 和最终综合项目优先共用根环境。

只有出现无法兼容的 PyTorch、CUDA 或 PaddlePaddle 依赖冲突时，才创建专用环境，并在 README 中记录原因和用途。

不要复制或继续使用另一台电脑中的 `.venv`。虚拟环境包含本机解释器和路径，应在新电脑重新创建。

在 Ubuntu/WSL 中执行：

```bash
cd ~/Projects/industrial-vision-30days

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

检查环境：

```bash
python --version
python -c "import cv2, numpy, matplotlib; print(cv2.__version__)"
```

日常进入项目后激活环境：

```bash
cd ~/Projects/industrial-vision-30days
source .venv/bin/activate
```

激活后，终端通常会显示 `(.venv)`。可以通过以下命令确认当前解释器来自项目根目录：

```bash
which python
python --version
```

预期 Python 路径：

```text
/home/jie/Projects/industrial-vision-30days/.venv/bin/python
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
