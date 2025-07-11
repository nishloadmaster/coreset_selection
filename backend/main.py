"""
AI Model Improver - FastAPI Backend

This module provides the main FastAPI application for the AI Model Improver tool.
It handles file uploads, media processing, and provides REST API endpoints for
the frontend application.

Author: AI Model Improver Team
Version: 1.0.0
"""

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Query, Form
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
from typing import Dict, List, Optional, Any

# Initialize FastAPI application
app = FastAPI(
    title="AI Model Improver API",
    description="Backend API for AI Model Improver - CoreSet Selection Tool",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Directory configuration
UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create uploads directory for zip files
ZIP_UPLOAD_DIR = Path("uploads")
ZIP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for serving processed images
app.mount("/static", StaticFiles(directory="static"), name="static")


def extract_zip_background(zip_path: Path) -> Dict[str, Any]:
    """
    Background task to extract and process zip file.
    
    This function runs asynchronously to handle large file processing
    without blocking the main application thread.
    
    Args:
        zip_path (Path): Path to the uploaded zip file
        
    Returns:
        Dict[str, Any]: Processing result with status and metadata
        
    Raises:
        Exception: If processing fails
    """
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


async def extract_zip_sync(zip_path: Path) -> Dict[str, Any]:
    """
    Synchronous version for immediate processing.
    
    This function processes the zip file immediately and returns results
    for real-time feedback to the user.
    
    Args:
        zip_path (Path): Path to the uploaded zip file
        
    Returns:
        Dict[str, Any]: Processing result with status and file list
        
    Raises:
        Exception: If processing fails
    """
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
    process_sync: bool = Form(False),
    model_name: str = Form("Model1"),
    labels: str = Form(""),
    sampling_factor: float = Form(0.5)
) -> Dict[str, Any]:
    """
    Upload and process a zip file containing images and videos.
    
    This endpoint handles zip file uploads and processes them either
    synchronously or asynchronously based on the process_sync parameter.
    
    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks
        file (UploadFile): The uploaded zip file
        process_sync (bool): If True, processes immediately and returns results
        model_name (str): Name of the model to improve
        labels (str): Comma-separated labels
        sampling_factor (float): Sampling factor for data selection (0.0-1.0)
        
    Returns:
        Dict[str, Any]: Upload and processing status
        
    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    # Print all parameters received
    print("=" * 50)
    print(f"Model name: {model_name}")
    print(f"Labels (raw): '{labels}'")
    print(f"Sampling factor: {sampling_factor}")

    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.zip'):
            return JSONResponse(
                status_code=400, 
                content={"error": "File must be a zip file"}
            )
        
        # Validate sampling factor
        if not 0.0 <= sampling_factor <= 1.0:
            return JSONResponse(
                status_code=400,
                content={"error": "Sampling factor must be between 0.0 and 1.0"}
            )
        
        # Parse labels into list
        labels_list = [label.strip() for label in labels.split(',') if label.strip()] if labels else []
        print(f"Parsed labels list: {labels_list}")
        print(f"Number of labels: {len(labels_list)}")
        
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
        print(f"Parameters for processing:")
        print(f"  - Model: {model_name}")
        print(f"  - Labels: {labels_list}")
        print(f"  - Sampling factor: {sampling_factor}")
        
        if process_sync:
            # Process immediately and return results
            result = await extract_zip_sync(zip_path)
            return {
                "status": "success",
                "message": f"Zip file uploaded and processed immediately.",
                "filename": zip_filename,
                "path": str(zip_path),
                "processing_result": result,
                "model_name": model_name,
                "labels": labels_list,
                "sampling_factor": sampling_factor
            }
        else:
            # Process in background
            background_tasks.add_task(extract_zip_background, zip_path)
            return {
                "status": "success", 
                "message": f"Zip file uploaded and saved to {zip_path}. Extraction is processing in the background.",
                "filename": zip_filename,
                "path": str(zip_path),
                "processing": "background",
                "model_name": model_name,
                "labels": labels_list,
                "sampling_factor": sampling_factor
            }
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/upload_and_curate")
async def upload_and_curate(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_name: str = Query(..., description="Name of the model to improve"),
    sampling_factor: float = Query(0.5, description="Sampling factor for data selection (0.0-1.0)"),
    process_sync: bool = Query(True, description="Process immediately instead of background")
) -> Dict[str, Any]:
    """
    Upload a zip file and immediately trigger curation process.
    
    This endpoint combines upload and curate functionality in a single workflow.
    Users can upload their data and immediately start the model improvement process.
    
    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks
        file (UploadFile): The uploaded zip file
        model_name (str): Name of the model to improve
        sampling_factor (float): Sampling factor for data selection (0.0-1.0)
        process_sync (bool): If True, processes immediately and returns results
        
    Returns:
        Dict[str, Any]: Upload, processing, and curation status
        
    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    # Print all parameters received
    print("=" * 50)
    print("UPLOAD_AND_CURATE ROUTE PARAMETERS:")
    print("=" * 50)
    print(f"File name: {file.filename}")
    print(f"File content type: {file.content_type}")
    print(f"File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
    print(f"Model name: {model_name}")
    print(f"Sampling factor: {sampling_factor}")
    print(f"Process sync: {process_sync}")
    print(f"Background tasks: {background_tasks}")
    print("=" * 50)
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.zip'):
            return JSONResponse(
                status_code=400, 
                content={"error": "File must be a zip file"}
            )
        
        # Validate sampling factor
        if not 0.0 <= sampling_factor <= 1.0:
            return JSONResponse(
                status_code=400,
                content={"error": "Sampling factor must be between 0.0 and 1.0"}
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
            # Process immediately and trigger curation
            processing_result = await extract_zip_sync(zip_path)
            
            if processing_result["status"] == "success":
                # Trigger curation with the processed data
                curation_result = await improve_model(
                    dataset_path=processing_result["output_folder"],
                    model_name=model_name,
                    sampling_factor=sampling_factor
                )
                
                return {
                    "status": "success",
                    "message": "Zip file uploaded, processed, and curation triggered successfully.",
                    "filename": zip_filename,
                    "path": str(zip_path),
                    "processing_result": processing_result,
                    "curation_result": curation_result,
                    "workflow": "upload_and_curate_sync"
                }
            else:
                return {
                    "status": "error",
                    "message": "File processing failed",
                    "processing_result": processing_result,
                    "workflow": "upload_and_curate_sync"
                }
        else:
            # Process in background and trigger curation
            def process_and_curate_background(zip_path: Path, model_name: str, sampling_factor: float):
                """Background task to process zip and trigger curation"""
                try:
                    # Process the zip file
                    processing_result = extract_zip_background(zip_path)
                    
                    if processing_result["status"] == "success":
                        # Trigger curation
                        curation_result = {
                            "status": "success",
                            "dataset": processing_result["output_folder"],
                            "model": model_name,
                            "sampling_factor": sampling_factor,
                            "message": "Curation triggered for processed dataset"
                        }
                        
                        print(f"Background processing and curation completed for {zip_path}")
                        print(f"Processing result: {processing_result}")
                        print(f"Curation result: {curation_result}")
                    else:
                        print(f"Background processing failed for {zip_path}: {processing_result}")
                        
                except Exception as e:
                    print(f"Error in background processing and curation: {e}")
            
            # Add background task
            background_tasks.add_task(
                process_and_curate_background, 
                zip_path, 
                model_name, 
                sampling_factor
            )
            
            return {
                "status": "success", 
                "message": f"Zip file uploaded and saved to {zip_path}. Processing and curation are running in the background.",
                "filename": zip_filename,
                "path": str(zip_path),
                "model_name": model_name,
                "sampling_factor": sampling_factor,
                "processing": "background",
                "workflow": "upload_and_curate_background"
            }
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/list_uploads")
def list_uploads() -> Dict[str, List[str]]:
    """
    List all uploaded zip files.
    
    Returns:
        Dict[str, List[str]]: List of uploaded zip file names
    """
    zip_files = [f.name for f in ZIP_UPLOAD_DIR.glob("*.zip")]
    return {"uploads": zip_files}


@app.get("/list_images")
def list_images() -> Dict[str, List[str]]:
    """
    List all processed images from all uploads.
    
    Scans all upload folders and returns paths to all processed images
    for display in the frontend gallery.
    
    Returns:
        Dict[str, List[str]]: List of image URLs for the frontend
    """
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
def list_upload_folders() -> Dict[str, List[Dict[str, Any]]]:
    """
    List all upload folders with their contents.
    
    Provides detailed information about each upload folder including
    file names, paths, and sizes for management purposes.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Detailed folder information
    """
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
def delete_image(filename: str) -> Dict[str, str]:
    """
    Delete a specific image from the gallery.
    
    Args:
        filename (str): Name of the image file to delete
        
    Returns:
        Dict[str, str]: Deletion status
    """
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})


@app.delete("/delete_upload")
def delete_upload(filename: str) -> Dict[str, str]:
    """
    Delete an uploaded zip file.
    
    Args:
        filename (str): Name of the zip file to delete
        
    Returns:
        Dict[str, str]: Deletion status
    """
    file_path = ZIP_UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted"}
    return JSONResponse(status_code=404, content={"error": "File not found"})


@app.delete("/delete_upload_folder")
def delete_upload_folder(folder_id: str) -> Dict[str, str]:
    """
    Delete an entire upload folder and its contents.
    
    Args:
        folder_id (str): ID of the folder to delete
        
    Returns:
        Dict[str, str]: Deletion status
    """
    folder_path = UPLOAD_DIR / folder_id
    if folder_path.exists() and folder_path.is_dir():
        shutil.rmtree(folder_path)
        return {"status": "deleted", "folder_id": folder_id}
    return JSONResponse(status_code=404, content={"error": "Folder not found"})


@app.post("/improve_model")
async def improve_model(
    dataset_path: str, 
    model_name: str, 
    sampling_factor: float
) -> Dict[str, Any]:
    """
    Trigger model improvement with specified parameters.
    
    This endpoint receives training parameters and initiates the model
    improvement process. Currently returns a confirmation response.
    
    Args:
        dataset_path (str): Path to the dataset
        model_name (str): Name of the model to improve
        sampling_factor (float): Sampling factor for data selection (0.0-1.0)
        
    Returns:
        Dict[str, Any]: Training status and parameters
    """
    return {
        "status": "success", 
        "dataset": dataset_path, 
        "model": model_name, 
        "sampling_factor": sampling_factor
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy", "service": "ai-model-improver-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)