# 工业机器视觉 30 天学习项目

这是一个面向工业落地的高强度学习项目，目标是在 1 个月内完成可展示的工业视觉作品。

主学习路线：

```text
OpenCV -> YOLO -> PaddleOCR -> 缺陷检测 -> 工业视觉项目整合
```

## 从这里继续

每次开始学习前，先阅读：

1. `LEARNING_PROGRESS.md`：当前学习进度、下一课内容和教学方法。
2. 对应日期目录中的练习代码。
3. Obsidian 中当天的理论笔记。

当前下一课：

```text
Day 2
第 1 部分：使用 cv2.rectangle() 画检测框
第 2 部分：批量处理文件夹中的图片
```

## 项目位置

当前 WSL 项目路径：

```text
/home/jie/Projects/industrial-vision-30days
```

Windows 访问路径：

```text
\\wsl.localhost\Ubuntu\home\jie\Projects\industrial-vision-30days
```

当前 Obsidian 知识库：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain
```

工业视觉笔记目录：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\raw\industrial
```

## 在另一台电脑恢复环境

不要复制或继续使用旧电脑中的 `.venv`。虚拟环境包含本机路径，应在新电脑重新创建。

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

## Git 与虚拟环境注意事项

当前项目的第一次 Git 提交误把下面的虚拟环境加入了版本控制：

```text
week01-opencv/day01/.venv
```

虚拟环境不适合在不同电脑之间同步，因为其中包含本机解释器和绝对路径。

在准备通过 Git 同步项目前，可以执行：

```bash
cd ~/Projects/industrial-vision-30days

# 只取消 Git 跟踪，不会删除电脑上的实际虚拟环境文件。
git rm -r --cached week01-opencv/day01/.venv

# 提交清理结果后，另一台电脑应使用 requirements.txt 重新创建环境。
```

执行前应先确认 `.gitignore` 已经包含 `.venv/`。

## 学习成果标准

学习不是以“看完课程”为完成标准，而是以以下成果为标准：

- 能解释代码为什么这样写。
- 能独立修改参数并观察结果。
- 能使用自己的图片完成练习。
- 能记录成功结果和失败案例。
- 每周至少完成一个可以运行和展示的小项目。
