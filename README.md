# DataEX-Sc User Guide

This guide helps you understand and effectively use the features of DataEX-Sc. DataEX-Sc is a modern web application for automatically extracting data from scatter plots.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Workflow](#basic-workflow)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Functional Panels](#functional-panels)
- [Status Indicators](#status-indicators)
- [Display Controls](#display-controls)
- [Batch Processing](#batch-processing)
- [User Management](#user-management)
- [FAQ](#faq)

## Quick Start

- Batch automatic processing tutorial
  
https://github.com/user-attachments/assets/fed87af9-5569-4e73-b2e6-8c93c68bf4a4

- Single image step-by-step tutorial

https://github.com/user-attachments/assets/64320b4f-c328-49f6-b466-b7d38339cf27

- Manual correction tutorial
  
https://github.com/user-attachments/assets/a183e8bf-0cb3-4729-aeec-707ba21d0c8b

https://github.com/user-attachments/assets/e037edf4-5187-49de-8121-454cf2739e31
  
## Basic Workflow

### 1. Upload Image

- **Upload method**: Drag and drop or click to upload scatter plot images
- **Supported formats**: JPG, PNG and other common image formats
- **Auto processing**: After upload, the system will automatically perform axis detection and axis tick value recognition

### 2. Axis Detection and Calibration

- **Auto detection**: Click the "Axis Recognition" button in the "coordinate calibration" panel, and the system will automatically:
  - Object detection (legend shapes, coordinate regions, solid line boundaries, legend boxes)
  - Axis label recognition (OCR recognizes tick mark values)
  - Auto-generate anchors (based on recognized tick mark values)

- **Manual calibration**: Use anchor tools to manually correct OCR-identified tick mark positions and axis scale types
  - **Regular anchor tool**: Manually add and edit anchors
  - **Smart anchor tool**: Automatically recognize tick values by selecting regions
  - **Axis scale**: Supports linear and logarithmic scales (X-axis and Y-axis can be set independently)

### 3. Legend Analysis

- **Smart analysis (recommended)**: Click the "Analyze Legend" button in the "legend detection" panel, and the system will automatically:
  - Detect symbols in the legend
  - Recognize legend text labels
  - Intelligently match symbols with labels

- **Manual process**:
  - First click "Detect Legend Boxes" to detect legend regions (you can manually add, adjust, and delete legend regions)
  - Then click the "Analyze Legend" button to extract legend information (you can manually add, edit, analyze, and delete legend symbols)

### 4. Chart Caption Detection (Optional)

- **Auto detection**: Click the "Auto Detect" button in the Caption Detection panel, and the system will automatically identify chart titles/captions at the bottom of the image
- **Manual selection**: Click the "Manual Select" button to manually select the title region for OCR recognition
- **Edit function**: Click the "Edit Caption" button to manually edit, or click the "Clear" button to clear the detected caption text

### 5. Extract Data

- **Extract button**: Click the "Extract Data Series" button in the data extraction panel
- **Auto processing**:
  - Scatter point classification
  - Coordinate conversion (pixel coordinates → real data coordinates)
  - Data deduplication (remove duplicate or overly close data points)
  - Series naming (automatically use legend labels as series names)

### 6. Data Correction (Optional)

Use tools to manually correct scatter classification results:

- **Delete incorrect data points**: Use the eraser tool
- **Add missing data points**: Use the data point tool
- **Reassign series**: Click data points in Data Visualization to move them to other series
- **Edit series names**: Edit data series names in the Data Series Management panel

### 7. Export Data

- **Export format**: CSV file
- **Export content**:
  - Series ID
  - Series name
  - X-axis data (using axis title)
  - Y-axis data (using axis title)
- **Export location**: Automatically downloaded to the browser's default download directory

## Keyboard Shortcuts

You can use keyboard shortcuts to quickly switch between tools and improve work efficiency.

### Main Tools

| Tool                | Shortcut | Description                                                  |
| ------------------- | -------- | ------------------------------------------------------------ |
| **Selection Tool**  | **F**    | Switch to selection state, can be used to select detected scatter points on the original image; can be used with arrow keys to fine-tune scatter point positions |
| **Eraser Tool**     | **S**    | Delete individual or consecutive data points. Click data points on the canvas to delete them |
| **Anchor Tool**     | **A**    | Set axis calibration points. Click on tick mark positions on the image, and the system will automatically identify them as X-axis or Y-axis anchors based on the click position (near bottom or left). Click to edit tick values |
| **Data Point Tool** | **D**    | Manually add data points to the chart. Click on the canvas to add data points to the currently selected series, or add unrecognized data series |

### Tool Usage Tips

- **Batch delete scatter points**: When using shortcut S, you can continuously click multiple data points to batch delete scatter points
- **Batch add scatter points**: First select the target series in the Data series panel, then continuously click multiple data points on the original image to batch add scatter points
- **Adjust the Data Visualization interface**: move the view with the left mouse button and zoom with the scroll wheel.

## Functional Panels

### 1. Object Detection Panel

**Function**:

- Controls YOLO model detection to identify key elements in charts:
  - Legend shapes (legend_shape)
  - Coordinate regions (coord_region)
  - Solid line boundaries (solid_line_bound)
  - Legend boxes (legend_box)

**Operations**:

- Clicking the "Axis Recognition" button (in the Coordinate Calibration panel) will automatically execute object detection
- Detection results will automatically display in the panel
- Supports manual drawing of detection boxes (via the "+ Add" button)

**Display control**:

- Toggle display of detection results on the canvas (via the display control bar)

**Manual annotation**:

- If automatic detection is inaccurate, you can manually draw detection boxes
- Supports adding, editing, and deleting manually annotated detection boxes

### 2. Coordinate Calibration Panel

**Function**:

- Manage axis tick anchors
- Click the "Add Anchor" button to manually add anchors
- Supports editing and deleting anchors
- Click the "Clear Anchors" button to clear all anchors
- Set axis scale type (linear/logarithmic)

**Axis recognition**:

- Click the "Axis Recognition" button to automatically recognize axis labels
- Auto-generate anchors (based on OCR-recognized tick values)

**Title recognition**:

- Click the "Select Title" button
- Select the axis title region on the image
- The system will automatically recognize the title text via OCR
- Click the "Edit Title" button to manually edit the title

**Smart anchor**:

- Click the "🔬Smart Anchor" button (experimental feature)
- Select a region containing tick marks on the image
- The system automatically recognizes tick values within the region and generates anchors

**Display control**:

- Toggle display of axis lines, labels, and anchors on the canvas

### 3. Legend Detection Panel

**Smart analysis (🔍) (recommended)**:

- System automatically detects symbols and text labels in the legend
- Performs intelligent matching to associate symbols with labels
- Supports various symbol types: circles, squares, triangles, diamonds, etc.
- Supports solid and hollow symbol recognition

**Manual process**:

1. Click the "Detect Legend Boxes" button to detect legend regions
2. Select detected legend boxes or click "+ Add Legend Box" to manually draw legend boxes
3. Click the "Analyze Legend" button to extract legend information
4. Manually add, edit, and delete legend symbols and labels

**Symbol management**:

- View all detected legend symbols
- Edit symbol labels
- Delete incorrect symbols
- Manually add symbols (by drawing)

**Optimization function**:

- Click the "Optimize" button (if available), and the system will automatically optimize symbol matching results

### 4. Caption Detection Panel

**Auto detection**:

- Click the "Auto Detect" button
- System automatically identifies chart titles/captions in the bottom region of the image
- Automatically executes OCR recognition

**Manual selection**:

- Click the "Manual Select" button
- Select the title/caption region on the image
- System automatically executes OCR recognition on that region

**Edit function**:

- View recognized caption text (displayed under the "Chart Caption" label)
- Click the "Edit Caption" button to manually edit
- Click the "Clear" button to clear the caption

### 5. Data Series Management Panel

**Data extraction**:

- Click the "Extract Data Series" button to execute data extraction
- System selects extraction strategy based on the following conditions:
  - With legend symbols: Prioritizes template matching
  - Without legend symbols: Uses color clustering
  - Without calibration data: Uses pixel coordinate mode

**Extraction status**:

- Display extraction progress and status
- Display the number of extracted data series
- Display the number of data points in each series

**Data series management**:

- View all extracted data series (displayed in the "Data series" area)
- Edit series names (click series name or edit icon)
- View series statistics (number of data points, etc.)
- Click the "Clear all" button to clear all data points

**Data point management**:

- View all data points
- Click data points to locate them in the chart
- Reassign data points to other series
- Delete data points

**Deduplication function**:

- Automatically remove duplicate or overly close data points
- Display deduplication statistics (number of data points before and after deduplication)

**Display control**:

- Toggle display of extracted data points on the canvas

### 6. Data Visualization and Export

**Chart display**:

- Use ECharts to visualize extracted data in real-time
- Supports interactive operations such as zoom and pan
- Toggle display/hide of specified data series
- Automatically uses labels recognized from legends as data series names

**Data interaction**:

- Click data points in the chart to locate corresponding original data points on the canvas
- View precise values of data points in the chart
- Supports chart type switching (scatter plot, line chart, etc.)

**Data export**:

- Click the "Export Data" button to export data (the button will display the number of valid data points, e.g., "Export Data (123 valid points)")
- Export format: CSV file (UTF-8 encoding with BOM)
- Export content:
  - Column 1: seriesId (series ID)
  - Column 2: seriesName (series name)
  - Column 3: X-axis data (using axis title as column name)
  - Column 4: Y-axis data (using axis title as column name)
- Filename: `extracted_data.csv`

## Status Indicators

There are 5 status indicators on the interface to help users understand which conditions have been met. **At least conditions 4 and 5 must be satisfied**. The more conditions that are met, the better the data extraction results:

### 1. Image Status

- 🟢 **Green**: Image uploaded
- 🔴 **Red**: No image uploaded

### 2. Detection Status

- 🟢 **Green**: Legend detection results exist (shapes or boxes)
- 🔴 **Red**: No legend detection results

**Note**: Detecting legends helps improve data extraction accuracy, but is not required.

### 3. Legend Analysis Status

- 🟢 **Green**: Labeled legend symbols exist (will be used for extraction)
- 🟠 **Orange**: No legend symbols (extraction is still possible, but labels will not be used)

**Note**: When legend symbols exist, the system will use template matching strategy for better extraction results.

### 4. X-axis Anchor Status

- 🟢 **Green**: ≥2 anchors
- 🔴 **Red**: <2 anchors
- **Display format**: `X-axis Anchors: Count/2`

**Note**: At least 2 anchors are required on the X-axis for coordinate conversion. If only pixel coordinates are available, real data coordinates cannot be converted.

### 5. Y-axis Anchor Status

- 🟢 **Green**: ≥2 anchors
- 🔴 **Red**: <2 anchors
- **Display format**: `Y-axis Anchors: Count/2`

**Note**: At least 2 anchors are required on the Y-axis for coordinate conversion. If only pixel coordinates are available, real data coordinates cannot be converted.

## Display Controls

The display control bar allows you to toggle the display/hide of various elements on the canvas for convenient viewing and editing:

### Control Items

1. **automatic detection box** (green)
   - Show/hide object detection results (coordinate regions, legend shapes, solid line boundaries, etc.)

2. **coordinate calibration** (blue)
   - Show/hide axis calibration information (axis lines, anchors, labels, etc.)

3. **legend box** (orange)
   - Show/hide legend detection results (legend region selection)

4. **caption detection** (purple)
   - Show/hide chart caption detection results

5. **data extraction** (red)
   - Show/hide data points after data extraction

### Usage Tips

- When performing different operations, you can hide elements that don't need to be displayed to keep the canvas clear
- When checking extraction results, you can show only data points and hide other detection boxes
- When calibrating axes, you can show only coordinate calibration-related elements

## Batch Processing

The system supports batch processing of multiple images to improve processing efficiency.

### Usage Method

1. **Select images**:
   - In the image list sidebar, enable multi-select mode
   - Select images that need batch processing (multiple selection supported)

2. **Start batch processing**:
   - Click the batch processing button
   - The system will process selected images in sequence

3. **Processing modes**:
   - **Pixel coordinate mode**: If there are insufficient calibration anchors, the system will use pixel coordinate mode to extract data
   - **Complete mode**: If there are sufficient calibration anchors, the system will perform complete coordinate conversion

4. **Processing status**:
   - Display processing progress for each image
   - Display processing success/failure status
   - Display error messages (if any)

5. **Result viewing**:
   - After processing is complete, you can view processing results image by image
   - You can perform individual corrections on each image

### Batch Processing Notes

- Batch processing uses saved analysis results for each image (detections, calibrations, legends, etc.)
- If an image lacks necessary analysis data, the system will use available data for processing
- If calibration data is missing, pixel coordinate mode will be used for extraction
- Batch processing can be cancelled at any time during the process

## User Management

The system supports multiple users and provides user management functions (available only to administrators).

### User Registration and Login

- **Registration**: New users can only register through administrators
- **Login**: Use email and password to log into the system
- **Session management**: Login status will be maintained until actively logged out

### Test Account

- Email：customer2025@test.com
- Password：DataEx251221!

## FAQ

### Q1: Why are the extracted data point coordinates inaccurate?

**Possible reasons**:

- Insufficient X-axis or Y-axis anchors (at least 2 required)
- Inaccurate anchor positions
- Incorrect axis scale type settings (linear/logarithmic)

**Solutions**:

- Check status indicators to ensure both X-axis and Y-axis have sufficient anchors
- In the Coordinate Calibration panel, click the "Axis Recognition" button to automatically recognize and generate anchors
- Or click the "Add Anchor" button to manually add anchors
- Recalibrate anchor positions and values (click anchors to edit)
- Confirm axis scale type settings are correct

### Q2: What if legend symbols are not recognized?

**Solutions**:

- In the Legend Detection panel, click the "Detect Legend Boxes" button to detect legend regions, and you can manually adjust the position and size of legend regions/legend shape regions on the original image
- Click the "Analyze Legend" button to analyze legend symbols, and you can manually adjust the position and size of legend symbol regions on the original image
- If automatic detection is inaccurate, you can click "+ Add Legend Box" to manually draw legend boxes
- After manually adding legend symbols, click "Analyze Added" for analysis

### Q3: No data points after data extraction?

**Possible reasons**:

- Coordinate regions were not correctly detected
- Legend symbol matching failed
- Color clustering failed to identify data points

**Solutions**:

- Click the "Axis Recognition" button in the Coordinate Calibration panel to perform detection
- Check detection results in the Object Detection panel to confirm coordinate regions were correctly detected
- If detection is inaccurate, you can manually draw coordinate regions in the Object Detection panel
- Check legend analysis results in the Legend Detection panel
- Confirm coordinate calibration is complete (at least 2 X-axis and 2 Y-axis anchors)

### Q4: How to improve data extraction accuracy?

**Recommendations**:

1. Ensure image quality is good with high resolution
2. Complete axis calibration and set sufficient anchors
3. Perform legend analysis to identify legend symbols and labels
4. Use display control functions to check detection results
5. Manually correct extraction results

### Q5: Some images fail during batch processing?

**Possible reasons**:

- Images lack necessary analysis data
- Image format not supported
- Insufficient server resources

**Solutions**:

- Check if analysis data for failed images is complete
- Process failed images individually and view detailed error messages
- Process in batches to reduce concurrent load; or visit the website again later

### Q6: What if the axis is logarithmic?

**Solutions**:

- In the Coordinate Calibration panel, set the scale type of the corresponding axis (X Axis or Y Axis) to "Logarithmic" (Log Scale)
- Ensure anchor values are logarithmic coordinate values
- The system will automatically use logarithmic conversion formulas for coordinate conversion

### Q7: How to effectively process composite plots containing multiple coordinate regions?

**Current Status**:

- The current model has not been specifically trained for composite plots and cannot achieve fully automated analysis at this time.
- The following **manual process** must be performed for each independent coordinate region:
  1. Select the horizontal and vertical axis anchor points for the current coordinate region.
  2. Complete data extraction for that coordinate region.
  3. Move to the next coordinate region and repeat the above operations.
  4. Manually add, delete, or adjust data points after extraction, if needed.

**Future Optimization Plan**:

- Expand the training dataset to improve the model's ability to recognize composite plots with multiple coordinate regions.
- Optimize the web interface to support parallel annotation and batch operations across multiple regions.
- Improve the automation workflow to reduce repetitive manual steps.

---

## Technical Support

If you have other questions or need assistance, please get in touch with our technical support team.

We welcome you to provide typical samples of composite plots to help us improve model training effectiveness.

**Version**: DataEX-Sc V251221
# DataEX-Sc 用户指南

本指南旨在帮助您了解并有效使用 DataEX-Sc 的各项功能。DataEX-Sc 是一个现代化的 Web 应用，用于从散点图中自动提取数据。

## 目录

- [快速开始](#快速开始)
- [基本流程](#基本流程)
- [快捷键](#快捷键)
- [功能面板](#功能面板)
- [状态指示器](#状态指示器)
- [显示控制](#显示控制)
- [批量处理详解](#批量处理详解)
- [用户管理](#用户管理)
- [常见问题](#常见问题)

## 快速开始

见英文指南处视频

## 基本流程

### 1. 上传图像

- **上传方式**：支持拖拽或点击上传散点图图像
- **支持格式**：JPG、PNG 等常见图像格式
- **自动处理**：上传后，系统将自动进行坐标轴检测与坐标轴刻度线数值识别

### 2. 坐标轴检测与校准

- **自动检测**：点击"coordinate calibration"面板中的"Axis Recognition"按钮，系统将自动进行：
  - 目标检测（图例形状、坐标区域、实线边界、图例框）
  - 坐标轴标签识别（OCR 识别刻度线数值）
  - 自动生成锚点（基于识别的刻度线数值）

- **手动校准**：使用锚点工具对 OCR 识别出的刻度线位置及坐标轴尺度类型进行手动校正
  - **普通锚点工具**：手动添加和编辑锚点
  - **智能锚点工具**：通过框选区域自动识别刻度值
  - **坐标轴尺度**：支持线性尺度和对数尺度（X轴、Y轴可独立设置）

### 3. 图例分析

- **智能分析（推荐）**：在"legend detection"面板中点击"Analyze Legend"按钮，系统将自动：
  - 检测图例中的符号
  - 识别图例文字标签
  - 进行符号与标签的智能匹配

- **手动流程**：
  - 先点击"Detect Legend Boxes"进行图例区域检测(可手动添加、调整、删除图例区域)
  - 再点击"Analyze Legend"按钮提取图例信息(可手动添加、编辑、分析、删除图例符号)

### 4. 图表说明检测（可选）

- **自动检测**：点击Caption Detection面板中的"Auto Detect"按钮，系统将自动识别图像底部的图表标题/说明
- **手动选择**：点击"Manual Select"按钮，可手动框选标题区域进行 OCR 识别
- **编辑功能**：点击"Edit Caption"按钮手动编辑，点击"Clear"按钮清除检测到的说明文本

### 5. 提取数据

- **提取按钮**：点击数据提取面板中的"Extract Data Series"按钮
- **自动处理**：
  - 散点分类
  - 坐标转换（像素坐标 → 真实数据坐标）
  - 数据去重（移除重复或过于接近的数据点）
  - 系列命名（自动使用图例标签作为系列名称）

### 6. 数据校正（可选）

使用工具对散点分类结果进行手动校正：

- **删除错误数据点**：使用橡皮擦工具
- **添加遗漏数据点**：使用数据点工具
- **重新分配系列**：在Data Visualization中点击数据点，可将其移动到其他系列
- **编辑系列名称**：在Data Series Management面板中编辑数据系列名称

### 7. 导出数据

- **导出格式**：CSV 文件
- **导出内容**：
  - 系列 ID
  - 系列名称
  - X 轴数据（使用坐标轴标题）
  - Y 轴数据（使用坐标轴标题）
- **导出位置**：自动下载到浏览器默认下载目录

## 快捷键

您可以使用键盘快捷键快速切换工具，提高工作效率。

### 主要工具

| 工具           | 快捷键 | 功能说明                                                     |
| -------------- | ------ | ------------------------------------------------------------ |
| **选择工具**   | **F**  | 切换为选择状态，可用于选择原图上检测出来的散点；可配合上下左右键微调散点位置 |
| **橡皮擦工具** | **S**  | 删除单个或连续的数据点。点击画布上的数据点即可删除           |
| **锚点工具**   | **A**  | 设置坐标轴校准点。点击图像上的刻度线位置，系统会根据点击位置（靠近底部或左侧）自动识别为 X 轴或 Y 轴锚点。点击后可编辑刻度值 |
| **数据点工具** | **D**  | 手动在图表上添加数据点。点击画布添加数据点到当前选定的系列，也可借此增加未识别的数据系列 |

### 工具使用技巧

- **批量删除散点**：使用快捷键S时，可以连续点击多个数据点进行批量删除散点
- **批量增加散点**：可在Data series面板中先选择目标系列，然后连续在原图上点击多个数据点进行批量增加散点
- **调整Data Visualization界面**：鼠标左键移动视图+滚轮进行缩放

## 功能面板

### 1. Object Detection 面板

**功能**：

- 控制 YOLO 模型检测，用于识别图表中的关键元素：
  - 图例形状（legend_shape）
  - 坐标区域（coord_region）
  - 实线边界（solid_line_bound）
  - 图例框（legend_box）

**操作**：

- 点击"Axis Recognition"按钮（在Coordinate Calibration面板中）会自动执行目标检测
- 检测结果会自动显示在面板中
- 支持手动绘制检测框（通过"+ Add"按钮）

**显示控制**：

- 可开启或关闭检测结果在画布上的显示（通过显示控制栏）

**手动标注**：

- 如果自动检测不准确，可以手动绘制检测框
- 支持添加、编辑、删除手动标注的检测框

### 2. Coordinate Calibration 面板

**功能**：

- 管理坐标轴刻度线锚点
- 点击"Add Anchor"按钮手动添加锚点
- 支持编辑、删除锚点
- 点击"Clear Anchors"按钮清除所有锚点
- 设置坐标轴尺度类型（线性/对数）

**坐标轴识别**：

- 点击"Axis Recognition"按钮自动识别坐标轴标签
- 自动生成锚点（基于 OCR 识别的刻度值）

**标题识别**：

- 点击"Select Title"按钮
- 在图像上框选坐标轴标题区域
- 系统将通过 OCR 自动识别标题文字
- 点击"Edit Title"按钮可手动编辑标题

**智能锚点**：

- 点击"🔬Smart Anchor"按钮（实验性功能）
- 在图像上框选包含刻度线的区域
- 系统自动识别区域内的刻度值并生成锚点

**显示控制**：

- 可开启或关闭坐标轴标线、标签及锚点在画布上的显示

### 3. 图例检测面板

**智能分析（🔍）（推荐）**：

- 系统自动检测图例中的符号与文字标签
- 进行智能匹配，关联符号与标签
- 支持多种符号类型：圆形、方形、三角形、菱形等
- 支持实心和空心符号识别

**手动流程**：

1. 点击"Detect Legend Boxes"按钮检测图例区域
2. 选择检测到的图例框或点击"+ Add Legend Box"手动绘制图例框
3. 点击"Analyze Legend"按钮提取图例信息
4. 可手动添加、编辑、删除图例符号和标签

**符号管理**：

- 查看所有检测到的图例符号
- 编辑符号标签
- 删除错误的符号
- 手动添加符号（通过绘制）

**优化功能**：

- 可点击"Optimize"按钮（如可用），系统会自动优化符号匹配结果

### 4. Caption Detection 面板

**自动检测**：

- 点击"Auto Detect"按钮
- 系统自动识别图像底部区域的图表标题/说明
- 自动执行 OCR 识别

**手动选择**：

- 点击"Manual Select"按钮
- 在图像上框选标题/说明区域
- 系统自动执行 OCR 识别该区域

**编辑功能**：

- 查看识别到的说明文本（显示在"Chart Caption"标签下）
- 点击"Edit Caption"按钮手动编辑
- 点击"Clear"按钮清除说明

### 5. Data Series Management 面板

**数据提取**：

- 点击"Extract Data Series"按钮执行数据提取
- 系统根据以下条件选择提取策略：
  - 有图例符号：优先使用模板匹配
  - 无图例符号：使用颜色聚类
  - 无校准数据：使用像素坐标模式

**提取状态**：

- 显示提取进度和状态
- 显示提取到的数据系列数量
- 显示每个系列的数据点数量

**数据系列管理**：

- 查看所有提取的数据系列（显示在"Data series"区域）
- 编辑系列名称（点击系列名称或编辑图标）
- 查看系列统计信息（数据点数量等）
- 点击"Clear all"按钮清除所有数据点

**数据点管理**：

- 查看所有数据点
- 点击数据点可在图表中定位
- 将数据点重新分配到其他系列
- 删除数据点

**去重功能**：

- 自动移除重复或过于接近的数据点
- 显示去重统计信息（去重前后的数据点数量）

**显示控制**：

- 可开启或关闭提取的数据点在画布上的显示

### 6. Data Visualization 与导出

**图表展示**：

- 使用 ECharts 实时可视化所提取的数据
- 支持缩放、平移等交互操作
- 可切换显示/隐藏指定数据系列
- 自动采用从图例中识别的标签作为数据系列名称

**数据交互**：

- 点击图表中的数据点，可在画布上定位对应的原始数据点
- 可在图表中查看数据点的精确数值
- 支持图表类型切换（散点图、折线图等）

**数据导出**：

- 点击"Export Data"按钮导出数据（按钮会显示有效数据点数量，如"Export Data (123 valid points)"）
- 导出格式：CSV 文件（UTF-8 编码，带 BOM）
- 导出内容：
  - 列1：seriesId（系列 ID）
  - 列2：seriesName（系列名称）
  - 列3：X 轴数据（使用坐标轴标题作为列名）
  - 列4：Y 轴数据（使用坐标轴标题作为列名）
- 文件名：`extracted_data.csv`

## 状态指示器

界面上有 5 个状态指示器，帮助用户了解哪些条件已满足。**至少需要满足条件 4、5**，满足的条件数量越多，数据提取效果越好：

### 1. 图像状态

- 🟢 **绿色**：已上传图像
- 🔴 **红色**：未上传图像

### 2. 检测状态

- 🟢 **绿色**：有图例检测结果（shapes 或 boxes）
- 🔴 **红色**：无图例检测结果

**说明**：检测到图例有助于提高数据提取的准确性，但不是必需的。

### 3. 图例分析状态

- 🟢 **绿色**：有标记的图例符号（会用于提取）
- 🟠 **橙色**：无图例符号（仍可提取，但不会使用标签）

**说明**：有图例符号时，系统会使用模板匹配策略，提取效果更好。

### 4. X 轴锚点状态

- 🟢 **绿色**：≥2 个锚点
- 🔴 **红色**：<2 个锚点
- **显示格式**：`X轴锚点: 数量/2`

**说明**：X 轴至少需要 2 个锚点才能进行坐标转换。如果只有像素坐标，则无法转换为真实数据坐标。

### 5.Y 轴锚点状态

- 🟢 **绿色**：≥2 个锚点
- 🔴 **红色**：<2 个锚点
- **显示格式**：`Y轴锚点: 数量/2`

**说明**：Y 轴至少需要 2 个锚点才能进行坐标转换。如果只有像素坐标，则无法转换为真实数据坐标。

## 显示控制

通过显示控制栏可以控制画布上各种元素的显示/隐藏，方便查看和编辑：

### 控制项

1. **automatic detection box**（绿色）
   - 显示/隐藏目标检测结果（坐标区域、图例形状、实线边界等）

2. **coordinate calibration**（蓝色）
   - 显示/隐藏坐标轴校准信息（坐标轴线、锚点、标签等）

3. **legend box**（橙色）
   - 显示/隐藏图例检测结果（图例区域框选）

4. **caption detection**（紫色）
   - 显示/隐藏图表说明检测结果

5. **data extraction**（红色）
   - 显示/隐藏数据提取后的数据点

### 使用技巧

- 在进行不同操作时，可以隐藏不需要显示的元素，保持画布清晰
- 在检查提取结果时，可以只显示数据点，隐藏其他检测框
- 在校准坐标轴时，可以只显示坐标校准相关元素

## 批量处理详解

系统支持批量处理多张图像，提高处理效率。

### 使用方法

1. **选择图像**：
   - 在图像列表侧边栏中，启用多选模式
   - 选择需要批量处理的图像（可多选）

2. **启动批量处理**：
   - 点击批量处理按钮
   - 系统将按顺序处理选中的图像

3. **处理模式**：
   - **像素坐标模式**：如果没有充足的校准锚点，系统将使用像素坐标模式提取数据
   - **完整模式**：如果有充足的校准锚点，系统将进行完整的坐标转换

4. **处理状态**：
   - 显示每张图像的处理进度
   - 显示处理成功/失败状态
   - 显示错误信息（如果有）

5. **结果查看**：
   - 处理完成后，可以逐张查看处理结果
   - 可以对每张图像进行单独校正

### 批量处理注意事项

- 批量处理使用每张图像已保存的分析结果（检测、校准、图例等）
- 如果某张图像缺少必要的分析数据，系统会使用可用的数据进行处理
- 如果缺少校准数据，会使用像素坐标模式提取
- 批量处理过程中可以随时取消

## 用户管理

系统支持多用户使用，并提供用户管理功能（仅管理员可用）。

### 用户注册与登录

- **注册**：新用户仅可以通过管理员注册
- **登录**：使用邮箱和密码登录系统
- **会话管理**：登录状态会保持，直到主动登出

### 测试账号

- Email：customer2025@test.com
- Password：DataEx251221!



## 常见问题

### Q1: 为什么提取的数据点坐标不准确？

**可能原因**：

- X 轴或 Y 轴锚点不足（需要至少 2 个）
- 锚点位置不准确
- 坐标轴尺度类型设置错误（线性/对数）

**解决方法**：

- 检查状态指示器，确保 X 轴和 Y 轴都有足够的锚点
- 在Coordinate Calibration面板中，点击"Axis Recognition"按钮自动识别并生成锚点
- 或点击"Add Anchor"按钮手动添加锚点
- 重新校准锚点位置和数值（点击锚点可编辑）
- 确认坐标轴尺度类型设置正确

### Q2: 图例符号没有被识别出来怎么办？

**解决方法**：

- 在Legend Detection面板中，点击"Detect Legend Boxes"按钮检测图例区域，可在原图上手动调整图例区域/图例形状区域的位置和尺寸
- 点击"Analyze Legend"按钮分析图例符号，可在原图上手动调整图例符号区域的位置和尺寸
- 如果自动检测不准确，可以点击"+ Add Legend Box"手动绘制图例框
- 手动添加图例符号后，需要点击"Analyze Added"进行分析

### Q3: 数据提取后没有数据点？

**可能原因**：

- 坐标区域没有被正确检测
- 图例符号匹配失败
- 颜色聚类未能识别数据点

**解决方法**：

- 在Coordinate Calibration面板中点击"Axis Recognition"按钮进行检测
- 检查Object Detection面板中的检测结果，确认坐标区域被正确检测
- 如果检测不准确，可以在Object Detection面板中手动绘制坐标区域
- 检查Legend Detection面板中的图例分析结果
- 确认已完成坐标校准（至少2个X轴和2个Y轴锚点）

### Q4: 如何提高数据提取的准确性？

**建议**：

1. 确保图像质量良好，清晰度高
2. 完成坐标轴校准，设置足够的锚点
3. 进行图例分析，识别图例符号和标签
4. 使用显示控制功能检查检测结果
5. 对提取结果进行手动校正

### Q5: 批量处理时某些图像处理失败？

**可能原因**：

- 图像缺少必要的分析数据
- 图像格式不支持
- 服务器资源不足

**解决方法**：

- 检查失败图像的分析数据是否完整
- 单独处理失败的图像，查看详细错误信息
- 分批处理，减少并发数量；或过段时间再访问网站

### Q6: 坐标轴是对数坐标怎么办？

**解决方法**：

- 在Coordinate Calibration面板中，将对应的坐标轴（X Axis或Y Axis）的尺度类型设置为"对数"（Log Scale）
- 确保锚点的数值是对数坐标的数值
- 系统会自动使用对数转换公式进行坐标转换



### Q7: 如何有效处理包含多个坐标区的组合图？

**现状说明**：

- 当前模型尚未针对组合图进行专项训练，暂无法实现全自动分析
- 需对每个独立坐标区**手动执行以下流程**：
  1. 分别选取当前坐标区的横纵坐标轴锚点
  2. 完成该坐标区的数据提取
  3. 进入下一个坐标区重复上述操作
  4. 可在提取后手动增删或调整数据点

**后续优化计划**：

- 扩充训练数据集，增强模型对多坐标区组合图的识别能力
- 优化网页交互界面，支持多区域并行标注与批量化操作
- 完善自动化流程，减少重复性手动操作步骤



---

## 技术支持

如有其他问题或需要帮助，请联系技术支持团队。

欢迎提供典型组合图样本，帮助我们优化模型训练效果。

**版本信息**：DataEX-Sc V251221

