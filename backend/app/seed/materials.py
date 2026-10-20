async def seed_materials(db):
    """Seed materials collection if empty"""
    count = await db.materials.count_documents({})
    if count > 0:
        return
    
    materials = [
        {"name": "Exterior Emulsion (Apex)", "category": "Paint", "rate": 8, "labor_rate": 6, "unit": "sqft", "coverage": 120, "wastage_pct": 0.10, "color": "#F5E6CA", "pattern": "solid", "description": "Asian Paints Apex exterior emulsion, standard finish"},
        {"name": "Weather Coat Premium", "category": "Paint", "rate": 12, "labor_rate": 7, "unit": "sqft", "coverage": 100, "wastage_pct": 0.10, "color": "#E8D5B7", "pattern": "solid", "description": "Berger Weather Coat, premium weather protection"},
        {"name": "Texture Paint - Roller", "category": "Texture", "rate": 18, "labor_rate": 12, "unit": "sqft", "coverage": 60, "wastage_pct": 0.15, "color": "#D4C5A9", "pattern": "solid", "description": "Roller-applied textured finish"},
        {"name": "Texture Paint - Trowel", "category": "Texture", "rate": 25, "labor_rate": 15, "unit": "sqft", "coverage": 40, "wastage_pct": 0.15, "color": "#C9B99A", "pattern": "solid", "description": "Trowel-applied premium textured finish"},
        {"name": "Natural Stone Cladding", "category": "Cladding", "rate": 85, "labor_rate": 35, "unit": "sqft", "coverage": None, "wastage_pct": 0.12, "color": "#8B7355", "pattern": "brick", "description": "Natural stone cladding, premium finish"},
        {"name": "Slate Stone Cladding", "category": "Cladding", "rate": 65, "labor_rate": 30, "unit": "sqft", "coverage": None, "wastage_pct": 0.12, "color": "#4A4A4A", "pattern": "brick", "description": "Dark slate stone cladding"},
        {"name": "Ceramic Wall Tiles 2x2", "category": "Tiles", "rate": 35, "labor_rate": 20, "unit": "sqft", "coverage": None, "wastage_pct": 0.08, "color": "#C4A882", "pattern": "grid", "description": "Standard ceramic exterior tiles"},
        {"name": "Vitrified Tiles 2x2", "category": "Tiles", "rate": 55, "labor_rate": 22, "unit": "sqft", "coverage": None, "wastage_pct": 0.08, "color": "#E0D5C0", "pattern": "grid", "description": "Vitrified exterior wall tiles"},
        {"name": "Porcelain Tiles 2x4", "category": "Tiles", "rate": 75, "labor_rate": 25, "unit": "sqft", "coverage": None, "wastage_pct": 0.10, "color": "#F0E8DA", "pattern": "grid", "description": "Premium porcelain rectangular tiles"},
        {"name": "Glass Railing 12mm", "category": "Railing", "rate": 450, "labor_rate": 150, "unit": "rft", "coverage": None, "wastage_pct": 0.05, "color": "#ADD8E6", "pattern": "lines", "description": "12mm tempered glass railing with SS fittings"},
        {"name": "SS Railing", "category": "Railing", "rate": 350, "labor_rate": 120, "unit": "rft", "coverage": None, "wastage_pct": 0.05, "color": "#C0C0C0", "pattern": "lines", "description": "Stainless steel railing, grade 304"},
        {"name": "MS Railing Powder Coated", "category": "Railing", "rate": 250, "labor_rate": 100, "unit": "rft", "coverage": None, "wastage_pct": 0.05, "color": "#2F4F4F", "pattern": "lines", "description": "Mild steel railing with powder coating"},
        {"name": "ACP Panel 4mm", "category": "Panel", "rate": 120, "labor_rate": 40, "unit": "sqft", "coverage": None, "wastage_pct": 0.10, "color": "#A9A9A9", "pattern": "horizontal_strips", "description": "4mm Aluminium Composite Panel"},
        {"name": "HPL Panel", "category": "Panel", "rate": 180, "labor_rate": 45, "unit": "sqft", "coverage": None, "wastage_pct": 0.10, "color": "#8B4513", "pattern": "horizontal_strips", "description": "High Pressure Laminate exterior panel"},
        {"name": "WPC Wall Panel", "category": "Panel", "rate": 95, "labor_rate": 35, "unit": "sqft", "coverage": None, "wastage_pct": 0.08, "color": "#D2B48C", "pattern": "vertical_strips", "description": "Wood Plastic Composite wall panel"},
    ]
    
    await db.materials.insert_many(materials)
    print(f"Seeded {len(materials)} materials")
