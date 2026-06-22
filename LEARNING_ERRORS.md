# 工业视觉学习错误知识库

最后更新：2026-06-22

这不是一次性的错题清单，而是整个 30 天学习项目持续维护的错误知识库。

以后检查任何练习时，只要发现代码错误、概念错误、分类错误或容易形成坏习惯的写法，都要追加到此文件。

## 错误记录规范

每个错误必须记录：

```text
1. 日期与课程
2. 出错文件
3. 错误代码
4. 实际现象或潜在后果
5. 根本原因
6. 正确代码
7. 为什么这样修改
8. 以后如何避免
```

不能只记录“哪里错了”，必须理解错误为什么发生。

# 一、实际错误记录

## E001：`is_file` 方法没有调用

日期与课程：Day 1，批量读取图片

出错文件：

```text
week01-opencv/day01/test03_read_imgs.py
```

错误代码：

```python
if img.is_file:
```

问题现象：

这段判断看起来是在检查路径是不是文件，但实际上没有执行 `is_file`。
`img.is_file` 只是取得“方法对象”本身。方法对象通常会被判断为真，因此可能把文件夹或其他不应该处理的内容继续交给 `cv2.imread()`。

根本原因：

Python 中的方法必须使用括号才能执行：

```text
对象.方法   -> 取得方法本身
对象.方法() -> 调用方法并得到返回值
```

正确代码：

```python
if img_path.is_file():
```

更完整的图片筛选：

```python
if not img_path.is_file():
    continue
```

以后如何避免：

看到 `is_file`、`lower`、`copy`、`iterdir` 等方法名时，先确认自己是要“取得方法”，还是要“执行方法”。绝大多数练习中都需要括号。

## E002：读取失败后继续操作 `None`

日期与课程：Day 1、Day 2，图片读取

错误代码：

```python
image = cv2.imread(str(image_path))

if image is None:
    print("图片读取失败")

marked_image = image.copy()
```

实际现象：

读取失败时 `image` 是 `None`。打印提示不会停止程序，下一行会报：

```text
AttributeError: 'NoneType' object has no attribute 'copy'
```

根本原因：

`cv2.imread()` 读取失败时通常不会自动抛出异常，而是返回 `None`。程序必须主动决定是终止还是跳过。

单张图片的正确写法：

```python
if image is None:
    raise FileNotFoundError(f"图片读取失败：{image_path}")
```

批量处理的正确写法：

```python
if image is None:
    error_count += 1
    print(f"图片读取失败：{image_path.name}")
    continue
```

为什么写法不同：

```text
单张程序：唯一图片失败，程序没有继续运行的意义，所以 raise。
批量程序：当前图片失败，其他图片仍可处理，所以 continue。
```

以后如何避免：

每次写完 `cv2.imread()`，立即写 `if image is None`，不要等到后面发生 `.shape` 或 `.copy()` 报错。

重复错误记录：

```text
日期：2026-06-21
课程：Day 3，自适应阈值
文件：week01-opencv/day03/test05_adaptive_threshold.py
```

再次出现的写法：

```python
if image is None:
    print("图片读取失败！")
```

打印提示不会终止程序，后续 `cv2.cvtColor(image, ...)` 仍会收到 `None`。
本次已改为抛出 `FileNotFoundError`，让单张图片脚本立即终止。

## E019：在新循环中误用上一个循环遗留的变量值

日期与课程：2026-06-22，Day 4，外接矩形与目标筛选

出错文件：

```text
week01-opencv/day04/test05_bounding_rect.py
```

错误逻辑：

```python
for contour in contours:
    area = cv2.contourArea(contour)
    if area >= min_area:
        valid_contours.append(contour)

for contour in valid_contours:
    print(area)
```

实际现象：

三个候选目标打印出的面积都为 `20.00`，与各自轮廓不对应。

根本原因：

Python 的 `for` 循环不会创建独立作用域。第一个循环结束后，`area` 仍然存在，但它只保存最后一次迭代的结果。本例最后处理的是面积为 `20.00` 的噪点，因此第二个循环反复打印了这个旧值。

正确写法：

```python
for contour in valid_contours:
    area = cv2.contourArea(contour)
    x, y, width, height = cv2.boundingRect(contour)
    print(area)
```

为什么这样修改：

面积、外接矩形和其他特征都必须由当前循环中的同一条 `contour` 计算，才能保证数据与目标一一对应。

以后如何避免：

- 每次进入新的轮廓循环，都重新计算当前轮廓需要使用的特征。
- 看到循环外或上一个循环遗留的变量时，确认它是否仍与当前对象对应。
- 调试多目标程序时，检查每个目标输出是否异常地完全相同。

## E003：错误理解 `break` 和 `continue`

日期与课程：Day 2，读取失败处理

错误想法：

```python
if image is None:
    break
```

问题：

`break` 和 `continue` 只能写在循环内部。单张图片脚本不在循环中，使用它们会报：

```text
SyntaxError: 'break' outside loop
```

区别：

```text
continue：结束当前一轮，继续下一轮
break：结束整个循环
raise：主动抛出异常并终止当前程序流程
```

正确选择：

```text
单张图片读取失败：raise
批量处理中某张图片失败：continue
确定不再需要处理任何后续图片：break
```

以后如何避免：

使用 `break` 或 `continue` 前，先向上检查当前代码是否位于 `for` 或 `while` 中，再判断是跳过一项还是结束全部循环。

## E004：图像 `shape` 的高宽顺序混淆

日期与课程：Day 1，读取图片信息

错误理解：

```python
# 1920x1080 图片
image.shape == (1920, 1080, 3)
```

正确理解：

通常所说的 `1920x1080` 是：

```text
宽度 1920 x 高度 1080
```

OpenCV/NumPy 的 `shape` 是：

```python
(1080, 1920, 3)
```

正确代码：

```python
height, width, channels = image.shape
```

根本原因：

NumPy 数组先表示行数，再表示列数：

```text
行数 -> 高度
列数 -> 宽度
```

以后如何避免：

背住一句：

```text
shape 是高宽，resize 是宽高。
```

## E005：像素和 ROI 坐标顺序写反

日期与课程：Day 1，ROI 裁剪

错误代码：

```python
roi = image[y1:x1, y2:x2]
```

正确代码：

```python
roi = image[y1:y2, x1:x2]
```

像素访问：

```python
pixel = image[y, x]
```

根本原因：

NumPy 数组使用：

```text
数组[行, 列]
图片[y, x]
```

但 OpenCV 画框函数使用几何坐标点：

```python
(x, y)
```

必须区分：

```text
像素/裁剪：方括号 [y, x]
画框/文字：圆括号 (x, y)
```

潜在后果：

- 裁剪区域完全不对。
- 得到空数组。
- `cv2.imshow()` 或 `cv2.imwrite()` 处理空图时失败。
- 后续 OCR、缺陷检测使用了错误区域。

以后如何避免：

写 ROI 前先写注释：

```python
# NumPy 裁剪顺序：[y1:y2, x1:x2]
```

## E006：图片后缀 `.jpeg` 缺少点

日期与课程：Day 2，批量处理

错误代码：

```python
IMAGE_SUFFIXES = {".png", ".jpg", "jpeg"}
```

正确代码：

```python
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
```

根本原因：

`Path.suffix` 返回的后缀包含点：

```python
Path("photo.jpeg").suffix
# ".jpeg"
```

错误后果：

合法的 `.jpeg` 图片会被当成非图片文件跳过。

以后如何避免：

后缀集合里的每一项都从点开始，并使用：

```python
image_path.suffix.lower()
```

## E007：读取失败被错误统计为“跳过”

日期与课程：Day 2，批量处理统计

错误代码：

```python
if image is None:
    skip_count += 1
```

为什么错误：

这张文件已经通过图片后缀筛选，程序尝试读取但失败了。它属于处理错误，不是主动跳过。

正确代码：

```python
if image is None:
    error_count += 1
    print(f"读取失败：{image_path.name}")
    continue
```

统计定义：

```text
success_count：读取和保存均成功
error_count：读取失败或保存失败
skip_count：不是文件或后缀不支持
```

工业意义：

统计分类必须准确。否则现场日志显示“没有失败，只有跳过”，会掩盖图片损坏、路径错误或格式异常。

以后如何避免：

先定义每个计数器的业务含义，再决定异常应该进入哪个计数器。

## E008：检测框坐标没有边界保护

日期与课程：Day 2，画检测框

原代码：

```python
x1 = width // 2 - 200
y1 = height // 2 - 200
x2 = width // 2 + 200
y2 = height // 2 + 200
```

问题：

当前图片足够大时可以运行，但如果图片宽高小于 400，左上角可能成为负数，右下角也可能超出图片边界。

正确代码：

```python
half_box_size = 200

x1 = max(width // 2 - half_box_size, 0)
y1 = max(height // 2 - half_box_size, 0)

x2 = min(width // 2 + half_box_size, width - 1)
y2 = min(height // 2 + half_box_size, height - 1)
```

为什么使用 `width - 1`：

像素坐标从 `0` 开始。如果宽度是 `640`，有效横坐标是：

```text
0 到 639
```

工业意义：

输入图片尺寸可能改变。没有边界保护的代码只适合当前测试图，无法稳定用于真实项目。

以后如何避免：

凡是通过加减计算出来的坐标，都检查：

```text
左上角是否 >= 0
右下角是否 < 图片宽高
```

## E009：定义了未使用的变量

日期与课程：Day 2，批量统计

原代码：

```python
total_count = 0
```

但最终没有更新或使用这个变量。

问题：

不会导致运行错误，但会使读代码的人误以为程序还存在另一套总数统计逻辑。

处理方法一：直接删除。

处理方法二：真正使用：

```python
total_count = success_count + error_count + skip_count
print(f"总数量：{total_count}")
```

以后如何避免：

完成脚本后检查每个变量是否至少被读取一次。没有用途的变量应删除。

## X001：实验验证高斯滤波不能使用偶数尺寸的核

日期与课程：Day 2，图像滤波

记录类型：主动实验，不计为练习错误。

实验文件：

```text
week01-opencv/day02/test03_image_filters.py
```

实验代码：

```python
kernel = (4, 4)

gaussian_image = cv2.GaussianBlur(
    filters_image,
    kernel,
    0
)
```

实验现象：

```text
Assertion failed:
ksize.width > 0
ksize.width % 2 == 1
ksize.height > 0
ksize.height % 2 == 1
```

错误含义：

```text
核宽度必须大于0并且是奇数。
核高度必须大于0并且是奇数。
```

实验结论与原因：

高斯滤波需要围绕一个明确的中心像素对周围像素分配权重。
正奇数尺寸，例如 `3、5、7、11`，都有唯一的中心位置。

`4x4` 没有唯一中心，所以不能作为这里的高斯核。

正确代码：

```python
kernel = (5, 5)

gaussian_image = cv2.GaussianBlur(
    filters_image,
    kernel,
    0
)
```

需要特别区分：

```text
cv2.blur()         可以使用矩形核，也可以使用偶数尺寸，例如 (4, 6)。
cv2.GaussianBlur() 核宽和高通常必须是正奇数，例如 (3, 5)。
cv2.medianBlur()   只传一个正奇数边长，例如 5。
```

这次主动使用 `(4, 4)` 并观察报错是有效的学习实验。
它验证了不同滤波函数对核参数的要求不完全相同，不能只凭函数名称推断参数限制。

## E012：只显示滤波结果，没有按要求保存结果图

日期与课程：Day 2，图像滤波

状态：已于 2026-06-18 修正，三种滤波结果均已保存。

出错文件：

```text
week01-opencv/day02/test03_image_filters.py
```

当前代码只使用：

```python
cv2.imshow("image", mean_image)
```

但没有：

```python
cv2.imwrite(...)
```

实际结果：

```text
outputs/filters 文件夹不存在
滤波输出图片数量为0
```

为什么这是问题：

`cv2.imshow()` 只用于临时观察。窗口关闭后，处理结果不会留下来，无法：

- 对比三种滤波效果。
- 复查不同参数的结果。
- 展示学习成果。
- 交给后续阈值分割或边缘检测使用。

正确流程：

```python
OUTPUT_DIR = BASE_DIR / "outputs" / "filters"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

mean_success = cv2.imwrite(
    str(OUTPUT_DIR / "mean_blur.png"),
    mean_image
)
```

高斯和中值滤波也应分别保存，并检查三个返回值。

以后如何避免：

开始练习前，把要求拆成检查清单：

```text
[ ] 读取
[ ] 处理
[ ] 显示
[ ] 保存
[ ] 检查保存结果
```

“在窗口中看到了”不等于“练习成果已经保存”。

## E013：对三种滤波的适用场景理解不够准确

日期与课程：Day 2，滤波理论问答

原回答：

```text
均值滤波适合需要快速取样的情况。
中值滤波在需要检测边缘的情况下用。
```

需要修正的地方：

### 均值滤波

它不是“快速取样”，而是使用邻域像素的平均值进行平滑。

更准确的理解：

```text
均值滤波计算简单、速度快，适合对速度要求高、
只需要基础平滑、并且不特别在意边缘变模糊的场景。
```

### 高斯滤波

原回答基本正确：

```text
常用于阈值分割、Canny边缘检测等操作前的平滑降噪。
```

高斯滤波会让靠近中心的像素具有更高权重，结果通常比简单均值滤波自然。

### 中值滤波

“保护边缘较好”是正确的，但它最典型的用途是去除椒盐噪声。

椒盐噪声表现为：

```text
图片中随机出现孤立的纯黑点或纯白点。
```

更准确的理解：

```text
中值滤波适合去除椒盐噪声，同时比均值滤波更能保护边缘。
它不代表所有边缘检测之前都应该优先使用中值滤波。
```

选择滤波方式要依据噪声类型和后续任务，而不是只看是否需要边缘。

## E014：没有理解 `GaussianBlur` 中 `sigmaX=0` 的实际含义

日期与课程：Day 2，滤波理论问答

原理解：

```text
0代表高斯分布在x方向的标准差，但不懂什么意思。
```

参数位置：

```python
cv2.GaussianBlur(
    image,
    (5, 5),
    0
)
```

第三个参数的名字是：

```text
sigmaX
```

它控制高斯分布在水平方向上的扩散程度，可以暂时把它理解成“模糊权重扩散得有多宽”。

但这里传入 `0` 的准确含义不是“标准差等于0，不发生模糊”，而是：

```text
让 OpenCV 根据高斯核尺寸自动计算 sigmaX。
```

因此：

```python
cv2.GaussianBlur(image, (5, 5), 0)
```

仍然会产生模糊效果。

当前学习阶段不需要计算高斯公式，只需要掌握：

```text
sigmaX = 0：让 OpenCV 自动选择，常用默认写法。
sigmaX 增大：高斯权重扩散范围通常更大，模糊效果会发生变化。
```

以后如何避免：

不能只根据传入值 `0` 猜测程序行为。应同时理解参数的特殊约定。

## E015：多个处理结果使用同一个输出路径，导致文件被覆盖

日期与课程：Day 2，图像滤波

状态：已于 2026-06-18 修正，均值、高斯和中值滤波使用不同输出文件名。

出错文件：

```text
week01-opencv/day02/test03_image_filters.py
```

当前只定义了一个输出路径：

```python
OUTPUTS_IMAGE_PATH = OUTPUTS_FILE_PATH / "IMG_9851.png"
```

随后三种滤波都保存到这个路径：

```python
cv2.imwrite(str(OUTPUTS_IMAGE_PATH), mean_image)
cv2.imwrite(str(OUTPUTS_IMAGE_PATH), gaussian_image)
cv2.imwrite(str(OUTPUTS_IMAGE_PATH), median_image)
```

实际现象：

控制台连续打印三次“保存成功”，但是 `outputs/filters` 中只有：

```text
IMG_9851.png
```

根本原因：

`cv2.imwrite()` 的“保存成功”只表示当前这一次写入成功。
如果目标路径已经存在，它会直接覆盖原来的文件，不会自动生成新文件名，也不会提示“文件已被覆盖”。

执行过程：

```text
第1次：保存均值滤波结果为 IMG_9851.png
第2次：高斯滤波结果覆盖 IMG_9851.png
第3次：中值滤波结果再次覆盖 IMG_9851.png
```

因此最后留下的是中值滤波结果，前两个结果已经丢失。

正确做法：

为不同处理结果定义不同路径：

```python
mean_output_path = OUTPUTS_FILE_PATH / "IMG_9851_mean.png"
gaussian_output_path = OUTPUTS_FILE_PATH / "IMG_9851_gaussian.png"
median_output_path = OUTPUTS_FILE_PATH / "IMG_9851_median.png"
```

分别保存：

```python
mean_save = cv2.imwrite(
    str(mean_output_path),
    mean_image
)

gaussian_save = cv2.imwrite(
    str(gaussian_output_path),
    gaussian_image
)

median_save = cv2.imwrite(
    str(median_output_path),
    median_image
)
```

为什么必须这样做：

- 三张结果可以并排比较。
- 可以确认每一种算法实际产生了什么效果。
- 后续处理可以选择指定结果。
- 不会因为覆盖而误以为三张结果都已保存。

工业项目中的影响：

如果原图、结果图、缺陷图或不同工位的图片使用相同路径，历史证据会被覆盖，可能导致检测记录无法追溯。

以后如何避免：

保存前先检查：

```text
每一种处理结果是否有唯一文件名？
不同输入图片是否会生成不同输出文件名？
重复运行是否允许覆盖旧结果？
```

判断“保存了几张图”时，不只看打印次数，还要检查输出目录中的实际文件数量。

## E016：把 `all()` 的返回值与 `None` 比较

日期与课程：Day 2，亮度与对比度

出错文件：

```text
week01-opencv/day02/test04_brightness_contrast.py
```

错误代码：

```python
if all((brighter_saved, contrast_saved, adjusted_saved)) is None:
    print("保存失败")
else:
    print("保存成功")
```

根本原因：

`all()` 的返回值一定是布尔值：

```python
True
False
```

它不会返回 `None`。

因此：

```python
all(...) is None
```

无论三张图保存成功还是失败，结果都一定是 `False`，程序总会进入 `else`，错误地打印保存成功。

示例：

```python
all((True, True, True))
# True

all((True, False, True))
# False

all((True, False, True)) is None
# False
```

正确代码：

```python
if all((brighter_saved, contrast_saved, adjusted_saved)):
    print("三张图片全部保存成功")
else:
    print("存在保存失败的图片")
```

也可以先保存结果：

```python
all_saved = all((
    brighter_saved,
    contrast_saved,
    adjusted_saved
))

if all_saved:
    print("全部保存成功")
else:
    print("存在保存失败")
```

以后如何避免：

使用函数前先确认返回值类型。`all()` 和 `any()` 返回布尔值，应该直接用于 `if`，不要与 `None` 比较。

## E017：打印字符串和路径时误用 `/`

日期与课程：Day 2，亮度与对比度

错误代码：

```python
print("保存成功，路径为："/brighter_image_path)
```

本次实际现象：

程序没有报错，但只打印了路径，前面的中文提示消失了。

原因：

`/` 在 `Path` 中用于拼接路径：

```python
BASE_DIR / "images" / "test.png"
```

这里不是在拼接文字。由于右侧是 `Path` 对象，Python 尝试把左侧字符串也当作路径的一部分处理。
而右侧路径是绝对路径，最终只保留了绝对路径，因此打印结果中没有中文提示。

正确写法一：使用逗号

```python
print("保存成功，路径为：", brighter_image_path)
```

正确写法二：使用 f-string

```python
print(f"保存成功，路径为：{brighter_image_path}")
```

必须区分：

```text
Path / "目录名"     用于路径拼接
"文字" + str(value) 用于字符串拼接
f"{value}"          用于格式化文字
print("文字", value) 用于打印多个值
```

以后如何避免：

看到 `/` 时先问自己：这里是在构造文件路径，还是在组织输出文字？只有构造路径时才使用 `/`。

## E018：输入图片与输出文件名来源标识不一致

日期与课程：Day 2，灰度直方图与均衡化

状态：已于 2026-06-18 修正，输出文件名改为通过 `IMAGE_FILE_PATH.stem` 自动生成。

出错文件：

```text
week01-opencv/day02/test05_histogram_equalization.py
```

当前输入：

```python
IMAGE_FILE_PATH = BASE_DIR / "images" / "IMG_9859.png"
```

当前输出：

```python
gray_path = OUTPUTS_FILE_PATH / "IMG_9852_gray.png"
equalized_path = OUTPUTS_FILE_PATH / "IMG_9852_equalized.png"
clahe_path = OUTPUTS_FILE_PATH / "IMG_9852_clahe.png"
histogram_path = OUTPUTS_FILE_PATH / "IMG_9852_histograms.png"
```

实际问题：

文件内容来自 `IMG_9859.png`，但输出名称却表示来自 `IMG_9852.png`。
图片可以正常生成，因此程序不会报错，但结果的来源信息是错误的。

工业项目中的风险：

- 无法根据结果图找到正确原图。
- NG 图片与生产记录可能对应错误。
- 调试时会使用错误样本复现问题。
- 客户追溯产品批次时得到错误证据。
- 批量处理时不同图片可能覆盖或混淆结果。

手动修正方法：

```python
gray_path = OUTPUTS_FILE_PATH / "IMG_9859_gray.png"
equalized_path = OUTPUTS_FILE_PATH / "IMG_9859_equalized.png"
clahe_path = OUTPUTS_FILE_PATH / "IMG_9859_clahe.png"
histogram_path = OUTPUTS_FILE_PATH / "IMG_9859_histograms.png"
```

更可靠的方法是从输入路径自动取得文件主名：

```python
image_name = IMAGE_FILE_PATH.stem

gray_path = OUTPUTS_FILE_PATH / f"{image_name}_gray.png"
equalized_path = OUTPUTS_FILE_PATH / f"{image_name}_equalized.png"
clahe_path = OUTPUTS_FILE_PATH / f"{image_name}_clahe.png"
histogram_path = OUTPUTS_FILE_PATH / f"{image_name}_histograms.png"
```

`stem` 的作用：

```python
Path("IMG_9859.png").stem
# "IMG_9859"
```

为什么推荐自动生成：

以后只要修改 `IMAGE_FILE_PATH`，所有输出文件名会自动同步，不需要手工修改四个位置。

以后如何避免：

输出文件名中包含输入来源时，不要重复手写编号。尽量从 `image_path.stem` 自动生成。

# 二、通用易错点参考

## 1. 图片尺寸与坐标顺序

### `shape` 的顺序

```python
height, width, channels = image.shape
```

顺序是：

```text
高度 height、宽度 width、通道数 channels
```

如果分辨率是 `1920x1080`，通常表示：

```text
宽度 1920，高度 1080
```

对应的彩色图片 `shape` 是：

```python
(1080, 1920, 3)
```

### 像素访问的顺序

```python
pixel = image[y, x]
```

NumPy 数组先写行、再写列，因此是先 `y` 后 `x`。

### ROI 裁剪的顺序

```python
roi = image[y1:y2, x1:x2]
```

错误写法：

```python
roi = image[y1:x1, y2:x2]
```

### OpenCV 画框的顺序

```python
cv2.rectangle(
    image,
    (x1, y1),
    (x2, y2),
    color,
    thickness
)
```

必须区分：

```text
NumPy 裁剪：[y, x]
OpenCV 坐标点：(x, y)
```

## 2. 图片读取失败

`cv2.imread()` 读取失败时不会自动抛出异常，而是返回 `None`：

```python
image = cv2.imread(str(image_path))
```

### 单张图片程序

读取失败后不能继续执行：

```python
if image is None:
    raise FileNotFoundError(f"图片读取失败：{image_path}")
```

如果只打印：

```python
if image is None:
    print("读取失败")
```

后面的 `image.copy()` 或 `image.shape` 仍会报错。

### 批量图片程序

批量处理中，一张图片失败不应该终止全部任务：

```python
if image is None:
    error_count += 1
    print(f"图片读取失败：{image_path.name}")
    continue
```

这里可以使用 `continue`，因为代码位于 `for` 循环内部。

### `break` 和 `continue`

两者只能在循环中使用：

```text
continue：结束当前一轮，继续下一轮
break：直接结束整个循环
```

单张图片程序不在循环中，不能使用 `break` 或 `continue`。

## 3. `Path` 路径处理

### 当前脚本目录

```python
BASE_DIR = Path(__file__).resolve().parent
```

含义：

```text
__file__  当前 Python 文件路径
resolve() 转换为绝对路径
parent    获取当前文件所在文件夹
```

### 拼接路径

```python
images_dir = BASE_DIR / "images"
output_path = output_dir / image_path.name
```

### 判断是否为文件

正确：

```python
image_path.is_file()
```

错误：

```python
image_path.is_file
```

`is_file` 是方法，必须使用括号执行。

### OpenCV 路径参数

为了兼容不同 OpenCV 版本，统一转换成字符串：

```python
image = cv2.imread(str(image_path))
cv2.imwrite(str(output_path), image)
```

## 4. 图片后缀筛选

推荐：

```python
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
```

注意 `.jpeg` 前面也有点。

使用 `lower()` 兼容大写后缀：

```python
image_path.suffix.lower()
```

例如：

```text
.PNG -> .png
.JPG -> .jpg
```

完整判断：

```python
if not image_path.is_file():
    skip_count += 1
    continue

if image_path.suffix.lower() not in IMAGE_SUFFIXES:
    skip_count += 1
    continue
```

## 5. 原图与结果图

`cv2.rectangle()` 和 `cv2.putText()` 会直接修改传入的图片。

为了保留原图，应先复制：

```python
marked_image = image.copy()
```

之后只修改：

```python
marked_image
```

原始变量 `image` 保持不变。

## 6. BGR 颜色

OpenCV 默认顺序是：

```text
(Blue, Green, Red)
```

常用颜色：

```python
(255, 0, 0)      # 蓝色
(0, 255, 0)      # 绿色
(0, 0, 255)      # 红色
(0, 255, 255)    # 黄色
(255, 255, 255)  # 白色
```

OpenCV 图片用 Matplotlib 显示前通常需要转换：

```python
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
```

## 7. 检测框边界

直接计算：

```python
x1 = width // 2 - 200
x2 = width // 2 + 200
```

在小图片中可能得到负数或超出图片范围。

推荐：

```python
half_box_size = 200

x1 = max(width // 2 - half_box_size, 0)
y1 = max(height // 2 - half_box_size, 0)

x2 = min(width // 2 + half_box_size, width - 1)
y2 = min(height // 2 + half_box_size, height - 1)
```

作用：

```text
max(..., 0)          防止左边和上边小于 0
min(..., width - 1)  防止右边超出图片
min(..., height - 1) 防止下边超出图片
```

## 8. 文字坐标

`cv2.putText()` 的坐标表示文字基线的左下角：

```python
cv2.putText(
    image,
    "ROI",
    (text_x, text_y),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 255, 0),
    2,
    cv2.LINE_AA
)
```

文字放在框上方：

```python
text_x = x1
text_y = max(y1 - 10, 30)
```

文字放在框内部：

```python
text_x = x1 + 5
text_y = y1 + 30
```

OpenCV 内置字体通常不能直接正确显示中文。学习阶段先使用：

```text
ROI、OK、NG、CHECK、DEFECT
```

## 9. 保存结果检查

`cv2.imwrite()` 返回布尔值：

```python
save_success = cv2.imwrite(str(output_path), marked_image)
```

应该检查：

```python
if save_success:
    success_count += 1
else:
    error_count += 1
```

不要只调用 `cv2.imwrite()` 而忽略返回值。

## 10. 批量处理计数分类

建议明确区分：

```text
success_count：图片读取和保存均成功
error_count：图片读取失败或保存失败
skip_count：不是文件或后缀不支持
```

总数量：

```python
total_count = success_count + error_count + skip_count
```

不要定义一个变量后完全不使用。

## 11. 缩放图片

`image.shape[:2]` 返回：

```python
height, width
```

但是 `cv2.resize()` 的尺寸参数是：

```python
(width, height)
```

示例：

```python
height, width = image.shape[:2]

small_image = cv2.resize(
    image,
    (int(width * scale), int(height * scale))
)
```

ROI 坐标必须基于当前实际处理的图片：

```text
在缩小图上确定的坐标，只能直接用于相同尺寸的缩小图。
不能不换算就用于原始大图。
```

## 12. 灰度图

转换：

```python
gray_image = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2GRAY
)
```

数据形状变化：

```text
彩色图：(height, width, 3)
灰度图：(height, width)
```

灰度图没有第三个颜色通道维度。

## 13. Day 1-2 核心记忆

```python
# 读取
image = cv2.imread(str(image_path))

# 尺寸
height, width = image.shape[:2]

# 像素
pixel = image[y, x]

# ROI
roi = image[y1:y2, x1:x2]

# 复制
marked_image = image.copy()

# 画框
cv2.rectangle(marked_image, (x1, y1), (x2, y2), color, thickness)

# 写字
cv2.putText(marked_image, text, (x, y), font, scale, color, thickness)

# 保存
save_success = cv2.imwrite(str(output_path), marked_image)
```
