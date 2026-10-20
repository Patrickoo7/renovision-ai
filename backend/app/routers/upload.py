import uuid
from datetime import datetime, timezone
from pathlib import Path
from bson import ObjectId
import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException, Request

from app.config import UPLOAD_DIR, MAX_IMAGE_SIZE
from app.utils.image import validate_image, generate_filename

router = APIRouter(tags=["Projects & Uploads"])

@router.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """Upload an exterior building image and create a new project."""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    contents = await file.read()
    size = len(contents)
    
    is_valid, msg = validate_image(file.content_type or "", size, MAX_IMAGE_SIZE)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    
    ext = Path(file.filename or "").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".jpg" if "png" not in (file.content_type or "") else ".png"
    
    filename = generate_filename(ext)
    file_path = UPLOAD_DIR / filename
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image file: {str(e)}")
    
    project_id = uuid.uuid4().hex
    project_doc = {
        "_id": project_id,
        "original_image": filename,
        "segments": [],
        "redesigned_image": None,
        "reference_segment_id": None,
        "reference_dimension_ft": None,
        "estimates": None,
        "created_at": datetime.now(timezone.utc)
    }
    
    db = request.app.state.db
    try:
        await db.projects.insert_one(project_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error creating project: {str(e)}")
    
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/uploads/{filename}"
    
    return {
        "project_id": project_id,
        "filename": filename,
        "image_url": image_url
    }

@router.get("/project/{project_id}")
async def get_project(project_id: str, request: Request):
    """Retrieve full project state including segments and estimates."""
    db = request.app.state.db
    
    project = await db.projects.find_one({"_id": project_id})
    if not project and ObjectId.is_valid(project_id):
        project = await db.projects.find_one({"_id": ObjectId(project_id)})
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project["id"] = str(project["_id"])
    project["_id"] = str(project["_id"])
    
    base_url = str(request.base_url).rstrip("/")
    if project.get("original_image"):
        project["original_image_url"] = f"{base_url}/uploads/{project['original_image']}"
    if project.get("redesigned_image"):
        project["redesigned_image_url"] = f"{base_url}/outputs/{project['redesigned_image']}"
    
    if isinstance(project.get("created_at"), datetime):
        project["created_at"] = project["created_at"].isoformat()
        
    return project

@router.get("/materials")
async def get_materials(request: Request):
    """Retrieve all available exterior renovation materials."""
    db = request.app.state.db
    cursor = db.materials.find({})
    materials = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["_id"] = str(doc["_id"])
        materials.append(doc)
    return materials
