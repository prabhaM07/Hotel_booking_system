import os
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.crud.backup_restore import take_backup_mongo, restore_backup_mongo, list_backups_mongo

router = APIRouter(prefix="/mongo/backup-restore", tags=["Mongo Backup Restore"])

BACKUP_DIR = r"D:\PROJECT\Hotel_Booking_System\app\backups\mongoDB"
os.makedirs(BACKUP_DIR, exist_ok=True)


@router.post("/backup")
def create_backup():
    """Trigger MongoDB backup and create a ZIP file."""
    try:
        backup_file = take_backup_mongo(BACKUP_DIR)
        
        return {
            "message": "Backup successful",
            "backup_file": os.path.basename(backup_file),
            "full_path": backup_file
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backup/list")
def list_backups_route():
    try:
        backups = list_backups_mongo(BACKUP_DIR)
        
        if not backups:
            return {"message": "No backups found", "backups": []}

        backup_info = []
        for idx, backup in enumerate(backups, 1):
            backup_name = os.path.basename(backup)
            file_size = os.path.getsize(backup)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            try:
                name_without_ext = backup_name.replace('.zip', '')
                parts = name_without_ext.split('_')
                timestamp_str = parts[-2] + '_' + parts[-1]
                backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                formatted_time = backup_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = "Unknown"
            
            backup_info.append({
                "id": idx,
                "name": backup_name,
                "created_at": formatted_time,
                "size_mb": file_size_mb,
                "path": backup
            })

        return {"backups": backup_info}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
def restore_backup_route(file: UploadFile = File(...)):
    """Restore MongoDB from uploaded ZIP backup file."""
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are accepted")
        
        temp_path = os.path.join(BACKUP_DIR, f"temp_{file.filename}")
        
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        restore_backup_mongo(temp_path)
        
        os.remove(temp_path)
        
        return {
            "message": "Restore successful",
            "restored_file": file.filename
        }

    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/backup/{filename}")
def delete_backup(filename: str):
    file_path = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    try:
        os.remove(file_path)
        return {
            "message": "Backup deleted successfully",
            "deleted_file": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))