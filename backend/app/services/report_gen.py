from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.config import UPLOAD_DIR, OUTPUT_DIR
from pathlib import Path
import uuid

class ReportGenerator:
    def generate_pdf(self, project: dict, materials: dict, estimates: dict) -> str:
        """Generate a clean, contractor-ready single-page PDF report."""
        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        filepath = OUTPUT_DIR / filename
        
        # A4 margins optimized to keep content on a single page
        doc = SimpleDocTemplate(
            str(filepath), 
            pagesize=A4,
            rightMargin=36, 
            leftMargin=36, 
            topMargin=30, 
            bottomMargin=25
        )
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle', 
            parent=styles['Title'],
            fontSize=18, 
            leading=22,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=0
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', 
            parent=styles['Normal'],
            fontSize=10, 
            textColor=colors.HexColor('#4a5568')
        )
        img_label_style = ParagraphStyle(
            'ImgLabel', 
            parent=styles['Normal'],
            fontSize=10, 
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2d3748'),
            alignment=1
        )
        
        elements = []
        
        # Header banner
        elements.append(Paragraph("Exterior Renovation & Cost Estimate", title_style))
        elements.append(Paragraph("E2M Solutions — AI-Powered Architectural Planning Assistant", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Visual Comparison: Side-by-Side Images in a 2-column Table
        orig_image = project.get('original_image')
        redesigned_image = project.get('redesigned_image')
        
        label_cells = []
        image_cells = []
        
        if orig_image and (UPLOAD_DIR / orig_image).exists():
            label_cells.append(Paragraph("Original Exterior", img_label_style))
            image_cells.append(RLImage(str(UPLOAD_DIR / orig_image), width=3.3*inch, height=2.3*inch))
            
        if redesigned_image and (OUTPUT_DIR / redesigned_image).exists():
            label_cells.append(Paragraph("Redesigned Preview", img_label_style))
            image_cells.append(RLImage(str(OUTPUT_DIR / redesigned_image), width=3.3*inch, height=2.3*inch))
            
        if image_cells:
            col_w = 3.5 * inch if len(image_cells) == 2 else 7.0 * inch
            comparison_table = Table([label_cells, image_cells], colWidths=[col_w] * len(image_cells))
            comparison_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                ('TOPPADDING', (0, 1), (-1, 1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 6),
            ]))
            elements.append(comparison_table)
            elements.append(Spacer(1, 8))
        
        # Cost breakdown table
        if estimates and estimates.get('breakdown'):
            table_heading = ParagraphStyle(
                'TableHeading', 
                parent=styles['Heading3'],
                fontSize=12,
                leading=14,
                textColor=colors.HexColor('#1a1a2e')
            )
            elements.append(Paragraph("Cost Breakdown & Material Quantities", table_heading))
            elements.append(Spacer(1, 6))
            
            # Use 'Rs.' instead of unicode ₹ to ensure crisp rendering on all PDF viewers without font tofu
            table_data = [["Region", "Material", "Area", "Quantity", "Material (Rs.)", "Labor (Rs.)", "Total (Rs.)"]]
            for row in estimates['breakdown']:
                table_data.append([
                    row['segment_label'].title(),
                    row['material_name'],
                    f"{row['area_sqft']} {row['unit']}",
                    f"{row['quantity']} {row['quantity_unit']}",
                    f"Rs. {row['material_cost']:,.0f}",
                    f"Rs. {row['labor_cost']:,.0f}",
                    f"Rs. {row['total_cost']:,.0f}",
                ])
            
            # Totals summary row
            table_data.append([
                "Total", "", "", "",
                f"Rs. {estimates.get('total_material_cost', 0):,.0f}",
                f"Rs. {estimates.get('total_labor_cost', 0):,.0f}",
                f"Rs. {estimates.get('grand_total', 0):,.0f}",
            ])
            
            cost_table = Table(table_data, colWidths=[1.0*inch, 1.5*inch, 0.8*inch, 0.9*inch, 1.0*inch, 0.9*inch, 1.0*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            elements.append(cost_table)
            elements.append(Spacer(1, 10))
            
            # Grand Total Highlight
            grand_total_style = ParagraphStyle(
                'GrandTotalStyle', 
                parent=styles['Normal'],
                fontSize=13, 
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1a1a2e')
            )
            elements.append(Paragraph(
                f"Estimated Grand Total: <font color='#1d4ed8'>Rs. {estimates.get('grand_total', 0):,.0f}</font>", 
                grand_total_style
            ))
        
        elements.append(Spacer(1, 8))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Italic'],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor('#64748b')
        )
        elements.append(Paragraph(
            "Note: This is an advisory estimate generated by E2M Solutions AI pre-construction planning system. "
            "Actual contractor costs may vary based on site accessibility, surface preparation, and market fluctuations.",
            disclaimer_style
        ))
        
        doc.build(elements)
        return filename
