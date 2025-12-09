# DataEX_Sc-User-Guide
**User Guide**  
This guide will help you understand how to effectively use the various features of DataEX-Sc.

**Basic Workflow**  
1. **Upload Image**: Drag-and-drop or click to upload a scatter plot image.  
2. **Automatic Detection**: Click "Start Detection" to automatically identify coordinate areas, legends, etc.  
3. **Set Anchor Points**: Use the anchor tool to mark known values on the axes for coordinate system calibration.  
4. **Extract Data**: The system will automatically or manually extract data points based on calibration information and legends.  
5. **Export Data**: Export extracted data in CSV, JSON, or Excel format.

**Tool Details**  
You can use keyboard shortcuts to quickly switch between tools.

- **Selection Tool (V)**: Used for panning and zooming the image. Hold Ctrl/Cmd to activate the magnifier.  
- **Box Selection Tool (B)**: Used to select multiple data points at once.  
- **Eraser Tool (E)**: Used to delete individual or continuous data points.  
- **Color Picker Tool (I)**: Click anywhere on the image to get the color value (hexadecimal) of that point, which is automatically copied to the clipboard.  
- **Anchor Tool (A)**: Used to set calibration points on the axes. Click near the bottom or left side of the image to automatically identify it as an X-axis or Y-axis anchor point.  
- **Data Point Tool (D)**: Used to manually add data points on the chart.

**Feature Panels**  
1. **Object Detection Panel**  
   - **Function**: Controls YOLO model detection for identifying legends, coordinate areas, solid boundaries, and legend boxes.  
   - **Display Control**: You can toggle the display of detection results on the canvas.

2. **Coordinate Calibration Panel**  
   - **Function**: Manages axis anchor points, supporting manual addition and deletion.  
   - **Title Selection**: Click the "📋" button to select axis titles, which will be automatically recognized via OCR.  
   - **Display Control**: You can toggle the display of axis lines, labels, and anchor points on the canvas.

3. **Legend Detection Panel**  
   - **Smart Analysis (🔍)**: Recommended for use. The system automatically detects symbols and text labels in the legend and performs intelligent matching.  
   - **Manual Process**: You can also first "Detect Legend Box" and then "Analyze Selected Area" for manual extraction.

4. **Data Extraction Panel**  
   - **Data Extraction**: Automatically extracts data series based on legend symbols or color clustering.  
   - **Legend Integration**: If legend symbols are detected, the system automatically uses legend labels as data series names.  
   - **Deduplication Mechanism**: Automatically removes duplicate or overly close data points and displays deduplication statistics.  
   - **Display Control**: You can toggle the display of extracted data points on the canvas.

5. **Data Chart & Export**  
   - **Chart Display**: Uses ECharts for real-time visualization of extracted data.  
   - **Smart Labeling**: Charts automatically use recognized labels from legends as series names.  
   - **Data Export**: Supports exporting data to CSV, JSON, or Excel files.

6. **Test Account**  
   - To be announced.
  
# 用户指南-中文

本指南将帮助您了解如何有效使用DataEX-Sc的各项功能。

## 基本流程

1.  **上传图像**: 通过拖拽或点击上传散点图图像。
2.  **自动检测**: 点击“开始检测”自动识别坐标区域、图例等。
3.  **设置锚点**: 使用锚点工具标记坐标轴上的已知数值，以校准坐标系。
4.  **提取数据**: 系统将根据校准信息和图例，自动或手动提取数据点。
5.  **导出数据**: 将提取的数据导出为CSV、JSON或Excel格式。

## 工具详解

您可以使用键盘快捷键快速切换工具。

- **选择工具 (V)**: 用于平移和缩放图像。按住`Ctrl/Cmd`键可激活放大镜。
- **框选工具 (B)**: 用于一次性选择多个数据点。
- **橡皮擦工具 (E)**: 用于删除单个或连续的数据点。
- **取色器工具 (I)**: 点击图像任意位置可获取该点的颜色值（十六进制），并自动复制到剪贴板。
- **锚点工具 (A)**: 用于设置坐标轴的校准点。靠近图像底部或左侧点击，可自动识别为X轴或Y轴锚点。
- **数据点工具 (D)**: 用于手动在图表上添加数据点。

## 功能面板

### 1. 目标检测面板

- **功能**: 控制YOLO模型的检测，用于识别图例、坐标区域、实线边界和图例框。
- **显示控制**: 您可以打开或关闭检测结果在画布上的显示。

### 2. 坐标校准面板

- **功能**: 管理坐标轴的锚点，支持手动添加和删除。
- **标题框选**: 点击“📋”按钮，可以框选坐标轴的标题，系统将通过OCR自动识别。
- **显示控制**: 您可以打开或关闭坐标轴标线、标签和锚点在画布上的显示。

### 3. 图例检测面板

- **智能分析 (🔍)**: 推荐使用此功能。系统会自动检测图例中的符号和文字标签，并进行智能匹配。
- **手动流程**: 您也可以先“检测图例框”，然后“分析选中区域”来手动提取。

### 4. 数据提取面板

- **数据提取**: 基于图例符号或颜色聚类，自动提取数据系列。
- **图例融合**: 如果检测到了图例符号，系统会自动将图例标签作为数据系列的名称。
- **去重机制**: 自动移除重复或距离过近的数据点，并显示去重统计。
- **显示控制**: 您可以打开或关闭提取的数据点在画布上的显示。

### 5. 数据图表与导出

- **图表展示**: 使用ECharts实时可视化提取的数据。
- **智能标签**: 图表会自动使用图例中识别的标签作为系列名称。
- **数据导出**: 支持将数据导出为CSV、JSON或Excel文件。

### 6. 测试账号
待公布
