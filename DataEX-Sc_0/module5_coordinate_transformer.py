import numpy as np
from typing import Tuple, Optional, Dict, List, Any


def pixel_to_physical(
    pixel_x: float,
    pixel_y: float,
    calibration: Dict[str, Any],
) -> Tuple[Optional[float], Optional[float]]:
    """
    根据 calibration 将像素 (pixel_x, pixel_y) 转换为物理 (x, y)。

    calibration 结构示例：
    {
        "x_anchors": [{"point": {"x": px, "y": py}, "value": v}, ...],
        "y_anchors": [...],
        "x_log_scale": bool,
        "y_log_scale": bool,
    }
    """
    x_anchors = calibration.get("x_anchors", [])
    y_anchors = calibration.get("y_anchors", [])
    x_log = calibration.get("x_log_scale", False)
    y_log = calibration.get("y_log_scale", False)
    if len(x_anchors) < 2 or len(y_anchors) < 2:
        return None, None

    px = np.array([a["point"]["x"] for a in x_anchors], dtype=np.float64)
    vx = np.array([a["value"] for a in x_anchors], dtype=np.float64)
    py = np.array([a["point"]["y"] for a in y_anchors], dtype=np.float64)
    vy = np.array([a["value"] for a in y_anchors], dtype=np.float64)

    if x_log and np.any(vx <= 0):
        vx = np.where(vx > 0, np.log10(vx), 0)
    if y_log and np.any(vy <= 0):
        vy = np.where(vy > 0, np.log10(vy), 0)

    cx = np.polyfit(px, vx, 1)
    cy = np.polyfit(py, vy, 1)

    data_x = cx[0] * pixel_x + cx[1]
    data_y = cy[0] * pixel_y + cy[1]

    if x_log:
        data_x = 10 ** data_x
    if y_log:
        data_y = 10 ** data_y

    return float(data_x), float(data_y)


def run_module5_physical_coordinates(
    data_pixel: Dict[int, List[List[float]]],
    calibration: Dict[str, Any],
) -> Dict[int, List[List[float]]]:
    """
    将各类散点的像素坐标转换为物理坐标。

    data_pixel: { class_id: [[x,y], ...] }（像素）
    calibration: 由模块4生成的刻度/映射信息（见 pixel_to_physical 的说明）
    """
    result: Dict[int, List[List[float]]] = {}
    for cls, points in data_pixel.items():
        result[cls] = []
        for (px, py) in points:
            dx, dy = pixel_to_physical(px, py, calibration)
            if dx is not None and dy is not None:
                result[cls].append([dx, dy])
    return result