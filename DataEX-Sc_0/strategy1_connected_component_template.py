# -*- coding: utf-8 -*-
"""
策略1：YOLO 区域 + 模板匹配（根据论文描述版本）

触发条件由流水线控制：当图例已检测且散点 YOLO（shape 模型）对“scatter”类的平均置信度
大于给定阈值 θs 时，认为散点符号“典型”，在 YOLO 识别的散点候选区域内进行模板匹配。

实现要点：
    - 输入：模块1输出的散点候选框 shape_boxes，模块2分析得到的图例模板 symbol/symbol_bw 及颜色 color；
    - 对每个 YOLO 检测框中心像素 (cx, cy)，用 otherlegend_score2 在 bw/symbol 上做形状+颜色匹配；
    - 将 best-match 的模板编号作为该点的类别，并输出按图例索引分组的像素坐标。

与原先“连通域+模板”版本不同，本文件不再做颜色筛选和连通域，而是专注于
“在 YOLO 提供的搜索窗口内用模板修正 YOLO 的识别结果”，以减少模板匹配的位置数量。
"""

import time
import numpy as np
from module3_scatter_classification import otherlegend_score2


def _run_strategy1_yolo_region_template_impl(
    shape_boxes,
    rgb,
    bw,
    symbol,
    symbol_bw,
    color,
    theta_c: float = 30,
    w_shape: float = 0.4,
):
    """
    策略1：在 YOLO 识别的散点候选区域内进行模板匹配。

    参数:
        shape_boxes: 模块1 YOLO 对散点的候选检测框列表（含 box=[x1,y1,x2,y2]）
        rgb: 原图 RGB
        bw: 用于模板匹配的二值图
        symbol, symbol_bw: 图例模板(RGB与二值)
        color: 图例代表色列表
        theta_c: 颜色相近阈值(传递给 otherlegend_score2)
        w_shape: 形状匹配权重

    返回:
        data: dict, data[class_id] = [[x,y], ...]，class_id 为图例模板索引
        若 symbol 或 shape_boxes 为空, 或无任何匹配, 返回 None。
    """
    if not symbol or not shape_boxes:
        return None
    data = {i: [] for i in range(len(symbol))}
    for box in shape_boxes:
        x1, y1, x2, y2 = box["box"][0], box["box"][1], box["box"][2], box["box"][3]
        cx = int(round((x1 + x2) / 2))
        cy = int(round((y1 + y2) / 2))
        match, _ = otherlegend_score2(
            cx,
            cy,
            bw,
            symbol,
            symbol_bw,
            rgb,
            1,
            theta_c=theta_c,
            w_shape=w_shape,
        )
        if 0 <= match < len(symbol):
            data[match].append([float(cx), float(cy)])
    total = sum(len(v) for v in data.values())
    if total == 0:
        return None
    return data


def run_strategy1_yolo_region_template(
    shape_boxes,
    rgb,
    bw,
    symbol,
    symbol_bw,
    color,
    theta_c: float = 30,
    w_shape: float = 0.4,
):
    """
    包装原始策略1入口函数，增加运行时间统计。
    """
    start = time.perf_counter()
    result = _run_strategy1_yolo_region_template_impl(
        shape_boxes,
        rgb,
        bw,
        symbol,
        symbol_bw,
        color,
        theta_c=theta_c,
        w_shape=w_shape,
    )
    elapsed = time.perf_counter() - start
    print(f"策略1（YOLO 区域 + 模板匹配）耗时: {elapsed:.3f} 秒")
    return result

