class EstimatorService:
    def calculate(self, segments: list, materials: dict, 
                  reference_segment_id: str, reference_dimension_ft: float) -> dict:
        """
        Calculate area, material quantities, and costs.
        Returns breakdown per segment + totals.
        """
        # Find reference segment to compute scale
        ref_segment = None
        for seg in segments:
            if seg['id'] == reference_segment_id:
                ref_segment = seg
                break
        
        if not ref_segment or not reference_dimension_ft or reference_dimension_ft <= 0:
            # Fallback: assume 10px = 1ft
            px_per_ft = 10.0
        else:
            # Use bbox height as the reference dimension
            ref_bbox_h = ref_segment['bbox'][3]  # height in pixels
            px_per_ft = ref_bbox_h / reference_dimension_ft if reference_dimension_ft > 0 else 10.0
        
        sqft_per_px = 1.0 / (px_per_ft * px_per_ft)
        
        breakdown = []
        total_material_cost = 0
        total_labor_cost = 0
        
        for seg in segments:
            if not seg.get('material_id') or seg['material_id'] not in materials:
                continue
            
            mat = materials[seg['material_id']]
            
            if mat['unit'] == 'rft':
                # Running feet — use bbox width
                length_px = seg['bbox'][2]  # width of bbox
                length_ft = length_px / px_per_ft
                length_with_wastage = length_ft * (1 + mat['wastage_pct'])
                
                material_cost = length_with_wastage * mat['rate']
                labor_cost = length_with_wastage * mat['labor_rate']
                
                breakdown.append({
                    "segment_id": seg['id'],
                    "segment_label": seg['label'],
                    "material_name": mat['name'],
                    "area_sqft": round(length_ft, 2),
                    "unit": "rft",
                    "quantity": round(length_with_wastage, 2),
                    "quantity_unit": "rft",
                    "material_rate": mat['rate'],
                    "labor_rate": mat['labor_rate'],
                    "material_cost": round(material_cost, 2),
                    "labor_cost": round(labor_cost, 2),
                    "total_cost": round(material_cost + labor_cost, 2),
                })
            else:
                # Square feet
                area_sqft = seg['area_px'] * sqft_per_px
                area_with_wastage = area_sqft * (1 + mat['wastage_pct'])
                
                # Material quantity
                if mat.get('coverage') and mat['coverage'] > 0:
                    # Paint: litres needed
                    quantity = area_with_wastage / mat['coverage']
                    quantity_unit = "litres"
                else:
                    quantity = area_with_wastage
                    quantity_unit = "sqft"
                
                material_cost = area_with_wastage * mat['rate']
                labor_cost = area_with_wastage * mat['labor_rate']
                
                breakdown.append({
                    "segment_id": seg['id'],
                    "segment_label": seg['label'],
                    "material_name": mat['name'],
                    "area_sqft": round(area_sqft, 2),
                    "unit": "sqft",
                    "quantity": round(quantity, 2),
                    "quantity_unit": quantity_unit,
                    "material_rate": mat['rate'],
                    "labor_rate": mat['labor_rate'],
                    "material_cost": round(material_cost, 2),
                    "labor_cost": round(labor_cost, 2),
                    "total_cost": round(material_cost + labor_cost, 2),
                })
            
            total_material_cost += breakdown[-1]['material_cost']
            total_labor_cost += breakdown[-1]['labor_cost']
        
        return {
            "breakdown": breakdown,
            "total_material_cost": round(total_material_cost, 2),
            "total_labor_cost": round(total_labor_cost, 2),
            "grand_total": round(total_material_cost + total_labor_cost, 2),
            "px_per_ft": round(px_per_ft, 2),
        }
