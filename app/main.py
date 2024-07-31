import os
import uuid
import zipfile
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
import requests
import time

app = FastAPI()

# Directory where files will be stored
FILES_DIR = "/files"
MAX_TOTAL_SIZE = 20 * 1024 * 1024  # 20 MB

# Ensure the FILES_DIR exists
os.makedirs(FILES_DIR, exist_ok=True)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_index():
    return FileResponse('static/index.html')


@app.post("/upload")
async def upload_file(description: str = Form(...), file: UploadFile = File(...)):
    if file.size > MAX_TOTAL_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Create a unique folder name
    unique_folder = str(uuid.uuid4())
    upload_folder = os.path.join(FILES_DIR, unique_folder)
    os.makedirs(upload_folder, exist_ok=True)

    # Save the uploaded file
    file_path = os.path.join(upload_folder, file.filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    # Ensure file has been saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Retry logic to call the tonutils-storage API endpoint
    api_url = "http://tonutils-storage:8080/api/v1/create"
    payload = {
        "description": description,
        "path": file_path
    }
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return JSONResponse(content=response.json())
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise HTTPException(
                    status_code=500, detail=f"Error calling storage API: {e}")


@app.post("/upload_folder")
async def upload_folder(description: str = Form(...), file: UploadFile = File(...)):
    if file.size > MAX_TOTAL_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Create a unique folder name
    unique_folder = str(uuid.uuid4())
    upload_folder = os.path.join(FILES_DIR, unique_folder)
    os.makedirs(upload_folder, exist_ok=True)

    # Save the uploaded zip file
    zip_path = os.path.join(upload_folder, file.filename)
    async with aiofiles.open(zip_path, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    # Ensure file has been saved
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Extract the zip file
    try:
        total_size = 0
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                total_size += zip_info.file_size
                if total_size > MAX_TOTAL_SIZE:
                    raise HTTPException(
                        status_code=400, detail="Total size of extracted files exceeds limit")

                # Prevent directory traversal
                zip_info.filename = os.path.basename(zip_info.filename)
                # Filter out unwanted macOS metadata files
                if not zip_info.filename.startswith('._'):
                    zip_ref.extract(zip_info, upload_folder)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")

    # Remove the uploaded zip file
    os.remove(zip_path)

    # Retry logic to call the tonutils-storage API endpoint
    api_url = "http://tonutils-storage:8080/api/v1/create"
    payload = {
        "description": description,
        "path": upload_folder  # Pass the folder path to the storage API
    }
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return JSONResponse(content=response.json())
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise HTTPException(
                    status_code=500, detail=f"Error calling storage API: {e}")
