from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from app.config import OUTPUT_DIR

router = APIRouter(tags=["Reports"])

@router.get("/report/{project_id}")
async def generate_project_report(project_id: str, request: Request):
    """Generate and download a PDF estimate report for the given project."""
    db = request.app.state.db
    
    project = await db.projects.find_one({"_id": project_id})
    if not project and ObjectId.is_valid(project_id):
        project = await db.projects.find_one({"_id": ObjectId(project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Fetch all materials
    cursor = db.materials.find({})
    materials_dict = {}
    async for m in cursor:
        m_id = str(m["_id"])
        m["id"] = m_id
        materials_dict[m_id] = m
        if "name" in m:
            materials_dict[m["name"]] = m
        
    estimates = project.get("estimates")
    if not estimates:
        # Fallback estimation if not yet calculated
        segments = project.get("segments", [])
        estimator_service = getattr(request.app.state, "estimator", None)
        if estimator_service and segments:
            ref_seg = project.get("reference_segment_id") or ""
            ref_dim = project.get("reference_dimension_ft") or 10.0
            estimates = estimator_service.calculate(segments, materials_dict, ref_seg, ref_dim)
        else:
            estimates = {
                "breakdown": [],
                "total_material_cost": 0,
                "total_labor_cost": 0,
                "grand_total": 0,
                "px_per_ft": 10.0
            }
            
    report_gen = getattr(request.app.state, "report_gen", None)
    if not report_gen:
        raise HTTPException(status_code=500, detail="Report generator service is not initialized")
        
    try:
        pdf_filename = report_gen.generate_pdf(project, materials_dict, estimates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
        
    pdf_path = OUTPUT_DIR / pdf_filename
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail="Generated PDF file not found on disk")
        
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"renovation_estimate_{project_id}.pdf"
    )
