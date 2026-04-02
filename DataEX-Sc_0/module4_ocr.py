"""
模块4（离线版）：坐标轴刻度识别与类型识别

功能：在坐标轴附近用 easyocr 识别刻度文字，解析为数值锚点，
并返回给模块5使用的 calibration 结构。

特性：
- 纯离线函数，不依赖 FastAPI / 路由 / 数据库；
- 不包含“智能锚点检测”等在线增强逻辑；
- 若 easyocr 未安装或刻度识别失败，会退回到简单的几何默认标定。
"""

from typing import Dict, Any, List, Optional

import numpy as np

try:
    import easyocr
except ImportError:
    easyocr = None


def _parse_numeric_text(text: str) -> Optional[float]:
    """将 OCR 文本尽量解析为数值，解析失败返回 None。"""
    if not text:
        return None
    import re

    t = text.strip()
    # 去掉非数字/小数点/符号/科学计数法字符
    cleaned = re.sub(r"[^\d\.\-\+eE]", "", t)
    if not cleaned or all(ch in ".-+eE" for ch in cleaned):
        return None
    try:
        return float(cleaned)
    except Exception:
        # 兜底：提取第一个连续数字片段
        nums = re.findall(r"\d+\.?\d*", cleaned)
        if not nums:
            return None
        try:
            return float(nums[0])
        except Exception:
            return None


def run_module4_axis_scale_recognition(
    image_rgb: np.ndarray,
    axis_boxes: List[Dict],
) -> Dict[str, Any]:
    """
    建立像素到数值的映射基准（离线函数版，供 pipeline_scatter_extraction 调用）。

    逻辑：
    - 首选：使用 easyocr 在坐标轴附近识别刻度文字，解析成数值锚点；
    - 失败或锚点不足时：退回几何默认规则（0~1 线性标度）。

    返回 calibration 结构，供模块5使用：
    {
        "x_anchors": [{"point": {"x": px, "y": py}, "value": v}, ...],
        "y_anchors": [...],
        "x_log_scale": bool,
        "y_log_scale": bool,
    }
    """
    h, w = image_rgb.shape[:2]

    def _default_calibration() -> Dict[str, Any]:
        """几何默认映射规则：根据轴框或整图构造 0~1 线性标度。"""
        cal: Dict[str, Any] = {
            "x_anchors": [],
            "y_anchors": [],
            "x_log_scale": False,
            "y_log_scale": False,
        }
        if not axis_boxes:
            # 没有显式轴框时，按整图对角线构造简单 0~1 映射
            cal["x_anchors"] = [
                {"point": {"x": 0, "y": h}, "value": 0.0},
                {"point": {"x": w, "y": h}, "value": 1.0},
            ]
            cal["y_anchors"] = [
                {"point": {"x": 0, "y": h}, "value": 0.0},
                {"point": {"x": 0, "y": 0}, "value": 1.0},
            ]
        else:
            # 使用第一个轴框近似主坐标区域
            b = axis_boxes[0]["box"]
            x1, y1, x2, y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            cal["x_anchors"] = [
                {"point": {"x": x1, "y": y2}, "value": 0.0},
                {"point": {"x": x2, "y": y2}, "value": 1.0},
            ]
            cal["y_anchors"] = [
                {"point": {"x": x1, "y": y2}, "value": 0.0},
                {"point": {"x": x1, "y": y1}, "value": 1.0},
            ]
        return cal

    # 如果 easyocr 不可用，直接退回默认映射
    if easyocr is None:
        print("模块4: easyocr 未安装，使用几何默认映射。")
        return _default_calibration()

    # 如果 YOLO 给出了轴框，就围绕轴框构造 OCR 搜索区域；否则使用整图近似
    if axis_boxes:
        b = axis_boxes[0]["box"]
        ax_x1, ax_y1, ax_x2, ax_y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
    else:
        ax_x1, ax_y1, ax_x2, ax_y2 = 0, 0, w, h

    # X 轴刻度一般紧贴坐标系底部，可能略高于或略低于轴框底边：
    # 为了兼容不同绘图风格，这里取轴框底边上下各一小段带状区域。
    x_band_above = int(0.10 * h)
    x_band_below = int(0.05 * h)
    x_region = {
        "x1": max(0, ax_x1),
        "y1": max(0, ax_y2 - x_band_above),
        "x2": min(w, ax_x2),
        "y2": min(h, ax_y2 + x_band_below),
    }
    # Y 轴刻度一般在左侧附近
    y_region = {
        "x1": max(0, ax_x1 - int(0.2 * w)),
        "y1": max(0, ax_y1),
        "x2": max(0, ax_x1),
        "y2": min(h, ax_y2),
    }

    # 初始化 easyocr
    # 语言列表和 GPU 配置可以按需调整，目前设为 CPU，支持英文和简体中文
    reader = easyocr.Reader(["en", "ch_sim"], gpu=False)

    def _detect_axis_labels(region: Dict[str, int], axis_type: str) -> List[Dict[str, Any]]:
        """
        在给定矩形区域内用 easyocr 检测文本，并解析为数值锚点：
        返回 [{"x": cx, "y": cy, "value": v, "label": 原始文本, "confidence": conf}, ...]
        """
        x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            return []

        crop = image_rgb[y1:y2, x1:x2]
        try:
            results = reader.readtext(crop)
        except Exception as e:
            print(f"模块4: easyocr 识别 {axis_type} 轴区域失败: {e}")
            return []

        labels: List[Dict[str, Any]] = []
        for bbox, text, conf in results:
            # 简单过滤低置信度与非数值文本
            if conf < 0.3:
                continue
            value = _parse_numeric_text(text)
            if value is None:
                continue

            pts = np.array(bbox, dtype=np.float64)
            cx = float(pts[:, 0].mean()) + x1
            cy = float(pts[:, 1].mean()) + y1
            labels.append(
                {
                    "x": cx,
                    "y": cy,
                    "value": float(value),
                    "label": text,
                    "confidence": float(conf),
                }
            )
        return labels

    # 在轴附近自动检测锚点（仅基于 easyocr）
    x_labels = _detect_axis_labels(x_region, "x")
    y_labels = _detect_axis_labels(y_region, "y")

    # 调试信息：打印第一次检测到的锚点数量
    print(
        f"模块4: 轴框附近 OCR 检测到 X 轴锚点 {len(x_labels)} 个, "
        f"Y 轴锚点 {len(y_labels)} 个。"
    )

    # 如果轴框附近锚点数量不足，尝试“全局底部/左侧带状区域”作为兜底
    if len(x_labels) < 2 or len(y_labels) < 2:
        print("模块4: 轴框附近锚点不足，尝试全局底部/左侧区域。")

        # 全局 X 轴候选区域：整幅图像底部一条带状区域
        global_x_region = {
            "x1": 0,
            "y1": int(h * 0.80),
            "x2": w,
            "y2": h,
        }
        # 全局 Y 轴候选区域：整幅图像左侧一条带状区域
        global_y_region = {
            "x1": 0,
            "y1": 0,
            "x2": int(w * 0.25),
            "y2": h,
        }

        global_x_labels = _detect_axis_labels(global_x_region, "x-global")
        global_y_labels = _detect_axis_labels(global_y_region, "y-global")

        print(
            f"模块4: 全局区域 OCR 检测到 X 轴锚点 {len(global_x_labels)} 个, "
            f"Y 轴锚点 {len(global_y_labels)} 个。"
        )

        # 若全局区域检测更好，则采用全局结果替换原结果
        if len(global_x_labels) >= 2:
            x_labels = global_x_labels
        if len(global_y_labels) >= 2:
            y_labels = global_y_labels

    # 若任一方向锚点仍少于 2 个，则退回默认几何标定
    if len(x_labels) < 2 or len(y_labels) < 2:
        print("模块4: OCR 锚点数量仍不足，使用几何默认映射。")
        return _default_calibration()

    # 按几何位置排序后构造 calibration
    x_labels_sorted = sorted(x_labels, key=lambda d: d["x"])
    y_labels_sorted = sorted(y_labels, key=lambda d: d["y"])

    calibration: Dict[str, Any] = {
        "x_anchors": [
            {"point": {"x": float(d["x"]), "y": float(d["y"])}, "value": float(d["value"])}
            for d in x_labels_sorted
        ],
        "y_anchors": [
            {"point": {"x": float(d["x"]), "y": float(d["y"])}, "value": float(d["value"])}
            for d in y_labels_sorted
        ],
        "x_log_scale": False,
        "y_log_scale": False,
    }

    return calibration

