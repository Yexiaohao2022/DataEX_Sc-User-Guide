#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略3：散点区域内 YOLO 检测 + 颜色分布纠正的模板/类别匹配

根据论文描述，本策略满足：
1. 对图例区域是否存在不作强制要求；无图例模板时也可直接执行。
2. 仅在 III A 策略1 与 III B 策略2 均未成功完成分类时激活（由主流水线控制）。
3. 当存在图例模板时，在 I 模块（YOLO）与 III B 策略2（若成功）的分类/定位结果基础上，
   利用每个搜索窗口（YOLO 检测框）内的颜色分布，重新调用模板匹配，对前序分类进行纠正/细化。
4. 当不存在模板信息，且散点符号超出 YOLO 训练集合时，仅能依赖 YOLO 原始类别，整体精度会下降。

实现要点：
- 定位：在「仅散点」二值图对应的 RGB 图（散点位置为原图颜色、其余白）上，用 YOLO 检测散点框，框中心记为候选位置。
- 有模板(symbol)时：对每个检测框中心调用 otherlegend_score2，并在窗口内计算与图例代表色的颜色接近度，
  以综合分数（模板形状+颜色分布）纠正/更新前序分类结果。
- 无模板时：仅返回 YOLO 给出的中心点，利用颜色信息对 YOLO 分类结果做了一次后验修正。
"""

import numpy as np
from module3_scatter_classification import otherlegend_score2

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


def _build_scatter_roi_from_bw(bw_scatter: np.ndarray, rgb: np.ndarray) -> np.ndarray:
    """
    根据 bw_scatter 构造用于 YOLO 的中间 RGB 图：散点位置保留原图颜色，其余置白。
    """
    h, w = bw_scatter.shape[:2]
    intermediate_image = np.full((h, w, 3), 255, dtype=np.uint8)
    mask = (bw_scatter == 1)
    intermediate_image[mask] = rgb[mask]
    return intermediate_image


def _infer_bw_scatter_from_boxes(
    shape_boxes,
    image_shape,
    incbox=None,
    excbox=None,
) -> np.ndarray:
    """
    在缺乏显式 bw_scatter 时，根据 YOLO 检测框近似构造一个候选散点前景掩码。
    - incbox / excbox 可选：若给出，仅在坐标轴区域内且不在图例框内的检测框被视为散点。
    """
    h, w = image_shape[:2]
    bw_scatter = np.zeros((h, w), dtype=np.uint8)
    if not shape_boxes:
        return bw_scatter
    for box in shape_boxes:
        x1, y1, x2, y2 = [int(box["box"][i]) for i in range(4)]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            continue
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        if incbox is not None:
            if not (incbox[0] <= cx <= incbox[1] and incbox[2] <= cy <= incbox[3]):
                continue
        if excbox is not None and not (excbox == [0, 0, 0, 0]):
            if excbox[0] <= cx <= excbox[1] and excbox[2] <= cy <= excbox[3]:
                continue
        bw_scatter[y1:y2, x1:x2] = 1
    return bw_scatter


def run_yolo_in_scatter(
    rgb,
    bw,
    shape_boxes,
    symbol=None,
    symbol_bw=None,
    color=None,
    bw_scatter=None,
    incbox=None,
    excbox=None,
    model_path: str = "shape11_250827_best.pt",
    theta_c: float = 30,
    w_shape: float = 0.4,
):
    """
    策略3 入口：在散点区域（bw_scatter 或由 YOLO 框推断）内用 YOLO 检测框，
    再结合模板/颜色分布对前序结果进行纠正或直接分类。

    参数:
        rgb: 原图 RGB
        bw: 原二值图（用于 otherlegend_score2 取块）
        shape_boxes: 模块1 YOLO 对散点的候选检测框列表
        symbol, symbol_bw, color: 图例模板与颜色（可为 None/空列表）
        bw_scatter: 可选的“仅散点”二值掩码；若为 None，则由 shape_boxes 推断
        incbox, excbox: 可选的坐标轴/图例范围，用于推断 bw_scatter
        model_path: YOLO 权重路径
        theta_c, w_shape: 传递给 otherlegend_score2 的颜色阈值与形状权重

    返回:
        data: dict
            - 若存在模板：data[l] = [[x,y], ...] 属于图例 l 的散点中心
            - 若不存在模板：data[class_id] = [[x,y], ...]，class_id 为 YOLO 原始类别
        bw_scatter_updated: 将已匹配到的框内像素置为背景后的 bw_scatter（可用于后续消除）
    """
    if not shape_boxes:
        return {}, np.zeros_like(bw, dtype=np.uint8)

    has_symbol = bool(symbol) and bool(symbol_bw)
    if has_symbol:
        n_classes = len(symbol)
        data = {i: [] for i in range(n_classes)}
    else:
        data = {}

    if bw_scatter is None:
        bw_scatter = _infer_bw_scatter_from_boxes(shape_boxes, rgb.shape, incbox=incbox, excbox=excbox)
    bw_scatter_updated = bw_scatter.copy()

    if not YOLO_AVAILABLE:
        # 无 YOLO 库时退化：直接用 shape_boxes 中心作为结果
        for box in shape_boxes:
            x1, y1, x2, y2 = [box["box"][i] for i in range(4)]
            cx = float((x1 + x2) / 2.0)
            cy = float((y1 + y2) / 2.0)
            if has_symbol:
                # 有模板但无法细分时，这里选择丢弃，避免误导精度
                continue
            else:
                cls_id = int(box.get("class", 0))
                if cls_id not in data:
                    data[cls_id] = []
                data[cls_id].append([cx, cy])
        return data, bw_scatter_updated

    try:
        shape_model = YOLO(model_path)
        intermediate_image = _build_scatter_roi_from_bw(bw_scatter, rgb)
        shape_results = shape_model(intermediate_image)
        h, w_img = bw_scatter.shape[:2]

        # 无模板时，也会使用颜色信息对 YOLO 原始分类结果做一次基于颜色分布的校准：
        # 1）先记录每个检测框的 YOLO 类别与该框内的平均颜色；
        # 2）再根据各类别的平均颜色，将每个检测框重新分配到“颜色最接近”的类别。
        raw_detections = []  # 仅在 has_symbol 为 False 时使用

        for result in shape_results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                center_x = int(round((x1 + x2) / 2))
                center_y = int(round((y1 + y2) / 2))
                center_x = max(0, min(center_x, w_img - 1))
                center_y = max(0, min(center_y, h - 1))

                if has_symbol:
                    otherlegend_score2_flag = 1
                    matchlegend, template_score = otherlegend_score2(
                        center_x, center_y, bw, symbol, symbol_bw, rgb, otherlegend_score2_flag,
                        theta_c=theta_c, w_shape=w_shape,
                    )
                    if matchlegend < 0 or matchlegend >= n_classes:
                        continue
                    legend_color = np.array(color[matchlegend][0], dtype=np.float64) if color else None
                    if legend_color is not None:
                        patch = rgb[max(0, y1):min(h, y2), max(0, x1):min(w_img, x2), :3].astype(np.float64)
                        if patch.size == 0:
                            color_score = 0.0
                        else:
                            diff = np.abs(patch - legend_color.reshape(1, 1, 3))
                            color_dist = np.mean(diff)
                            color_score = 1.0 - min(1.0, color_dist / 255.0)
                    else:
                        color_score = 0.0
                    combined = (1.0 - w_shape) * color_score + w_shape * template_score
                    if combined <= 0:
                        continue
                    data[matchlegend].append([float(center_x), float(center_y)])
                else:
                    # 无模板：先按 YOLO 原始类别分组，同时记录颜色信息，之后再用颜色分布做一次校准
                    cls_id = int(box.cls[0].cpu().numpy()) if hasattr(box, "cls") else 0
                    patch = rgb[max(0, y1):min(h, y2), max(0, x1):min(w_img, x2), :3]
                    if patch.size == 0:
                        mean_color = None
                    else:
                        mean_color = patch.reshape(-1, 3).mean(axis=0)
                    raw_detections.append(
                        {
                            "x": float(center_x),
                            "y": float(center_y),
                            "cls": cls_id,
                            "color": mean_color,
                        }
                    )

                r_coords = np.arange(bw_scatter.shape[0])
                c_coords = np.arange(bw_scatter.shape[1])
                rr, cc = np.meshgrid(r_coords, c_coords, indexing="ij")
                inside = (rr >= y1) & (rr < y2) & (cc >= x1) & (cc < x2)
                bw_scatter_updated[inside] = 0

        # 若无模板，则用颜色信息对 YOLO 原始类别做一次后验校准
        if not has_symbol and raw_detections:
            # 1. 以 YOLO 原始类别为初始分组，估计每一类的平均颜色
            class_colors = {}
            for det in raw_detections:
                if det["color"] is None:
                    continue
                cls_id = det["cls"]
                if cls_id not in class_colors:
                    class_colors[cls_id] = []
                class_colors[cls_id].append(det["color"])
            class_means = {}
            for cls_id, colors in class_colors.items():
                if not colors:
                    continue
                class_means[cls_id] = np.mean(np.vstack(colors), axis=0)

            # 2. 对每个检测框，根据其颜色与各类平均颜色的距离，选择最近的类别
            #    若某些类没有颜色统计，则保持其原 YOLO 类别不变。
            data = {}
            for det in raw_detections:
                cx, cy, cls_id, color_vec = det["x"], det["y"], det["cls"], det["color"]
                if color_vec is None or not class_means:
                    final_cls = cls_id
                else:
                    best_cls = cls_id
                    best_dist = float("inf")
                    for cid, mean_col in class_means.items():
                        d = float(np.linalg.norm(color_vec - mean_col))
                        if d < best_dist:
                            best_dist = d
                            best_cls = cid
                    final_cls = best_cls
                if final_cls not in data:
                    data[final_cls] = []
                data[final_cls].append([cx, cy])
    except Exception:
        pass

    return data, bw_scatter_updated
