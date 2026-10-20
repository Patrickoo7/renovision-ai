import asyncio
import cv2
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import os
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import UPLOAD_DIR, OUTPUT_DIR
from app.database import get_db, client
from app.seed.materials import seed_materials
from app.services.segmentation import SegmentationService
from app.services.texture import TextureService
from app.services.estimator import EstimatorService
from app.services.report_gen import ReportGenerator

def create_synthetic_house_image(path: Path):
    """Draws a synthetic exterior house photo (800x600) for testing."""
    img = np.full((600, 800, 3), (240, 240, 240), dtype=np.uint8)
    
    # Sky
    cv2.rectangle(img, (0, 0), (800, 200), (235, 206, 135), -1)
    
    # Ground
    cv2.rectangle(img, (0, 520), (800, 600), (100, 100, 100), -1)
    
    # Main Building Wall
    cv2.rectangle(img, (150, 150), (650, 520), (210, 210, 220), -1)
    
    # Roof / Parapet
    cv2.rectangle(img, (130, 120), (670, 150), (80, 80, 90), -1)
    
    # Second Floor Windows
    cv2.rectangle(img, (200, 180), (280, 280), (120, 90, 60), -1)
    cv2.rectangle(img, (520, 180), (600, 280), (120, 90, 60), -1)
    
    # Balcony (Middle level)
    cv2.rectangle(img, (320, 240), (480, 320), (180, 180, 190), -1)
    cv2.rectangle(img, (320, 300), (480, 340), (150, 150, 160), -1) # railing zone
    
    # Ground Floor Windows & Door
    cv2.rectangle(img, (200, 380), (280, 480), (120, 90, 60), -1)
    cv2.rectangle(img, (360, 380), (440, 520), (60, 40, 30), -1) # Entrance door
    cv2.rectangle(img, (520, 380), (600, 480), (120, 90, 60), -1)
    
    # Boundary Gate at bottom
    cv2.rectangle(img, (250, 510), (550, 560), (40, 40, 40), -1)
    
    # Add subtle texture noise
    noise = np.random.randint(-10, 10, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    cv2.imwrite(str(path), img)
    print(f"Synthetic house test image created at {path}")

async def run_e2e_test():
    print("=" * 60)
    print("E2M SOLUTIONS - COMPLETE PIPELINE VERIFICATION")
    print("=" * 60)
    
    db = get_db()
    
    # 1. Test Database & Seeding
    print("\n1. Testing MongoDB connection & seeding...")
    await seed_materials(db)
    mat_count = await db.materials.count_documents({})
    print(f"   [PASS] MongoDB connected. Materials catalog has {mat_count} items.")
    
    # 2. Test Image Creation
    test_img_path = UPLOAD_DIR / "test_house_exterior.jpg"
    create_synthetic_house_image(test_img_path)
    
    # 3. Test Segmentation Service
    print("\n2. Testing AI Segmentation Service (SAM ViT-B on GPU)...")
    seg_service = SegmentationService()
    seg_service.load_model()
    segments, mask_filename = seg_service.segment_image(str(test_img_path))
    print(f"   [PASS] Segmentation complete! Detected {len(segments)} architectural segments.")
    print(f"   [PASS] Segment mask visual saved: {OUTPUT_DIR / mask_filename}")
    for s in segments[:5]:
        print(f"      - Segment {s['id']}: label='{s['label']}', area={s['area_px']}px, bbox={s['bbox']}")
    
    # 4. Test Texture & Material Application
    print("\n3. Testing Texture & Redesign Visualization Service...")
    cursor = db.materials.find({})
    materials_dict = {}
    async for m in cursor:
        m_id = str(m["_id"])
        m["id"] = m_id
        materials_dict[m_id] = m
        if "name" in m:
            materials_dict[m["name"]] = m
            
    # Assign materials to first few segments
    mat_list = list(materials_dict.values())
    assignments = []
    for i, seg in enumerate(segments):
        assigned_mat = mat_list[i % len(mat_list)]
        seg['material_id'] = str(assigned_mat['_id'])
        assignments.append({
            "segment_id": seg['id'],
            "material_id": str(assigned_mat['_id'])
        })
        
    tex_service = TextureService()
    redesigned_filename = tex_service.apply_materials(
        test_img_path.name,
        segments,
        assignments,
        materials_dict
    )
    print(f"   [PASS] Redesign visualization generated: {OUTPUT_DIR / redesigned_filename}")
    
    # 5. Test Cost & Area Estimation Service
    print("\n4. Testing Area & Cost Estimation Service...")
    estimator = EstimatorService()
    ref_seg_id = segments[0]['id'] if segments else ""
    estimates = estimator.calculate(segments, materials_dict, ref_seg_id, 12.0)
    print(f"   [PASS] Cost estimation calculated successfully!")
    print(f"      - Scale factor: {estimates.get('px_per_ft')} px/ft")
    print(f"      - Line items estimated: {len(estimates.get('breakdown', []))}")
    print(f"      - Material Cost Subtotal: Rs. {estimates.get('total_material_cost'):,.2f}")
    print(f"      - Labor Cost Subtotal: Rs. {estimates.get('total_labor_cost'):,.2f}")
    print(f"      - Grand Total: Rs. {estimates.get('grand_total'):,.2f}")
    
    # 6. Test PDF Report Generation
    print("\n5. Testing PDF Report Generation (ReportLab)...")
    report_gen = ReportGenerator()
    project_mock = {
        "_id": "test_proj_001",
        "original_image": test_img_path.name,
        "redesigned_image": redesigned_filename
    }
    pdf_filename = report_gen.generate_pdf(project_mock, materials_dict, estimates)
    pdf_path = OUTPUT_DIR / pdf_filename
    print(f"   [PASS] PDF Report generated at {pdf_path} (size: {pdf_path.stat().st_size} bytes)")
    
    client.close()
    print("\n" + "=" * 60)
    print("ALL CORE SERVICES VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
