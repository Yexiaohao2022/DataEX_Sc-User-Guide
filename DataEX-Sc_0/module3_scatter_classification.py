# -*- coding: utf-8 -*-
"""
模块3：散点分类与像素级定位（合并原 module3_scatter_classification 与 module3_scatter_strategy_common）

1) 公共函数（供 strategy1/2/3 调用）：
   otherlegend_score2, search_space, select_pix, inbox1,
   eliminate_legend, eliminate_legend2, check_black_white_colors,
   remove_text_regions_advanced, process_coordinates

2) 模块入口（供 pipeline 调用）：
   run_module3_scatter_classification —— 按优先级调用 strategy1 -> strategy2 -> strategy3 -> strategy4。
"""

from typing import Dict, List, Optional, Tuple

import time
import json
import cv2
import numpy as np

try:
    import easyocr
except ImportError:
    easyocr = None


# ---------------------------------------------------------------------------
# 公共函数（原 module3_scatter_strategy_common）
# ---------------------------------------------------------------------------

def otherlegend_score2(x, y, bw, symbol, symbol_bw, rgb, flag, theta_c=30, w_shape=0.4):
    """
    给定中心点 (x,y)，与每个图例模板做形状+颜色匹配，返回 (最佳图例编号, 得分)。
    用于「分类」：判定该点属于哪个图例类型。
    theta_c: 图例模板与搜索区域颜色相近的阈值（像素差阈值，用于二值化）
    w_shape: 形状匹配分数权重，颜色权重为 (1 - w_shape)
    """
    sscores = np.zeros(len(symbol))
    cscores = np.zeros(len(symbol))
    scores = np.zeros(len(symbol))
    pad_bw = {}
    for k in range(len(symbol)):
        try:
            hs = symbol[k].shape[0]
            ws = symbol[k].shape[1]
            nfill = np.sum(symbol_bw[k])

            # 方式1
            start_y1 = int(round(y - hs / 2))
            end_y1 = start_y1 + hs
            start_x1 = int(round(x - ws / 2))
            end_x1 = start_x1 + ws
            pad_bw1 = bw[start_y1:end_y1, start_x1:end_x1]
            delta = ~(np.logical_xor(pad_bw1, symbol_bw[k]))
            mask1 = np.logical_and(delta, symbol_bw[k])
            nmatch = np.sum(mask1)
            sscore1 = nmatch / nfill
            nfill3_1 = np.sum(pad_bw1)
            sscore3 = nmatch / nfill3_1 if nfill3_1 != 0 else 0
            sscore_1 = min(sscore1, sscore3)

            # 方式2
            start_y2 = int(round(y - hs / 2)) + 1
            end_y2 = start_y2 + hs
            start_x2 = int(round(x - ws / 2)) + 1
            end_x2 = start_x2 + ws
            pad_bw2 = bw[start_y2:end_y2, start_x2:end_x2]
            delta = ~(np.logical_xor(pad_bw2, symbol_bw[k]))
            mask2 = np.logical_and(delta, symbol_bw[k])
            nmatch = np.sum(mask2)
            sscore2 = nmatch / nfill
            nfill3_2 = np.sum(pad_bw2)
            sscore4 = nmatch / nfill3_2 if nfill3_2 != 0 else 0
            sscore_2 = min(sscore2, sscore4)

            # 方式3
            start_y3 = int(round(y - hs / 2)) + 1
            end_y3 = start_y3 + hs
            start_x3 = int(round(x - ws / 2))
            end_x3 = start_x3 + ws
            pad_bw3 = bw[start_y3:end_y3, start_x3:end_x3]
            delta = ~(np.logical_xor(pad_bw3, symbol_bw[k]))
            mask3 = np.logical_and(delta, symbol_bw[k])
            nmatch = np.sum(mask3)
            sscore3_1 = nmatch / nfill
            nfill3_3 = np.sum(pad_bw3)
            sscore3_2 = nmatch / nfill3_3 if nfill3_3 != 0 else 0
            sscore_3 = min(sscore3_1, sscore3_2)

            # 方式4
            start_y4 = int(round(y - hs / 2))
            end_y4 = start_y4 + hs
            start_x4 = int(round(x - ws / 2)) + 1
            end_x4 = start_x4 + ws
            pad_bw4 = bw[start_y4:end_y4, start_x4:end_x4]
            delta = ~(np.logical_xor(pad_bw4, symbol_bw[k]))
            mask4 = np.logical_and(delta, symbol_bw[k])
            nmatch = np.sum(mask4)
            sscore4_1 = nmatch / nfill
            nfill3_4 = np.sum(pad_bw4)
            sscore4_2 = nmatch / nfill3_4 if nfill3_4 != 0 else 0
            sscore_4 = min(sscore4_1, sscore4_2)

            sscore = max(sscore_1, sscore_2, sscore_3, sscore_4)
            if sscore == sscore_1:
                pad_bw[k] = pad_bw1
                nfill_pad = nfill3_1
                mask = mask1
                pad = rgb[start_y1:end_y1, start_x1:end_x1, :3].astype(np.float64)
            elif sscore == sscore_2:
                pad_bw[k] = pad_bw2
                nfill_pad = nfill3_2
                mask = mask2
                pad = rgb[start_y2:end_y2, start_x2:end_x2, :3].astype(np.float64)
            elif sscore == sscore_3:
                pad_bw[k] = pad_bw3
                nfill_pad = nfill3_3
                mask = mask3
                pad = rgb[start_y3:end_y3, start_x3:end_x3, :3].astype(np.float64)
            else:
                pad_bw[k] = pad_bw4
                nfill_pad = nfill3_4
                mask = mask4
                pad = rgb[start_y4:end_y4, start_x4:end_x4, :3].astype(np.float64)

            if (np.sum(pad_bw[k]) > np.sum(symbol_bw[k]) + 10) and flag:
                sscore -= 0.1
            sscores[k] = sscore

            symbol_k = symbol[k].astype(np.float64)
            delta = np.abs(pad - symbol_k)
            delta[:, :, 0] += (~mask) * 255
            delta[:, :, 1] += (~mask) * 255
            delta[:, :, 2] += (~mask) * 255
            thre_colordev = theta_c
            delta[delta <= thre_colordev] = 1
            delta[delta > thre_colordev] = 0
            s1 = np.sum(delta, axis=2)
            s1[s1 < 3] = 0
            s1[s1 == 3] = 1
            cscore1 = np.sum(s1) / nfill
            cscore2 = np.sum(s1) / nfill_pad if nfill_pad != 0 else 0
            cscores[k] = min(cscore1, cscore2)
            if cscores[k] < 0.02:
                scores[k] = 0
            else:
                scores[k] = w_shape * sscores[k] + (1 - w_shape) * cscores[k]
        except Exception:
            scores[k] = 0
            continue

    number = np.argmax(scores)
    best_score = float(scores[number]) if number >= 0 and len(scores) > 0 else 0.0
    if scores[number] == 0:
        number = -1
        best_score = 0.0
    elif np.count_nonzero(scores == scores[number]) > 1:
        number = np.where(scores == scores[number])[0][0]
    if number >= 0 and (np.sum(pad_bw.get(number, [])) > np.sum(symbol_bw[number]) + 10) and flag:
        number = -1
        best_score = 0.0
    return number, best_score


def search_space(row0, col0, hs, ws, maxh, maxw, scale_factor=1.0):
    """
    由候选像素扩展出模板左上角搜索空间（在图像范围内的候选点）。
    scale_factor: 搜索窗口与图例模板尺寸的比率；窗口大小为 (hs*scale_factor, ws*scale_factor)。
    返回 (row_result, col_result)，调用方应按 (hs_eff, ws_eff) 切片。
    """
    hs_eff = max(1, int(round(hs * scale_factor)))
    ws_eff = max(1, int(round(ws * scale_factor)))
    np_ = len(row0)
    h2 = round(hs_eff / 2)
    w2 = round(ws_eff / 2)
    row, col = [], []
    for i in range(np_):
        r_start = row0[i] - h2
        r_end = row0[i] + h2 + 1
        c_start = col0[i] - w2
        c_end = col0[i] + w2 + 1
        for r in range(r_start, r_end):
            for c in range(c_start, c_end):
                row.append(r)
                col.append(c)
    if not row:
        return [], [], hs_eff, ws_eff
    id_coords = np.column_stack((np.array(col), np.array(row)))
    id_coords = np.unique(id_coords, axis=0)
    row_result = id_coords[:, 1]
    col_result = id_coords[:, 0]
    incl = np.where(
        (row_result >= 1) & (row_result <= maxh - hs_eff + 1) &
        (col_result >= 1) & (col_result <= maxw - ws_eff + 1)
    )[0]
    row_result = row_result[incl]
    col_result = col_result[incl]
    return row_result.tolist(), col_result.tolist(), hs_eff, ws_eff


def inbox1(point, box):
    """判断点是否在矩形 box=(x1,x2,y1,y2) 内。"""
    x, y = point
    x1, x2, y1, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def select_pix(row0, col0, incbox, excbox):
    """返回在 incbox 内且不在 excbox 内的像素 (row, col) 列表。"""
    row, col = [], []
    for j in range(len(row0)):
        flag_in = inbox1((col0[j], row0[j]), incbox)
        flag_ex = inbox1((col0[j], row0[j]), excbox)
        if flag_in and not flag_ex:
            row.append(row0[j])
            col.append(col0[j])
    return row, col


def eliminate_legend(data, i, symbol_bw, bw):
    """在二值图 bw 上把已识别图例 i 的匹配点区域涂成背景 0。"""
    hs = symbol_bw[i].shape[0]
    ws = symbol_bw[i].shape[1]
    try:
        for j in range(len(data[i])):
            x, y = data[i][j][0], data[i][j][1]
            if x * y > 0:
                y0 = round(y - hs / 2)
                x0 = round(x - ws / 2)
                bw[y0:y0 + hs, x0:x0 + ws] = 0
    except Exception:
        pass
    return bw


def eliminate_legend2(data2, symbol_bw, remain_bw_all):
    """对所有图例依次 eliminate_legend，得到再次消除后的剩余图。"""
    data, bw = data2, remain_bw_all
    remain_bw = {}
    for i in range(len(symbol_bw)):
        remain_bw[i] = eliminate_legend(data, i, symbol_bw, bw.copy())
        if i == 1:
            remain_bw_all = eliminate_legend(data, i, symbol_bw, remain_bw[i - 1].copy())
        elif i > 1:
            remain_bw_all = eliminate_legend(data, i, symbol_bw, remain_bw_all.copy())
    return remain_bw_all


def check_black_white_colors(symbol):
    """检测 symbol 中是否包含纯黑，用于决定是否走黑白/去文字分支。返回 1 表示含纯黑。"""
    for array in symbol:
        if np.any(np.all(array == [0, 0, 0], axis=2)):
            return 1
    return 0


def remove_text_regions_advanced(bw, background_value=0, confidence_threshold=0.3,
                                 dilation_kernel_size=3, show_debug=False):
    """用 EasyOCR 检测文字区域并置为背景。"""
    bw_ = bw.copy()
    if easyocr is None:
        return bw_
    try:
        reader = easyocr.Reader(['en'])
        if len(bw.shape) == 2:
            rgb_image = cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)
        else:
            rgb_image = bw
        results = reader.readtext(rgb_image)
        total_text_mask = np.zeros_like(bw, dtype=np.uint8)
        for (bbox, text, confidence) in results:
            if confidence < confidence_threshold:
                continue
            bbox = np.array(bbox, dtype=np.int32)
            mask = np.zeros_like(bw, dtype=np.uint8)
            cv2.fillPoly(mask, [bbox], 255)
            if dilation_kernel_size > 0:
                kernel = np.ones((dilation_kernel_size, dilation_kernel_size), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=1)
            total_text_mask = cv2.bitwise_or(total_text_mask, mask)
        bw_[total_text_mask > 0] = background_value
    except Exception:
        return bw.copy()
    return bw_


def process_coordinates(coords):
    """对坐标列表做邻近点合并：画点→膨胀→腐蚀→连通域→取质心。"""
    if not coords:
        return []
    valid_coords = [p for p in coords if isinstance(p, (list, tuple)) and len(p) == 2]
    if not valid_coords:
        return []
    try:
        max_x = max(p[0] for p in valid_coords) + 10
        max_y = max(p[1] for p in valid_coords) + 10
        img = np.zeros((max_y, max_x), dtype=np.uint8)
        for x, y in valid_coords:
            if x < max_x and y < max_y:
                img[y, x] = 255
        kernel = np.ones((3, 3), np.uint8)
        img_dilated = cv2.dilate(img, kernel, iterations=1)
        img_processed = cv2.erode(img_dilated, kernel, iterations=1)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            img_processed, connectivity=8)
        result = []
        for i in range(1, num_labels):
            cx, cy = centroids[i]
            result.append([int(round(cx)), int(round(cy))])
        return result
    except Exception:
        return valid_coords


# ---------------------------------------------------------------------------
# 模块3 入口与策略调度（调用 strategy1/2/3/4）
# ---------------------------------------------------------------------------

def _run_strategy1_yolo_region_template(
    shape_boxes: List[dict],
    rgb: np.ndarray,
    bw: np.ndarray,
    symbol: List,
    symbol_bw: List,
    color: List,
    theta_c: float = 30,
    w_shape: float = 0.4,
) -> Tuple[Optional[Dict[int, List[List[float]]]], List[List[float]]]:
    """
    策略1：在 YOLO 识别的散点候选区域内进行模板匹配。委托 strategy1 实现。
    返回 (data, candidate_positions)，candidate_positions 近似为所有 YOLO 检测框中心，
    作为后续策略4“由前3个策略传输的潜在像素区域”分支的输入之一。
    """
    candidate_positions: List[List[float]] = []
    for box in shape_boxes:
        c = box.get("center", [(box["box"][0] + box["box"][2]) / 2, (box["box"][1] + box["box"][3]) / 2])
        candidate_positions.append([float(c[0]), float(c[1])])
    try:
        from strategy1_connected_component_template import run_strategy1_yolo_region_template as _impl
        data = _impl(shape_boxes, rgb, bw, symbol, symbol_bw, color, theta_c=theta_c, w_shape=w_shape)
        return data, candidate_positions
    except Exception as e:
        print(f"策略1 导入失败: {e}")
        return None, candidate_positions


def _run_strategy2_global_template_scanning(
    rgb: np.ndarray,
    bw0: np.ndarray,
    symbol: List,
    symbol_bw: List,
    incbox: List[int],
    excbox: List[int],
    color: List,
    scale_factor: float = 1.0,
    theta_c: float = 30,
    w_shape: float = 0.4,
    w_a: float = 0.85,
) -> Tuple[Optional[Dict[int, List[List[float]]]], List[List[float]]]:
    """
    策略2：在坐标区域内进行全局模板匹配。委托 strategy2 实现。
    返回 (data, candidate_positions)，candidate_positions 近似为本策略输出的所有散点坐标，
    供策略4在“由前三策略传输的潜在像素区域”分支中使用。
    """
    candidate_positions: List[List[float]] = []
    try:
        from strategy2_template_scanning import run_template_scanning
        data = run_template_scanning(
            rgb, bw0, symbol, symbol_bw, incbox, excbox, color,
            scale_factor=scale_factor, theta_c=theta_c, w_shape=w_shape, w_a=w_a,
        )
        if data and sum(len(v) for v in data.values()) > 0:
            for pts in data.values():
                for x, y in pts:
                    candidate_positions.append([float(x), float(y)])
            return data, candidate_positions
    except Exception as e:
        print(f"策略2 失败: {e}")
    return None, candidate_positions


def _run_strategy3_yolo_in_scatter(
    image_rgb: np.ndarray,
    bw0: np.ndarray,
    shape_boxes: List[dict],
    symbol: List,
    symbol_bw: List,
    color: List,
    incbox: List[int],
    excbox: List[int],
    theta_c: float = 30,
    w_shape: float = 0.4,
) -> Tuple[Optional[Dict[int, List[List[float]]]], List[List[float]]]:
    """
    策略3：散点区域内 YOLO 检测 + 颜色分布纠正。委托 strategy3 实现。
    返回 (data, candidate_positions)，candidate_positions 为本策略输出的所有散点坐标，
    用于在策略4中走“由前三策略传输的潜在像素区域”分支。
    """
    try:
        from strategy3_yolo_in_scatter import run_yolo_in_scatter
    except Exception as e:
        print(f"策略3（YOLO in scatter）导入失败: {e}")
        return None, []

    if not shape_boxes:
        return None, []

    data, _ = run_yolo_in_scatter(
        rgb=image_rgb,
        bw=bw0,
        shape_boxes=shape_boxes,
        symbol=symbol if symbol else None,
        symbol_bw=symbol_bw if symbol_bw else None,
        color=color if color else None,
        bw_scatter=None,
        incbox=incbox,
        excbox=excbox,
        model_path="shape11_250827_best.pt",
        theta_c=theta_c,
        w_shape=w_shape,
    )

    if not data or sum(len(v) for v in data.values()) == 0:
        return None, []

    candidate_positions: List[List[float]] = []
    for pts in data.values():
        for x, y in pts:
            candidate_positions.append([float(x), float(y)])
    return data, candidate_positions


def _run_strategy4_kmeans_fallback(
    image_rgb: np.ndarray,
    pixel_positions: List[List[float]],
    n_clusters: int,
) -> Dict[int, List[List[float]]]:
    """策略4：K-Means 兜底聚类。委托 strategy4 实现。"""
    if not pixel_positions:
        return {}
    try:
        from strategy4_backup_yolo_smart_clustering import run_strategy4_kmeans_fallback as _impl
        return _impl(image_rgb, pixel_positions, n_clusters)
    except Exception as e:
        print(f"策略4 K-Means 兜底失败（全部归为单类）: {e}")
        return {0: list(pixel_positions)}


def run_module3_scatter_classification(
    image_rgb: np.ndarray,
    axis_boxes: List[dict],
    legend_boxes: List[dict],
    shape_boxes: List[dict],
    legend_result: Optional[dict],
    shape_info_in_legend: List[dict],
    symbol: List,
    symbol_bw: List,
    color: List,
    incbox: List[int],
    excbox: List[int],
    theta_s: float = 0.5,
    scale_factor: float = 1.0,
    theta_c: float = 30,
    w_shape: float = 0.4,
    w_a: float = 0.85,
    # 质量判定相关超参数（用于是否“接受当前策略”）
    min_points_s1: int = 3,
    min_points_s2: int = 3,
    min_points_s3: int = 3,
    force_strategy: Optional[int] = None,
) -> Dict[int, List[List[float]]]:
    """
    模块3 入口：多策略散点分类与像素定位。
    按顺序尝试：策略1（当 YOLO 典型时）-> 策略2 -> 策略3 -> 策略4。
    theta_s: 散点 YOLO 置信度阈值，>= 时认为典型才尝试策略1。
    force_strategy: 若为 1/2/3/4，则仅执行该策略（用于测试）；默认 None 表示自动按优先级尝试。
    返回 data: { class_id: [[x,y], ...] }（像素坐标）。
    额外在日志中打印各策略的尝试/点数/耗时等信息，便于做流水线级 A–I 分析。
    """
    h, w = image_rgb.shape[:2]
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    _, bw0 = cv2.threshold(gray, 0.8 * 255, 1, cv2.THRESH_BINARY_INV)
    n_classes = len(symbol) if symbol else 1

    shape_yolo_typical = False
    if shape_boxes:
        confs = [b.get("confidence", 0.0) for b in shape_boxes]
        mean_conf = sum(confs) / len(confs) if confs else 0.0
        shape_yolo_typical = mean_conf >= theta_s

    # 运行轨迹统计：记录每个策略是否被尝试、耗时与输出点数
    strategy_trace: Dict[str, Dict[str, float]] = {
        "s1": {"tried": 0, "accepted": 0, "n_points": 0, "elapsed": 0.0},
        "s2": {"tried": 0, "accepted": 0, "n_points": 0, "elapsed": 0.0},
        "s3": {"tried": 0, "accepted": 0, "n_points": 0, "elapsed": 0.0},
        "s4": {"tried": 0, "accepted": 0, "n_points": 0, "elapsed": 0.0},
    }

    def _count_points(data: Optional[Dict[int, List[List[float]]]]) -> int:
        if not data:
            return 0
        return int(sum(len(v) for v in data.values()))

    def run_only_1():
        strategy_trace["s1"]["tried"] = 1
        if not (symbol and shape_boxes and shape_yolo_typical):
            return {}, []
        t0 = time.perf_counter()
        data, cand = _run_strategy1_yolo_region_template(
            shape_boxes, image_rgb, bw0, symbol, symbol_bw, color,
            theta_c=theta_c, w_shape=w_shape,
        )
        elapsed = time.perf_counter() - t0
        n_pts = _count_points(data)
        strategy_trace["s1"]["elapsed"] = float(elapsed)
        strategy_trace["s1"]["n_points"] = float(n_pts)
        return data, cand

    def run_only_2():
        strategy_trace["s2"]["tried"] = 1
        if not symbol:
            return {}, []
        t0 = time.perf_counter()
        data, cand = _run_strategy2_global_template_scanning(
            image_rgb, bw0, symbol, symbol_bw, incbox, excbox, color,
            scale_factor=scale_factor, theta_c=theta_c, w_shape=w_shape, w_a=w_a,
        )
        elapsed = time.perf_counter() - t0
        n_pts = _count_points(data)
        strategy_trace["s2"]["elapsed"] = float(elapsed)
        strategy_trace["s2"]["n_points"] = float(n_pts)
        return data, cand

    def run_only_3():
        strategy_trace["s3"]["tried"] = 1
        t0 = time.perf_counter()
        data, cand = _run_strategy3_yolo_in_scatter(
            image_rgb=image_rgb,
            bw0=bw0,
            shape_boxes=shape_boxes,
            symbol=symbol,
            symbol_bw=symbol_bw,
            color=color,
            incbox=incbox,
            excbox=excbox,
            theta_c=theta_c,
            w_shape=w_shape,
        )
        elapsed = time.perf_counter() - t0
        n_pts = _count_points(data)
        strategy_trace["s3"]["elapsed"] = float(elapsed)
        strategy_trace["s3"]["n_points"] = float(n_pts)
        return data, cand

    def run_only_4(candidate_positions: Optional[List[List[float]]] = None):
        # 分支1：若前三个策略传入了潜在散点坐标，则优先对这些坐标做聚类
        strategy_trace["s4"]["tried"] = 1
        t0 = time.perf_counter()
        if candidate_positions:
            data = _run_strategy4_kmeans_fallback(image_rgb, candidate_positions, n_clusters=n_classes)
            elapsed = time.perf_counter() - t0
            n_pts = _count_points(data)
            strategy_trace["s4"]["elapsed"] = float(elapsed)
            strategy_trace["s4"]["n_points"] = float(n_pts)
            return data
        # 分支2：否则退化为仅基于 YOLO 检测框中心的聚类
        all_positions: List[List[float]] = []
        for box in shape_boxes:
            c = box.get("center", [(box["box"][0] + box["box"][2]) / 2, (box["box"][1] + box["box"][3]) / 2])
            all_positions.append([float(c[0]), float(c[1])])
        if not all_positions:
            return {}
        data = _run_strategy4_kmeans_fallback(image_rgb, all_positions, n_clusters=n_classes)
        elapsed = time.perf_counter() - t0
        n_pts = _count_points(data)
        strategy_trace["s4"]["elapsed"] = float(elapsed)
        strategy_trace["s4"]["n_points"] = float(n_pts)
        return data

    if force_strategy is not None:
        if force_strategy == 1:
            data, _ = run_only_1()
            if _count_points(data) >= min_points_s1:
                strategy_trace["s1"]["accepted"] = 1
                print("模块3 [强制策略1] 使用策略1（YOLO 区域 + 模板匹配）完成。")
            print("模块3 [强制策略1] 运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data if data else {}
        if force_strategy == 2:
            data, _ = run_only_2()
            if _count_points(data) >= min_points_s2:
                strategy_trace["s2"]["accepted"] = 1
                print("模块3 [强制策略2] 使用策略2（全局模板匹配）完成。")
            print("模块3 [强制策略2] 运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data if data else {}
        if force_strategy == 3:
            data, _ = run_only_3()
            if _count_points(data) >= min_points_s3:
                strategy_trace["s3"]["accepted"] = 1
                print("模块3 [强制策略3] 使用策略3（YOLO in scatter + 颜色纠正）完成。")
            print("模块3 [强制策略3] 运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data if data else {}
        if force_strategy == 4:
            data = run_only_4()
            if _count_points(data) > 0:
                strategy_trace["s4"]["accepted"] = 1
                print("模块3 [强制策略4] 使用策略4（K-Means 无监督聚类）完成。")
            print("模块3 [强制策略4] 运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data

    # 记录前三策略“潜在散点坐标”，供策略4在需要时聚类
    candidate_positions_from_strategies: List[List[float]] = []

    # 策略1
    if symbol and shape_boxes and shape_yolo_typical:
        data, cand1 = run_only_1()
        n_pts = _count_points(data)
        candidate_positions_from_strategies.extend(cand1)
        if n_pts >= min_points_s1:
            strategy_trace["s1"]["accepted"] = 1
            print("模块3 使用策略1（YOLO 区域 + 模板匹配）完成。")
            print("模块3 自动模式运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data

    # 策略2
    if symbol:
        data, cand2 = run_only_2()
        n_pts = _count_points(data)
        candidate_positions_from_strategies.extend(cand2)
        if n_pts >= min_points_s2:
            strategy_trace["s2"]["accepted"] = 1
            print("模块3 使用策略2（全局模板匹配）完成。")
            print("模块3 自动模式运行轨迹:",
                  json.dumps(strategy_trace, ensure_ascii=False))
            return data

    # 策略3
    data, cand3 = run_only_3()
    n_pts = _count_points(data)
    candidate_positions_from_strategies.extend(cand3)
    if n_pts >= min_points_s3:
        strategy_trace["s3"]["accepted"] = 1
        print("模块3 使用策略3（YOLO in scatter + 颜色纠正）完成。")
        print("模块3 自动模式运行轨迹:",
              json.dumps(strategy_trace, ensure_ascii=False))
        return data

    # 策略4
    # 若前三策略传回了潜在散点坐标，则优先对这些点做 K-Means 聚类；
    # 否则退化为仅基于 YOLO 检测框中心的聚类。
    unique_candidates = []
    if candidate_positions_from_strategies:
        seen = set()
        for x, y in candidate_positions_from_strategies:
            key = (float(x), float(y))
            if key not in seen:
                seen.add(key)
                unique_candidates.append([float(x), float(y)])

    data = run_only_4(candidate_positions=unique_candidates if unique_candidates else None)
    if _count_points(data) > 0:
        strategy_trace["s4"]["accepted"] = 1
    print("模块3 使用策略4（K-Means 无监督聚类）完成。")
    print("模块3 自动模式运行轨迹:",
          json.dumps(strategy_trace, ensure_ascii=False))
    return data
