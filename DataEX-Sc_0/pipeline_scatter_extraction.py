# -*- coding: utf-8 -*-
"""
散点图提取流水线：按五模块固定流程提取散点的分类与真实坐标

流程：
  1. 关键视觉元素检测（YOLO）
  2. 图例特征分析与提取（构建分类模板）
  3. 散点分类与像素级定位（多策略，按优先级依次执行）
  4. 坐标轴刻度识别与类型识别（像素-数值映射）
  5. 物理坐标计算
"""

import os
import sys
import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np
from module3_scatter_classification import run_module3_scatter_classification
from module4_ocr import run_module4_axis_scale_recognition as run_module4_axis_scale_recognition_external
from module5_coordinate_transformer import run_module5_physical_coordinates as run_module5_physical_coordinates_external

# ---------------------------------------------------------------------------
# 模块1：关键视觉元素检测（YOLO）
# ---------------------------------------------------------------------------

def run_module1_yolo_detection(
    image_path: str,
    axis_model_path: str = "axis250821.pt",
    legendbox_model_path: str = "legendbox_best250821.pt",
    shape_model_path: str = "shape11_250827_best.pt",
    device: str = "cpu",
    conf: float = 0.5,
) -> Tuple[List[Dict], List[Dict], List[Dict], np.ndarray]:
    """
    建立图像结构的整体理解：检测坐标轴、图例框、散点候选框。
    返回: axis_boxes, legend_boxes, shape_boxes, image_bgr
    """
    from module1_yolo_service import YOLOService

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        raise FileNotFoundError(f"无法读取图像: {image_path}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    axis_boxes = []
    legend_boxes = []
    shape_boxes = []

    async def _detect():
        axis_svc = YOLOService(axis_model_path, device=device)
        legend_svc = YOLOService(legendbox_model_path, device=device)
        shape_svc = YOLOService(shape_model_path, device=device)
        ax = await axis_svc.detect_image(image_bgr, confidence_threshold=conf)
        lg = await legend_svc.detect_image(image_bgr, confidence_threshold=conf)
        sh = await shape_svc.detect_image(image_bgr, confidence_threshold=conf)
        return ax, lg, sh

    try:
        ax, lg, sh = asyncio.run(_detect())
    except Exception as e:
        print(f"YOLO 检测异常（将使用空框）: {e}")
        ax, lg, sh = [], [], []

    for d in ax:
        axis_boxes.append({"box": [d["x1"], d["y1"], d["x2"], d["y2"]], **d})
    for d in lg:
        legend_boxes.append({"box": [d["x1"], d["y1"], d["x2"], d["y2"]], **d})
    for d in sh:
        shape_boxes.append({
            "box": [d["x1"], d["y1"], d["x2"], d["y2"]],
            "center": [(d["x1"] + d["x2"]) / 2, (d["y1"] + d["y2"]) / 2],
            "class": d["class"],
            **d
        })

    return axis_boxes, legend_boxes, shape_boxes, image_bgr


# ---------------------------------------------------------------------------
# 模块2：图例特征分析与提取（构建散点分类模板）
# ---------------------------------------------------------------------------

def run_module2_legend_analysis(
    image_path: str,
    image_rgb: np.ndarray,
    legend_box_info: Dict,
    shape_info: List[Dict],
) -> Optional[Dict]:
    """构建散点分类的模板。"""
    from module2_legend_feature_analyzer import LegendFeatureAnalyzer
    analyzer = LegendFeatureAnalyzer()
    return analyzer.analyze_legend_features(
        image_path,
        legend_box_info,
        shape_info,
        image=cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR),
    )


def build_symbols_and_boxes(
    image_rgb: np.ndarray,
    legend_result: Optional[Dict],
    shape_info_in_legend: List[Dict],
    axis_boxes: List[Dict],
    legend_boxes: List[Dict],
) -> Tuple[List[np.ndarray], List[np.ndarray], List[Any], List[int], List[int]]:
    """
    从图例分析结果与 YOLO 形状框构建 symbol, symbol_bw, color, incbox, excbox。
    """
    h, w = image_rgb.shape[:2]
    symbol = []
    symbol_bw = []
    color = []

    if shape_info_in_legend:
        for s in shape_info_in_legend:
            x1, y1, x2, y2 = [int(s["box"][i]) for i in range(4)]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 <= x1 or y2 <= y1:
                continue
            crop = image_rgb[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
            _, bw = cv2.threshold(gray, 0.8 * 255, 1, cv2.THRESH_BINARY_INV)
            symbol.append(crop)
            symbol_bw.append(bw)
            # 简单前景色：取非白像素的均值作为代表色
            mask = bw.astype(bool)
            if np.any(mask):
                cols = crop[mask]
                mean_c = np.median(cols, axis=0).astype(np.uint8)
                color.append([mean_c.tolist()])
            else:
                color.append([np.array([128, 128, 128], dtype=np.uint8).tolist()])

    if not symbol:
        return symbol, symbol_bw, color, [0, w, 0, h], [0, 0, 0, 0]

    # incbox = 坐标轴内 [x1,x2,y1,y2]，excbox = 图例框
    if axis_boxes:
        boxes = [a["box"] for a in axis_boxes]
        x1 = min(b[0] for b in boxes)
        y1 = min(b[1] for b in boxes)
        x2 = max(b[2] for b in boxes)
        y2 = max(b[3] for b in boxes)
        incbox = [int(x1), int(x2), int(y1), int(y2)]
    else:
        incbox = [0, w, 0, h]

    if legend_boxes:
        b = legend_boxes[0]["box"]
        excbox = [int(b[0]), int(b[2]), int(b[1]), int(b[3])]
    else:
        excbox = [0, 0, 0, 0]

    return symbol, symbol_bw, color, incbox, excbox


# ---------------------------------------------------------------------------
# 模块3：散点分类与像素级定位（由 module3_scatter_classification 提供，内部调用 4 个策略）
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def extract_scatter_classification_and_coordinates(
    image_path: str,
    axis_model_path: str = "axis250821.pt",
    legendbox_model_path: str = "legendbox_best250821.pt",
    shape_model_path: str = "shape11_250827_best.pt",
    theta_s: float = 0.5,
    scale_factor: float = 1.0,
    theta_c: float = 30,
    w_shape: float = 0.4,
    w_a: float = 0.85,
    force_strategy: Optional[int] = None,
) -> Dict[str, Any]:
    """
    按五模块固定流程提取输入散点图上的散点分类与真实坐标。

    布局/判决外显参数:
        theta_s: 散点 YOLO（shape 模型）平均置信度阈值，>= 时认为典型，才尝试策略1
        scale_factor: 搜索窗口与图例模板尺寸的比率（模板匹配时）
        theta_c: 图例模板与搜索区域颜色相近的阈值（像素差）
        w_shape: 形状匹配分数权重（颜色权重 = 1 - w_shape）
        w_a: 图像分析部分权重（策略1 综合得分中颜色一致性权重，策略4 中 rgb_weight）
        force_strategy: 若为 1/2/3/4，则模块3 仅执行该策略（用于测试）；默认 None 表示自动按优先级尝试

    返回:
        image_rgb: 原图 RGB
        axis_boxes, legend_boxes, shape_boxes: YOLO 检测结果
        legend_result: 图例分析结果
        data_pixel: 按类别分的散点像素坐标 { class_id: [[x,y], ...] }
        data_physical: 按类别分的散点物理坐标 { class_id: [[x,y], ...] }
        calibration: 模块4 的刻度/映射信息
    """
    result = {
        "image_rgb": None,
        "axis_boxes": [],
        "legend_boxes": [],
        "shape_boxes": [],
        "legend_result": None,
        "data_pixel": {},
        "data_physical": {},
        "calibration": {},
    }

    # 1. 关键视觉元素检测
    print("--- 模块1: 关键视觉元素检测（YOLO） ---")
    try:
        axis_boxes, legend_boxes, shape_boxes, image_bgr = run_module1_yolo_detection(
            image_path,
            axis_model_path=axis_model_path,
            legendbox_model_path=legendbox_model_path,
            shape_model_path=shape_model_path,
        )
        result["axis_boxes"] = axis_boxes
        result["legend_boxes"] = legend_boxes
        result["shape_boxes"] = shape_boxes
        result["image_rgb"] = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"模块1 失败: {e}")
        result["image_rgb"] = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        return result

    image_rgb = result["image_rgb"]
    h, w = image_rgb.shape[:2]

    # 筛选落在图例框内的 shape_boxes，作为 module2 的 shape_info
    shape_info_in_legend = []
    if legend_boxes:
        lb = legend_boxes[0]["box"]
        lx1, ly1, lx2, ly2 = lb[0], lb[1], lb[2], lb[3]
        for s in shape_boxes:
            cx = (s["box"][0] + s["box"][2]) / 2
            cy = (s["box"][1] + s["box"][3]) / 2
            if lx1 <= cx <= lx2 and ly1 <= cy <= ly2:
                shape_info_in_legend.append({"box": s["box"]})
    # 注意：没有图例框时，不应“用散点框伪造图例模板”，否则会误触发策略1/2。
    # 无图例时让 symbol 为空，模块3 会自然跳过策略1/2，进入策略3/4。

    # 2. 图例特征分析与提取
    print("--- 模块2: 图例特征分析与提取 ---")
    legend_result = None
    if legend_boxes and shape_info_in_legend:
        try:
            legend_result = run_module2_legend_analysis(
                image_path,
                image_rgb,
                {"box": legend_boxes[0]["box"]},
                shape_info_in_legend,
            )
            result["legend_result"] = legend_result
        except Exception as e:
            print(f"模块2 失败: {e}")

    symbol, symbol_bw, color, incbox, excbox = build_symbols_and_boxes(
        image_rgb,
        legend_result,
        shape_info_in_legend,
        axis_boxes,
        legend_boxes,
    )

    # 3. 散点分类与像素级定位
    print("--- 模块3: 散点分类与像素级定位（多策略） ---")
    data_pixel = run_module3_scatter_classification(
        image_rgb,
        axis_boxes,
        legend_boxes,
        shape_boxes,
        legend_result,
        shape_info_in_legend,
        symbol,
        symbol_bw,
        color,
        incbox,
        excbox,
        theta_s=theta_s,
        scale_factor=scale_factor,
        theta_c=theta_c,
        w_shape=w_shape,
        w_a=w_a,
        force_strategy=force_strategy,
    )
    result["data_pixel"] = data_pixel

    # 4. 坐标轴刻度识别与类型识别
    print("--- 模块4: 坐标轴刻度识别与类型识别 ---")
    calibration = run_module4_axis_scale_recognition_external(image_rgb, axis_boxes)
    result["calibration"] = calibration

    # 5. 物理坐标计算
    print("--- 模块5: 物理坐标计算 ---")
    result["data_physical"] = run_module5_physical_coordinates_external(data_pixel, calibration)

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="散点图提取：分类与真实坐标")
    parser.add_argument("image_path", help="输入散点图路径")
    parser.add_argument("--axis-model", default="axis250821.pt", help="坐标轴模型")
    parser.add_argument("--legendbox-model", default="legendbox_best250821.pt", help="图例框模型")
    parser.add_argument("--shape-model", default="shape11_250827_best.pt", help="散点形状模型")
    parser.add_argument("--output-dir", default=".", help="结果输出目录")
    parser.add_argument("--theta-s", type=float, default=0.5, help="散点YOLO平均置信度阈值，>=时尝试策略1")
    parser.add_argument("--scale-factor", type=float, default=1.0, help="搜索窗口与图例模板尺寸比率")
    parser.add_argument("--theta-c", type=float, default=30, help="图例与搜索区域颜色相近阈值")
    parser.add_argument("--w-shape", type=float, default=0.4, help="形状匹配权重")
    parser.add_argument("--w-a", type=float, default=0.85, help="图像分析权重(策略1/4)")
    parser.add_argument("--force-strategy", type=int, default=None, choices=[1, 2, 3, 4],
                        help="测试用：强制模块3只执行指定策略(1/2/3/4)，不指定则自动按优先级尝试")
    args = parser.parse_args()

    if not os.path.isfile(args.image_path):
        print(f"文件不存在: {args.image_path}")
        return

    t0 = time.perf_counter()
    result = extract_scatter_classification_and_coordinates(
        args.image_path,
        axis_model_path=args.axis_model,
        legendbox_model_path=args.legendbox_model,
        shape_model_path=args.shape_model,
        theta_s=args.theta_s,
        scale_factor=args.scale_factor,
        theta_c=args.theta_c,
        w_shape=args.w_shape,
        w_a=args.w_a,
        force_strategy=args.force_strategy,
    )
    elapsed = time.perf_counter() - t0

    # 简单输出
    os.makedirs(args.output_dir, exist_ok=True)
    out_txt = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.image_path))[0] + "_scatter_result.txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("散点分类与坐标提取结果\n")
        f.write("=" * 50 + "\n")
        f.write("像素坐标（按类别）:\n")
        for cls, points in result["data_pixel"].items():
            f.write(f"  类别 {cls}: {len(points)} 个点\n")
            for p in points[:20]:
                f.write(f"    [{p[0]}, {p[1]}]\n")
            if len(points) > 20:
                f.write(f"    ... 共 {len(points)} 个\n")
        f.write("\n物理坐标（按类别）:\n")
        for cls, points in result["data_physical"].items():
            f.write(f"  类别 {cls}: {len(points)} 个点\n")
            for p in points[:20]:
                f.write(f"    [{p[0]}, {p[1]}]\n")
            if len(points) > 20:
                f.write(f"    ... 共 {len(points)} 个\n")
    print(f"结果已写入: {out_txt}")
    print(f"整条流水线总耗时: {elapsed:.3f} 秒")


if __name__ == "__main__":
    main()
