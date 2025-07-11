from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from zipfile import ZipFile
import shutil
import tempfile
import os

app = FastAPI()

UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_zip_background(zip_path: Path):
    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            for idx, member in enumerate(zip_ref.infolist(), 1):
                if member.is_dir():
                    continue
                member_name = Path(member.filename).name
                target_path = UPLOAD_DIR / member_name
                counter = 1
                while target_path.exists():
                    target_path = UPLOAD_DIR / f"{target_path.stem}_{counter}{target_path.suffix}"
                    counter += 1
                with zip_ref.open(member) as source_file, open(target_path, "wb") as out_file:
                    shutil.copyfileobj(source_file, out_file)
                if idx % 1000 == 0:
                    print(f"Extracted {idx} files so far...")
        print("Extraction completed.")
    except Exception as e:
        print(f"Error during extraction: {e}")
    finally:
        zip_path.unlink(missing_ok=True)

@app.post("/upload_zip")
async def upload_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
        background_tasks.add_task(extract_zip_background, tmp_path)
        return {"status": "success", "message": "Zip file uploaded. Extraction is processing in the background."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/list_images")
def list_images():
    images = [f"/static/images/{p.name}" for p in UPLOAD_DIR.glob("*") if p.is_file()]
    return {"images": images}

@app.delete("/delete_image")
def delete_image(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.post("/improve_model")
async def improve_model(dataset_path: str, model_name: str, sampling_factor: float):
    return {"status": "success", "dataset": dataset_path, "model": model_name, "sampling_factor": sampling_factor}
