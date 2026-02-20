import os
import uuid
import io
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 5

# Cloudinary em prod, disco local em dev
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if not CLOUDINARY_URL:
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/imagem")
async def upload_imagem(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido. Use JPEG, PNG ou WebP.")

    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Arquivo muito grande. Máximo {MAX_SIZE_MB}MB.")

    # --- Cloudinary (produção) ---
    if CLOUDINARY_URL:
        try:
            import cloudinary
            import cloudinary.uploader
            public_id = f"futzer/{uuid.uuid4().hex}"
            result = cloudinary.uploader.upload(
                io.BytesIO(content),
                public_id=public_id,
                resource_type="image",
                folder="futzer",
            )
            url = result["secure_url"]
            return {"url": url, "filename": public_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao enviar para Cloudinary: {str(e)}")

    # --- Disco local (desenvolvimento) ---
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{filename}", "filename": filename}
