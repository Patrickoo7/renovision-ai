from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Material(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str
    rate: float
    labor_rate: float
    unit: str
    coverage: Optional[float] = None
    wastage_pct: float
    color: str
    pattern: str
    description: str

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
