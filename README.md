# DataEX_Sc-User-Guide

**User Guide for DataEX-Sc**

This guide will help you understand and effectively use the various features of DataEX-Sc.

## Basic Workflow

1. **Upload Image**  
   Drag and drop or click to upload a scatter plot image. The system will automatically perform axis detection and axis tick value recognition.

2. **Correct Ticks**  
   Use the Anchor Point Tool or Smart Anchor Point Tool to manually correct OCR-identified tick marks and axis scale types (the web version does not use paid high-precision OCR services).

3. **Legend Analysis**  
   If the image contains a legend, click the **Analyze Legend** button in the Legend Detection panel to perform legend feature analysis.

4. **Extract Data**  
   Click the **Extract Data Series** button. The system will automatically classify scatter points and extract their real-world coordinates.

5. **Correct Data**  
   Use the tools described below to manually correct scatter point classification results.

6. **Export Data**  
   Export the extracted data as a CSV file.

https://github.com/user-attachments/assets/64320b4f-c328-49f6-b466-b7d38339cf27


## Tool Details

You can use keyboard shortcuts to quickly switch between tools.

**Primary Shortcuts:**

*   **Eraser Tool (E)**: Deletes individual or contiguous data points.
*   **Data Point Tool (D)**: Manually adds data points to the chart.
*   **Anchor Point Tool (A)**: Sets calibration points for the axes. Clicking near the bottom or left side of the image will automatically identify the point as an X-axis or Y-axis anchor.

**Additional Shortcuts (To be expanded):**

* **Selection Tool (V)**: Used to pan and zoom the image. Hold down the `Ctrl` (Windows/Linux) or `Cmd` (macOS) key to activate the magnifier.

* **Box Selection Tool (B)**: Selects multiple data points at once.

* **Color Picker Tool (I)**: Click anywhere on the image to get the hexadecimal color value of that point, which is automatically copied to the clipboard.

  There are 5 status indicators on the interface to help users understand which conditions have been met. At a minimum, conditions 4 and 5 must be satisfied. The more conditions are met, the better the data extraction results will be:

  **5.1 🖼️ Image Status**

  - 🟢 Green: Image uploaded
  - 🔴 Red: No image uploaded

  **5.2 🔍 Detection Status**

  - 🟢 Green: Legend detection results (shapes or boxes) exist
  - 🔴 Red: No legend detection results

  **5.3 🏷️ Legend Analysis Status**

  - 🟢 Green: Labeled legend symbols exist (will be used for extraction)
  - 🟠 Orange: No legend symbols (extraction is still possible, but labels will not be used)

  **5.4 📏 X-axis Anchor Status**

  - 🟢 Green: ≥2 anchors
  - 🔴 Red: <2 anchors
  - Display format: `X-axis Anchors: Number/2`

  **5.5 📏 Y-axis Anchor Status**

  - 🟢 Green: ≥2 anchors
  - 🔴 Red: <2 anchors
  - Display format: `Y-axis Anchors: Number/2`

  

  Manual correction (optional)

https://github.com/user-attachments/assets/f0025ae3-d88b-425d-a9ba-459636688ab3



## Functional Panels

### 1. Object Detection Panel

*   **Function**: Controls YOLO model detection for identifying legends, coordinate regions, solid boundaries, and legend boxes.
*   **Display Control**: You can toggle the display of detection results on the canvas.

### 2. Coordinate Calibration Panel

*   **Function**: Manages axis tick anchor points and supports manual correction of tick values.
*   **Title Selection**: You can select the axis title area. The system will automatically recognize the title text via OCR.
*   **Display Control**: You can toggle the display of axis lines, labels, and anchor points on the canvas.

### 3. Legend Detection Panel

*   **Smart Analysis (🔍) (Recommended)**: The system automatically detects symbols and text labels in the legend and performs intelligent matching.
*   **Manual Process**: You can also first click "Detect Legend Box," then use the "Analyze Selected Area" function to manually extract legend information.

### 4. Caption Detection Panel

*   **Auto Detect**: Click the **Auto Detect** button for the system to automatically identify captions/titles in the image.
*   **Manual Select**: Click the **Manual Select** button to manually select the caption/title area and invoke OCR for recognition.

### 5. Data Extraction Panel

*   **Data Extraction**: Automatically extracts data series based on legend symbols or color clustering.
*   **Legend Fusion**: If legend symbols are detected, the system automatically uses the legend labels as data series names.
*   **Deduplication**: Automatically removes duplicate or overly close data points and displays deduplication statistics.
*   **Display Control**: You can toggle the display of extracted data points on the canvas.

### 6. Data Chart & Export(Due to limited system computing power, service may experience overload and interruption under high-concurrency scenarios)

*   **Chart Visualization**: Uses ECharts for real-time visualization of the extracted data.
*   **Smart Labeling**: Charts automatically use labels identified from the legend as data series names.
*   **Data Export**: Supports exporting data as a CSV file.

## Test Account

To be announced.

# 用户指南-中文

本指南旨在帮助您了解并有效使用 DataEX-Sc 的各项功能。

## 基本流程

1.  **上传图像**  
    支持拖拽或点击上传散点图图像。上传后，系统将自动进行坐标轴检测与坐标轴刻度线数值识别。

2.  **刻度线校正**  
    可使用锚点工具或智能锚点工具，对 OCR 识别出的刻度线位置及坐标轴尺度类型进行手动校正（网站版本未调用付费高精度 OCR 服务）。

3.  **图例分析**  
    若图像包含图例，可在图例检测面板中点击 **Analyze Legend** 按钮，进行图例特征分析。

4.  **提取数据**  
    点击 **Extract Data Series** 按钮，系统将自动进行散点分类并抽取散点的真实坐标。

5.  **数据校正**  
    可使用下文介绍的工具对散点分类结果进行手动校正。

6.  **导出数据**  
    将提取的数据导出为 CSV 格式文件。

## 工具详解

您可以使用键盘快捷键快速切换工具。

**主要快捷键：**

- **橡皮擦工具 (E)**：删除单个或连续的数据点。
- **数据点工具 (D)**：手动在图表上添加数据点。
- **锚点工具 (A)**：设置坐标轴校准点。靠近图像底部或左侧点击，可自动识别为 X 轴或 Y 轴锚点。

**其他快捷键（持续更新中）：**

- **选择工具 (V)**：用于平移和缩放图像。按住 `Ctrl`（Windows/Linux）或 `Cmd`（macOS）键可激活放大镜功能。
- **框选工具 (B)**：一次性选择多个数据点。
- **取色器工具 (I)**：点击图像任意位置可获取该点的十六进制颜色值，并自动复制到剪贴板。

## 功能面板

### 1. 目标检测面板

- **功能**：控制 YOLO 模型检测，用于识别图例、坐标区域、实线边界及图例框。
- **显示控制**：可开启或关闭检测结果在画布上的显示。

### 2. 坐标校准面板

- **功能**：管理坐标轴刻度线锚点，支持手动校正刻度线数值。
- **标题框选**：可框选坐标轴标题区域，系统将通过 OCR 自动识别标题文字。
- **显示控制**：可开启或关闭坐标轴标线、标签及锚点在画布上的显示。

### 3. 图例检测面板

- **智能分析 (🔍)**（推荐）：系统自动检测图例中的符号与文字标签，并进行智能匹配。
- **手动流程**：也可先点击“检测图例框”，再使用“分析选中区域”功能手动提取图例信息。

### 4. 说明检测面板

- **自动检测**：点击 **Auto Detect** 按钮，系统将自动识别图像中的标题。
- **手动检测**：点击 **Manual Select** 按钮，可手动选择标题区域，并调用 OCR 进行识别。

### 5. 数据提取面板

- **数据提取**：基于图例符号或颜色聚类，自动提取数据系列。
- **图例融合**：若检测到图例符号，系统会自动将图例标签作为数据系列的名称。

界面上有5个状态指示器，帮助用户了解哪些条件已满足，至少需要满足条件4、5，满足的条件数量越多数据提取效果越好：

5.1**🖼️ 图像状态**

- 🟢 绿色：已上传图像
- 🔴 红色：未上传图像

5.2**🔍 检测状态**

- 🟢 绿色：有图例检测结果（shapes或boxes）
- 🔴 红色：无图例检测结果

5.3**🏷️ 图例分析状态** 

- 🟢 绿色：有标记的图例符号（会用于提取）
- 🟠 橙色：无图例符号（仍可提取，但不会使用标签）

5.4**📏 X轴锚点状态**

- 🟢 绿色：≥2个锚点
- 🔴 红色：<2个锚点
- 显示格式：`X轴锚点: 数量/2`

5.5**📏 Y轴锚点状态** 

- 🟢 绿色：≥2个锚点
- 🔴 红色：<2个锚点
- 显示格式：`Y轴锚点: 数量/2`

### 6. 数据图表与导出

- **图表展示**：使用 ECharts 实时可视化所提取的数据。
- **智能标签**：图表会自动采用从图例中识别的标签作为数据系列名称。
- **数据导出**：支持将数据导出为 CSV 文件。



## 测试账号（系统算力有限，高并发场景下可能因过载导致服务中断）

待公布。
