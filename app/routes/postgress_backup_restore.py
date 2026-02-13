import os
from fastapi import File, HTTPException, UploadFile
from fastapi.responses import FileResponse
import shutil
from fastapi import APIRouter
from app.crud.backup_restore import restore_backup, take_backup

router = APIRouter(prefix="/postgress/backup-restore",tags=["Postgress Backup Restore"])

BACKUP_DIR = r"D:\PROJECT\Hotel_Booking_System\app\backups\postgressDB"
os.makedirs(BACKUP_DIR, exist_ok=True)


@router.post("/backup")
def create_backup():
    try:
        backup_file = take_backup(BACKUP_DIR)
        
        return {"message": "Backup successful", "backup_file": backup_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backup/download/{filename}")
def download_backup(filename: str):
    file_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    return FileResponse(file_path, filename=filename)

@router.post("/restore")
def restore_backup_route(file: UploadFile = File(...)):
    try:
        temp_path = os.path.join(BACKUP_DIR, file.filename)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        restore_backup(temp_path)
        return {"message": "Restore successful", "restored_file": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      
      
      