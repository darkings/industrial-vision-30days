# 相机公共模块设计

## 目标

把重复出现的相机抓拍代码统一收进一个公共学习模块。这样 Day10 以及后续练习可以直接导入同一套海康 MVS 辅助函数，而不是在每个脚本里重复复制 SDK 初始化、打开相机、抓图、释放资源等代码。

## 放置位置

使用当前项目内的这个路径：

```text
D:\Projects\industrial-vision-30days\week02-camera\camera_common\
```

这样相机采集代码仍然归在 `week02-camera` 下，`week01-opencv` 继续只负责 OpenCV 图像基础，不混在一起。

## 模块结构

```text
week02-camera/
  camera_common/
    __init__.py
    hik_mvs.py
    image_stats.py
```

`hik_mvs.py` 负责相机采集相关内容：

- 从 Windows 已安装路径加载海康 MVS SDK
- 初始化和反初始化 SDK
- 枚举相机设备
- 创建、打开、关闭、销毁相机句柄
- 设置常用相机参数，例如曝光、增益、触发模式、像素格式
- 抓取一帧图像，并转换为 `numpy.ndarray`
- 正确释放 SDK 图像缓存

`image_stats.py` 负责图像统计辅助函数：

- 计算图像宽度和高度
- 计算 mean、min、max
- 计算过曝像素比例
- 后续可扩展 ROI 统计、直方图摘要、清晰度评分

## 导入方式

因为父目录名是 `week02-camera`，中间有连字符，不能直接作为 Python 包名导入。所以各练习脚本先把 `week02-camera` 目录加入 `sys.path`，再把 `camera_common` 当作普通包导入。

示例：

```python
from pathlib import Path
import sys

WEEK02_DIR = Path(__file__).resolve().parents[1]
if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import grab_one_frame
from camera_common.image_stats import calculate_gray_stats
```

## 学习策略

Day08 的脚本保留为学习记录，不立刻重构。它们的价值是展示完整 SDK 生命周期：加载 SDK、枚举设备、打开相机、抓帧、转图像、释放资源。

从 Day10 开始，新的练习代码优先导入 `camera_common`，让每一节课专注当前主题：

- Day10：稳定成像、FOV、固定曝光、重复采集
- Day11：批量采图和数据集目录规则
- 后续：触发采集、标定、测量、检测

## 初始实现范围

第一版实现保持小而清楚：

- 提供一个可复用的单帧抓拍函数
- 提供简单灰度统计函数
- 添加一个 Day10 练习脚本，用它来验证公共模块可以被导入和调用

暂时不做成大型框架。只有当后续练习反复需要同一种能力时，再逐步扩展这个模块。

## 验证方式

通过运行一个 Day10 脚本验证公共模块：

- 能导入 `camera_common`
- 能从 MV-13MG-E 相机抓取一帧
- 能计算图像统计值
- 能把图像保存到 Day10 输出目录
- 能打印相机参数和保存路径
