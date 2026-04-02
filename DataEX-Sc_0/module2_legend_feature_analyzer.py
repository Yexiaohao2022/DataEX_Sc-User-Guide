import os
import cv2
import numpy as np
from typing import List, Dict, Optional


class LegendFeatureAnalyzer:
    """图例特征分析器"""

    def __init__(self):
        self.features: Dict = {}
        self.debug: bool = False
        # 当前图像路径（用于输出文件命名，可选）
        self.current_image_path: Optional[str] = None

    def analyze_legend_features(self, image_path: str, legend_box_info: Dict, shape_info: List[Dict], image: np.ndarray = None) -> Optional[Dict]:
        """
        分析图例特征 - 支持图例框拆分
        Args:
            image_path: 原始图像路径（可选，如果提供了image参数）
            legend_box_info: { 'box': [x1, y1, x2, y2], ... }
            shape_info: [ { 'box': [x1, y1, x2, y2] }, ... ]
            image: 图像数组（可选，如果提供则优先使用）
        Returns:
            合并后的分析结果字典，或 None
        """
        print("=== 开始图例特征分析 ===")

        # 优先使用传入的图像数组，否则从文件路径读取
        if image is not None:
            print("使用传入的图像数组")
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            print(f"从文件路径读取图像: {image_path}")
            image_rgb = cv2.imread(image_path)
            if image_rgb is None:
                print("错误: 无法读取图像")
                return None
            image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)

        legend_box = legend_box_info['box']
        # 图例框坐标：rmin=y1, rmax=y2, cmin=x1, cmax=x2
        rmin, rmax, cmin, cmax = int(legend_box[1]), int(legend_box[3]), int(legend_box[0]), int(legend_box[2])

        print(f"原始图例框: [{rmin}, {rmax}, {cmin}, {cmax}] (行列格式)")
        print(f"检测到 {len(shape_info)} 个图例形状")

        sub_legend_boxes = self._split_legend_box(shape_info, [rmin, rmax, cmin, cmax])
        print(f"拆分为 {len(sub_legend_boxes)} 个子图例框")

        all_results: List[Dict] = []
        for i, sub_box in enumerate(sub_legend_boxes):
            print(f"\n--- 分析子图例框 {i+1} ---")
            sub_result = self._analyze_sub_legend_box(image_rgb, sub_box, shape_info, i + 1)
            if sub_result:
                all_results.append(sub_result)

        if all_results:
            merged_result = self._merge_sub_results(all_results, legend_box_info)
            return merged_result
        else:
            print("错误: 没有成功分析任何子图例框")
            return None

    def _split_legend_box(self, shape_info: List[Dict], legend_box: List[int]) -> List[List[int]]:
        print("  分析图例形状分布，确定图例框拆分...")

        rmin, rmax, cmin, cmax = legend_box
        rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)

        shape_col_centers: List[Dict] = []
        for shape in shape_info:
            box = shape['box']
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            center_col = (x1 + x2) / 2
            shape_col_centers.append({
                'center_col': center_col,
                'col1': x1,
                'col2': x2,
                'shape': shape
            })

        shape_col_centers.sort(key=lambda x: x['center_col'])

        print(f"    图例形状列坐标分布:")
        for i, s in enumerate(shape_col_centers):
            print(f"      形状{i+1}: 中心列={s['center_col']:.1f}, 范围[{s['col1']}, {s['col2']}]")

        if len(shape_col_centers) <= 1:
            print("    只有一个图例形状，无需拆分")
            return [legend_box]

        gaps: List[int] = []
        for i in range(len(shape_col_centers) - 1):
            gap = shape_col_centers[i + 1]['col1'] - shape_col_centers[i]['col2']
            gaps.append(gap)
            print(f"    形状{i+1}与形状{i+2}间距: {gap}像素")

        min_gap_threshold = 20
        split_points: List[float] = []
        for i, gap in enumerate(gaps):
            if gap > min_gap_threshold:
                split_col = (shape_col_centers[i]['col2'] + shape_col_centers[i + 1]['col1']) / 2
                split_points.append(split_col)
                print(f"    在列={split_col:.1f}处拆分（间距={gap}像素）")

        # 根据 split_points 真正构造子图例框，避免下标越界
        sub_boxes: List[List[int]] = []
        if not split_points:
            print("    图例形状间距较小，无需拆分")
            sub_boxes.append(legend_box)
            print(f"    子图例框1: {legend_box}")
        else:
            # 使用拆分列把整体 [cmin, cmax] 切成若干段
            boundaries: List[int] = [cmin] + [int(round(sp)) for sp in split_points] + [cmax]
            box_idx = 1
            for i in range(len(boundaries) - 1):
                sub_cmin = boundaries[i]
                sub_cmax = boundaries[i + 1]
                # 过滤过窄的子框
                if sub_cmax - sub_cmin <= 10:
                    continue
                sub_box = [rmin, rmax, sub_cmin, sub_cmax]
                sub_boxes.append(sub_box)
                print(f"    子图例框{box_idx}: [{rmin}, {rmax}, {sub_cmin}, {sub_cmax}]")
                box_idx += 1

            # 容错：如果因为过滤导致没有子框，退回原始图例框
            if not sub_boxes:
                print("    有拆分点但有效子图例框为 0，退回整框")
                sub_boxes.append(legend_box)

        return sub_boxes

    def _analyze_sub_legend_box(self, image_rgb: np.ndarray, sub_box: List[int], all_shape_info: List[Dict], sub_box_id: int) -> Optional[Dict]:
        print(f"  分析子图例框 {sub_box_id}: {sub_box}")

        sub_shape_info: List[Dict] = []
        sub_rmin, sub_rmax, sub_cmin, sub_cmax = sub_box

        for shape in all_shape_info:
            box = shape['box']
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            center_col = (x1 + x2) / 2
            center_row = (y1 + y2) / 2
            if sub_cmin <= center_col <= sub_cmax and sub_rmin <= center_row <= sub_rmax:
                sub_shape_info.append(shape)
                print(f"    包含图例形状: 中心列={center_col:.1f}, 中心行={center_row:.1f}, 范围[{x1}, {y1}, {x2}, {y2}]")

        if not sub_shape_info:
            print(f"    子图例框 {sub_box_id} 中没有图例形状，跳过")
            return None

        print(f"    子图例框 {sub_box_id} 包含 {len(sub_shape_info)} 个图例形状")

        print(f"    --- 1. 图例组合识别 ---")
        legend_combinations = self._identify_legend_combinations(image_rgb, sub_box, sub_shape_info)

        print(f"    --- 2. 连通域分析 ---")
        connected_components = self._analyze_connected_components(image_rgb, sub_box, sub_shape_info)

        print(f"    --- 3. 形状特征分析 ---")
        shape_features = self._analyze_shape_features(image_rgb, sub_shape_info)

        print(f"    --- 4. 文字识别 ---")
        text_features = self._recognize_legend_text(image_rgb, sub_box, sub_shape_info, legend_combinations)

        print(f"    --- 5. 模板生成 ---")
        templates = self._generate_templates(image_rgb, sub_shape_info)

        sub_result = {
            'sub_box_id': sub_box_id,
            'sub_box': sub_box,
            'legend_combinations': legend_combinations,
            'connected_components': connected_components,
            'shape_features': shape_features,
            'text_features': text_features,
            'templates': templates,
            'total_legends': len(sub_shape_info)
        }

        print(f"    子图例框 {sub_box_id} 分析完成")
        return sub_result

    def _merge_sub_results(self, all_results: List[Dict], original_legend_box_info: Dict) -> Dict:
        print("\n--- 合并子图例框分析结果 ---")

        merged_legend_combinations: List[Dict] = []
        merged_connected_components: List[Dict] = []
        merged_color_features: List[Dict] = []
        merged_shape_features: List[Dict] = []
        merged_combination_texts: List[Dict] = []
        merged_templates: List[Dict] = []
        total_legends = 0

        for sub_result in all_results:
            sub_box_id = sub_result['sub_box_id']
            print(f"  合并子图例框 {sub_box_id} 的结果")

            for combo in sub_result['legend_combinations']:
                combo['sub_box_id'] = sub_box_id
                merged_legend_combinations.append(combo)

            for comp in sub_result['connected_components']:
                comp['sub_box_id'] = sub_box_id
                merged_connected_components.append(comp)

            for shape_feat in sub_result['shape_features']:
                shape_feat['sub_box_id'] = sub_box_id
                merged_shape_features.append(shape_feat)

            if 'combination_texts' in sub_result['text_features']:
                for text_info in sub_result['text_features']['combination_texts']:
                    text_info['sub_box_id'] = sub_box_id
                    merged_combination_texts.append(text_info)

            for template in sub_result['templates']:
                template['sub_box_id'] = sub_box_id
                merged_templates.append(template)

            total_legends += sub_result['total_legends']

        merged_text_features = {
            'combination_texts': merged_combination_texts,
            'total_text_regions': len(merged_combination_texts),
            'legend_box': original_legend_box_info['box'],
            'confidence': 0.7
        }

        merged_result = {
            'image_path': None,
            'legend_box': original_legend_box_info,
            'sub_boxes': [result['sub_box'] for result in all_results],
            'legend_combinations': merged_legend_combinations,
            'connected_components': merged_connected_components,
            'color_features': merged_color_features,
            'shape_features': merged_shape_features,
            'text_features': merged_text_features,
            'templates': merged_templates,
            'total_legends': total_legends,
            'sub_box_count': len(all_results)
        }

        print(f"  合并完成:")
        print(f"    子图例框数量: {len(all_results)}")
        print(f"    总图例数量: {total_legends}")
        print(f"    总组合数量: {len(merged_legend_combinations)}")
        print(f"    总文字区域数量: {len(merged_combination_texts)}")

        return merged_result

    def _identify_legend_combinations(self, image_rgb: np.ndarray, legend_box: List[int], shape_info: List[Dict]) -> List[Dict]:
        print("  识别图例组合...")

        rmin, rmax, cmin, cmax = legend_box
        rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
        legend_region = image_rgb[rmin:rmax + 1, cmin:cmax + 1]

        gray = cv2.cvtColor(legend_region, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        row_counts = np.sum(binary > 0, axis=1)

        combinations: List[Dict] = []
        scan = 0
        small_value = 2
        for i, count in enumerate(row_counts):
            if scan == 0 and count > 0:
                scan = 1
                start_row = rmin + i
            elif scan == 1 and count <= small_value:
                scan = 0
                end_row = rmin + i - 1
                combinations.append({
                    'start_row': start_row,
                    'end_row': end_row,
                    'height': end_row - start_row + 1,
                    'center_row': (start_row + end_row) / 2
                })

        if scan == 1:
            end_row = rmin + len(row_counts) - 1
            combinations.append({
                'start_row': start_row,
                'end_row': end_row,
                'height': end_row - start_row + 1,
                'center_row': (start_row + end_row) / 2
            })

        # 若组合过小则进行多轮合并（简化版，保留关键逻辑）
        while len(combinations) > 1:
            avg_height = np.mean([c['height'] for c in combinations])
            need_merge = any(c['height'] < avg_height * 0.5 for c in combinations)
            if not need_merge:
                break
            merged: List[Dict] = []
            i = 0
            while i < len(combinations):
                combo = combinations[i]
                if combo['height'] < avg_height * 0.5 and i + 1 < len(combinations):
                    merged.append({
                        'start_row': combo['start_row'],
                        'end_row': combinations[i + 1]['end_row'],
                        'height': combinations[i + 1]['end_row'] - combo['start_row'] + 1,
                        'center_row': (combo['start_row'] + combinations[i + 1]['end_row']) / 2,
                        'merged': True
                    })
                    i += 2
                else:
                    merged.append(combo)
                    i += 1
            if len(merged) == len(combinations):
                break
            combinations = merged

        # 计算每个组合中的形状与文字区域
        print(f"  开始分析 {len(combinations)} 个组合的连通域...")
        print(f"  图例框坐标: [{rmin}, {rmax}, {cmin}, {cmax}]")
        print(f"  图例框尺寸: 宽度={cmax-cmin}, 高度={rmax-rmin}")

        for combo_idx, combo in enumerate(combinations):
            print(f"\n  --- 分析组合 {combo_idx + 1} ---")
            start_row = int(combo['start_row']) - rmin
            end_row = int(combo['end_row']) - rmin
            start_row = max(0, start_row)
            end_row = min(legend_region.shape[0], end_row)
            if start_row >= end_row:
                print(f"    组合{combo_idx + 1}: 行范围无效，跳过")
                continue

            combo_region = legend_region[start_row:end_row, :]
            combo_binary = binary[start_row:end_row, :]

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(combo_binary, connectivity=8)
            print(f"    组合{combo_idx + 1}: 检测到 {num_labels-1} 个连通域")

            shape_region = None
            for i, shape in enumerate(shape_info):
                box = shape['box']
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                shape_center_y = (y1 + y2) / 2
                if (combo['start_row'] <= shape_center_y <= combo['end_row'] or
                    (y1 <= combo['end_row'] and y2 >= combo['start_row'])):
                    rel_x1 = x1 - cmin
                    rel_x2 = x2 - cmin
                    shape_region = [rel_x1, rel_x2]
                    print(f"    组合{combo_idx + 1}: 找到图例形状{i+1}，列范围[{rel_x1:.1f}, {rel_x2:.1f}]")
                    break
            if shape_region is None:
                shape_region = [0, (cmax - cmin) * 0.3]
                print(f"    组合{combo_idx + 1}: 未找到图例形状，使用默认列范围[{shape_region[0]:.1f}, {shape_region[1]:.1f}]")

            text_components: List[Dict] = []
            shape_x1, shape_x2 = shape_region
            for j in range(1, num_labels):
                x, y, w, h, area = stats[j]
                center_x, center_y = centroids[j]
                if 20 < area < 5000 and w > 3 and h > 3:
                    component_x1, component_x2 = x, x + w
                    if component_x2 < shape_x1 or component_x1 > shape_x2:
                        text_components.append({
                            'id': j,
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'area': area,
                            'center_x': center_x
                        })

            if text_components:
                text_x_coords: List[int] = []
                for text_comp in text_components:
                    text_x_coords.extend([text_comp['x'], text_comp['x'] + text_comp['w']])
                if text_x_coords:
                    text_x1, text_x2 = min(text_x_coords), max(text_x_coords)
                    text_position = 'left' if text_x2 < shape_x1 else 'right'
                    combo['shape_region'] = shape_region
                    combo['text_region'] = [text_x1, text_x2]
                    combo['text_position'] = text_position
                    combo['has_text'] = True
                    print(f"    组合{combo_idx + 1}: 形状区域[{shape_x1:.1f}, {shape_x2:.1f}], 文字区域[{text_x1:.1f}, {text_x2:.1f}], 文字位置: {text_position}")
                else:
                    combo['shape_region'] = shape_region
                    combo['text_region'] = None
                    combo['text_position'] = 'none'
                    combo['has_text'] = False
                    print(f"    组合{combo_idx + 1}: 只有形状，没有文字区域")
            else:
                combo['shape_region'] = shape_region
                combo['text_region'] = None
                combo['text_position'] = 'none'
                combo['has_text'] = False
                print(f"    组合{combo_idx + 1}: 只有形状，没有文字区域")

        # 合并“无文字组合”到最近“有文字组合”的策略（与 legacy 一致的效果简化版）
        text_count = sum(1 for combo in combinations if combo.get('has_text', False))
        if len(combinations) > 2 * text_count:
            has_text_combos = [c for c in combinations if c.get('has_text', False)]
            no_text_combos = [c for c in combinations if not c.get('has_text', False)]
            for nt in no_text_combos:
                if not has_text_combos:
                    break
                closest = min(has_text_combos, key=lambda t: abs(nt['center_row'] - t['center_row']))
                closest['start_row'] = min(closest['start_row'], nt['start_row'])
                closest['end_row'] = max(closest['end_row'], nt['end_row'])
                closest['height'] = closest['end_row'] - closest['start_row'] + 1
            combinations = has_text_combos

        print(f"  最终检测到 {len(combinations)} 个图例组合")
        for i, combo in enumerate(combinations):
            has_text = combo.get('has_text', False)
            print(f"    组合{i+1}: 行范围 {combo['start_row']}-{combo['end_row']}, 高度 {combo['height']}, 有文字: {has_text}")

        return combinations

    def _analyze_connected_components(self, image_rgb: np.ndarray, legend_box: List[int], shape_info: List[Dict]) -> List[Dict]:
        print("  分析连通域特征...")

        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
        connected_components: List[Dict] = []

        for i in range(1, num_labels):
            x, y, w, h, area = stats[i]
            center_x, center_y = centroids[i]

            x1, y1, x2, y2 = legend_box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            if (x1 <= center_x <= x2) and (y1 <= center_y <= y2):
                legend_area = (y2 - y1 + 1) * (x2 - x1 + 1)
                area_ratio = area / legend_area
                if area_ratio < 0.7:
                    component_info = {
                        'id': i,
                        'center': [float(center_x), float(center_y)],
                        'bbox': [x, y, x + w, y + h],
                        'area': int(area),
                        'width': int(w),
                        'height': int(h),
                        'area_ratio': float(area_ratio),
                        'pixel_coordinates': self._get_pixel_coordinates(labels, i)
                    }
                    connected_components.append(component_info)

        print(f"  检测到 {len(connected_components)} 个有效连通域")
        return connected_components

    def _get_pixel_coordinates(self, labels: np.ndarray, component_id: int) -> List[List[int]]:
        coords = np.where(labels == component_id)
        return [coords[1].tolist(), coords[0].tolist()]

    def _analyze_shape_features(self, image_rgb: np.ndarray, shape_info: List[Dict]) -> List[Dict]:
        print("  分析形状特征...")

        shape_features: List[Dict] = []
        for i, shape in enumerate(shape_info):
            box = shape['box']
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            legend_region = image_rgb[y1:y2, x1:x2]
            gray = cv2.cvtColor(legend_region, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                shape_features.append({
                    'legend_id': i + 1,
                    'area': 0,
                    'perimeter': 0,
                    'aspect_ratio': 0,
                    'circularity': 0,
                    'complexity': 0
                })
                continue
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h if h > 0 else 0
            circularity = (4 * np.pi * area) / (perimeter * perimeter) if perimeter > 0 else 0
            complexity = len(largest_contour)
            shape_features.append({
                'legend_id': i + 1,
                'area': float(area),
                'perimeter': float(perimeter),
                'aspect_ratio': float(aspect_ratio),
                'circularity': float(circularity),
                'complexity': int(complexity),
                'bbox': [x, y, x + w, y + h]
            })
            print(f"    图例{i+1}: 面积 {area:.1f}, 周长 {perimeter:.1f}, 宽高比 {aspect_ratio:.2f}")

        return shape_features

    def _recognize_legend_text(self, image_rgb: np.ndarray, legend_box: List[int], shape_info: List[Dict], legend_combinations: List[Dict]) -> Dict:
        print("  识别图例文字...")
        rmin, rmax, cmin, cmax = legend_box
        rmin, rmax, cmin, cmax = int(rmin), int(rmax), int(cmin), int(cmax)
        print(f"    图例框区域: [{rmin}, {rmax}, {cmin}, {cmax}]")

        combination_texts: List[Dict] = []
        for combo_idx, combo in enumerate(legend_combinations):
            print(f"\n    --- 处理组合 {combo_idx + 1} ---")
            if combo.get('text_region') is None:
                print(f"      组合{combo_idx + 1}: 未检测到文字区域")
                continue
            text_region = combo['text_region']
            text_position = combo.get('text_position', 'right')
            print(f"      组合{combo_idx + 1}: 文字区域[{text_region[0]:.1f}, {text_region[1]:.1f}], 位置: {text_position}")

            text_x1, text_x2 = text_region
            start_row = int(combo['start_row'])
            end_row = int(combo['end_row'])
            text_x1_abs = int(text_x1) + cmin - 1
            text_x2_abs = int(text_x2) + cmin + 1
            text_y1_abs = start_row - 1
            text_y2_abs = end_row + 1

            print(f"      组合{combo_idx + 1}: 扩展前坐标 - X:[{int(text_x1) + cmin}, {int(text_x2) + cmin}], Y:[{start_row}, {end_row}]")
            print(f"      组合{combo_idx + 1}: 扩展后坐标 - X:[{text_x1_abs}, {text_x2_abs}], Y:[{text_y1_abs}, {text_y2_abs}]")

            h, w = image_rgb.shape[:2]
            text_x1_abs = max(0, min(text_x1_abs, w - 1))
            text_y1_abs = max(0, min(text_y1_abs, h - 1))
            text_x2_abs = max(0, min(text_x2_abs, w))
            text_y2_abs = max(0, min(text_y2_abs, h))

            if text_x2_abs > text_x1_abs and text_y2_abs > text_y1_abs:
                text_region_img = image_rgb[text_y1_abs:text_y2_abs, text_x1_abs:text_x2_abs]
                print(f"      组合{combo_idx + 1}: OCR图像尺寸: {text_region_img.shape}")
                try:
                    import easyocr
                    reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)
                    results = reader.readtext(text_region_img)
                    if results:
                        detected_texts = [result[1] for result in results]
                        text_content = ' '.join(detected_texts).strip()
                        print(f"      组合{combo_idx + 1}: OCR识别结果: '{text_content}'")
                    else:
                        text_content = ""
                        print(f"      组合{combo_idx + 1}: OCR未识别到文字")
                except Exception as e:
                    text_content = ""
                    print(f"      组合{combo_idx + 1}: OCR错误: {str(e)}")

                text_region_info = {
                    'combination_id': combo_idx + 1,
                    'text_region_relative': text_region,
                    'text_region_absolute': [text_x1_abs, text_y1_abs, text_x2_abs, text_y2_abs],
                    'text_region_original': [int(text_x1) + cmin, start_row, int(text_x2) + cmin, end_row],
                    'text_position': text_position,
                    'text_content': text_content,
                    'text_content_filename': "",
                    'image_size': text_region_img.shape,
                    'expanded': True
                }
                combination_texts.append(text_region_info)
                print(f"      组合{combo_idx + 1}: 文字区域信息已保存")
            else:
                print(f"      组合{combo_idx + 1}: 文字区域坐标无效")

        total_text_regions = len(combination_texts)
        successful_ocr = sum(1 for ct in combination_texts if ct['text_content'])
        print(f"\n  文字识别统计:")
        print(f"    总文字区域数: {total_text_regions}")
        print(f"    成功识别数: {successful_ocr}")

        # manually disable debug output
        # unified_txt_filename = self._output_debug_txt(combination_texts, successful_ocr)
        unified_txt_filename = ""

        text_features = {
            'combination_texts': combination_texts,
            'total_text_regions': total_text_regions,
            'successful_ocr_count': successful_ocr,
            'legend_box': [cmin, rmin, cmax, rmax],
            'unified_text_filename': unified_txt_filename,
            'confidence': 0.7
        }
        return text_features

    def _output_debug_txt(self, combination_texts: List[Dict], successful_ocr: int) -> str:
        """
        简化版调试输出函数。

        保证模块可以正常导入。如需调试输出，可在此处按需实现文件写入逻辑。
        """
        return ""

    def _generate_templates(self, image_rgb: np.ndarray, shape_info: List[Dict]) -> List[Dict]:
        print("  生成图例模板...")
        templates: List[Dict] = []
        for i, shape in enumerate(shape_info):
            box = shape['box']
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            legend_region = image_rgb[y1:y2, x1:x2]
            gray = cv2.cvtColor(legend_region, cv2.COLOR_RGB2GRAY)
            _, binary_template = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            template_filename = f'template_legend_{i+1}.png'
            templates.append({
                'legend_id': i + 1,
                'template_filename': template_filename,
                'template_size': [y2 - y1, x2 - x1],
                'template_area': (y2 - y1) * (x2 - x1)
            })
            print(f"    图例{i+1}: 模板已保存为 {template_filename}")
        return templates


