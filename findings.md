# 30 天计划制定发现记录

## 当前项目结构发现

- 项目根目录：`D:\Projects\industrial-vision-30days`
- 关键项目文件：
  - `README.md`
  - `LEARNING_PROGRESS.md`
  - `LEARNING_ERRORS.md`
  - `requirements.txt`
- 已有代码：
  - `week01-opencv/day01` 到 `day06`
  - `week02-camera/day08`
  - `week02-camera/day09`

## 当前 Obsidian 笔记发现

笔记目录：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

已有笔记：

- `_IndustrialVisionMap.md`
- `Day01_图像与OpenCV基础.md`
- `Day02_图像增强与批处理.md`
- `Day03_阈值分割与形态学.md`
- `Day04_边缘检测与轮廓分析.md`
- `Day05_几何特征与尺寸测量基础.md`
- `Day06_OpenCV几何测量综合检测.md`
- `Day08_工业相机与GigE接入预研.md`
- `Day09_相机抓帧接入OpenCV检测流程.md`

缺口：

- 未看到独立 `Day07` Obsidian 笔记文件。
- Day07 内容在 `README.md` 和 `LEARNING_PROGRESS.md` 中已有记录。

## 当前学习状态发现

- Day01-Day06：OpenCV 基础与几何测量综合检测已完成。
- Day07：相机、镜头、光源、标定基础已完成。
- Day08：工业相机与 GigE 接入预研已完成。
- Day09：相机图像接入 OpenCV 检测流程已开始，完成第 1 节。

## README 与学习进度发现

主学习路线：

```text
OpenCV -> YOLO -> PaddleOCR -> 缺陷检测 -> 工业视觉项目整合
```

当前下一步：

```text
Day09：调整阈值参数，观察二值图和轮廓数量变化。
```

项目教学方法要求：

```text
理论 -> Python 语法 -> API 参数 -> 完整示范 -> 跟写 -> 修改参数 -> 独立练习 -> 验收
```

每课完成后必须同步：

- `README.md`
- `LEARNING_PROGRESS.md`
- `LEARNING_ERRORS.md`
- Obsidian 当天笔记

## 错误库发现

高频能力缺口：

- 路径和文件读取失败处理。
- OpenCV 图像 `shape`、像素、ROI 的高宽和坐标顺序。
- 批量处理中的跳过、失败、成功分类。
- 检测结果来源追溯。
- SDK 资源生命周期和 buffer 释放。
- 十六进制错误码、C 字符数组解码等工业 SDK 细节。

这些应在后续 30 天计划中反复嵌入，而不是只在某一天讲一次。

## 计划输出

已生成：

```text
D:\Projects\industrial-vision-30days\30_DAY_LEARNING_PLAN.md
```

计划特点：

- Day01-Day08 保留为已完成基座。
- Day09 从当前真实相机图像接入 OpenCV 继续。
- Day13 开始进入 YOLO。
- Day18 开始进入 PaddleOCR。
- Day20-Day21 进入缺陷检测。
- Day22-Day30 进入项目架构、稳定性、最终展示和复盘。

## 硬件状态约束

- 已有：GigE 工业相机、8mm 镜头。
- 预计 2026-06-30 到位：支架、光源、控制器。
- 因此 Day10 应提前进入成像系统搭建：机械固定、光源初调、控制器认识、曝光/阈值重选、连续抓图稳定性。
- 正式尺寸测量和正式 OK/NG 结论仍需等固定、光照、参数稳定性验证完成后再做。
