import numpy as np
import cv2
from pathlib import Path
import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
from app.config import MODEL_DIR, SAM_CHECKPOINT, OUTPUT_DIR
import uuid

class SegmentationService:
    def __init__(self):
        self.model = None
        self.mask_generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        checkpoint = MODEL_DIR / SAM_CHECKPOINT
        if not checkpoint.exists():
            raise FileNotFoundError(f"SAM checkpoint not found at {checkpoint}")
        sam = sam_model_registry["vit_b"](checkpoint=str(checkpoint))
        sam.to(self.device)
        self.model = sam
        self.mask_generator = SamAutomaticMaskGenerator(
            model=sam,
            points_per_side=16,  # Lower for speed on GTX 1650 Ti
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            min_mask_region_area=500,
        )
        print(f"SAM model loaded on {self.device}")
    
    def segment_image(self, image_path: str) -> tuple[list[dict], str]:
        """Returns (segments_list, mask_image_path)"""
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Failed to read image at {image_path}")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        
        if self.mask_generator is None:
            self.load_model()
        
        # Generate masks
        masks = self.mask_generator.generate(image_rgb)
        
        # Sort by area (largest first)
        masks = sorted(masks, key=lambda x: x['area'], reverse=True)
        
        # Filter: keep top 20 meaningful masks
        masks = masks[:20]
        
        segments = []
        mask_overlay = image.copy()
        
        # Color palette for segments
        colors = [
            (66, 133, 244), (234, 67, 53), (52, 168, 83), (251, 188, 4),
            (255, 109, 0), (171, 71, 188), (0, 172, 193), (124, 179, 66),
            (255, 167, 38), (141, 110, 99), (48, 63, 159), (0, 137, 123),
            (121, 85, 72), (158, 157, 36), (33, 150, 243), (255, 87, 34),
            (103, 58, 183), (0, 150, 136), (205, 220, 57), (255, 193, 7)
        ]
        
        for i, mask_data in enumerate(masks):
            mask = mask_data['segmentation']  # Boolean mask
            bbox = mask_data['bbox']  # [x, y, w, h]
            area_px = int(mask_data['area'])
            
            # Get polygon from mask contours
            mask_uint8 = (mask * 255).astype(np.uint8)
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                continue
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            # Simplify polygon
            epsilon = 0.01 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            polygon = approx.squeeze().tolist()
            if not isinstance(polygon, list) or len(polygon) < 3 or isinstance(polygon[0], int):
                continue
            
            # Heuristic label
            label = self._heuristic_label(bbox, area_px, h, w)
            
            seg_id = str(uuid.uuid4())[:8]
            segments.append({
                "id": seg_id,
                "label": label,
                "bbox": [int(b) for b in bbox],
                "area_px": area_px,
                "polygon": polygon,
                "material_id": None
            })
            
            # Draw on overlay
            color = colors[i % len(colors)]
            mask_colored = np.zeros_like(image)
            mask_colored[mask] = color
            mask_overlay = cv2.addWeighted(mask_overlay, 1, mask_colored, 0.35, 0)
            
            # Draw contour
            cv2.drawContours(mask_overlay, [largest_contour], -1, color, 2)
            
            # Label text
            cx, cy = int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2)
            cv2.putText(mask_overlay, f"{label}", (cx-20, cy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        
        # Save mask overlay image
        mask_filename = f"mask_{uuid.uuid4().hex[:8]}.png"
        mask_path = str(OUTPUT_DIR / mask_filename)
        cv2.imwrite(mask_path, mask_overlay)
        
        return segments, mask_filename
    
    def _heuristic_label(self, bbox, area_px, img_h, img_w) -> str:
        """Classify segment by position and size heuristics"""
        x, y, bw, bh = bbox
        cx = x + bw / 2
        cy = y + bh / 2
        
        total_area = img_h * img_w
        area_ratio = area_px / total_area
        aspect_ratio = bw / max(bh, 1)
        
        # Relative positions
        rel_y = cy / img_h  # 0=top, 1=bottom
        rel_x = cx / img_w
        
        # Largest region covering most of image → wall
        if area_ratio > 0.15:
            return "wall"
        
        # Top region → roof/parapet
        if rel_y < 0.15 and aspect_ratio > 1.5:
            return "parapet"
        if rel_y < 0.1:
            return "roof"
        
        # Bottom region → gate
        if rel_y > 0.85:
            return "gate"
        
        # Small rectangular in middle → window
        if 0.002 < area_ratio < 0.08 and 0.5 < aspect_ratio < 2.5 and 0.15 < rel_y < 0.75:
            return "window"
        
        # Tall narrow → pillar
        if aspect_ratio < 0.4 and area_ratio < 0.1:
            return "pillar"
        
        # Wide region in middle height → balcony
        if aspect_ratio > 2.0 and 0.3 < rel_y < 0.7 and area_ratio > 0.03:
            return "balcony"
        
        # Horizontal at mid-top → parapet
        if aspect_ratio > 3.0 and rel_y < 0.3:
            return "parapet"
        
        # Default
        return "wall"
