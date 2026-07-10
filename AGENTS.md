# AGENTS.md

本文件是 `industrial-vision-30days` 项目的助手协作规则。以后新会话、新电脑或上下文丢失时，先读本文件，再继续学习。

## 项目入口

```text
当前项目目录：D:\Projects\industrial-vision-30days
Windows Obsidian 笔记目录：C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

继续学习时的入口判断：

```text
1. 先读本文件，确认协作规则、路径规则和文档维护规则。
2. 再读 30_DAY_LEARNING_PLAN.md，确认阶段路线。
3. 再读 Obsidian 当天笔记，确认真实学习进度和下一节内容。
4. 不在 AGENTS.md 中维护“当前进度”或“下一课”，避免过期。
```

## 文档更新规则

从 2026-07-04 起，根目录历史文档不再逐课更新。

已删除的历史规划/进度文件：

```text
LEARNING_PROGRESS.md
task_plan.md
progress.md
findings.md
```

不要恢复这些文件作为日常进度来源。

默认不逐课更新：

```text
README.md
30_DAY_LEARNING_PLAN.md
```

这些文件保留为项目级说明。不要因为每一节课完成就机械同步它们。

日常学习主要维护：

```text
Obsidian 当天笔记
当天代码文件
当天 outputs 结果
必要的 JSON / 配置文件
```

只有以下情况才更新根目录文档：

```text
1. 用户明确要求更新某个根目录文档。
2. 30 天学习路线发生变化。
3. 环境、路径、依赖或硬件规则发生变化。
4. 项目级协作规则发生变化。
5. 某个错误需要升级成长期规则，而不只是当天学习笔记。
6. 助手准备讲解的新内容已经偏离 30_DAY_LEARNING_PLAN.md 的天级安排，或把后续天数的内容提前/延后讲解。
```

## 计划文档职责

`30_DAY_LEARNING_PLAN.md`：

```text
用途：维护 30 天总体路线、Day12-Day16 等阶段计划。
更新时机：学习路线变化、天级安排变化、用户要求重新规划。
不做：每节课完成后的流水账同步。
可以记录阶段路线和天级安排，但不要承担逐节进度记录。
讲解新内容前要先对照本文件：如果当前要讲的内容仍在原天级路线内，不必更新；如果实际学习节奏已经把某天内容提前、延后、拆分或合并，则先更新本文件的天级安排，再继续讲解。
```

`README.md`：

```text
用途：项目概览、环境入口、硬件信息、恢复说明。
更新时机：环境安装方式、硬件状态、项目入口发生变化。
不做：逐节课进度记录。
```

`LEARNING_PROGRESS.md`：

```text
当前状态：已删除。
原因：进度信息改由 AGENTS.md、30_DAY_LEARNING_PLAN.md 和 Obsidian 当天笔记维护。
```

`_LearningErrors.md`：

```text
用途：个人错误知识库，存放在 Obsidian 中。
当前状态：继续维护。
维护规则：只记录错误本身，例如 API 误用、坐标/shape/ROI 混淆、资源释放问题、JSON 结构设计错误、检测结果不可追溯等。
不记录：普通拼写、临时变量名、无长期复盘价值的小笔误。
重复错误：在原错误条目下追加重复出现记录。
```

错误记录规则：

```text
1. 根目录不再维护 LEARNING_ERRORS.md。
2. 所有值得复盘的错误统一写入 Obsidian 的 _LearningErrors.md。
3. 错误库不按天数记录，只记录错误条目。
4. 当天课程笔记只保留必要的“本节易错点”和关键结论，不承担完整错误库职责。
5. 无长期价值的小拼写、临时变量名、手滑类问题，不记录到错误库。
6. 如果同类错误重复出现，在 _LearningErrors.md 原条目下追加重复记录。
```

Obsidian 错误笔记路径：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision\_LearningErrors.md
```

`task_plan.md`、`progress.md`、`findings.md`：

```text
当前状态：已删除。
原因：它们是制定 30 天计划时的临时规划文件，内容已过时。
```

## Obsidian 笔记协作方式

用户偏好的学习流程：

```text
1. 助手先讲概念。
2. 用户自己记录笔记。
3. 用户说“检查”。
4. 助手检查笔记，发现遗漏或错误时直接补到 Obsidian。
5. 助手告知练习目标。
6. 用户写代码。
7. 助手检查代码和输出，让用户自己修改练习代码。
8. 重要实验结果、路径、参数和结论由助手补进当天笔记。
```

注意：

```text
概念理解优先让用户自己写。
实验结果、路径、参数、结论可以由助手直接补充。
练习代码错误优先指出问题，由用户自己修改。
```

## Obsidian 笔记格式规则

修改 Obsidian 笔记时必须遵守以下格式规则。

标题层级：

```text
每篇文章只能有一个 # H1，作为文章标题。
正文标题从 ## H2 开始，后续按 ### H3、#### H4、##### H5、###### H6 往下排。
不要把正文大章节也写成 # H1。
```

笔记开头：

```text
每篇笔记开头统一包含 YAML 属性：
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [标签 1, 标签 2]
---
YAML 后直接接文章 # H1 标题，不留空行。
标题下方可以接 所属主题、上一课、下一课 等导航信息。
```

标题空行：

```text
所有 H1-H6 标题上方不要有空行。
所有 H1-H6 标题下方如果紧跟正文、列表、代码块，也不要有空行。
```

代码块空行：

```text
如果代码块上方有文字，文字和代码块之间不要有空行。
代码块内部内容不因为排版规则改动。
```

列表空行：

```text
如果有序列表或无序列表上方有文字，文字和列表之间不要有空行。
包括：
说明文字
- 列表项
和：
说明文字
1. 列表项
```

## 代码协作规则

当前阶段代码放在：

```text
week02-camera/dayXX/
```

输出放在：

```text
week02-camera/dayXX/outputs/<实验名>/
```

命名建议：

```text
test01_*.py
test02_*.py
test03_*.py
```

Day12 起优先保持：

```text
main() 只负责流程编排
图像处理函数返回结果
保存动作集中在 save_outputs() 或 main()
配置参数不要散落硬编码
JSON 输出必须可追溯输入、参数、结果和 OK/NG 原因
```

## 当前硬件与默认基线

```text
相机：MV-13MG-E
序列号：7A050E5PAK00046
分辨率：1280 x 1024
镜头：8mm
曝光：1200 us
丢弃缓存帧：5 帧
背景：白纸背景
目标：黑色键帽
Day11 多帧验证：20 帧 OK，0 帧 NG
```

当前稳定性结论：

```text
x/y 坐标稳定
OTSU 阈值稳定
面积轻微波动
当前成像条件能支撑基础轮廓检测和 OK/NG 判定
```

## 路径规则

Windows 项目路径：

```text
D:\Projects\industrial-vision-30days
```

Windows Obsidian 路径：

```text
C:\Users\Jie\iCloudDrive\iCloud~md~obsidian\SecondBrain\learning\IndustrialVision
```

macOS 和 Windows 都可以学习。在哪台电脑学习，就使用那台电脑的本地路径。不要把 Windows 路径硬写进 macOS 代码，也不要把 macOS 路径硬写进 Windows 代码。

## 进度记录规则

```text
AGENTS.md 不维护当前进度和下一课。
真实学习进度以 Obsidian 当天笔记、当天代码和 outputs 为准。
路线调整才更新 30_DAY_LEARNING_PLAN.md。
项目入口、环境、硬件、协作规则变化才更新 README.md 或 AGENTS.md。
```
