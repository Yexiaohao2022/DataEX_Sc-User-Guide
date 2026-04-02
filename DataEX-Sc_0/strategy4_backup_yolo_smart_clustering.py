#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略4：K-Means 兜底聚类

当前面 3 个策略由于图像质量较差、散点特征模糊等原因无法完成有效分类时，
本策略作为最终兜底被激活，确保系统在任何情况下都能给出一个散点分类结果。

核心思想：
    - 利用 I 模块（YOLO）或前三个策略传递的散点“潜在像素位置”（像素坐标），
      在原始 RGB 图上截取每个散点周围的小块（RGB 矩阵）作为特征；
    - 将这些 RGB 特征展平后，使用 K-Means 算法进行无监督聚类；
    - 聚类标签即作为散点的类别编号输出。

由于完全不依赖模板和图例信息，且仅基于局部颜色与亮度结构，
因此本策略的分类精度相对较低，仅用于在其他策略全部失败时提供一个“可用但粗糙”的结果。
"""

from typing import Dict, List

import numpy as np


def _extract_rgb_patches(
    image_rgb: np.ndarray,
    pixel_positions: List[List[float]],
    patch_radius: int = 3,
) -> np.ndarray:
    """
    从原始 RGB 图中提取以每个像素坐标为中心的 RGB 小块（patch），并展平成特征向量。

    参数:
        image_rgb: 原图 RGB, H x W x 3
        pixel_positions: [[x, y], ...] 像素坐标列表
        patch_radius: 半径 r，对应 patch 尺寸为 (2r+1) x (2r+1)

    返回:
        features: N x D 的特征矩阵，N 为像素个数，D 为展平后的维度
    """
    h, w, _ = image_rgb.shape
    size = 2 * patch_radius + 1
    features = []
    for x, y in pixel_positions:
        cx, cy = int(round(x)), int(round(y))
        x1 = max(0, cx - patch_radius)
        y1 = max(0, cy - patch_radius)
        x2 = min(w, cx + patch_radius + 1)
        y2 = min(h, cy + patch_radius + 1)
        patch = image_rgb[y1:y2, x1:x2, :]
        if patch.size == 0:
            continue
        # 若靠近边界导致 patch 比标准尺寸小，则用简单的零填充到统一尺寸
        if patch.shape[0] != size or patch.shape[1] != size:
            padded = np.zeros((size, size, 3), dtype=patch.dtype)
            padded[: patch.shape[0], : patch.shape[1], :] = patch
            patch = padded
        features.append(patch.reshape(-1).astype(np.float32) / 255.0)
    if not features:
        return np.zeros((0, size * size * 3), dtype=np.float32)
    return np.stack(features, axis=0)


def run_strategy4_kmeans_fallback(
    image_rgb: np.ndarray,
    pixel_positions: List[List[float]],
    n_clusters: int,
    patch_radius: int = 3,
) -> Dict[int, List[List[float]]]:
    """
    策略4：基于 K-Means 的无监督聚类兜底。

    当图像质量较差或前三个策略均无法给出可靠分类时调用：
        - 利用 I 模块或前三策略输出的「潜在散点像素坐标」；
        - 在原图上截取每个坐标周围的 RGB 小块；
        - 对这些 RGB 特征使用 K-Means 进行无监督聚类；
        - 输出聚类标签作为最终类别编号。

    参数:
        image_rgb: 原图 RGB
        pixel_positions: [[x,y], ...]，散点的像素级位置（来自 YOLO 或前 3 个策略）
        n_clusters: 目标类别数（通常为图例类别数，如未知可传入 1）
        patch_radius: 用于构造 RGB 特征的局部窗口半径

    返回:
        data: dict, data[cluster_id] = [[x,y], ...]，cluster_id 为 K-Means 聚类标签
    """
    if not pixel_positions:
        return {}
    if n_clusters <= 0:
        n_clusters = 1

    try:
        from sklearn.cluster import KMeans
    except Exception as e:
        print(f"策略4 K-Means 兜底：导入 sklearn 失败（全部归为单类）: {e}")
        return {0: list(pixel_positions)}

    # 1. 提取 RGB 特征
    features = _extract_rgb_patches(image_rgb, pixel_positions, patch_radius=patch_radius)
    if features.shape[0] == 0:
        # 无法提取有效特征时，退化为单类
        return {0: list(pixel_positions)}

    # 2. K-Means 聚类（无监督）
    try:
        n_clusters = min(n_clusters, features.shape[0])
        if n_clusters < 1:
            return {0: list(pixel_positions)}
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(features)
        data: Dict[int, List[List[float]]] = {i: [] for i in range(n_clusters)}
        # 注意：features 可能比 pixel_positions 少（靠边 patch 被丢弃）
        # 这里简单使用前 features.shape[0] 个 pixel_positions 对应的标签
        for pos, lab in zip(pixel_positions[: features.shape[0]], labels):
            data[int(lab)].append(pos)
        return data
    except Exception as e:
        print(f"策略4 K-Means 兜底失败（全部归为单类）: {e}")
        return {0: list(pixel_positions)}

