import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import requests
import time

app = FastAPI()

# Directory where files will be stored
FILES_DIR = "/files"

# Ensure the FILES_DIR exists
os.makedirs(FILES_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(description: str, file: UploadFile = File(...)):
    if file.size > 50 * 1024 * 1024:  # 50 MB limit
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
