import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Optional

class YOLOService:
    def __init__(self, model_path: str, device: str = "cpu"):
        """初始化 YOLO 服务
        
        Args:
            model_path: 模型文件路径
            device: 运行设备，'cpu' 或 'cuda' (默认: 'cpu')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载 YOLO 模型"""
        try:
            self.model = YOLO(self.model_path)
            # 将模型移到指定设备
            self.model.to(self.device)
            print(f"成功加载模型: {self.model_path} (device: {self.device})")
        except Exception as e:
            print(f"加载模型失败: {self.model_path}, 错误: {e}")
            raise
    
    async def detect(self, image_path: str, confidence_threshold: float = 0.5) -> List[Dict]:
        """执行目标检测"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # 执行预测，显式指定设备
        results = self.model.predict(
            image_path,
            conf=confidence_threshold,
            save=False,
            verbose=False,
            device=self.device
        )
        
        detections = []
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                scores = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                
                for box, score, cls in zip(boxes, scores, classes):
                    x1, y1, x2, y2 = box
                    detection = {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                        "confidence": float(score),
                        "class": int(cls),
                        "label": self.model.names.get(int(cls), "unknown")
                    }
                    detections.append(detection)
        
        return detections
    
    async def detect_image(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict]:
        """对 numpy 数组格式的图像执行检测"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # 执行预测，显式指定设备
        results = self.model.predict(
            image,
            conf=confidence_threshold,
            save=False,
            verbose=False,
            device=self.device
        )
        
        detections = []
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                scores = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                
                for box, score, cls in zip(boxes, scores, classes):
                    x1, y1, x2, y2 = box
                    detection = {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                        "confidence": float(score),
                        "class": int(cls),
                        "label": self.model.names.get(int(cls), "unknown")
                    }
                    detections.append(detection)
        
        return detections
    
    def merge_boxes(self, detections: List[Dict], merge_threshold: float = 1.0) -> List[Dict]:
        """合并接近的检测框（用于图例检测）"""
        if not detections:
            return []
        
        merged = []
        for det in detections:
            merged_flag = False
            
            for i, merged_det in enumerate(merged):
                # 检查是否在同一列（x坐标接近）
                if (abs(det["x1"] - merged_det["x1"]) <= merge_threshold or 
                    abs(det["x2"] - merged_det["x2"]) <= merge_threshold):
                    
                    # 合并边界框
                    merged[i] = {
                        "x1": min(merged_det["x1"], det["x1"]),
                        "y1": min(merged_det["y1"], det["y1"]),
                        "x2": max(merged_det["x2"], det["x2"]),
                        "y2": max(merged_det["y2"], det["y2"]),
                        "confidence": max(merged_det["confidence"], det["confidence"]),
                        "class": merged_det["class"],
                        "label": merged_det["label"]
                    }
                    merged_flag = True
                    break
            
            if not merged_flag:
                merged.append(det.copy())
        
        return merged
    
    def filter_by_size(self, detections: List[Dict], min_area: float = 100) -> List[Dict]:
        """根据最小面积过滤检测结果"""
        filtered = []
        for det in detections:
            width = det["x2"] - det["x1"]
            height = det["y2"] - det["y1"]
            area = width * height
            
            if area >= min_area:
                filtered.append(det)
        
        return filtered
    
    def non_max_suppression(self, detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
        """非极大值抑制"""
        if not detections:
            return []
        
        # 转换为 numpy 数组
        boxes = np.array([[d["x1"], d["y1"], d["x2"], d["y2"]] for d in detections])
        scores = np.array([d["confidence"] for d in detections])
        
        # 计算面积
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        
        # 按置信度排序
        order = scores.argsort()[::-1]
        
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            
            # 计算 IoU
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h
            
            iou = inter / (areas[i] + areas[order[1:]] - inter)
            
            # 保留 IoU 小于阈值的框
            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]
        
        return [detections[i] for i in keep]