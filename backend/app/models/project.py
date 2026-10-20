from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class Segment(BaseModel):
    id: str
    label: str
    bbox: List[int]
    area_px: int
    polygon: List[List[int]]
    material_id: Optional[str] = None

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    original_image: str
    segments: List[Segment] = Field(default_factory=list)
    redesigned_image: Optional[str] = None
    reference_segment_id: Optional[str] = None
    reference_dimension_ft: Optional[float] = None
    estimates: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
