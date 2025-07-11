from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import tempfile
from media_processor import MediaProcessor
import os
import zipfile
import uuid
import asyncio

app = FastAPI()

UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create uploads directory for zip files
ZIP_UPLOAD_DIR = Path("uploads")
ZIP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_zip_background(zip_path: Path):
    """Background task to extract and process zip file"""
    try:
        # Create a unique folder for this upload
        upload_id = str(uuid.uuid4())
        upload_folder = UPLOAD_DIR / upload_id
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing zip file: {zip_path}")
        print(f"Output folder: {upload_folder}")
        
        # Use MediaProcessor to handle the extraction and processing
        processor = MediaProcessor(zip_path, upload_folder)
        all_images = processor.process()
        
        print(f"Extraction complete, {len(all_images)} files processed.")
        print(f"Files saved to: {upload_folder}")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "processed_files": len(all_images),
            "output_folder": str(upload_folder)
        }
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def extract_zip_sync(zip_path: Path):
    """Synchronous version for immediate processing"""
    try:
        # Create a unique folder for this upload
        upload_id = str(uuid.uuid4())
        upload_folder = UPLOAD_DIR / upload_id
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing zip file synchronously: {zip_path}")
        print(f"Output folder: {upload_folder}")
        
        # Use MediaProcessor to handle the extraction and processing
        processor = MediaProcessor(zip_path, upload_folder)
        all_images = processor.process()
        
        print(f"Extraction complete, {len(all_images)} files processed.")
        print(f"Files saved to: {upload_folder}")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "processed_files": len(all_images),
            "output_folder": str(upload_folder),
            "files": all_images
        }
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/upload_zip")
async def upload_zip(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    process_sync: bool = Query(False, description="Process immediately instead of background")
):
    """
    Upload and process a zip file containing images and videos.
    
    - process_sync: If True, processes immediately and returns results
    - If False, processes in background and returns immediately
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.zip'):
            return JSONResponse(
                status_code=400, 
                content={"error": "File must be a zip file"}
            )
        
        # Save zip file to uploads directory with original filename
        zip_filename = file.filename
        
        # Ensure filename is unique
        counter = 1
        original_name = zip_filename
        while (ZIP_UPLOAD_DIR / zip_filename).exists():
            name_parts = original_name.rsplit('.', 1)
            if len(name_parts) > 1:
                zip_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                zip_filename = f"{original_name}_{counter}"
            counter += 1
        
        zip_path = ZIP_UPLOAD_DIR / zip_filename
        
        # Save the uploaded file
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Zip file saved to: {zip_path}")
        
        if process_sync:
            # Process immediately and return results
            result = await extract_zip_sync(zip_path)
            return {
                "status": "success",
                "message": f"Zip file uploaded and processed immediately.",
                "filename": zip_filename,
                "path": str(zip_path),
                "processing_result": result
            }
        else:
            # Process in background
            background_tasks.add_task(extract_zip_background, zip_path)
            return {
                "status": "success", 
                "message": f"Zip file uploaded and saved to {zip_path}. Extraction is processing in the background.",
                "filename": zip_filename,
                "path": str(zip_path),
                "processing": "background"
            }
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/list_uploads")
def list_uploads():
    """List all uploaded zip files"""
    zip_files = [f.name for f in ZIP_UPLOAD_DIR.glob("*.zip")]
    return {"uploads": zip_files}

@app.get("/list_images")
def list_images():
    """List all processed images from all uploads"""
    all_images = []
    for upload_folder in UPLOAD_DIR.iterdir():
        if upload_folder.is_dir():
            for image_file in upload_folder.rglob("*"):
                if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                    # Return relative path from static/images
                    relative_path = image_file.relative_to(UPLOAD_DIR)
                    all_images.append(f"/static/images/{relative_path}")
    
    return {"images": all_images}

@app.get("/list_upload_folders")
def list_upload_folders():
    """List all upload folders with their contents"""
    folders = []
    for upload_folder in UPLOAD_DIR.iterdir():
        if upload_folder.is_dir():
            folder_info = {
                "folder_id": upload_folder.name,
                "folder_path": str(upload_folder),
                "files": []
            }
            for file_path in upload_folder.rglob("*"):
                if file_path.is_file():
                    folder_info["files"].append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(upload_folder)),
                        "size": file_path.stat().st_size
                    })
            folders.append(folder_info)
    
    return {"upload_folders": folders}

@app.delete("/delete_image")
def delete_image(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.delete("/delete_upload")
def delete_upload(filename: str):
    """Delete an uploaded zip file"""
    file_path = ZIP_UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.delete("/delete_upload_folder")
def delete_upload_folder(folder_id: str):
    """Delete an entire upload folder and its contents"""
    folder_path = UPLOAD_DIR / folder_id
    if folder_path.exists() and folder_path.is_dir():
        shutil.rmtree(folder_path)
        return {"status": "deleted", "folder_id": folder_id}
    return JSONResponse(status_code=404, content={"error": "Folder not found"})

@app.post("/improve_model")
async def improve_model(dataset_path: str, model_name: str, sampling_factor: float):
    return {"status": "success", "dataset": dataset_path, "model": model_name, "sampling_factor": sampling_factor}