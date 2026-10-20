from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEXTURE_DIR = BASE_DIR / "textures"
MODEL_DIR = BASE_DIR / "models"

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "e2m_solutions"
SAM_CHECKPOINT = "sam_vit_b_01ec64.pth"
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure directories exist
for d in [UPLOAD_DIR, OUTPUT_DIR, TEXTURE_DIR, MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)
