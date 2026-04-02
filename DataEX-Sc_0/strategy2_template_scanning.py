# -*- coding: utf-8 -*-
"""
策略2：模板逐点扫描 + 形状/颜色/边缘匹配 + 模板分类

定位：在「仅散点」二值图 bw_scatter 上，对每个图例模板用 search_space 得到候选左上角，
      逐块计算形状/颜色/边缘得分，通过阈值的点做连通域合并，取加权中心为散点位置。
分类：对每个加权中心用 otherlegend_score2 判定归属；再经第三、第四次放宽阈值扫描补漏。
对应原代码：extract_overlap_data 主循环 + third_match（两次）+ eliminate_legend2 + process_coordinates。
"""

import cv2
import numpy as np
from scipy.ndimage import label
import time
from module3_scatter_classification import (
    otherlegend_score2,
    search_space,
    select_pix,
    eliminate_legend,
    eliminate_legend2,
    remove_text_regions_advanced,
    process_coordinates,
    check_black_white_colors,
)


def _third_match(remain_bw_all, symbol_bw, symbol, rgb, data, incbox, excbox, color,
                 thre_colordev, thre_shape, thre_shape2, thre_shape_high, edge_thre_shape, thre_color, bw0,
                 scale_factor=1.0, theta_c=30, w_shape=0.4):
    """第三次/第四次匹配：在剩余二值图上用相同形状/颜色/边缘规则扫描，归属用 otherlegend_score2。"""
    h, w = remain_bw_all.shape[0], remain_bw_all.shape[1]
    bw = remain_bw_all.copy()
    bwnew = np.zeros_like(bw)
    inbox, exbox = incbox, excbox
    bwnew[inbox[2]:inbox[3] + 1, inbox[0]:inbox[1] + 1] = bw[inbox[2]:inbox[3] + 1, inbox[0]:inbox[1] + 1]
    bwnew[exbox[2]:exbox[3] + 1, exbox[0]:exbox[1] + 1] = 0
    bw = bwnew
    bw_scatter = bw
    data2 = {i: list(data[i]) for i in data}
    row0, col0 = np.where(bw_scatter == 1)
    row0, col0 = select_pix(row0, col0, incbox, excbox)
    edge_symbol = {}
    for i in range(len(symbol)):
        hs, ws = symbol[i].shape[0], symbol[i].shape[1]
        nfill = np.sum(symbol_bw[i])
        row, col, hs_eff, ws_eff = search_space(row0, col0, hs, ws, h, w, scale_factor=scale_factor)
        np_ = len(row)
        row2, col2 = np.where(symbol_bw[i] == 1)
        center = [np.mean(col2), np.mean(row2)]
        score_shape = np.zeros((h, w))
        score_color = np.zeros((h, w))
        pos = []
        edge_symbol[i] = cv2.Canny(symbol_bw[i].astype(np.uint8), 0.1, 0.2) / 255
        symbol_i = symbol[i].astype(np.float64)
        for j in range(np_):
            if row[j] + hs_eff > bw_scatter.shape[0] or col[j] + ws_eff > bw_scatter.shape[1]:
                continue
            pad_bw = bw_scatter[row[j]:row[j] + hs_eff, col[j]:col[j] + ws_eff]
            pad_bw_resized = (cv2.resize(pad_bw.astype(np.uint8), (ws, hs), interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
            delta = ~(np.logical_xor(pad_bw_resized, symbol_bw[i]))
            mask = np.logical_and(delta, symbol_bw[i])
            nmatch = np.sum(mask)
            sscore = nmatch / nfill
            nfill3 = np.sum(pad_bw_resized)
            sscore3 = nmatch / nfill3 if nfill3 != 0 else 0
            shape_flag = 0
            if sscore >= thre_shape and sscore3 >= thre_shape2:
                if sscore >= thre_shape_high:
                    shape_flag = 1
                pad = rgb[row[j]:row[j] + hs_eff, col[j]:col[j] + ws_eff, :3].astype(np.float64)
                pad_resized = cv2.resize(pad, (ws, hs), interpolation=cv2.INTER_LINEAR)
                delta = np.abs(pad_resized - symbol_i)
                delta[:, :, 0] += (~mask) * 255
                delta[:, :, 1] += (~mask) * 255
                delta[:, :, 2] += (~mask) * 255
                delta[delta <= thre_colordev] = 1
                delta[delta > thre_colordev] = 0
                s1 = np.sum(delta, axis=2)
                s1[s1 < 3], s1[s1 == 3] = 0, 1
                cscore = np.sum(s1) / nfill
                if cscore > thre_color or (shape_flag and cscore >= thre_color - 0.05):
                    edge_pad_bw = cv2.Canny(pad_bw_resized.astype(np.uint8), 0.1, 0.2) / 255
                    delta = ~(np.logical_xor(edge_pad_bw, edge_symbol[i]))
                    mask2 = np.logical_and(delta, edge_symbol[i])
                    nmatch2 = np.sum(mask2)
                    nfill2 = np.sum(edge_symbol[i])
                    sscore2 = nmatch2 / nfill2 if nfill2 != 0 else (1 if np.sum(edge_pad_bw) <= 5 else 0)
                    if sscore2 > edge_thre_shape:
                        pos.append(np.round([col[j] + center[0] - 1, row[j] + center[1] - 1]))
                        pos[-1][0] = np.clip(pos[-1][0], 1, w)
                        pos[-1][1] = np.clip(pos[-1][1], 1, h)
                        score_shape[int(pos[-1][1]), int(pos[-1][0])] = sscore
                        score_color[int(pos[-1][1]), int(pos[-1][0])] = cscore
        try:
            im0 = np.zeros((h, w))
            if len(pos) > 0:
                pos_array = np.array(pos)
                ind = np.ravel_multi_index((pos_array[:, 1].astype(int), pos_array[:, 0].astype(int)), (h, w))
                im0.flat[ind] = 1
            bwcn, nobj = label(im0)
            pid = [np.column_stack(np.where(bwcn == label_id)) for label_id in range(1, nobj + 1)]
            for j in range(nobj):
                coords = pid[j]
                row3, col3 = coords[:, 0], coords[:, 1]
                ss1 = score_shape[row3, col3]
                y = int((np.sum(row3 * ss1) / np.sum(ss1)))
                x = int((np.sum(col3 * ss1) / np.sum(ss1)))
                matchleg, _ = otherlegend_score2(x, y, bw0, symbol, symbol_bw, rgb, 0, theta_c=theta_c, w_shape=w_shape)
                if matchleg == i:
                    data2[i].append([x, y])
        except Exception:
            pass
    return data2


def _locate_and_classify_by_connected_components(
    bw,
    symbol,
    symbol_bw,
    row0,
    col0,
    rgb,
    color,
    incbox,
    excbox,
    theta_c=30,
    w_shape=0.4,
    w_a=0.85,
    combined_threshold=0.25,
):
    """
    策略2 内部使用：连通域定位 + 模板分类的初筛。
    在坐标区内、图例区外, 按图例颜色筛选前景 → 连通域分析 → 按尺寸过滤 → each 连通域中心
    用 otherlegend_score2 与模板匹配, 作为后续模板扫描的起点, 并返回剩余候选前景 bw_scatter。
    """
    h_img, w_img = rgb.shape[0], rgb.shape[1]
    bwnew = np.ones_like(bw)
    bw_scatter = np.zeros_like(bw, dtype=np.uint8)
    rgbnew = np.full(rgb.shape, 255, dtype=np.uint8)
    rgbnew[row0, col0] = rgb[row0, col0]
    bw_scatter[row0, col0] = bw[row0, col0]

    crit = 45
    for i in range(len(color)):
        for i2 in range(len(color[i])):
            c = np.array(color[i][i2], dtype=np.uint8).reshape(1, 1, 3)
            if np.isnan(c).any():
                continue
            delta = np.abs(rgbnew.astype(np.float64) - c.astype(np.float64))
            indr_row, indr_col = np.where(delta[:, :, 0] <= crit)
            indg_row, indg_col = np.where(delta[:, :, 1] <= crit)
            indb_row, indb_col = np.where(delta[:, :, 2] <= crit)
            indr = np.ravel_multi_index((indr_row, indr_col), (h_img, w_img))
            indg = np.ravel_multi_index((indg_row, indg_col), (h_img, w_img))
            indb = np.ravel_multi_index((indb_row, indb_col), (h_img, w_img))
            candidate = np.intersect1d(np.intersect1d(indr, indg), indb)
            I, J = np.unravel_index(candidate, (h_img, w_img))
            for j in range(len(I)):
                bwnew[I[j], J[j]] = 0

    color_flag = 0
    bwnew2 = bwnew.copy()
    flag_0 = check_black_white_colors(symbol)
    if np.sum(bwnew2) < (1 / 4) * bw.shape[0] * bw.shape[1] or flag_0:
        bw_ = remove_text_regions_advanced((bw * 255).astype(np.uint8)) / 255
        bwnew = 1 - bw_
        bwnew2 = 1 - bw_
        color_flag = 1
        bw_scatter[row0, col0] = bw_[row0, col0]

    hs = [symbol_bw[i].shape[0] for i in range(len(symbol_bw))]
    ws = [symbol_bw[i].shape[1] for i in range(len(symbol_bw))]
    nfill = [np.sum(symbol_bw[i] == 1) for i in range(len(symbol_bw))]
    min_hs, max_hs = min(hs), max(hs)
    min_ws, max_ws = min(ws), max(ws)
    min_nfill = min(nfill)

    bw_inverted = 1 - bwnew
    n0, L = cv2.connectedComponents((bw_inverted * 255).astype(np.uint8), connectivity=4)
    add_space, del_space = 2, 3
    for i in range(1, n0):
        r, c = np.where(L == i)
        rmax, rmin = np.max(r), np.min(r)
        cmax, cmin = np.max(c), np.min(c)
        width = cmax - cmin + 1
        height = rmax - rmin + 1
        if (width > max_ws + add_space or height > max_hs + add_space or
                width < min_ws - del_space or height < min_hs - del_space):
            bw_inverted[r, c] = 0
    n0, L = cv2.connectedComponents((bw_inverted * 255).astype(np.uint8), connectivity=4)

    data1 = {l: [] for l in range(len(color))}
    bwnew2 = bwnew.copy()
    for i in range(1, n0):
        r, c = np.where(L == i)
        if len(r) <= min_nfill - 10:
            continue
        current_center = [np.mean(c), np.mean(r)]
        x = round(current_center[0])
        y = round(current_center[1])
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        otherlegend_score2_flag = 1
        matchlegend, template_score = otherlegend_score2(
            x, y, bw, symbol, symbol_bw, rgb, otherlegend_score2_flag,
            theta_c=theta_c, w_shape=w_shape
        )
        if matchlegend < 0:
            continue
        legend_color = np.array(color[matchlegend][0], dtype=np.float64)
        pixel_color = rgb[y, x, :3].astype(np.float64)
        color_dist = np.mean(np.abs(pixel_color - legend_color))
        color_score = 1.0 - min(1.0, color_dist / 255.0)
        combined = w_a * color_score + (1.0 - w_a) * template_score
        if combined < combined_threshold:
            continue
        for l in range(len(color)):
            if matchlegend == l:
                data1[l].append([x, y])
                bwnew2[r, c] = 1
                bw_scatter[r, c] = 0
                break
    return data1, bw_scatter, color_flag


def _run_template_scanning_impl(rgb, bw0, symbol, symbol_bw, incbox, excbox, color,
                                scale_factor=1.0, theta_c=30, w_shape=0.4, w_a=0.85):
    """
    策略2 入口：先按策略1得到初始 data1 与 bw_scatter，再逐模板扫描 + 第三第四次匹配 + 坐标合并。

    参数:
        rgb, bw0: 原图 RGB 与二值图
        symbol, symbol_bw, color: 图例模板与颜色
        incbox, excbox: [x1,x2,y1,y2]
        scale_factor: 搜索窗口与图例模板尺寸的比率
        theta_c: 颜色相近阈值（用于 otherlegend_score2 与 thre_colordev）
        w_shape: 形状匹配权重
        w_a: 图像分析权重（策略1 综合得分用）

    返回:
        data: dict，data[l] = 图例 l 的散点中心坐标列表（已做邻近点合并）
    """
    h, w = rgb.shape[0], rgb.shape[1]
    bwnew = np.ones_like(bw0)
    bwnew[incbox[2]:incbox[3] + 1, incbox[0]:incbox[1] + 1] = bw0[incbox[2]:incbox[3] + 1, incbox[0]:incbox[1] + 1]
    bwnew[excbox[2]:excbox[3] + 1, excbox[0]:excbox[1] + 1] = 1
    bw = bwnew
    row0, col0 = np.where(bw == 1)
    row0, col0 = select_pix(row0, col0, incbox, excbox)
    # 内部首轮“连通域 + 模板分类”初筛, 得到 data1 与 bw_scatter
    data1, bw_scatter, color_flag = _locate_and_classify_by_connected_components(
        bw, symbol, symbol_bw, row0, col0, rgb, color, incbox, excbox,
        theta_c=theta_c, w_shape=w_shape, w_a=w_a)
    if color_flag:
        bw0 = remove_text_regions_advanced((bw0 * 255).astype(np.uint8)) / 255
    row0, col0 = np.where(bw_scatter == 1)
    row0, col0 = select_pix(row0, col0, incbox, excbox)
    data = {i: list(data1[i]) for i in data1}
    remain_bw = {}
    thre_colordev = theta_c
    thre_shape, thre_shape2 = 0.8, 0.6
    thre_shape_high, edge_thre_shape, thre_color = 0.85, 0.4, 0.3
    for i in range(len(symbol)):
        hs, ws = symbol[i].shape[0], symbol[i].shape[1]
        nfill = np.sum(symbol_bw[i])
        row, col, hs_eff, ws_eff = search_space(row0, col0, hs, ws, h, w, scale_factor=scale_factor)
        np_ = len(row)
        row2, col2 = np.where(symbol_bw[i] == 1)
        center = [np.mean(col2), np.mean(row2)]
        score_shape = np.zeros((h, w))
        score_color = np.zeros((h, w))
        pos = []
        edge_symbol_i = cv2.Canny(symbol_bw[i].astype(np.uint8), 0.1, 0.2) / 255
        for j in range(np_):
            if row[j] + hs_eff > bw_scatter.shape[0] or col[j] + ws_eff > bw_scatter.shape[1]:
                continue
            pad_bw = bw_scatter[row[j]:row[j] + hs_eff, col[j]:col[j] + ws_eff]
            pad_bw_resized = (cv2.resize(pad_bw.astype(np.uint8), (ws, hs), interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
            delta = ~(np.logical_xor(pad_bw_resized, symbol_bw[i]))
            mask = np.logical_and(delta, symbol_bw[i])
            nmatch = np.sum(mask)
            sscore = nmatch / nfill
            nfill3 = np.sum(pad_bw_resized)
            sscore3 = nmatch / nfill3 if nfill3 != 0 else 0
            shape_flag = 0
            if sscore >= thre_shape and sscore3 >= thre_shape2:
                if sscore >= thre_shape_high:
                    shape_flag = 1
                pad = rgb[row[j]:row[j] + hs_eff, col[j]:col[j] + ws_eff, :3].astype(np.float64)
                pad_resized = cv2.resize(pad, (ws, hs), interpolation=cv2.INTER_LINEAR)
                delta = np.abs(pad_resized - symbol[i].astype(np.float64))
                delta[:, :, 0] += (~mask) * 255
                delta[:, :, 1] += (~mask) * 255
                delta[:, :, 2] += (~mask) * 255
                delta[delta <= thre_colordev] = 1
                delta[delta > thre_colordev] = 0
                s1 = np.sum(delta, axis=2)
                s1[s1 < 3], s1[s1 == 3] = 0, 1
                cscore = np.sum(s1) / nfill
                if cscore > thre_color or (shape_flag and cscore >= thre_color - 0.05):
                    edge_pad_bw = cv2.Canny(pad_bw_resized.astype(np.uint8), 0.1, 0.2) / 255
                    delta = ~(np.logical_xor(edge_pad_bw, edge_symbol_i))
                    mask2 = np.logical_and(delta, edge_symbol_i)
                    nfill2 = np.sum(edge_symbol_i)
                    sscore2 = (np.sum(mask2) / nfill2 if nfill2 != 0 else (1 if np.sum(edge_pad_bw) <= 5 else 0))
                    if sscore2 > edge_thre_shape:
                        pos.append(np.round([col[j] + center[0] - 1, row[j] + center[1] - 1]))
                        pos[-1][0] = np.clip(pos[-1][0], 1, w)
                        pos[-1][1] = np.clip(pos[-1][1], 1, h)
                        score_shape[int(pos[-1][1]), int(pos[-1][0])] = sscore
                        score_color[int(pos[-1][1]), int(pos[-1][0])] = cscore
        try:
            im0 = np.zeros((h, w))
            if len(pos) > 0:
                pos_array = np.array(pos)
                ind = np.ravel_multi_index((pos_array[:, 1].astype(int), pos_array[:, 0].astype(int)), (h, w))
                im0.flat[ind] = 1
            bwcn, nobj = label(im0)
            pid = [np.column_stack(np.where(bwcn == k)) for k in range(1, nobj + 1)]
            for j in range(nobj):
                coords = pid[j]
                row3, col3 = coords[:, 0], coords[:, 1]
                ss1 = score_shape[row3, col3]
                y = int((np.sum(row3 * ss1) / np.sum(ss1)))
                x = int((np.sum(col3 * ss1) / np.sum(ss1)))
                matchleg, _ = otherlegend_score2(x, y, bw0, symbol, symbol_bw, rgb, 0, theta_c=theta_c, w_shape=w_shape)
                if matchleg == i:
                    data[i].append([x, y])
        except Exception:
            pass
        remain_bw[i] = eliminate_legend(data, i, symbol_bw, bw0.copy())
        if i == 1:
            remain_bw_all = eliminate_legend(data, i, symbol_bw, remain_bw[i - 1].copy())
        elif i > 1:
            remain_bw_all = eliminate_legend(data, i, symbol_bw, remain_bw_all.copy())
    if len(symbol) == 1:
        remain_bw_all = remain_bw[0]
    thre_shape, edge_thre_shape, thre_color = 0.6, 0.35, 0.3
    data2 = _third_match(remain_bw_all, symbol_bw, symbol, rgb, data, incbox, excbox, color,
                         thre_colordev, thre_shape, thre_shape2, thre_shape_high, edge_thre_shape, thre_color, bw0,
                         scale_factor=scale_factor, theta_c=theta_c, w_shape=w_shape)
    remain_bw_all_2 = eliminate_legend2(data2, symbol_bw, remain_bw_all)
    thre_color = 0.1
    data3 = _third_match(remain_bw_all_2, symbol_bw, symbol, rgb, data2, incbox, excbox, color,
                         thre_colordev, thre_shape, thre_shape2, thre_shape_high, edge_thre_shape, thre_color, bw0,
                         scale_factor=scale_factor, theta_c=theta_c, w_shape=w_shape)
    data = {key: process_coordinates(coords) for key, coords in data3.items()}
    return data


def run_template_scanning(rgb, bw0, symbol, symbol_bw, incbox, excbox, color,
                          scale_factor=1.0, theta_c=30, w_shape=0.4, w_a=0.85):
    """
    包装原始策略2入口函数，增加运行时间统计。
    """
    start = time.perf_counter()
    result = _run_template_scanning_impl(
        rgb, bw0, symbol, symbol_bw, incbox, excbox, color,
        scale_factor=scale_factor, theta_c=theta_c, w_shape=w_shape, w_a=w_a,
    )
    elapsed = time.perf_counter() - start
    print(f"策略2（模板逐点扫描）耗时: {elapsed:.3f} 秒")
    return result

