import shutil
from fastapi import FastAPI
import subprocess
import os
from datetime import datetime
from app.core.config import get_settings


settings = get_settings()
app = FastAPI()

MONGODUMP_PATH = r"C:\Users\ADMIN\Downloads\SOFTWARE\mongodb-database-tools-windows-x86_64-100.13.0\mongodb-database-tools-windows-x86_64-100.13.0\bin\mongodump.exe"
MONGORESTORE_PATH = r"C:\Users\ADMIN\Downloads\SOFTWARE\mongodb-database-tools-windows-x86_64-100.13.0\mongodb-database-tools-windows-x86_64-100.13.0\bin\mongorestore.exe"


def take_backup(BACKUP_DIR):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{settings.POSTGRES_DB}_{timestamp}.backup")
    
    print(f"Connecting to PostgreSQL:")
    print(f"  User: {settings.POSTGRES_USER}")
    print(f"  Host: {settings.POSTGRES_HOST}")
    print(f"  Port: {settings.POSTGRES_PORT}")
    print(f"  Database: {settings.POSTGRES_DB}")
    print(f"  Password length: {len(settings.POSTGRES_PASSWORD)}")
    
    cmd = [
        "pg_dump",
        "-U", settings.POSTGRES_USER,
        "-h", settings.POSTGRES_HOST,
        "-p", str(settings.POSTGRES_PORT),
        "-F", "c",         
        "-b",               
        "-v",              
        "-f", backup_file,
        settings.POSTGRES_DB
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            env=env,
            capture_output=True,
            text=True
        )
        
        print(f"Backup successful!")
        print(result.stdout)
        return backup_file
    
    except subprocess.CalledProcessError as e:
        print(f"STDERR: {e.stderr}")
        print(f"STDOUT: {e.stdout}")
        raise RuntimeError(f"Backup failed: {e.stderr}")
    

def restore_backup(backup_file_path: str):

    cmd = [
        "pg_restore",
        "-U", settings.POSTGRES_USER,
        "-h", settings.POSTGRES_HOST,
        "-p", str(settings.POSTGRES_PORT),
        "-d", settings.POSTGRES_DB,
        "-c",              
        "-v",              
        backup_file_path
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Restore failed: {e}")
    

def take_backup_mongo(BACKUP_DIR):
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(BACKUP_DIR, f"{settings.MONGO_DB}_{timestamp}")
    
    print(f"Connecting to MongoDB:")
    print(f"  Database: {settings.MONGO_DB}")
    print(f"  Backup folder: {backup_folder}")
    
    cmd = [
        MONGODUMP_PATH,
        "--uri", settings.MONGO_URL,
        "--db", settings.MONGO_DB,
        "--out", backup_folder,
        "--gzip"
    ]

    try:
        result = subprocess.run(
            cmd, 
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Backup successful!")
        print(result.stdout)
        zip_filename = f"{settings.MONGO_DB}_{timestamp}.zip"
        zip_path = os.path.join(BACKUP_DIR, zip_filename)
        
        shutil.make_archive(
            os.path.join(BACKUP_DIR, f"{settings.MONGO_DB}_{timestamp}"),
            'zip',
            backup_folder
        )
        
        shutil.rmtree(backup_folder)
        
        print(f"✓ Backup compressed to: {zip_path}")
        return zip_path
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Backup failed!")
        print(f"STDERR: {e.stderr}")
        print(f"STDOUT: {e.stdout}")
        if os.path.exists(backup_folder):
            shutil.rmtree(backup_folder)
        raise RuntimeError(f"Backup failed: {e.stderr}")
    except Exception as e:
        if os.path.exists(backup_folder):
            shutil.rmtree(backup_folder)
        raise


def restore_backup_mongo(zip_path: str):
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Backup file not found: {zip_path}")
    
    if not zip_path.endswith('.zip'):
        raise ValueError("Backup file must be a ZIP file")
    
    extract_dir = zip_path.replace('.zip', '_extract')
    
    try:
        # Extract the ZIP file
        print(f"Extracting backup from: {zip_path}")
        shutil.unpack_archive(zip_path, extract_dir)
        
        # Find the database folder inside extracted directory
        db_backup_path = os.path.join(extract_dir, settings.MONGO_DB)
        
        if not os.path.exists(db_backup_path):
            raise FileNotFoundError(f"Database backup not found at: {db_backup_path}")
        
        print(f"Restoring MongoDB:")
        print(f"  Database: {settings.MONGO_DB}")
        print(f"  From: {db_backup_path}")
        
        cmd = [
            MONGORESTORE_PATH,
            "--uri", settings.MONGO_URL,
            "--db", settings.MONGO_DB,
            "--gzip",
            "--drop",  # Drop existing collections before restoring
            db_backup_path
        ]

        result = subprocess.run(
            cmd, 
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Restore successful!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Restore failed!")
        print(f"STDERR: {e.stderr}")
        print(f"STDOUT: {e.stdout}")
        raise RuntimeError(f"Restore failed: {e.stderr}")
    finally:
        # Clean up extracted directory
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)


def list_backups_mongo(BACKUP_DIR):
    """Lists all available ZIP backups in the backup directory."""
    if not os.path.exists(BACKUP_DIR):
        print(f"No backup directory found at: {BACKUP_DIR}")
        return []
    
    backups = []
    for item in os.listdir(BACKUP_DIR):
        if item.endswith('.zip') and item.startswith(settings.MONGO_DB):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isfile(item_path):
                backups.append(item_path)
    
    backups.sort(reverse=True) 
    return backups