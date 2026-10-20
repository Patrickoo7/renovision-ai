from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["Design"])

class MaterialAssignment(BaseModel):
    segment_id: str
    material_id: str

class ApplyMaterialsRequest(BaseModel):
    project_id: str
    assignments: List[MaterialAssignment]

@router.post("/apply-materials")
async def apply_materials(req: ApplyMaterialsRequest, request: Request):
    """Apply chosen materials/textures to building segments and generate redesigned visual."""
    db = request.app.state.db
    
    project = await db.projects.find_one({"_id": req.project_id})
    if not project and ObjectId.is_valid(req.project_id):
        project = await db.projects.find_one({"_id": ObjectId(req.project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    segments = project.get("segments", [])
    if not segments:
        raise HTTPException(status_code=400, detail="No segments found. Please run segmentation first.")
        
    # Fetch all materials to build lookup
    cursor = db.materials.find({})
    materials_dict = {}
    async for m in cursor:
        m_id = str(m["_id"])
        m["id"] = m_id
        materials_dict[m_id] = m
        if "name" in m:
            materials_dict[m["name"]] = m
        
    texture_service = getattr(request.app.state, "texture", None)
    if not texture_service:
        raise HTTPException(status_code=500, detail="Texture service is not initialized")
        
    assignments_data = [{"segment_id": a.segment_id, "material_id": a.material_id} for a in req.assignments]
    
    try:
        redesigned_filename = texture_service.apply_materials(
            project["original_image"],
            segments,
            assignments_data,
            materials_dict
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply materials: {str(e)}")
        
    # Update segment material_id in project segments
    assign_map = {a.segment_id: a.material_id for a in req.assignments}
    for seg in segments:
        if seg["id"] in assign_map:
            seg["material_id"] = assign_map[seg["id"]]
            
    try:
        await db.projects.update_one(
            {"_id": project["_id"]},
            {"$set": {
                "redesigned_image": redesigned_filename,
                "segments": segments
            }}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
        
    base_url = str(request.base_url).rstrip("/")
    redesigned_image_url = f"{base_url}/outputs/{redesigned_filename}"
    
    return {
        "project_id": str(project["_id"]),
        "redesigned_image_url": redesigned_image_url
    }
