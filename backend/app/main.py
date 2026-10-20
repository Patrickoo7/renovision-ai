from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR, OUTPUT_DIR
from app.database import get_db, client
from app.seed.materials import seed_materials
from app.services.segmentation import SegmentationService
from app.services.texture import TextureService
from app.services.estimator import EstimatorService
from app.services.report_gen import ReportGenerator
from app.routers import upload, segment, design, estimate, report

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = get_db()
    try:
        await seed_materials(db)
    except Exception as e:
        print(f"Warning: Database seeding failed: {e}")
    
    # Load services
    seg_service = SegmentationService()
    try:
        seg_service.load_model()
    except Exception as e:
        print(f"Warning: SAM model not loaded: {e}")
    
    app.state.db = db
    app.state.segmentation = seg_service
    app.state.texture = TextureService()
    app.state.estimator = EstimatorService()
    app.state.report_gen = ReportGenerator()
    
    yield
    
    # Shutdown
    client.close()

app = FastAPI(title="E2M Solutions - Exterior Renovation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# Routers
app.include_router(upload.router, prefix="/api")
app.include_router(segment.router, prefix="/api")
app.include_router(design.router, prefix="/api")
app.include_router(estimate.router, prefix="/api")
app.include_router(report.router, prefix="/api")
