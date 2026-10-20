from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["Estimates"])

class EstimateRequest(BaseModel):
    project_id: str
    reference_segment_id: Optional[str] = None
    reference_dimension_ft: Optional[float] = 10.0

@router.post("/estimate")
async def calculate_estimate(req: EstimateRequest, request: Request):
    """Calculate cost estimate for the renovation based on segment materials and dimension scaling."""
    db = request.app.state.db
    
    project = await db.projects.find_one({"_id": req.project_id})
    if not project and ObjectId.is_valid(req.project_id):
        project = await db.projects.find_one({"_id": ObjectId(req.project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    segments = project.get("segments", [])
    if not segments:
        raise HTTPException(status_code=400, detail="No segments found. Please segment the image first.")
        
    # Fetch all materials
    cursor = db.materials.find({})
    materials_dict = {}
    async for m in cursor:
        m_id = str(m["_id"])
        m["id"] = m_id
        materials_dict[m_id] = m
        if "name" in m:
            materials_dict[m["name"]] = m
        
    estimator_service = getattr(request.app.state, "estimator", None)
    if not estimator_service:
        raise HTTPException(status_code=500, detail="Estimator service is not initialized")
        
    dimension_ft = req.reference_dimension_ft if (req.reference_dimension_ft and req.reference_dimension_ft > 0) else 10.0
    
    try:
        estimates = estimator_service.calculate(
            segments,
            materials_dict,
            req.reference_segment_id or "",
            dimension_ft
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")
        
    try:
        await db.projects.update_one(
            {"_id": project["_id"]},
            {"$set": {
                "reference_segment_id": req.reference_segment_id,
                "reference_dimension_ft": req.reference_dimension_ft,
                "estimates": estimates
            }}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
        
    return {
        "project_id": str(project["_id"]),
        **estimates
    }
