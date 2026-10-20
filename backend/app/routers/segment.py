from pathlib import Path
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from app.config import UPLOAD_DIR, OUTPUT_DIR

router = APIRouter(tags=["Segmentation"])

@router.post("/segment/{project_id}")
async def segment_building(project_id: str, request: Request):
    """Run AI segmentation on the project image and return detected architectural segments."""
    db = request.app.state.db
    
    project = await db.projects.find_one({"_id": project_id})
    if not project and ObjectId.is_valid(project_id):
        project = await db.projects.find_one({"_id": ObjectId(project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    image_filename = project.get("original_image")
    if not image_filename:
        raise HTTPException(status_code=400, detail="Project does not have an associated image")
        
    image_path = UPLOAD_DIR / image_filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Original image file not found on disk")
        
    seg_service = getattr(request.app.state, "segmentation", None)
    if not seg_service:
        raise HTTPException(status_code=500, detail="Segmentation service is not initialized")
        
    try:
        segments, mask_filename = seg_service.segment_image(str(image_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")
        
    try:
        await db.projects.update_one(
            {"_id": project["_id"]},
            {"$set": {"segments": segments}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project segments: {str(e)}")
        
    base_url = str(request.base_url).rstrip("/")
    mask_image_url = f"{base_url}/outputs/{mask_filename}"
    
    return {
        "project_id": str(project["_id"]),
        "segments": segments,
        "mask_image_url": mask_image_url
    }

from pydantic import BaseModel
from typing import List, Any, Dict

class UpdateSegmentsRequest(BaseModel):
    segments: List[Dict[str, Any]]

@router.put("/project/{project_id}/segments")
async def update_project_segments(project_id: str, req: UpdateSegmentsRequest, request: Request):
    """Save user-adjusted or relabeled segments for the project."""
    db = request.app.state.db
    project = await db.projects.find_one({"_id": project_id})
    if not project and ObjectId.is_valid(project_id):
        project = await db.projects.find_one({"_id": ObjectId(project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        await db.projects.update_one(
            {"_id": project["_id"]},
            {"$set": {"segments": req.segments}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update segments: {str(e)}")
        
    return {"status": "success", "segment_count": len(req.segments)}

