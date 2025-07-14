import os
import requests
import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from dotenv import load_dotenv

# ───── Chargement des clés ─────
load_dotenv()
OCR_API_KEY = os.getenv("OCR_API_KEY")
if not OCR_API_KEY:
    raise RuntimeError("Il manque OCR_API_KEY dans l’environnement")

MAX_SIZE = 1_000_000  # 1 Mo

app = FastAPI()

def ocr_space(path: Path) -> str:
    data = path.read_bytes()
    resp = requests.post(
        "https://api.ocr.space/parse/image",
        files={"filename": (path.name, data)},
        data={"apikey": OCR_API_KEY, "language": "fre"},
        timeout=180
    )
    resp.raise_for_status()
    j = resp.json()
    if not j.get("ParsedResults"):
        raise RuntimeError(j.get("ErrorMessage"))
    return j["ParsedResults"][0]["ParsedText"].strip()

def split_and_ocr(path: Path) -> str:
    txt = ""
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages, start=1):
        tmp = path.with_name(f"{path.stem}_p{i}.pdf")
        writer = PdfWriter()
        writer.add_page(page)
        with open(tmp, "wb") as f:
            writer.write(f)
        if tmp.stat().st_size <= MAX_SIZE:
            txt += ocr_space(tmp) + "\n"
        else:
            raise RuntimeError(f"Page {i} de {path.name} > 1 Mo")
    return txt

def ocr_by_images(path: Path) -> str:
    txt = ""
    images = convert_from_path(str(path), dpi=150)
    for i, img in enumerate(images, start=1):
        img_path = path.with_name(f"{path.stem}_img{i}.jpg")
        for q in (60, 40, 20):
            img.save(img_path, "JPEG", quality=q)
            if img_path.stat().st_size <= MAX_SIZE:
                break
        else:
            w, h = img.size
            img.resize((w//2, h//2)).save(img_path, "JPEG", quality=20)
        txt += ocr_space(img_path) + "\n"
    return txt

def ocr_auto(path: Path) -> str:
    try:
        if path.suffix.lower() == ".pdf" and path.stat().st_size > MAX_SIZE:
            return split_and_ocr(path)
        return ocr_space(path)
    except Exception:
        return ocr_by_images(path)

@app.post("/ocr_extract/", response_class=PlainTextResponse)
async def ocr_extract(files: List[UploadFile] = File(...)):
    raw_text = ""
    with tempfile.TemporaryDirectory() as tmpdir:
        for upload in files:
            ext = Path(upload.filename).suffix.lower()
            tmp_path = Path(tmpdir) / upload.filename
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(upload.file, f)

            try:
                if ext == ".pdf":
                    raw_text += ocr_auto(tmp_path) + "\n"
                elif ext in {".jpg", ".jpeg", ".png", ".tiff", ".bmp"}:
                    raw_text += ocr_space(tmp_path) + "\n"
                else:
                    raise HTTPException(400, detail=f"Format non supporté : {ext}")
            except Exception as e:
                # si c’est déjà une HTTPException, on le remonte, sinon c’est un 500 interne
                if isinstance(e, HTTPException):
                    raise
                raise HTTPException(500, detail=f"OCR error on {upload.filename}: {e}")

    return raw_text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ocr_api:app", host="0.0.0.0", port=8000, reload=True)
