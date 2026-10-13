# DataEX-Sc User Guide

This guide helps you understand and effectively use the features of DataEX-Sc. DataEX-Sc is a modern web application for automatically extracting data from scatter plots.

**Version**: DataEX-Sc V261013  
**Highlights**: smart subplot split · per-panel extraction · Scatter Review

### Test Account

- Email：customer2025@test.com
- Password：DataEx251221!

## Table of Contents

- [Quick Start](#quick-start)
- [Main Tabs](#main-tabs)
- [Basic Workflow](#basic-workflow)
- [Composite Figures (Subplots)](#composite-figures-subplots)
- [Scatter Review](#scatter-review)
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

## Main Tabs

The top navigation has three main tabs:

| Tab | Purpose |
| --- | --- |
| **Upload Image** | Upload images and manage the image library |
| **Extract Data** | Axis calibration, legend analysis, subplot split, data extraction and correction |
| **Scatter Review** | Quickly classify images as scatter / not-scatter before or after upload |

Administrators also see **User Management**. **Help Docs** opens the online user guide.

Page header should show **V261013**. If you still see an older version string, hard-refresh the browser.

## Basic Workflow

### 1. Upload Image

- **Upload method**: Drag and drop or click to upload scatter plot images
- **Supported formats**: JPG, PNG and other common image formats
- **Tip**: For mixed batches that may contain non-scatter figures, use **Scatter Review** first to hide non-scatter images

### 2. Axis Detection and Calibration

- **Auto detection**: Click the "Axis Recognition" button in the **Calibration** panel, and the system will automatically:

  - Object detection (legend shapes, coordinate regions, solid line boundaries, legend boxes)
  - Axis label recognition (OCR recognizes tick mark values)
  - Auto-generate anchors (based on recognized tick mark values)
- **Manual calibration**: Use anchor tools to manually correct OCR-identified tick mark positions and axis scale types

  - **Regular anchor tool**: Manually add and edit anchors
  - **Smart anchor tool**: Automatically recognize tick values by selecting regions
  - **Axis scale**: Supports linear and logarithmic scales (X-axis and Y-axis can be set independently)

### 3. Legend Analysis

- **Smart analysis (recommended)**: Click the "Analyze Legend" button in the **Legend** panel, and the system will automatically:

  - Detect symbols in the legend
  - Recognize legend text labels
  - Intelligently match symbols with labels
- **Manual process**:

  - First click "Detect Legend Boxes" to detect legend regions (you can manually add, adjust, and delete legend regions)
  - Then click the "Analyze Legend" button to extract legend information (you can manually add, edit, analyze, and delete legend symbols)

### 4. Chart Caption Detection (Optional)

- **Auto detection**: Click the "Auto Detect" button in the **Caption** panel, and the system will automatically identify chart titles/captions at the bottom of the image
- **Manual selection**: Click the "Manual Select" button to manually select the title region for OCR recognition
- **Edit function**: Click the "Edit Caption" button to manually edit, or click the "Clear" button to clear the detected caption text

### 5. Subplot Split (Composite Figures)

For figures with multiple coordinate regions, open the **Subplots** panel (see [Composite Figures](#composite-figures-subplots)). Batch / automatic extraction also enables per-panel extraction by default.

### 6. Extract Data

- **Extract button**: Click the "Extract Data Series" button in the data extraction panel
- **Auto processing**:
  - Scatter point classification
  - Coordinate conversion (pixel coordinates → real data coordinates)
  - Data deduplication (remove duplicate or overly close data points)
  - Series naming (automatically use legend labels as series names)
  - **Composite figures**: When multiple subplots are present (or `auto_panels` is on), each panel is processed separately and results are merged with `panel_index`

### 7. Data Correction (Optional)

Use tools to manually correct scatter classification results:

- **Delete incorrect data points**: Use the eraser tool or brush (delete mode)
- **Add missing data points**: Use the data point tool or brush (extract mode)
- **Reassign series**: Click data points in Data Visualization to move them to other series
- **Edit series names**: Edit data series names in the Data Series Management panel
- **Filter by panel**: Use the green **Subplots** bar (All / P1 / P2 …) to focus on one panel

### 8. Export Data

- **Export format**: CSV file
- **Export content**:
  - Series ID
  - Series name
  - X-axis data (using axis title)
  - Y-axis data (using axis title)
- **Export location**: Automatically downloaded to the browser's default download directory

## Composite Figures (Subplots)

V261013 adds intelligent multi-panel split and per-panel extraction so composite figures are less likely to mix or miss points across panels.

### Automatic path (batch / extract)

When you run **Extract Data Series** or **batch processing**, the backend defaults to `auto_panels=true`:

1. Detect coordinate axes (YOLO)
2. Decide whether the figure is composite (`prepare_subplot_boxes`)
3. **Composite**: for each panel ROI, run legend detection + template matching, then merge results (`panel_index`)
4. **Single panel**: original extraction logic
5. Save `analysis.meta.subplots` / `is_composite`

Supported layouts include left/right or top/bottom halves, grids, nested insets, and single full-figure panels.

### Manual path (Extract → Subplots panel)

1. Open **Extract Data** → middle column → **Subplots**
2. **Auto Detect**: preview panel boxes on the main image
3. Or **Draw on image**: drag rectangles on the canvas; remove unwanted boxes as needed
4. Optional: check **Also export each panel as a sidebar image**
5. Click **Apply N Panel(s) on Figure**: runs per-panel axis OCR and reassigns scatter points to panels
6. Use the green **Subplots** bar above the canvas:
   - **All**: show all panels in Data Visualization
   - **P1 / P2 / …**: filter series and sync Calibration to that panel

### Tips

- After Auto Detect, check strategy tags such as `halves_lr`, `grid`, `nested_inner` in the panel list
- If auto split is wrong, clear boxes, draw manually, then Apply
- For nested insets, the outer panel may mask the inner region so points are not double-counted

## Scatter Review

Use the top **Scatter Review** tab to quickly screen whether images are scatter plots.

| Action | Shortcut | Effect |
| ------ | -------- | ------ |
| Keep as scatter | **Y** or **→** | Mark as scatter; keep in the extract queue |
| Not scatter | **N** or **←** | Soft-delete (hide from the sidebar library) |
| Skip | **S** | Leave unclassified and move to the next image |
| Undo | **U** | Restore the previous action (including soft-deleted images) |

- Entering Review starts from the image currently selected in the sidebar when possible
- Queue stats show remaining / kept / removed / skipped; use **Refresh** to reload
- After review, continue with **Extract Data** / **Subplots** on remaining scatter figures

> Note: In Extract Data, **S** is the eraser tool. In Scatter Review, **S** means Skip. Shortcuts apply to the active tab.

## Keyboard Shortcuts

You can use keyboard shortcuts to quickly switch between tools and improve work efficiency.

### Extract Data — Main Tools

| Tool | Shortcut | Description |
| ---- | -------- | ----------- |
| **Selection Tool** | **F** | Switch to selection state; select detected scatter points on the original image; fine-tune with arrow keys |
| **Eraser Tool** | **S** | Delete individual or consecutive data points. Click data points on the canvas to delete them |
| **Color Picker** | **I** | Sample a color on the canvas for the brush tool (hex value) |
| **Brush Tool** | **B** | Drag a region to extract or delete points by sampled color (modes: Extract / Delete; adjust width W and tolerance Tol) |
| **Anchor Tool** | **A** | Set axis calibration points. Click tick mark positions; the system infers X/Y from position (near bottom or left). Click to edit tick values |
| **Data Point Tool** | **D** | Manually add data points to the current series, or create unrecognized series |

Esc cancels the current selection / drawing / title-selection mode.

### Tool Usage Tips

- **Batch delete scatter points**: With shortcut S, continuously click multiple data points to batch delete
- **Batch add scatter points**: First select the target series in the Data series panel, then continuously click on the original image
- **Brush workflow**: Sample with **I**, switch to **B**, choose Extract or Delete, then drag a region
- **Adjust the Data Visualization interface**: move the view with the left mouse button and zoom with the scroll wheel
- Shortcut hints also appear in the **CanvasShortcutBar** next to the green Subplots bar

## Functional Panels

In **Extract Data**, the middle column tabs are: **Calibration** · **Legend** · **Caption** · **Subplots**. Data extraction and visualization are on the right (**DataDisplayPanel** / Data Series).

### 1. Object Detection (via Axis Recognition)

**Function** (trigger is merged into the Calibration panel):

- Controls YOLO model detection to identify key elements in charts:
  - Legend shapes (legend_shape)
  - Coordinate regions (coord_region)
  - Solid line boundaries (solid_line_bound)
  - Legend boxes (legend_box)

**Operations**:

- Clicking the "Axis Recognition" button (in the Calibration panel) will automatically execute object detection
- Detection results display on the canvas via display controls
- Supports manual drawing of detection boxes where the UI exposes "+ Add"

**Display control**:

- Toggle display of detection results on the canvas (via the display control bar)

### 2. Calibration Panel

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

**Composite figures**:

- With the green Subplots bar set to P1/P2/…, Calibration syncs to that panel’s anchors when per-panel calibration is available

### 3. Legend Panel

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

### 4. Caption Panel

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

### 5. Subplots Panel

See [Composite Figures (Subplots)](#composite-figures-subplots).

Buttons: **Auto Detect** · **Draw on image** · **Clear** · **Apply N Panel(s) on Figure**.

### 6. Data Series Management Panel

**Data extraction**:

- Click the "Extract Data Series" button to execute data extraction
- System selects extraction strategy based on the following conditions:
  - With legend symbols: Prioritizes template matching
  - Without legend symbols: Uses color clustering
  - Without calibration data: Uses pixel coordinate mode
  - With multiple subplots: Extracts per panel and merges (series names may be prefixed like `P1/...`)

**Extraction status**:

- Display extraction progress and status
- Display the number of extracted data series
- Display the number of data points in each series

**Data series management**:

- View all extracted data series (displayed in the "Data series" area)
- Edit series names (click series name or edit icon)
- View series statistics (number of data points, etc.)
- Click the "Clear all" button to clear all data points
- Filter by panel via the green Subplots bar

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

### 7. Data Visualization and Export

**Chart display**:

- Use ECharts to visualize extracted data in real-time
- Supports interactive operations such as zoom and pan
- Toggle display/hide of specified data series
- Automatically uses labels recognized from legends as data series names
- For composites, **All** shows multi-panel data together; P1/P2 filters one panel

**Data interaction**:

- Click data points in the chart to locate corresponding original data points on the canvas
- View precise values of data points in the chart

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

There are 6 status indicators on the interface to help users understand which conditions have been met. **At least conditions 5 and 6 must be satisfied**. The more conditions that are met, the better the data extraction results:

### 1. Image Status

- 🟢 **Green**: Image uploaded
- 🔴 **Red**: No image uploaded

### 2. Detection Status

- 🟢 **Green**: Legend detection results exist (shapes or boxes)
- 🔴 **Red**: No legend detection results

**Note**: Detecting legends helps improve data extraction accuracy, but is not required.

### 3. Detection status of coordinate area

- 🟢 **Green**: Coordinate region detection result exists
- 🔴 **Red**: No coordinate region detection result

### 4. Legend Analysis Status

- 🟢 **Green**: Labeled legend symbols exist (will be used for extraction)
- 🟠 **Orange**: No legend symbols (extraction is still possible, but labels will not be used)

**Note**: When legend symbols exist, the system will use template matching strategy for better extraction results.

### 5. X-axis Anchor Status

- 🟢 **Green**: ≥2 anchors
- 🔴 **Red**: <2 anchors
- **Display format**: `X-axis Anchors: Count/2`

**Note**: At least 2 anchors are required on the X-axis for coordinate conversion. If only pixel coordinates are available, real data coordinates cannot be converted.

### 6. Y-axis Anchor Status

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

   - **Pixel coordinate mode**: If there are insufficient calibration anchors, the system uses pixel-only extraction (`auto_panels=true` by default for composite split)
   - **Complete mode**: If there are sufficient calibration anchors, the system performs full coordinate conversion (backend also defaults to per-panel extraction for composites)
4. **Processing status**:

   - Display processing progress for each image
   - Display processing success/failure status
   - Composite success may note `(composite → N panels)`
   - Display error messages (if any)
5. **Result viewing**:

   - After processing is complete, you can view processing results image by image
   - You can perform individual corrections on each image; use the green Subplots bar for composites

### Batch Processing Notes

- Batch processing uses saved analysis results for each image when available (detections, calibrations, legends, etc.)
- If an image lacks necessary analysis data, the system will use available data for processing
- If calibration data is missing, pixel coordinate mode will be used for extraction
- Composite figures are split and extracted per panel by default
- Batch processing can be cancelled at any time during the process
- Long-running extractions may take several minutes; keep the tab open until finished

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
- Image noise is misidentified as data points
- On composites, anchors from the wrong panel were used

**Solutions**:

- Recalibrate anchor positions and values (click anchors to edit)
- Confirm axis scale type settings are correct
- Use the Subplots bar to switch to the correct panel, then calibrate
- Manually correct the classification and position of data points

### Q2: What if legend symbols are not recognized?

**Solutions**:

- In the Legend panel, click the "Detect Legend Boxes" button to detect legend regions, and you can manually adjust the position and size of legend regions/legend shape regions on the original image
- Click the "Analyze Legend" button to analyze legend symbols, and you can manually adjust the position and size of legend symbol regions on the original image
- If automatic detection is inaccurate, you can click "+ Add Legend Box" to manually draw legend boxes
- After manually adding legend symbols, click "Analyze Added" for analysis

### Q3: No data points after data extraction?

**Possible reasons**:

- Coordinate regions were not correctly detected
- Legend symbol matching failed
- Color clustering failed to identify data points
- On composites, the wrong panel ROI was used

**Solutions**:

- Click the "Axis Recognition" button in the Calibration panel to perform detection
- Confirm coordinate regions were correctly detected on the canvas
- Check legend analysis results in the Legend panel
- Confirm coordinate calibration is complete (at least 2 X-axis and 2 Y-axis anchors)
- For composites: Subplots → Auto Detect / Draw → Apply, then extract again
- Try the brush tool (I then B) to extract points by color

### Q4: How to improve data extraction accuracy?

**Recommendations**:

1. Ensure image quality is good with high resolution
2. Complete axis calibration and set sufficient anchors
3. Perform legend analysis to identify legend symbols and labels
4. For composite figures, confirm subplot boxes before extraction
5. Use display control functions to check detection results
6. Manually correct extraction results (eraser / brush / data point tools)

### Q5: Some images fail during batch processing?

**Possible reasons**:

- Images lack necessary analysis data
- Image format not supported
- Insufficient server resources / long inference timeout

**Solutions**:

- Check if analysis data for failed images is complete
- Process failed images individually and view detailed error messages
- Process in batches to reduce concurrent load; or visit the website again later
- Soft-delete obvious non-scatter images in Scatter Review first

### Q6: What if the axis is logarithmic?

**Solutions**:

- In the Calibration panel, set the scale type of the corresponding axis (X Axis or Y Axis) to "Logarithmic" (Log Scale)
- Ensure anchor values are logarithmic coordinate values
- The system will automatically use logarithmic conversion formulas for coordinate conversion

### Q7: How to process composite plots with multiple coordinate regions?

**Current capabilities (V261013)**:

1. **Automatic**: Run Extract Data Series or batch processing — per-panel extraction is enabled by default
2. **Manual split**: Extract → **Subplots** → Auto Detect or Draw on image → **Apply N Panel(s) on Figure**
3. **Browse results**: Use the green **Subplots** bar (All / P1 / P2 …) to filter series and sync Calibration
4. **Correct**: Adjust anchors / legends / points per panel as needed, then re-extract or export

**If auto split is wrong**:

- Clear preview boxes, draw panels manually, then Apply
- For nested inset figures, check that inner/outer panels look correct before extraction

---

## Technical Support

If you have other questions or need assistance, please get in touch with our technical support team.

We welcome you to provide typical samples of composite plots to help us improve model training effectiveness.

**Version**: DataEX-Sc V261013

---

# DataEX-Sc 用户指南

本指南旨在帮助您了解并有效使用 DataEX-Sc 的各项功能。DataEX-Sc 是一个现代化的 Web 应用，用于从散点图中自动提取数据。

**版本**：DataEX-Sc V261013  
**本版重点**：组合图智能分割 · 按子图提取 · 人工分类图片

## 目录

- [快速开始](#快速开始-1)
- [顶部标签页](#顶部标签页)
- [基本流程](#基本流程-1)
- [组合图（Subplots）](#组合图subplots)
- [Scatter Review（人工分类）](#scatter-review人工分类)
- [快捷键](#快捷键-1)
- [功能面板](#功能面板-1)
- [状态指示器](#状态指示器-1)
- [显示控制](#显示控制-1)
- [批量处理详解](#批量处理详解)
- [用户管理](#用户管理-1)
- [常见问题](#常见问题)

## 快速开始

见英文指南处视频

## 顶部标签页

顶栏主要有三个标签：

| 标签 | 作用 |
| ---- | ---- |
| **Upload Image** | 上传图像、管理图库 |
| **Extract Data** | 坐标校准、图例分析、子图分割、数据提取与校正 |
| **Scatter Review** | 快速判定图片是否为散点图（可在提取前筛图） |

管理员可见 **User Management**。**Help Docs** 打开在线用户指南。

页头应显示 **V261013**。若仍为旧版本号，请强制刷新浏览器。

## 基本流程

### 1. 上传图像

- **上传方式**：支持拖拽或点击上传散点图图像
- **支持格式**：JPG、PNG 等常见图像格式
- **建议**：批量中可能混有非散点图时，可先用 **Scatter Review** 软删除非散点图

### 2. 坐标轴检测与校准

- **自动检测**：点击 **Calibration** 面板中的 "Axis Recognition" 按钮，系统将自动进行：

  - 目标检测（图例形状、坐标区域、实线边界、图例框）
  - 坐标轴标签识别（OCR 识别刻度线数值）
  - 自动生成锚点（基于识别的刻度线数值）
- **手动校准**：使用锚点工具对 OCR 识别出的刻度线位置及坐标轴尺度类型进行手动校正

  - **普通锚点工具**：手动添加和编辑锚点
  - **智能锚点工具**：通过框选区域自动识别刻度值
  - **坐标轴尺度**：支持线性尺度和对数尺度（X轴、Y轴可独立设置）

### 3. 图例分析

- **智能分析（推荐）**：在 **Legend** 面板中点击 "Analyze Legend" 按钮，系统将自动：

  - 检测图例中的符号
  - 识别图例文字标签
  - 进行符号与标签的智能匹配
- **手动流程**：

  - 先点击 "Detect Legend Boxes" 进行图例区域检测（可手动添加、调整、删除图例区域）
  - 再点击 "Analyze Legend" 按钮提取图例信息（可手动添加、编辑、分析、删除图例符号）

### 4. 图表说明检测（可选）

- **自动检测**：点击 **Caption** 面板中的 "Auto Detect" 按钮，系统将自动识别图像底部的图表标题/说明
- **手动选择**：点击 "Manual Select" 按钮，可手动框选标题区域进行 OCR 识别
- **编辑功能**：点击 "Edit Caption" 按钮手动编辑，点击 "Clear" 按钮清除检测到的说明文本

### 5. 子图分割（组合图）

含多个坐标区时，打开 **Subplots** 面板（见 [组合图](#组合图subplots)）。批量 / 自动提取默认也会按子图分别提取。

### 6. 提取数据

- **提取按钮**：点击数据提取面板中的 "Extract Data Series" 按钮
- **自动处理**：
  - 散点分类
  - 坐标转换（像素坐标 → 真实数据坐标）
  - 数据去重（移除重复或过于接近的数据点）
  - 系列命名（自动使用图例标签作为系列名称）
  - **组合图**：存在多个子图（或默认开启 `auto_panels`）时，按子图分别提取再合并，结果带 `panel_index`

### 7. 数据校正（可选）

使用工具对散点分类结果进行手动校正：

- **删除错误数据点**：使用橡皮擦工具，或画笔删除模式
- **添加遗漏数据点**：使用数据点工具，或画笔提取模式
- **重新分配系列**：在 Data Visualization 中点击数据点，可将其移动到其他系列
- **编辑系列名称**：在 Data Series Management 面板中编辑数据系列名称
- **按子图筛选**：使用绿色 **Subplots** 条（All / P1 / P2 …）聚焦某一子图

### 8. 导出数据

- **导出格式**：CSV 文件
- **导出内容**：
  - 系列 ID
  - 系列名称
  - X 轴数据（使用坐标轴标题）
  - Y 轴数据（使用坐标轴标题）
- **导出位置**：自动下载到浏览器默认下载目录

## 组合图（Subplots）

V261013 增加了组合图智能分割与按子图提取，降低多子图串点、漏点。

### 自动路径（批量 / 提取）

执行 **Extract Data Series** 或 **批量处理** 时，后端默认 `auto_panels=true`：

1. YOLO 检测坐标轴
2. 判断是否为组合图（`prepare_subplot_boxes`）
3. **组合图**：对每个子图 ROI 分别做图例检测 + 模板匹配，再合并（`panel_index`）
4. **单图**：走原提取逻辑
5. 写入 `analysis.meta.subplots` / `is_composite`

支持左右/上下对切、网格、嵌套 inset、单轴整图等布局。

### 人工路径（Extract → Subplots）

1. 打开 **Extract Data** → 中间栏 → **Subplots**
2. **Auto Detect**：在主图画预览子图框
3. 或 **Draw on image**：在画布上拖拽画框，可 remove 多余框
4. 可选勾选 **Also export each panel as a sidebar image**（同时导出子图到侧栏）
5. 点击 **Apply N Panel(s) on Figure**：对各子图做轴 OCR，并按子图重分配散点
6. 使用画布上方绿色 **Subplots** 条：
   - **All**：Data Visualization 同屏显示多轴
   - **P1 / P2 / …**：筛选系列，并同步该子图的 Calibration

### 使用提示

- Auto Detect 后可在列表中查看策略标签（如 `halves_lr`、`grid`、`nested_inner`）
- 自动分割不准时：Clear → 手动画框 → Apply
- 嵌套 inset：确认内外层框正确，外层可能遮罩内嵌区域以避免重复计数

## Scatter Review（人工分类）

顶部 **Scatter Review** 用于快速筛图：

| 操作 | 快捷键 | 效果 |
| ---- | ------ | ---- |
| 保留为散点 | **Y** 或 **→** | 标记为 scatter，保留在提取队列 |
| 非散点 | **N** 或 **←** | 软删除（从图库侧栏隐藏） |
| 跳过 | **S** | 不分类，进入下一张 |
| 撤销 | **U** | 撤销上一步（含恢复软删除） |

- 进入 Review 时尽量从侧栏当前选中图开始
- 可查看队列剩余 / 保留 / 移除 / 跳过统计；**Refresh** 重新加载
- 筛完后对剩余散点图继续 **Extract Data** / **Subplots**

> 注意：在 Extract Data 中 **S** 是橡皮擦；在 Scatter Review 中 **S** 表示跳过。快捷键随当前标签页生效。

## 快捷键

您可以使用键盘快捷键快速切换工具，提高工作效率。

### Extract Data — 主要工具

| 工具 | 快捷键 | 功能说明 |
| ---- | ------ | -------- |
| **选择工具** | **F** | 切换为选择状态，可用于选择原图上检测出来的散点；可配合上下左右键微调散点位置 |
| **橡皮擦工具** | **S** | 删除单个或连续的数据点。点击画布上的数据点即可删除 |
| **取色器** | **I** | 在画布上取色，供画笔工具使用（十六进制颜色） |
| **画笔工具** | **B** | 按取样颜色拖拽区域提取或删除散点（Extract / Delete；可调宽度 W 与容差 Tol） |
| **锚点工具** | **A** | 设置坐标轴校准点。点击图像上的刻度线位置，系统会根据点击位置（靠近底部或左侧）自动识别为 X 轴或 Y 轴锚点。点击后可编辑刻度值 |
| **数据点工具** | **D** | 手动在图表上添加数据点。点击画布添加数据点到当前选定的系列，也可借此增加未识别的数据系列 |

Esc 可取消当前框选 / 绘制 / 标题选择等模式。

### 工具使用技巧

- **批量删除散点**：使用快捷键 S 时，可以连续点击多个数据点进行批量删除
- **批量增加散点**：可在 Data series 面板中先选择目标系列，然后连续在原图上点击多个数据点
- **画笔流程**：先用 **I** 取色，再按 **B**，选择 Extract 或 Delete，然后拖拽区域
- **调整 Data Visualization 界面**：鼠标左键移动视图 + 滚轮缩放
- 画布上方 **CanvasShortcutBar**（与绿色 Subplots 条同行）也会显示当前工具提示

## 功能面板

在 **Extract Data** 中，中间栏标签为：**Calibration** · **Legend** · **Caption** · **Subplots**。数据提取与可视化在右侧（Data Series / Data Visualization）。

### 1. Object Detection（经 Axis Recognition 触发）

**功能**（触发已合并至 Calibration 面板）：

- 控制 YOLO 模型检测，用于识别图表中的关键元素：
  - 图例形状（legend_shape）
  - 坐标区域（coord_region）
  - 实线边界（solid_line_bound）
  - 图例框（legend_box）

**操作**：

- 点击 "Axis Recognition" 按钮（在 Calibration 面板中）会自动执行目标检测
- 检测结果通过显示控制栏在画布上展示
- 支持在界面提供 "+ Add" 时手动绘制检测框

**显示控制**：

- 可开启或关闭检测结果在画布上的显示（通过显示控制栏）

### 2. Calibration 面板

**功能**：

- 管理坐标轴刻度线锚点
- 点击 "Add Anchor" 按钮手动添加锚点
- 支持编辑、删除锚点
- 点击 "Clear Anchors" 按钮清除所有锚点
- 设置坐标轴尺度类型（线性/对数）

**坐标轴识别**：

- 点击 "Axis Recognition" 按钮自动识别坐标轴标签
- 自动生成锚点（基于 OCR 识别的刻度值）

**标题识别**：

- 点击 "Select Title" 按钮
- 在图像上框选坐标轴标题区域
- 系统将通过 OCR 自动识别标题文字
- 点击 "Edit Title" 按钮可手动编辑标题

**智能锚点**：

- 点击 "🔬Smart Anchor" 按钮（实验性功能）
- 在图像上框选包含刻度线的区域
- 系统自动识别区域内的刻度值并生成锚点

**显示控制**：

- 可开启或关闭坐标轴标线、标签及锚点在画布上的显示

**组合图**：

- 绿色 Subplots 条切换到 P1/P2/… 时，若已有按子图校准，Calibration 会同步到对应子图锚点

### 3. Legend 面板

**智能分析（🔍）（推荐）**：

- 系统自动检测图例中的符号与文字标签
- 进行智能匹配，关联符号与标签
- 支持多种符号类型：圆形、方形、三角形、菱形等
- 支持实心和空心符号识别

**手动流程**：

1. 点击 "Detect Legend Boxes" 按钮检测图例区域
2. 选择检测到的图例框或点击 "+ Add Legend Box" 手动绘制图例框
3. 点击 "Analyze Legend" 按钮提取图例信息
4. 可手动添加、编辑、删除图例符号和标签

**符号管理**：

- 查看所有检测到的图例符号
- 编辑符号标签
- 删除错误的符号
- 手动添加符号（通过绘制）

### 4. Caption 面板

**自动检测**：

- 点击 "Auto Detect" 按钮
- 系统自动识别图像底部区域的图表标题/说明
- 自动执行 OCR 识别

**手动选择**：

- 点击 "Manual Select" 按钮
- 在图像上框选标题/说明区域
- 系统自动执行 OCR 识别该区域

**编辑功能**：

- 查看识别到的说明文本（显示在 "Chart Caption" 标签下）
- 点击 "Edit Caption" 按钮手动编辑
- 点击 "Clear" 按钮清除说明

### 5. Subplots 面板

见 [组合图（Subplots）](#组合图subplots)。

按钮：**Auto Detect** · **Draw on image** · **Clear** · **Apply N Panel(s) on Figure**。

### 6. Data Series Management 面板

**数据提取**：

- 点击 "Extract Data Series" 按钮执行数据提取
- 系统根据以下条件选择提取策略：
  - 有图例符号：优先使用模板匹配
  - 无图例符号：使用颜色聚类
  - 无校准数据：使用像素坐标模式
  - 有多个子图：按子图提取后合并（系列名可能带 `P1/...` 前缀）

**提取状态**：

- 显示提取进度和状态
- 显示提取到的数据系列数量
- 显示每个系列的数据点数量

**数据系列管理**：

- 查看所有提取的数据系列（显示在 "Data series" 区域）
- 编辑系列名称（点击系列名称或编辑图标）
- 查看系列统计信息（数据点数量等）
- 点击 "Clear all" 按钮清除所有数据点
- 可通过绿色 Subplots 条按子图筛选

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

### 7. Data Visualization 与导出

**图表展示**：

- 使用 ECharts 实时可视化所提取的数据
- 支持缩放、平移等交互操作
- 可切换显示/隐藏指定数据系列
- 自动采用从图例中识别的标签作为数据系列名称
- 组合图下 **All** 同屏多轴；P1/P2 只看某一子图

**数据交互**：

- 点击图表中的数据点，可在画布上定位对应的原始数据点
- 可在图表中查看数据点的精确数值

**数据导出**：

- 点击 "Export Data" 按钮导出数据（按钮会显示有效数据点数量，如 "Export Data (123 valid points)"）
- 导出格式：CSV 文件（UTF-8 编码，带 BOM）
- 导出内容：
  - 列1：seriesId（系列 ID）
  - 列2：seriesName（系列名称）
  - 列3：X 轴数据（使用坐标轴标题作为列名）
  - 列4：Y 轴数据（使用坐标轴标题作为列名）
- 文件名：`extracted_data.csv`

## 状态指示器

界面上有 6 个状态指示器，帮助用户了解哪些条件已满足。**至少需要满足条件 5、6**，满足的条件数量越多，数据提取效果越好：

### 1. 图像状态

- 🟢 **绿色**：已上传图像
- 🔴 **红色**：未上传图像

### 2. 检测状态

- 🟢 **绿色**：有图例检测结果（shapes 或 boxes）
- 🔴 **红色**：无图例检测结果

**说明**：检测到图例有助于提高数据提取的准确性，但不是必需的。

### 3. 坐标区检测状态

- 🟢 **绿色**：有坐标区检测结果
- 🔴 **红色**：无坐标区检测结果

### 4. 图例分析状态

- 🟢 **绿色**：有标记的图例符号（会用于提取）
- 🟠 **橙色**：无图例符号（仍可提取，但不会使用标签）

**说明**：有图例符号时，系统会使用模板匹配策略，提取效果更好。

### 5. X 轴锚点状态

- 🟢 **绿色**：≥2 个锚点
- 🔴 **红色**：<2 个锚点
- **显示格式**：`X轴锚点: 数量/2`

**说明**：X 轴至少需要 2 个锚点才能进行坐标转换。如果只有像素坐标，则无法转换为真实数据坐标。

### 6. Y 轴锚点状态

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

   - **像素坐标模式**：校准锚点不足时，使用 pixel-only 提取（默认 `auto_panels=true`，组合图会分流）
   - **完整模式**：校准锚点充足时，进行完整坐标转换（后端对组合图同样默认按子图提取）
4. **处理状态**：

   - 显示每张图像的处理进度
   - 显示处理成功/失败状态
   - 组合图成功时可能提示 `(composite → N panels)`
   - 显示错误信息（如果有）
5. **结果查看**：

   - 处理完成后，可以逐张查看处理结果
   - 可以对每张图像进行单独校正；组合图用绿色 Subplots 条切换

### 批量处理注意事项

- 批量处理会尽量使用每张图像已保存的分析结果（检测、校准、图例等）
- 如果某张图像缺少必要的分析数据，系统会使用可用的数据进行处理
- 如果缺少校准数据，会使用像素坐标模式提取
- 组合图默认按子图分割并分别提取
- 批量处理过程中可以随时取消
- 长耗时提取可能需数分钟，请保持页面打开直至完成

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
- 图像噪声被误识别为数据点
- 组合图下使用了错误子图的锚点

**解决方法**：

- 重新校准锚点位置和数值（点击锚点可编辑）
- 确认坐标轴尺度类型设置正确
- 用 Subplots 条切换到正确子图后再校准
- 手动校正数据点分类和位置

### Q2: 图例符号没有被识别出来怎么办？

**解决方法**：

- 在 Legend 面板中，点击 "Detect Legend Boxes" 按钮检测图例区域，可在原图上手动调整图例区域/图例形状区域的位置和尺寸
- 点击 "Analyze Legend" 按钮分析图例符号，可在原图上手动调整图例符号区域的位置和尺寸
- 如果自动检测不准确，可以点击 "+ Add Legend Box" 手动绘制图例框
- 手动添加图例符号后，需要点击 "Analyze Added" 进行分析

### Q3: 数据提取后没有数据点？

**可能原因**：

- 坐标区域没有被正确检测
- 图例符号匹配失败
- 颜色聚类未能识别数据点
- 组合图使用了错误的子图 ROI

**解决方法**：

- 在 Calibration 面板中点击 "Axis Recognition" 按钮进行检测
- 在画布上确认坐标区域是否正确
- 检查 Legend 面板中的图例分析结果
- 确认已完成坐标校准（至少 2 个 X 轴和 2 个 Y 轴锚点）
- 组合图：Subplots → Auto Detect / 手动画框 → Apply，再重新提取
- 可用画笔（先 I 再 B）按颜色补提散点

### Q4: 如何提高数据提取的准确性？

**建议**：

1. 确保图像质量良好，清晰度高
2. 完成坐标轴校准，设置足够的锚点
3. 进行图例分析，识别图例符号和标签
4. 组合图先确认子图框再提取
5. 使用显示控制功能检查检测结果
6. 对提取结果进行手动校正（橡皮擦 / 画笔 / 数据点工具）

### Q5: 批量处理时某些图像处理失败？

**可能原因**：

- 图像缺少必要的分析数据
- 图像格式不支持
- 服务器资源不足 / 推理耗时较长

**解决方法**：

- 检查失败图像的分析数据是否完整
- 单独处理失败的图像，查看详细错误信息
- 分批处理，减少并发数量；或过段时间再访问网站
- 可先在 Scatter Review 中软删除明显非散点图

### Q6: 坐标轴是对数坐标怎么办？

**解决方法**：

- 在 Calibration 面板中，将对应的坐标轴（X Axis 或 Y Axis）的尺度类型设置为 "对数"（Log Scale）
- 确保锚点的数值是对数坐标的数值
- 系统会自动使用对数转换公式进行坐标转换

### Q7: 如何有效处理包含多个坐标区的组合图？

**当前能力（V261013）**：

1. **自动**：直接 Extract Data Series 或批量处理——默认按子图分别提取
2. **手动分割**：Extract → **Subplots** → Auto Detect 或 Draw on image → **Apply N Panel(s) on Figure**
3. **查看结果**：用绿色 **Subplots** 条（All / P1 / P2 …）筛选系列并同步 Calibration
4. **校正**：按子图调整锚点 / 图例 / 散点后，可再提取或导出

**自动分割不准时**：

- Clear 预览框 → 手动画子图 → Apply
- 嵌套 inset 图请先确认内外层框是否正确再提取

---

## 技术支持

如有其他问题或需要帮助，请联系技术支持团队。

欢迎提供典型组合图样本，帮助我们优化模型训练效果。

**版本信息**：DataEX-Sc V261013
