import cv2
import numpy as np
import random
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import math
import json

# 定义图例元素
COLORS = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0),
    'pink': (255, 192, 203),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'brown': (165, 42, 42),
    'black': (0, 0, 0),
    'gray': (128, 128, 128)
}

SHAPES = {
    'circle': 'circle',
    'square': 'square',
    'triangle': 'triangle',
    'diamond': 'diamond',
    'star': 'star',
    'cross': 'cross',
    'plus': 'plus',
    'pentagon': 'pentagon',
    'xmark': 'xmark'
}

FILL_TYPES = {
    'solid': 'solid',
    'hollow': 'hollow'
}

MIN_SIZE = 5
MAX_SIZE = 20

# OpenCV putText 笔画粗细：仅 1、2…，1 最细；全图文字统一用细笔画
TEXT_STROKE_THIN = 1
# 刻度数字略小于轴标题，避免糊成一团
TICK_LABEL_FONT_SCALE = 0.35

# 模仿真实科学图表的图例文字模板（随机组合，提高多样性）
# 由于 OpenCV 默认字体不支持中文，会显示为“????”，这里统一使用 ASCII 字符避免乱码
LEGEND_LABEL_PREFIXES = (
    "Series", "Sample", "Group", "Dataset", "Condition", "Set", "Run",
    "Case", "Type", "Category", "Exp", "Ctrl"
)
LEGEND_LABEL_SUFFIXES = ("A", "B", "C", "1", "2", "3", "I", "II", "III", "a", "b", "c")

def get_random_legend_label(index):
    """生成随机图例标签，模仿真实图表中的系列命名"""
    if random.random() < 0.5:
        return random.choice(LEGEND_LABEL_PREFIXES) + " " + random.choice(LEGEND_LABEL_SUFFIXES)
    return random.choice(LEGEND_LABEL_PREFIXES) + " " + str(index + 1)

def get_safe_thickness():
    """获取安全的线条粗细（确保在OpenCV有效范围内），范围更广以增加多样性"""
    return random.randint(1, 5)


def get_legend_border_thickness():
    """图例框描边：仅用细线，避免随机过粗影响观感"""
    return random.randint(1, 2)

def draw_shape(image, center, size, shape_name, color, fill_type, thickness=None):
    """绘制指定形状（确保线条粗细安全）"""
    x, y = center
    half_size = max(1, size // 2)
    
    # 处理线条粗细，确保安全
    if thickness is None:
        if fill_type == 'solid':
            thickness = -1  # 实心填充，无描边
        else:
            thickness = 1   # 默认空心厚度
    elif thickness <= 0 and fill_type == 'hollow':
        thickness = 1   # 空心时厚度至少为 1
    
    # 实心+描边：先填满再画边框；thickness>0 表示要描边
    solid_with_border = (fill_type == 'solid' and thickness > 0)
    if thickness > 0:
        thickness = max(1, min(thickness, 10))  # 限制在 1–10

    if shape_name == 'circle':
        if fill_type == 'solid':
            cv2.circle(image, (x, y), half_size, color, -1)
        if solid_with_border or fill_type == 'hollow':
            cv2.circle(image, (x, y), half_size, color, thickness)
    
    elif shape_name == 'square':
        pt1 = (x - half_size, y - half_size)
        pt2 = (x + half_size, y + half_size)
        if fill_type == 'solid':
            cv2.rectangle(image, pt1, pt2, color, -1)
        if solid_with_border or fill_type == 'hollow':
            cv2.rectangle(image, pt1, pt2, color, thickness)
    
    elif shape_name == 'triangle':
        pts = np.array([
            [x, y - half_size],
            [x - half_size, y + half_size],
            [x + half_size, y + half_size]
        ], np.int32)
        if fill_type == 'solid':
            cv2.fillPoly(image, [pts], color)
        if solid_with_border or fill_type == 'hollow':
            cv2.polylines(image, [pts], True, color, thickness)
    
    elif shape_name == 'diamond':
        pts = np.array([
            [x, y - half_size],
            [x + half_size, y],
            [x, y + half_size],
            [x - half_size, y]
        ], np.int32)
        if fill_type == 'solid':
            cv2.fillPoly(image, [pts], color)
        if solid_with_border or fill_type == 'hollow':
            cv2.polylines(image, [pts], True, color, thickness)
    
    elif shape_name == 'star':
        outer_radius = half_size
        inner_radius = max(1, half_size // 2)
        pts = []
        for i in range(5):
            angle = np.pi/2 + i * 2*np.pi/5
            pts.append([x + outer_radius * np.cos(angle), y - outer_radius * np.sin(angle)])
            angle += np.pi/5
            pts.append([x + inner_radius * np.cos(angle), y - inner_radius * np.sin(angle)])
        
        pts = np.array(pts, np.int32)
        if fill_type == 'solid':
            cv2.fillPoly(image, [pts], color)
        if solid_with_border or fill_type == 'hollow':
            cv2.polylines(image, [pts], True, color, thickness)
    
    elif shape_name == 'cross':
        # 确保坐标在图像范围内
        x1, y1 = max(0, x - half_size), y
        x2, y2 = min(image.shape[1] - 1, x + half_size), y
        x3, y3 = x, max(0, y - half_size)
        x4, y4 = x, min(image.shape[0] - 1, y + half_size)
        
        line_thickness = thickness if thickness and thickness > 0 else 1
        cv2.line(image, (x1, y1), (x2, y2), color, line_thickness)
        cv2.line(image, (x3, y3), (x4, y4), color, line_thickness)
    
    elif shape_name == 'plus':
        x1, y1 = max(0, x - half_size), y
        x2, y2 = min(image.shape[1] - 1, x + half_size), y
        x3, y3 = x, max(0, y - half_size)
        x4, y4 = x, min(image.shape[0] - 1, y + half_size)
        
        line_thickness = thickness if thickness and thickness > 0 else 1
        cv2.line(image, (x1, y1), (x2, y2), color, line_thickness)
        cv2.line(image, (x3, y3), (x4, y4), color, line_thickness)
    
    elif shape_name == 'pentagon':
        pts = []
        for i in range(5):
            angle = 2 * np.pi * i / 5 - np.pi/2
            pts.append([x + half_size * np.cos(angle), y + half_size * np.sin(angle)])
        pts = np.array(pts, np.int32)
        if fill_type == 'solid':
            cv2.fillPoly(image, [pts], color)
        if solid_with_border or fill_type == 'hollow':
            cv2.polylines(image, [pts], True, color, thickness)
    
    elif shape_name == 'xmark':
        x1, y1 = max(0, x - half_size), max(0, y - half_size)
        x2, y2 = min(image.shape[1] - 1, x + half_size), min(image.shape[0] - 1, y + half_size)
        x3, y3 = max(0, x - half_size), min(image.shape[0] - 1, y + half_size)
        x4, y4 = min(image.shape[1] - 1, x + half_size), max(0, y - half_size)
        
        line_thickness = thickness if thickness and thickness > 0 else 1
        cv2.line(image, (x1, y1), (x2, y2), color, line_thickness)
        cv2.line(image, (x3, y3), (x4, y4), color, line_thickness)


def draw_shape_with_alpha(image, center, size, shape_name, color, fill_type, thickness=None, alpha=1.0):
    """绘制带透明度的形状（模仿真实图表中的半透明标记）。alpha=1 时直接绘制，否则先绘到 overlay 再混合。"""
    if alpha >= 0.99:
        draw_shape(image, center, size, shape_name, color, fill_type, thickness)
        return
    overlay = np.zeros_like(image)
    draw_shape(overlay, center, size, shape_name, color, fill_type, thickness)
    mask = np.any(overlay != 0, axis=2)
    if np.any(mask):
        image[mask] = (alpha * overlay[mask] + (1 - alpha) * image[mask]).astype(np.uint8)


def get_text_size(text, font_scale=0.35, thickness=1):
    """获取文本的尺寸"""
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    return text_width, text_height + baseline

def create_voc_xml(image_path, image_size, shapes_data):
    """创建VOC格式的XML文件"""
    root = ET.Element("annotation")
    
    folder = ET.SubElement(root, "folder")
    folder.text = "scatter_images"
    
    filename = ET.SubElement(root, "filename")
    filename.text = os.path.basename(image_path)
    
    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width")
    width.text = str(image_size[0])
    height = ET.SubElement(size, "height")
    height.text = str(image_size[1])
    depth = ET.SubElement(size, "depth")
    depth.text = "3"
    
    for shape_name, points in shapes_data.items():
        for (x, y, size_val) in points:
            obj = ET.SubElement(root, "object")
            
            name = ET.SubElement(obj, "name")
            name.text = shape_name
            
            bndbox = ET.SubElement(obj, "bndbox")
            xmin = ET.SubElement(bndbox, "xmin")
            xmin.text = str(max(0, x - size_val//2))
            ymin = ET.SubElement(bndbox, "ymin")
            ymin.text = str(max(0, y - size_val//2))
            xmax = ET.SubElement(bndbox, "xmax")
            xmax.text = str(min(image_size[0], x + size_val//2))
            ymax = ET.SubElement(bndbox, "ymax")
            ymax.text = str(min(image_size[1], y + size_val//2))
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    xml_path = image_path.replace('.png', '.xml')
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)


def primary_x_axis_label_baseline(origin_y, is_log_x, image_height):
    """主 X 轴名称的 putText baseline：置于刻度数字下方，避免与刻度线及数值重叠。"""
    tick_num_baseline = origin_y + 22 if is_log_x else origin_y + 20
    _, tick_h = cv2.getTextSize("8", cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, TEXT_STROKE_THIN)
    y = tick_num_baseline + tick_h + 10
    return min(y, image_height - 5)


def draw_coordinate_system(
    image,
    width,
    height,
    origin_x,
    origin_y,
    scale_type,
    chart_title_text,
    x_label_text_primary,
    y_label_text_primary,
    x_label_text_secondary,
    y_label_text_secondary,
    has_second_x,
    has_second_y,
    axis_label_font_scale,
    axis_label_thickness,
    title_font_scale,
    title_thickness,
    linear_plot_span_x=None,
    linear_plot_span_y=None,
):
    """绘制坐标轴系统。
    linear_plot_span_x/y：线性轴上用于等分刻度的半轴像素跨度（与 num_ticks 相除得步长）；
    若给定且大于 min(左右/上下) 可用距离，可使刻度数值范围覆盖更远的散点（默认仅对称半宽）。"""
    margin = 50
    
    origin_x = max(margin, min(width - margin, origin_x))
    origin_y = max(margin, min(height - margin, origin_y))
    
    axis_thickness = get_safe_thickness()
    
    cv2.line(image, (origin_x, margin), (origin_x, height - margin), (0, 0, 0), axis_thickness)
    cv2.line(image, (margin, origin_y), (width - margin, origin_y), (0, 0, 0), axis_thickness)
    
    cv2.arrowedLine(image, (origin_x, margin), (origin_x, margin - 10), (0, 0, 0), axis_thickness)
    cv2.arrowedLine(image, (width - margin, origin_y), 
                   (width - margin + 10, origin_y), (0, 0, 0), axis_thickness)
    
    if chart_title_text:
        (title_w, title_h), _ = cv2.getTextSize(
            chart_title_text, cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, TEXT_STROKE_THIN
        )
        title_x = max(margin, (width - title_w) // 2)
        # 标题一般放在图片下方（靠近底边，居中）
        title_y = height - 10
        cv2.putText(image, chart_title_text, (title_x, title_y),
                    cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, (0, 0, 0), TEXT_STROKE_THIN)

    cv2.putText(image, y_label_text_primary, (origin_x - 20, margin - 10),
                cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, (0, 0, 0), TEXT_STROKE_THIN)

    # 是否为对数坐标轴（需在绘制 X 轴标题前确定，以便与刻度数字纵向错开）
    is_log_x = scale_type in ("log_x", "log_xy")
    is_log_y = scale_type in ("log_y", "log_xy")

    # X 轴标题右侧容易超出画布边界：根据文字宽度把它“贴住画布右侧但不越界”
    (xw, _xh), _xb = cv2.getTextSize(
        x_label_text_primary, cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, TEXT_STROKE_THIN
    )
    x_label_x = max(margin, width - margin - xw - 5)
    x_label_baseline = primary_x_axis_label_baseline(origin_y, is_log_x, height)
    cv2.putText(
        image,
        x_label_text_primary,
        (x_label_x, x_label_baseline),
        cv2.FONT_HERSHEY_SIMPLEX,
        axis_label_font_scale,
        (0, 0, 0),
        TEXT_STROKE_THIN,
    )

    # 线性刻度：关于原点对称，以左右（上下）可用空间的最小值确定步长
    num_ticks = 5
    x_left_range = origin_x - margin
    x_right_range = width - margin - origin_x
    y_top_range = origin_y - margin
    y_bottom_range = height - margin - origin_y

    x_half_range = min(x_left_range, x_right_range)
    y_half_range = min(y_top_range, y_bottom_range)

    x_span_linear = (
        linear_plot_span_x if (linear_plot_span_x is not None and not is_log_x) else x_half_range
    )
    y_span_linear = (
        linear_plot_span_y if (linear_plot_span_y is not None and not is_log_y) else y_half_range
    )
    x_step = x_span_linear / num_ticks if num_ticks > 0 else 0
    y_step = y_span_linear / num_ticks if num_ticks > 0 else 0
    
    for i in range(1, num_ticks + 1):
        # X 轴线性刻度（正负对称）
        if not is_log_x:
            # 右侧刻度
            x_pos = int(origin_x + i * x_step)
            if margin < x_pos < width - margin:
                cv2.line(image, (x_pos, origin_y), (x_pos, origin_y + 5), (0, 0, 0), 1)
                cv2.putText(image, str(i), (x_pos - 5, origin_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)
            
            # 左侧刻度（与右侧步长相同，保证对称）
            x_pos = int(origin_x - i * x_step)
            if margin < x_pos < width - margin:
                cv2.line(image, (x_pos, origin_y), (x_pos, origin_y + 5), (0, 0, 0), 1)
                cv2.putText(image, str(-i), (x_pos - 10, origin_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)

        # Y 轴线性刻度（正负对称）
        if not is_log_y:
            # 上侧刻度
            y_pos = int(origin_y - i * y_step)
            if margin < y_pos < height - margin:
                cv2.line(image, (origin_x, y_pos), (origin_x - 5, y_pos), (0, 0, 0), 1)
                cv2.putText(image, str(i), (origin_x - 25, y_pos + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)
            
            # 下侧刻度
            y_pos = int(origin_y + i * y_step)
            if margin < y_pos < height - margin:
                cv2.line(image, (origin_x, y_pos), (origin_x - 5, y_pos), (0, 0, 0), 1)
                cv2.putText(image, str(-i), (origin_x - 25, y_pos + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)

    # 线性双轴时在原点附近标注原点坐标 0（对数轴在数据上不含 0，不标注以免歧义）
    if not is_log_x and not is_log_y:
        cv2.putText(
            image,
            "0",
            (origin_x - 15, origin_y + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            TICK_LABEL_FONT_SCALE,
            (0, 0, 0),
            TEXT_STROKE_THIN,
        )

    # 对数刻度：只在正方向绘制 10^0,10^1,10^2,10^3 及其间的次刻度
    # X 轴对数刻度（单/双对数时）
    if is_log_x:
        min_decade, max_decade = 0, 3  # 1 ~ 1000
        total_decades = max_decade - min_decade
        for decade in range(min_decade, max_decade + 1):
            v = 10 ** decade
            frac = (decade - min_decade) / total_decades if total_decades > 0 else 0
            x_pos = int(origin_x + frac * x_right_range)
            if margin < x_pos < width - margin:
                # 主刻度
                cv2.line(image, (x_pos, origin_y), (x_pos, origin_y + 6), (0, 0, 0), 1)
                label = str(v)
                cv2.putText(image, label, (x_pos - 8, origin_y + 22),
                            cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)
            # 次刻度：2~9
            for m in range(2, 10):
                log_v = decade + math.log10(m)
                if log_v > max_decade:
                    break
                frac_m = (log_v - min_decade) / total_decades if total_decades > 0 else 0
                x_minor = int(origin_x + frac_m * x_right_range)
                if margin < x_minor < width - margin:
                    cv2.line(image, (x_minor, origin_y), (x_minor, origin_y + 3), (0, 0, 0), 1)

    # Y 轴对数刻度（单/双对数时）
    if is_log_y:
        min_decade, max_decade = 0, 3  # 1 ~ 1000
        total_decades = max_decade - min_decade
        for decade in range(min_decade, max_decade + 1):
            v = 10 ** decade
            frac = (decade - min_decade) / total_decades if total_decades > 0 else 0
            y_pos = int(origin_y - frac * y_top_range)
            if margin < y_pos < height - margin:
                cv2.line(image, (origin_x, y_pos), (origin_x - 6, y_pos), (0, 0, 0), 1)
                label = str(v)
                cv2.putText(image, label, (origin_x - 40, y_pos + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, TICK_LABEL_FONT_SCALE, (0, 0, 0), TEXT_STROKE_THIN)
            for m in range(2, 10):
                log_v = decade + math.log10(m)
                if log_v > max_decade:
                    break
                frac_m = (log_v - min_decade) / total_decades if total_decades > 0 else 0
                y_minor = int(origin_y - frac_m * y_top_range)
                if margin < y_minor < height - margin:
                    cv2.line(image, (origin_x, y_minor), (origin_x - 3, y_minor), (0, 0, 0), 1)

    # 第二横轴：位于顶部，刻度与主 X 轴一致，标签为 X2
    if has_second_x:
        y2 = margin
        cv2.line(image, (margin, y2), (width - margin, y2), (0, 0, 0), axis_thickness)
        cv2.arrowedLine(image, (width - margin, y2), (width - margin + 10, y2), (0, 0, 0), axis_thickness)
        (xw2, _xh2), _xb2 = cv2.getTextSize(
            x_label_text_secondary, cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, TEXT_STROKE_THIN
        )
        x2_label_x = max(margin, width - margin - xw2 - 5)
        cv2.putText(image, x_label_text_secondary, (x2_label_x, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, (0, 0, 0), TEXT_STROKE_THIN)

        # 线性第二横轴刻度（不重复数值，只有刻度线）
        if not is_log_x:
            for i in range(1, num_ticks + 1):
                x_pos = int(origin_x + i * x_step)
                if margin < x_pos < width - margin:
                    cv2.line(image, (x_pos, y2), (x_pos, y2 - 5), (0, 0, 0), 1)
                x_pos = int(origin_x - i * x_step)
                if margin < x_pos < width - margin:
                    cv2.line(image, (x_pos, y2), (x_pos, y2 - 5), (0, 0, 0), 1)
        else:
            # 对数第二横轴刻度：复制主对数轴的刻度位置
            min_decade, max_decade = 0, 3
            total_decades = max_decade - min_decade
            for decade in range(min_decade, max_decade + 1):
                frac = (decade - min_decade) / total_decades if total_decades > 0 else 0
                x_pos = int(origin_x + frac * x_right_range)
                if margin < x_pos < width - margin:
                    cv2.line(image, (x_pos, y2), (x_pos, y2 - 5), (0, 0, 0), 1)
                for m in range(2, 10):
                    log_v = decade + math.log10(m)
                    if log_v > max_decade:
                        break
                    frac_m = (log_v - min_decade) / total_decades if total_decades > 0 else 0
                    x_minor = int(origin_x + frac_m * x_right_range)
                    if margin < x_minor < width - margin:
                        cv2.line(image, (x_minor, y2), (x_minor, y2 - 3), (0, 0, 0), 1)

    # 第二纵轴：位于右侧，刻度与主 Y 轴一致，标签为 Y2
    if has_second_y:
        x2 = width - margin
        cv2.line(image, (x2, margin), (x2, height - margin), (0, 0, 0), axis_thickness)
        cv2.arrowedLine(image, (x2, margin), (x2, margin - 10), (0, 0, 0), axis_thickness)
        cv2.putText(image, y_label_text_secondary, (x2 - 20, margin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, (0, 0, 0), TEXT_STROKE_THIN)

        if not is_log_y:
            for i in range(1, num_ticks + 1):
                y_pos = int(origin_y - i * y_step)
                if margin < y_pos < height - margin:
                    cv2.line(image, (x2, y_pos), (x2 + 5, y_pos), (0, 0, 0), 1)
                y_pos = int(origin_y + i * y_step)
                if margin < y_pos < height - margin:
                    cv2.line(image, (x2, y_pos), (x2 + 5, y_pos), (0, 0, 0), 1)
        else:
            min_decade, max_decade = 0, 3
            total_decades = max_decade - min_decade
            for decade in range(min_decade, max_decade + 1):
                frac = (decade - min_decade) / total_decades if total_decades > 0 else 0
                y_pos = int(origin_y - frac * y_top_range)
                if margin < y_pos < height - margin:
                    cv2.line(image, (x2, y_pos), (x2 + 5, y_pos), (0, 0, 0), 1)
                for m in range(2, 10):
                    log_v = decade + math.log10(m)
                    if log_v > max_decade:
                        break
                    frac_m = (log_v - min_decade) / total_decades if total_decades > 0 else 0
                    y_minor = int(origin_y - frac_m * y_top_range)
                    if margin < y_minor < height - margin:
                        cv2.line(image, (x2, y_minor), (x2 + 3, y_minor), (0, 0, 0), 1)
    
    return origin_x, origin_y

def draw_grid(
    image,
    width,
    height,
    origin_x,
    origin_y,
    linear_span_x=None,
    linear_span_y=None,
):
    """绘制网格线：位置和间隔与刻度线严格对齐。须在 draw_coordinate_system 之前调用，使网格位于刻度线之下。"""
    margin = 50
    num_ticks = 5
    # 浅灰、更接近白底，视觉上透明度更高，干扰更弱（原 220 略偏深）
    grid_color = (240, 240, 240)

    x_left_range = origin_x - margin
    x_right_range = width - margin - origin_x
    y_top_range = origin_y - margin
    y_bottom_range = height - margin - origin_y

    x_half_range = min(x_left_range, x_right_range)
    y_half_range = min(y_top_range, y_bottom_range)

    x_span = linear_span_x if linear_span_x is not None else x_half_range
    y_span = linear_span_y if linear_span_y is not None else y_half_range

    x_step = x_span / num_ticks if num_ticks > 0 else 0
    y_step = y_span / num_ticks if num_ticks > 0 else 0

    grid_thickness = random.choice([1, 2])

    # 水平网格线：与 y 方向刻度对应
    for i in range(1, num_ticks + 1):
        y_pos = int(origin_y - i * y_step)
        if margin < y_pos < height - margin:
            cv2.line(image, (margin, y_pos), (width - margin, y_pos), grid_color, grid_thickness)

        y_pos = int(origin_y + i * y_step)
        if margin < y_pos < height - margin:
            cv2.line(image, (margin, y_pos), (width - margin, y_pos), grid_color, grid_thickness)

    # 垂直网格线：与 x 方向刻度对应
    for i in range(1, num_ticks + 1):
        x_pos = int(origin_x - i * x_step)
        if margin < x_pos < width - margin:
            cv2.line(image, (x_pos, margin), (x_pos, height - margin), grid_color, grid_thickness)

        x_pos = int(origin_x + i * x_step)
        if margin < x_pos < width - margin:
            cv2.line(image, (x_pos, margin), (x_pos, height - margin), grid_color, grid_thickness)

def draw_trend_line(image, width, height, origin_x, origin_y, points):
    """绘制趋势线（干扰线）。须在 draw_coordinate_system 之前调用，以免盖住刻度与数值。"""
    if len(points) < 2:
        return
    
    trend_type = random.choice(['linear', 'quadratic'])
    margin = 50
    
    trend_thickness = get_safe_thickness()
    trend_color = random.choice(list(COLORS.values()))

    if trend_type == 'linear':
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        if len(set(x_coords)) > 1:
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]
            
            x1 = margin
            x2 = width - margin
            y1 = int(m * x1 + c)
            y2 = int(m * x2 + c)
            
            if margin <= y1 <= height - margin and margin <= y2 <= height - margin:
                cv2.line(image, (x1, y1), (x2, y2), trend_color, trend_thickness)

def is_point_in_legend(x, y, legend_rect):
    """检查点是否在图例框内"""
    lx, ly, lw, lh = legend_rect
    return lx <= x <= lx + lw and ly <= y <= ly + lh

def calculate_legend_size(legend_items, padding=20, item_spacing=30, symbol_width=30):
    """计算图例框的大小（根据每项 label 与 font_scale 自适应）"""
    max_text_width = 0
    total_height = padding * 2
    
    for item in legend_items:
        text = item.get('label', item['shape'])
        font_scale = item.get('font_scale', 0.35)
        text_width, text_height = get_text_size(text, font_scale=font_scale)
        
        total_width = symbol_width + text_width + 15
        max_text_width = max(max_text_width, total_width)
        
        total_height += item_spacing
    
    return max_text_width + padding, total_height

def get_legend_count():
    """获取图例数量：通常为2（模仿真实科学图表），小概率为1、3、4、5以增加多样性"""
    weights = [0.08, 0.60, 0.20, 0.08, 0.04]  # 1, 2, 3, 4, 5
    return random.choices([1, 2, 3, 4, 5], weights=weights)[0]

def generate_scatter_plot(image_idx):
    """生成一张散点图，并返回用于 JSON 标注的信息"""
    width = random.randint(480, 520)
    height = random.randint(480, 520)
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    margin = 60
    # 原点尽量置于画面几何中心，小范围随机偏移以保留样本多样性（随后仍经 margin 钳制）
    _cj = 28
    origin_x = width // 2 + random.randint(-_cj, _cj)
    origin_y = height // 2 + random.randint(-_cj, _cj)
    # 坐标轴类型：60% 线性；40% 概率为单/双对数
    r = random.random()
    if r < 0.60:
        scale_type = 'linear'
    elif r < 0.76:
        scale_type = 'log_x'   # 16%：仅 X 为对数
    elif r < 0.92:
        scale_type = 'log_y'   # 16%：仅 Y 为对数
    else:
        scale_type = 'log_xy'  # 8%：双对数

    # 图标题与坐标轴标题（含单位）：保证 JSON 与图像一致且不为空
    chart_titles = [
        "Experimental Scatter Results",
        "Material Property Analysis",
        "Measurement Data Overview",
        "Physics Dataset Summary",
        "Engineering Parameter Mapping",
    ]
    chart_title_text = random.choice(chart_titles)

    axis_param_templates = [
        ("Energy", "eV"),
        ("Time", "s"),
        ("Temperature", "K"),
        ("Frequency", "Hz"),
        ("Pressure", "Pa"),
        ("Concentration", "mol/L"),
        ("Stress", "MPa"),
        ("Strain", "%"),
        ("Velocity", "m/s"),
        ("Distance", "m"),
    ]
    x_param_name, x_unit = random.choice(axis_param_templates)
    y_param_name, y_unit = random.choice(axis_param_templates)

    x_label_text_primary = f"{x_param_name} ({x_unit})"
    y_label_text_primary = f"{y_param_name} ({y_unit})"

    # 双轴：部分图随机出现第二横轴/第二纵轴（适当降低占比）
    has_second_x = random.random() < 0.08
    has_second_y = random.random() < 0.08
    x_label_text_secondary = f"{x_param_name}2 ({x_unit})"
    y_label_text_secondary = f"{y_param_name}2 ({y_unit})"

    # 字重：OpenCV 仅支持笔画粗细 1/2…，统一用最细笔画；字号略收敛，避免视觉上偏粗
    axis_label_font_scale = round(random.uniform(0.40, 0.62), 2)
    axis_label_thickness = TEXT_STROKE_THIN
    title_font_scale = round(random.uniform(0.38, 0.58), 2)
    title_thickness = TEXT_STROKE_THIN

    # 与 draw_coordinate_system 内一致，先钳制原点；网格须先于坐标轴/刻度绘制，否则会盖住刻度线
    coord_margin_pre = 50
    origin_x = max(coord_margin_pre, min(width - coord_margin_pre, origin_x))
    origin_y = max(coord_margin_pre, min(height - coord_margin_pre, origin_y))

    coord_margin = 50  # draw_coordinate_system 内的 margin
    num_ticks = 5
    is_log_x = scale_type in ("log_x", "log_xy")
    is_log_y = scale_type in ("log_y", "log_xy")

    x_left_range = origin_x - coord_margin
    x_right_range = width - coord_margin - origin_x
    y_top_range = origin_y - coord_margin
    y_bottom_range = height - coord_margin - origin_y

    x_half_range = min(x_left_range, x_right_range)
    y_half_range = min(y_top_range, y_bottom_range)

    num_shapes = get_legend_count()
    shapes_to_use = random.sample(list(SHAPES.keys()), num_shapes)

    # 生成图例项信息：形状、颜色、大小、填充、线宽、透明度、标签、字体大小（多样且模仿真实图表）
    legend_items = []
    for idx, shape_name in enumerate(shapes_to_use):
        color_name = random.choice(list(COLORS.keys()))
        color = COLORS[color_name]
        size = random.randint(MIN_SIZE, MAX_SIZE)
        fill_type = random.choice(list(FILL_TYPES.keys()))
        # 线条粗细：空心必选，实心也可加细描边以增加多样性
        thickness = -1
        if fill_type == 'hollow':
            thickness = get_safe_thickness()
        elif random.random() < 0.25:
            thickness = get_safe_thickness()  # 实心+描边
        # 透明度：多数不透明，部分半透明以模仿真实图表
        alpha = 1.0 if random.random() < 0.75 else random.uniform(0.5, 0.95)
        font_scale = round(random.uniform(0.26, 0.36), 2)
        legend_items.append({
            'shape': shape_name,
            'color': color,
            'color_name': color_name,
            'size': size,
            'fill_type': fill_type,
            'thickness': thickness,
            'alpha': alpha,
            'label': get_random_legend_label(idx),
            'font_scale': font_scale,
        })

    legend_w, legend_h = calculate_legend_size(legend_items)

    legend_positions = [
        ('top-right', width - legend_w - 20, 20),
        ('top-left', 20, 20),
        ('bottom-right', width - legend_w - 20, height - legend_h - 20),
        ('bottom-left', 20, height - legend_h - 20),
        ('center-right', width - legend_w - 20, height // 2 - legend_h // 2),
        ('center-left', 20, height // 2 - legend_h // 2),
        ('center-top', width // 2 - legend_w // 2, 20),
        ('center-bottom', width // 2 - legend_w // 2, height - legend_h - 20)
    ]

    # 尽量避免图例与坐标轴/刻度区域重叠
    axis_pad = 18

    def rect_overlap_area(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
        inter_w = max(0, min(ax2, bx2) - max(ax1, bx1))
        inter_h = max(0, min(ay2, by2) - max(ay1, by1))
        return inter_w * inter_h

    forbidden_rects = []
    # 主坐标轴：竖轴（y 方向全段）与横轴（x 方向全段）
    forbidden_rects.append((
        origin_x - axis_pad, coord_margin,
        origin_x + axis_pad, height - coord_margin
    ))
    forbidden_rects.append((
        coord_margin, origin_y - axis_pad,
        width - coord_margin, origin_y + axis_pad
    ))
    # 双坐标轴：次横轴在 y=coord_margin，次纵轴在 x=width-coord_margin
    if has_second_x:
        forbidden_rects.append((
            coord_margin, coord_margin - axis_pad,
            width - coord_margin, coord_margin + axis_pad
        ))
    if has_second_y:
        x2 = width - coord_margin
        forbidden_rects.append((
            x2 - axis_pad, coord_margin,
            x2 + axis_pad, height - coord_margin
        ))

    best = None
    best_score = None
    for pos_name, cand_x, cand_y in legend_positions:
        # 约束到图像内（避免负坐标导致异常）
        cand_x = max(0, min(width - legend_w, cand_x))
        cand_y = max(0, min(height - legend_h, cand_y))
        cand_x2 = cand_x + legend_w
        cand_y2 = cand_y + legend_h

        score = 0
        for (fx1, fy1, fx2, fy2) in forbidden_rects:
            score += rect_overlap_area(cand_x, cand_y, cand_x2, cand_y2, fx1, fy1, fx2, fy2)

        # 选择“重叠面积最小”的候选；若完全不重叠，优先选这些
        if best is None or score < best_score:
            best = (pos_name, cand_x, cand_y)
            best_score = score

    # 在最优解附近再做一点随机性：允许在少数 top 候选里随机选
    # 为简化，这里直接使用最优解（score 最小）。
    legend_pos, legend_x, legend_y = best
    legend_rect = (legend_x, legend_y, legend_w, legend_h)

    # 先采样散点像素位置（不绘制），据此扩展线性轴刻度跨度，使刻度数值范围覆盖散点 real 坐标
    num_points = random.randint(10, 50)
    shapes_data = {shape: [] for shape in shapes_to_use}
    all_points = []

    attempts = 0
    max_attempts = num_points * 10

    while len(all_points) < num_points and attempts < max_attempts:
        attempts += 1

        # 若为对数坐标，强制点落在正半轴（避免 log(0)/log(负数)）。
        if is_log_x:
            x = random.randint(origin_x + 10, width - margin - 20)
        else:
            # 线性 X 允许正负两侧
            if random.random() < 0.5:
                x = random.randint(margin + 20, origin_x - 10)
            else:
                x = random.randint(origin_x + 10, width - margin - 20)

        if is_log_y:
            # log_y：真实坐标 y>0，对应像素 y 在 origin_y 上方
            y = random.randint(margin + 20, origin_y - 10)
        else:
            # 线性 Y 允许正负两侧
            if random.random() < 0.5:
                y = random.randint(margin + 20, origin_y - 10)
            else:
                y = random.randint(origin_y + 10, height - margin - 20)

        if is_point_in_legend(x, y, legend_rect):
            continue

        legend_item = random.choice(legend_items)

        shape_name = legend_item['shape']
        size = legend_item['size']

        shapes_data[shape_name].append((x, y, size))
        all_points.append((x, y))

    max_dx = max((abs(x - origin_x) for x, _ in all_points), default=0)
    max_dy = max((abs(y - origin_y) for _, y in all_points), default=0)
    plot_span_x = max(x_half_range, max_dx) if not is_log_x else x_half_range
    plot_span_y = max(y_half_range, max_dy) if not is_log_y else y_half_range

    # 仅在线性坐标系下绘制网格线，使其与线性刻度完全对齐（作为背景层）
    has_grid = (scale_type == 'linear') and (random.random() < 0.3)
    if has_grid:
        draw_grid(
            image,
            width,
            height,
            origin_x,
            origin_y,
            plot_span_x,
            plot_span_y,
        )

    # 干扰趋势线：须在坐标轴/刻度之前绘制，否则会盖住刻度线及数值
    if random.random() < 0.4 and len(all_points) >= 5:
        draw_trend_line(image, width, height, origin_x, origin_y, all_points)

    origin_x, origin_y = draw_coordinate_system(
        image,
        width,
        height,
        origin_x,
        origin_y,
        scale_type,
        chart_title_text,
        x_label_text_primary,
        y_label_text_primary,
        x_label_text_secondary,
        y_label_text_secondary,
        has_second_x,
        has_second_y,
        axis_label_font_scale,
        axis_label_thickness,
        title_font_scale,
        title_thickness,
        linear_plot_span_x=None if is_log_x else plot_span_x,
        linear_plot_span_y=None if is_log_y else plot_span_y,
    )

    # ----------------------------
    # 像素 -> 真实坐标映射参数（与上面 plot_span_* 一致）
    # ----------------------------
    x_step = plot_span_x / num_ticks if (num_ticks > 0 and not is_log_x) else 0.0
    y_step = plot_span_y / num_ticks if (num_ticks > 0 and not is_log_y) else 0.0

    # 对数坐标轴使用的数量级范围：1 ~ 1000
    min_decade, max_decade = 0, 3
    total_decades = max_decade - min_decade

    # ----------------------------
    # 计算刻度：ticks.positions + ticks.pixelPositions
    # （与 draw_coordinate_system 绘制逻辑一致）
    # ----------------------------
    plot_margin = coord_margin  # draw_coordinate_system 内 margin=50

    x_ticks_positions = []
    x_ticks_pixelPositions = []
    y_ticks_positions = []
    y_ticks_pixelPositions = []

    # X 轴刻度
    if not is_log_x:
        neg_pos, neg_pix = [], []
        pos_pos, pos_pix = [], []
        for i in range(1, num_ticks + 1):
            x_pos = int(origin_x - i * x_step)
            if plot_margin < x_pos < width - plot_margin:
                neg_pos.append(-i)
                neg_pix.append([x_pos, origin_y])

            x_pos = int(origin_x + i * x_step)
            if plot_margin < x_pos < width - plot_margin:
                pos_pos.append(i)
                pos_pix.append([x_pos, origin_y])

        x_ticks_positions = neg_pos + [0] + pos_pos
        x_ticks_pixelPositions = neg_pix + [[origin_x, origin_y]] + pos_pix
    else:
        # log_x：仅正半轴，主刻度 10^0~10^3，次刻度 2~9
        if x_right_range > 0 and total_decades > 0:
            for decade in range(min_decade, max_decade + 1):
                v = 10 ** decade
                frac = (decade - min_decade) / total_decades
                x_major = int(origin_x + frac * x_right_range)
                if plot_margin < x_major < width - plot_margin:
                    x_ticks_positions.append(v)
                    x_ticks_pixelPositions.append([x_major, origin_y])

                for m in range(2, 10):
                    log_v = decade + math.log10(m)
                    if log_v > max_decade:
                        break
                    frac_m = (log_v - min_decade) / total_decades
                    x_minor = int(origin_x + frac_m * x_right_range)
                    if plot_margin < x_minor < width - plot_margin:
                        x_ticks_positions.append(v * m)
                        x_ticks_pixelPositions.append([x_minor, origin_y])

    # Y 轴刻度
    if not is_log_y:
        neg_pos, neg_pix = [], []
        pos_pos, pos_pix = [], []
        for i in range(1, num_ticks + 1):
            # 下侧刻度对应 -i
            y_pos = int(origin_y + i * y_step)
            if plot_margin < y_pos < height - plot_margin:
                neg_pos.append(-i)
                neg_pix.append([origin_x, y_pos])

            # 上侧刻度对应 +i
            y_pos = int(origin_y - i * y_step)
            if plot_margin < y_pos < height - plot_margin:
                pos_pos.append(i)
                pos_pix.append([origin_x, y_pos])

        y_ticks_positions = neg_pos + [0] + pos_pos
        y_ticks_pixelPositions = neg_pix + [[origin_x, origin_y]] + pos_pix
    else:
        # log_y：仅正值（像素在 origin_y 上方），主刻度 10^0~10^3，次刻度 2~9
        if y_top_range > 0 and total_decades > 0:
            for decade in range(min_decade, max_decade + 1):
                v = 10 ** decade
                frac = (decade - min_decade) / total_decades
                y_major = int(origin_y - frac * y_top_range)
                if plot_margin < y_major < height - plot_margin:
                    y_ticks_positions.append(v)
                    y_ticks_pixelPositions.append([origin_x, y_major])

                for m in range(2, 10):
                    log_v = decade + math.log10(m)
                    if log_v > max_decade:
                        break
                    frac_m = (log_v - min_decade) / total_decades
                    y_minor = int(origin_y - frac_m * y_top_range)
                    if plot_margin < y_minor < height - plot_margin:
                        y_ticks_positions.append(v * m)
                        y_ticks_pixelPositions.append([origin_x, y_minor])

    # secondary 轴：只有存在时才填充 ticks 信息
    x_ticks_positions_secondary = x_ticks_positions if has_second_x else []
    x_ticks_pixelPositions_secondary = x_ticks_pixelPositions if has_second_x else []
    y_ticks_positions_secondary = y_ticks_positions if has_second_y else []
    y_ticks_pixelPositions_secondary = y_ticks_pixelPositions if has_second_y else []

    has_border = random.random() < 0.7
    border_thickness = get_legend_border_thickness() if has_border else 0
    
    # 绘制图例框（边框有无与粗细随机，自适应内容）
    if has_border:
        cv2.rectangle(image, (legend_x, legend_y),
                      (legend_x + legend_w, legend_y + legend_h),
                      (0, 0, 0), border_thickness)
    
    for i, item in enumerate(legend_items):
        shape_name = item['shape']
        color = item['color']
        size = item['size']
        fill_type = item['fill_type']
        color_name = item['color_name']
        thickness = item['thickness']
        alpha = item.get('alpha', 1.0)
        label = item.get('label', shape_name)
        font_scale = item.get('font_scale', 0.35)
        
        symbol_x = legend_x + 15
        symbol_y = legend_y + 25 + i * 30
        
        item['symbol_position'] = [symbol_x, symbol_y]
        item['text_position'] = [symbol_x + 20, symbol_y + 5]
        
        # 绘制图例符号（支持透明度与线宽多样性）
        draw_shape_with_alpha(image, (symbol_x, symbol_y), size, shape_name, color, fill_type, thickness, alpha)
        
        cv2.putText(image, label, (symbol_x + 20, symbol_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), TEXT_STROKE_THIN)
    
    # 绘制已采样的散点（样式与对应图例项一致）
    shape_to_item = {item["shape"]: item for item in legend_items}
    for shape_name, pts in shapes_data.items():
        item = shape_to_item[shape_name]
        for (x, y, size_val) in pts:
            draw_shape_with_alpha(
                image,
                (x, y),
                size_val,
                shape_name,
                item["color"],
                item["fill_type"],
                item["thickness"],
                item.get("alpha", 1.0),
            )
    
    # 构造结构化 JSON 标注信息（参考 结构化标注.json）
    # 坐标轴标题位置与 draw_coordinate_system 内部 margin(=50) 保持一致
    coord_margin = 50
    # X/X2 标题右对齐且不越界：与 draw_coordinate_system 内计算保持一致
    (xw, _xh), _xb = cv2.getTextSize(
        x_label_text_primary, cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, TEXT_STROKE_THIN
    )
    x_label_x = max(coord_margin, width - coord_margin - xw - 5)
    x_label_pos = [
        x_label_x,
        primary_x_axis_label_baseline(origin_y, scale_type in ("log_x", "log_xy"), height),
    ]
    y_label_pos = [origin_x - 20, coord_margin - 10]
    
    (xw2, _xh2), _xb2 = cv2.getTextSize(
        x_label_text_secondary, cv2.FONT_HERSHEY_SIMPLEX, axis_label_font_scale, TEXT_STROKE_THIN
    )
    x2_label_x = max(coord_margin, width - coord_margin - xw2 - 5)
    x2_label_pos = [x2_label_x, coord_margin + 20]
    y2_label_pos = [width - coord_margin - 20, coord_margin - 10]
    
    # 图例框顶点
    legend_box_top_left = [legend_x, legend_y]
    legend_box_bottom_right = [legend_x + legend_w, legend_y + legend_h]
    
    # 根据图例和散点构造 dataSeries
    data_series = []
    for series_idx, item in enumerate(legend_items):
        shape_name = item["shape"]
        color_name = item["color_name"]
        size = item["size"]
        series_name = (item.get("label") or "").strip()
        if not series_name:
            # 图例 name 为空时，使用 dataSeries 的序号兜底（保证同类散点一致）
            series_name = f"Sample {series_idx + 1}"
        series_points = []
        for (x, y, size_val) in shapes_data.get(shape_name, []):
            # 计算像素坐标对应的真实坐标（用于结构化标注 realCoordinates）
            if is_log_x:
                if x_right_range > 0:
                    frac = (x - origin_x) / x_right_range
                    frac = max(0.0, min(1.0, frac))
                    log_v = min_decade + frac * total_decades
                    real_x = float(10 ** log_v)
                else:
                    real_x = 1.0
            else:
                real_x = float((x - origin_x) / x_step) if x_step != 0 else 0.0

            if is_log_y:
                if y_top_range > 0:
                    frac = (origin_y - y) / y_top_range
                    frac = max(0.0, min(1.0, frac))
                    log_v = min_decade + frac * total_decades
                    real_y = float(10 ** log_v)
                else:
                    real_y = 1.0
            else:
                real_y = float((origin_y - y) / y_step) if y_step != 0 else 0.0

            series_points.append({
                "pixelCoordinates": [x, y],
                "realCoordinates": [round(real_x, 4), round(real_y, 4)],
                "dataLabel": series_name
            })
        data_series.append({
            "name": series_name,
            "symbolType": shape_name,
            "symbolColor": color_name,
            "symbolSize": size,
            "points": series_points
        })
    
    # 图例 entries（与显示一致：使用 label）
    legend_entries = []
    for series_idx, item in enumerate(legend_items):
        legend_name = (item.get("label") or "").strip()
        if not legend_name:
            legend_name = f"Sample {series_idx + 1}"
        legend_entries.append({
            "name": legend_name,
            "textPosition": item.get("text_position", []),
            "symbol": {
                "type": item["shape"],
                "color": item["color_name"],
                "pixelPosition": item.get("symbol_position", []),
                "size": item["size"]
            }
        })
    
    annotation = {
        "chartMetadata": {
            "title": {
                "text": chart_title_text,
                # 与 draw_coordinate_system 中标题 baseline 的位置一致
                "pixelPosition": [width // 2, height - 10],
                "fontSize": str(title_font_scale),
                "fontWeight": str(title_thickness)
            }
        },
        "axes": {
            "xAxis": {
                "primary": {
                    "name": x_param_name,
                    "unit": x_unit,
                    "label": {
                        "text": x_label_text_primary,
                        "pixelPosition": x_label_pos,
                        "fontSize": str(axis_label_font_scale),
                        "fontWeight": str(axis_label_thickness),
                    },
                    "ticks": {
                        "values": x_ticks_positions,
                        "pixelPositions": x_ticks_pixelPositions
                    }
                },
                "secondary": {
                    "name": x_param_name if has_second_x else "",
                    "unit": x_unit if has_second_x else "",
                    "label": {
                        "text": x_label_text_secondary if has_second_x else "",
                        "pixelPosition": x2_label_pos if has_second_x else [],
                        "fontSize": str(axis_label_font_scale) if has_second_x else "",
                        "fontWeight": str(axis_label_thickness) if has_second_x else "",
                    }
                }
            },
            "yAxis": {
                "primary": {
                    "name": y_param_name,
                    "unit": y_unit,
                    "label": {
                        "text": y_label_text_primary,
                        "pixelPosition": y_label_pos,
                        "fontSize": str(axis_label_font_scale),
                        "fontWeight": str(axis_label_thickness),
                        "rotation": ""
                    },
                    "ticks": {
                        "values": y_ticks_positions,
                        "pixelPositions": y_ticks_pixelPositions
                    }
                },
                "secondary": {
                    "name": y_param_name if has_second_y else "",
                    "unit": y_unit if has_second_y else "",
                    "label": {
                        "text": y_label_text_secondary if has_second_y else "",
                        "pixelPosition": y2_label_pos if has_second_y else [],
                        "fontSize": str(axis_label_font_scale) if has_second_y else "",
                        "fontWeight": str(axis_label_thickness) if has_second_y else "",
                        "rotation": ""
                    }
                }
            }
        },
        "legend": {
            # 图例像素位置：使用图例框中心点（在合成阶段已确定 legend_x/legend_y/legend_w/legend_h）
            "pixelPosition": [
                int(legend_x + legend_w // 2),
                int(legend_y + legend_h // 2)
            ],
            "box": {
                "topLeft": legend_box_top_left,
                "bottomRight": legend_box_bottom_right,

            },
            "entries": legend_entries
        },
        "dataSeries": data_series,
        "gridLines": {
            "xMajor": {
                "visible": has_grid
            },
            "yMajor": {
                "visible": has_grid
            }
        }
    }
    
    return image, shapes_data, (width, height), annotation

def main():
    output_dir = "scatter_dataset"
    images_dir = os.path.join(output_dir, "images")
    annotations_dir = os.path.join(output_dir, "annotations")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(annotations_dir, exist_ok=True)
    
    print("仅供测试")
    
    for i in range(50):
        print(f"生成第 {i+1}/50 张图像...")
        
        try:
            image, shapes_data, image_size, annotation = generate_scatter_plot(i)
            image_path = os.path.join(images_dir, f"scatter_{i:04d}.png")
            cv2.imwrite(image_path, image)
            create_voc_xml(image_path, image_size, shapes_data)
            
            # 生成对应的 JSON 标注文件（与图像同名）
            json_path = os.path.join(annotations_dir, f"scatter_{i:04d}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                # 更紧凑的 JSON 排版：更少空格，便于减小文件体积
                json.dump(annotation, jf, ensure_ascii=False, indent=1, separators=(',', ':'))
        except Exception as e:
            print(f"生成第 {i+1} 张图像时出错: {e}")
            continue
    
    print("数据集生成完成！")

if __name__ == "__main__":
    main()