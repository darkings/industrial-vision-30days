# 工业机器视觉 30 天学习项目

这是一个面向工业落地的高强度学习项目，目标是在 1 个月内完成可展示的工业视觉作品。

最后更新：2026-07-14

主学习路线：

```text
OpenCV -> YOLO -> PaddleOCR -> 缺陷检测 -> 工业视觉项目整合
```

## 文档职责

README 只维护项目概览、环境恢复、硬件信息和长期规则，不维护逐课进度。

逐课学习进度以以下内容为准：

```text
Obsidian 当天笔记
当天代码文件
当天 outputs 结果
必要的 JSON / 配置文件
```

错误记录以以下内容为准：

```text
Obsidian _LearningErrors.md：统一错误知识库，只记录错误条目，不按天数记录。
当天课程笔记：只保留必要易错点和关键结论。
```

路线和天级安排查看：

```text
30_DAY_LEARNING_PLAN.md
```

## 从这里继续

每次开始学习前，先阅读：

1. `AGENTS.md`：协作规则、文档更新规则和路径规则。
2. `30_DAY_LEARNING_PLAN.md`：当前 30 天路线和阶段节奏。
3. Obsidian 中当天的理论笔记。
4. 对应日期目录中的练习代码和 outputs。

更新说明：从 2026-07-04 起，日常学习入口和文档更新规则以根目录 `AGENTS.md` 为准。`LEARNING_PROGRESS.md` 和 `LEARNING_ERRORS.md` 已删除；错误知识库迁移到 Obsidian 的 `_LearningErrors.md`。

README 不维护“当前下一课”。需要继续学习时，优先查看 Obsidian 当天笔记和 `30_DAY_LEARNING_PLAN.md`。

## 当前环境状态（2026-07-14）

当前根环境新增 YOLO 和 PaddleOCR 依赖，统一通过项目根目录 `requirements.txt` 恢复：

```text
ultralytics==8.4.90
paddleocr==3.7.0
paddlepaddle==3.3.1
numpy==2.3.5
opencv-python==4.13.0.92
opencv-contrib-python==4.10.0.84
```

注意：当前环境里 YOLO 依赖 `opencv-python`，PaddleOCR/PaddleX 依赖 `opencv-contrib-python`。实际 `import cv2` 时显示版本为：

```text
cv2 4.10.0
```

这是 PaddleOCR 依赖带来的正常结果。换电脑时不要手动只装其中一个 OpenCV 包，优先执行：

```powershell
python -m pip install -r requirements.txt
```

验证环境：

```powershell
python -c "import cv2, numpy, ultralytics, paddle; from paddleocr import PaddleOCR; print(cv2.__version__, numpy.__version__, ultralytics.__version__, paddle.__version__)"
```

## YOLO 数据集恢复信息

当前 YOLO 数据集位置：

```text
D:\Projects\industrial-vision-30days\week03-yolo_ocr\day16\dataset
```

当前类别配置：

```yaml
names:
  0: dpi_button
```

标注规则：

```text
只框 DPI 按钮本体。
不框滚轮。
不框 logo。
不框中间整条装饰条。
不把滚轮反光或外壳反光当成 dpi_button。
类别只使用：dpi_button。
```

CVAT Raw labels 可使用：

```json
[
  {
    "name": "dpi_button",
    "type": "any",
    "attributes": []
  }
]
```

## Windows 学习环境提示

当前已经在 Windows 上完成 MVS、SDK、相机、支架、光源和稳定成像验证。

Windows 继续学习时，不从 README 判断课程进度。先按 `AGENTS.md` 的规则读取 Obsidian 当天笔记，再查看项目代码和 outputs。

Windows 项目目录：

```text
D:\Projects\industrial-vision-30days
```

Windows Obsidian 笔记目录：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

Windows 换机或重装环境前先做：

```text
1. 拉取或同步项目源码。
2. 根据 requirements.txt 重新创建 .venv，不复制 macOS 的 .venv。
3. 安装并打开 MVS / 海康 SDK。
4. 确认 GigE 相机能在 MVS 中枚举并预览。
5. 确认 Python 能调用 SDK 抓到一帧。
6. 再按 AGENTS.md、30_DAY_LEARNING_PLAN.md 和 Obsidian 当天笔记继续。
```

当前硬件和基础检测边界：

```text
Day10 已完成固定支架、相机、镜头、环形光源和光源控制器。
Day11 已完成基础轮廓检测、OK/NG、JSON 输出和多帧稳定性验证。
后续学习在此硬件基线和基础检测能力上继续扩展。
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

当前硬件已能支撑后续传统视觉、ROI、模板匹配和批量验证练习。具体学习进度以 Obsidian 当天笔记为准。

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

从 2026-07-04 起，根目录文档不再逐课同步。

日常学习完成后，优先更新：

1. Obsidian 当天笔记
   - 记录概念、关键参数、代码文件、输出路径、实验结果和结论。
2. 代码和输出目录
   - 保留可运行脚本、结果图、JSON 汇总和必要配置。
3. 错误记录
   - 值得复盘的错误统一写入 Obsidian 的 `_LearningErrors.md`。
   - 不按天数记录，只记录错误条目。

仅在以下情况更新根目录文档：

```text
学习路线变化
环境或路径规则变化
项目级协作规则变化
用户明确要求更新 README / 30_DAY_LEARNING_PLAN / _LearningErrors
```

详细规则见根目录 `AGENTS.md`。

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

