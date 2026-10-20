import cv2
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
from app.config import UPLOAD_DIR, OUTPUT_DIR
import uuid

class TextureService:
    def apply_materials(self, image_path: str, segments: list, assignments: list, materials: dict) -> str:
        """
        Apply material textures to segments on the original image.
        assignments: [{segment_id, material_id}]
        materials: {material_id: material_doc}
        Returns filename of redesigned image.
        """
        img_path = Path(image_path)
        if not img_path.is_absolute():
            img_path = UPLOAD_DIR / image_path
            
        image = cv2.imread(str(img_path))
        if image is None:
            raise FileNotFoundError(f"Failed to read image at {img_path}")
        result = image.copy()
        h, w = image.shape[:2]
        
        # Build assignment lookup
        assign_map = {a['segment_id']: a['material_id'] for a in assignments}
        
        for seg in segments:
            mat_id = assign_map.get(seg['id'])
            if not mat_id or mat_id not in materials:
                continue
            
            material = materials[mat_id]
            polygon = np.array(seg['polygon'], dtype=np.int32)
            
            # Create mask for this segment
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [polygon], 255)
            
            # Generate texture pattern
            texture = self._generate_texture(w, h, material)
            
            # Blend texture onto result using mask
            # Use original image luminance to preserve depth/shadow
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
            
            # Modulate texture by original lighting
            textured = (texture.astype(np.float32) * (0.3 + 0.7 * gray_3ch)).clip(0, 255).astype(np.uint8)
            
            # Apply with alpha blending
            alpha = 0.80
            mask_3ch = cv2.merge([mask, mask, mask]) / 255.0
            result = (result * (1 - mask_3ch * alpha) + textured * mask_3ch * alpha).astype(np.uint8)
            
            # Edge feathering - blur the mask edges slightly
            mask_blurred = cv2.GaussianBlur(mask.astype(np.float32), (5, 5), 2) / 255.0
            edge_mask = ((mask.astype(np.float32)/255.0 - mask_blurred) > 0.1).astype(np.float32)
            edge_3ch = cv2.merge([edge_mask, edge_mask, edge_mask])
            result = (result * (1 - edge_3ch * 0.3) + image * edge_3ch * 0.3).astype(np.uint8)
        
        # Save result
        output_filename = f"redesigned_{uuid.uuid4().hex[:8]}.png"
        cv2.imwrite(str(OUTPUT_DIR / output_filename), result)
        return output_filename
    
    def _generate_texture(self, width: int, height: int, material: dict) -> np.ndarray:
        """Generate a texture image based on material properties."""
        color_hex = material.get('color', '#CCCCCC')
        pattern = material.get('pattern', 'solid')
        
        # Parse hex color to BGR
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        base_color = np.array([b, g, r], dtype=np.uint8)
        
        texture = np.full((height, width, 3), base_color, dtype=np.uint8)
        
        if pattern == 'solid':
            # Add slight noise for realism
            noise = np.random.randint(-8, 8, texture.shape, dtype=np.int16)
            texture = np.clip(texture.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
        elif pattern == 'brick':
            # Brick/stone pattern
            brick_h, brick_w = 30, 60
            grout_color = np.clip(base_color.astype(np.int16) - 40, 0, 255).astype(np.uint8)
            for y in range(0, height, brick_h):
                cv2.line(texture, (0, y), (width, y), grout_color.tolist(), 2)
                offset = (brick_w // 2) if (y // brick_h) % 2 else 0
                for x in range(offset, width, brick_w):
                    cv2.line(texture, (x, y), (x, y + brick_h), grout_color.tolist(), 2)
            # Add noise
            noise = np.random.randint(-12, 12, texture.shape, dtype=np.int16)
            texture = np.clip(texture.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
        elif pattern == 'grid':
            # Tile grid pattern
            tile_size = 40
            grout_color = np.clip(base_color.astype(np.int16) - 30, 0, 255).astype(np.uint8)
            for y in range(0, height, tile_size):
                cv2.line(texture, (0, y), (width, y), grout_color.tolist(), 2)
            for x in range(0, width, tile_size):
                cv2.line(texture, (x, 0), (x, height), grout_color.tolist(), 2)
            noise = np.random.randint(-5, 5, texture.shape, dtype=np.int16)
            texture = np.clip(texture.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
        elif pattern == 'horizontal_strips':
            strip_h = 25
            alt_color = np.clip(base_color.astype(np.int16) + 20, 0, 255).astype(np.uint8)
            for y in range(0, height, strip_h * 2):
                texture[y:y+strip_h] = alt_color
            # Subtle line between strips
            line_color = np.clip(base_color.astype(np.int16) - 20, 0, 255).astype(np.uint8)
            for y in range(0, height, strip_h):
                cv2.line(texture, (0, y), (width, y), line_color.tolist(), 1)
                
        elif pattern == 'vertical_strips':
            strip_w = 25
            alt_color = np.clip(base_color.astype(np.int16) + 20, 0, 255).astype(np.uint8)
            for x in range(0, width, strip_w * 2):
                texture[:, x:x+strip_w] = alt_color
            line_color = np.clip(base_color.astype(np.int16) - 20, 0, 255).astype(np.uint8)
            for x in range(0, width, strip_w):
                cv2.line(texture, (x, 0), (x, height), line_color.tolist(), 1)
                
        elif pattern == 'lines':
            # Railing-like pattern — vertical lines with spacing
            spacing = 15
            line_color = np.clip(base_color.astype(np.int16) - 50, 0, 255).astype(np.uint8)
            for x in range(0, width, spacing):
                cv2.line(texture, (x, 0), (x, height), line_color.tolist(), 2)
            # Horizontal bars
            for y_frac in [0.2, 0.5, 0.8]:
                y = int(height * y_frac)
                cv2.line(texture, (0, y), (width, y), line_color.tolist(), 3)
        
        return texture
