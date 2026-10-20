# AI-Based Exterior House Renovation & Cost Estimation System

An end-to-end digital platform that accepts exterior photos of residential buildings, detects architectural components using AI (Meta's Segment Anything Model / SAM), renders redesigned visual options with realistic construction textures, estimates surface areas and material quantities, and calculates transparent renovation costs using real-world Mumbai market rates.

---

## 🏗️ System Architecture

```
[ Frontend: React + Vite + TailwindCSS ]
                     │  (HTTP / REST)
                     ▼
[ Backend: FastAPI (Python 3.13) ]
     ├── Lifespan / Startup (SAM ViT-B loading on CUDA GPU)
     ├── Database Service (Async MongoDB Motor client)
     ├── AI Segmentation Engine (SAM ViT-B + Heuristic Architectural Labeler)
     ├── Texture & Redesign Engine (Procedural Patterns + Luminance Blending + Feathering)
     ├── Area & Quantity Estimator (Pixel-Ratio Scale + Wastage Factor Formulas)
     └── Report Engine (ReportLab PDF Generation)
```

---

## 🚀 Key Features & Workflow

1. **Media Upload & Preprocessing (`/`)**:
   - Supports JPEG/PNG exterior building photographs up to 10MB.
   - Validates file format and dimensions.

2. **Exterior Structure Identification (`/segment/:projectId`)**:
   - Runs SAM (Segment Anything Model) ViT-B with CUDA hardware acceleration on local NVIDIA GPU (GeForce GTX 1650 Ti).
   - Automatically clusters contours and classifies architectural elements:
     - `wall` (large building surfaces)
     - `window` (mid-level rectangular apertures)
     - `balcony` (wide horizontal zones)
     - `pillar` (tall vertical columns)
     - `parapet` / `roof` (upper boundary elements)
     - `gate` (lower entrance zones)
   - Interactive HTML5 Canvas overlay enables users to review, click, relabel, or delete detected regions.

3. **Material Catalog & Design Application (`/design/:projectId`)**:
   - Catalog of 15 authentic Mumbai construction materials categorized into Paint, Texture Paint, Stone Cladding, Ceramic/Vitrified/Porcelain Tiles, Railings, and Panels.
   - Assign materials per architectural region with category-based filtering.
   - Generates composite redesigned preview with realistic texture tiling, edge feathering, and luminance lighting modulation.
   - Interactive draggable Before/After comparison slider.

4. **Surface Area & Cost Estimation (`/cost/:projectId`)**:
   - **Reference Scaling**: Users select one known dimension (e.g., standard door height = 7 ft, or wall height = 10 ft).
   - Derives accurate pixel-per-foot scaling ratio (`px_per_ft`).
   - Calculates real surface areas (`sqft`) and linear lengths (`rft`).
   - Applies material-specific coverage metrics and industry wastage margins (5%–15%).
   - Generates itemized cost breakdowns (material cost + labor cost + subtotals + grand total).
   - Allows users to directly override material and labor rates with instantaneous live recalculations.

5. **Downloadable PDF Report (`/report/:projectId`)**:
   - Compiles a professional contractor-ready PDF estimate containing:
     - Side-by-side original and redesigned building visuals.
     - Itemized table with regions, selected materials, quantities, and rates.
     - Grand total and advisory disclaimer.

---

## 📐 How the Estimation Works

### 1. Scaling Ratio
$$\text{Scale Ratio (px/ft)} = \frac{\text{Height of Reference Bounding Box (px)}}{\text{User-Supplied Reference Dimension (ft)}}$$

$$\text{Area Scale Factor} = \frac{1}{\text{Scale Ratio}^2} \quad (\text{sqft per pixel})$$

### 2. Area & Quantity Formulas
- **Flat Surfaces (Paint, Tiles, Cladding, Panels)**:
  $$\text{Nominal Area (sqft)} = \text{Segment Area (px)} \times \text{Area Scale Factor}$$
  $$\text{Effective Quantity} = \text{Nominal Area} \times (1 + \text{Wastage \%})$$
  - *Paint Quantity*: $\text{Liters} = \frac{\text{Effective Area}}{\text{Coverage (sqft/L)}}$
  - *Tiles / Cladding Quantity*: $\text{Square Feet} = \text{Effective Area}$

- **Linear Elements (Railings)**:
  $$\text{Length (rft)} = \frac{\text{Bounding Box Width (px)}}{\text{Scale Ratio}} \times (1 + \text{Wastage \%})$$

### 3. Cost Calculation
$$\text{Material Cost} = \text{Effective Quantity} \times \text{Material Rate}$$
$$\text{Labor Cost} = \text{Effective Quantity} \times \text{Labor Rate}$$
$$\text{Total Cost} = \text{Material Cost} + \text{Labor Cost}$$

---

## 🧱 Mumbai Renovation Material Catalog

| Material Name | Category | Unit | Mat Rate (₹) | Labor Rate (₹) | Coverage | Wastage |
|---|---|---|---|---|---|---|
| Exterior Emulsion (Asian Paints Apex) | Paint | sqft | ₹8 | ₹6 | 120 sqft/L | 10% |
| Weather Coat Premium (Berger) | Paint | sqft | ₹12 | ₹7 | 100 sqft/L | 10% |
| Texture Paint - Roller | Texture | sqft | ₹18 | ₹12 | 60 sqft/L | 15% |
| Texture Paint - Trowel | Texture | sqft | ₹25 | ₹15 | 40 sqft/L | 15% |
| Natural Stone Cladding | Cladding | sqft | ₹85 | ₹35 | — | 12% |
| Slate Stone Cladding | Cladding | sqft | ₹65 | ₹30 | — | 12% |
| Ceramic Wall Tiles 2×2 | Tiles | sqft | ₹35 | ₹20 | — | 8% |
| Vitrified Tiles 2×2 | Tiles | sqft | ₹55 | ₹22 | — | 8% |
| Porcelain Tiles 2×4 | Tiles | sqft | ₹75 | ₹25 | — | 10% |
| Glass Railing 12mm Tempered | Railing | rft | ₹450 | ₹150 | — | 5% |
| SS Railing (Grade 304) | Railing | rft | ₹350 | ₹120 | — | 5% |
| MS Railing Powder Coated | Railing | rft | ₹250 | ₹100 | — | 5% |
| ACP Panel 4mm | Panel | sqft | ₹120 | ₹40 | — | 10% |
| HPL Panel | Panel | sqft | ₹180 | ₹45 | — | 10% |
| WPC Wall Panel | Panel | sqft | ₹95 | ₹35 | — | 8% |

---

## ⚠️ System Limitations & Assumptions

1. **Single Monocular View**:
   - Area estimates rely on frontal perspective scaling. Angled or oblique photos may experience slight foreshortening without depth calibration.
2. **Advisory Estimates**:
   - Rates represent prevailing Mumbai market averages. Final contractor bids may vary depending on scaffolding requirements, site accessibility, and surface preparation.
3. **Low-Rise Residential Scope**:
   - Optimized for individual homes, bungalows, and low-rise building facades.

---

## 🛠️ Quickstart

### Prerequisites
- Windows 10/11 with Python 3.13 & Node.js 20+
- NVIDIA GPU with driver support (GTX 1650 Ti or better)
- MongoDB running locally on default port `27017`

### Running the App
Double-click `run_all.bat` or run individually:

**Backend:**
```cmd
run_backend.bat
# Runs FastAPI on http://localhost:8000
```

**Frontend:**
```cmd
run_frontend.bat
# Runs Vite dev server on http://localhost:5173
```
