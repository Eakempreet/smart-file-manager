from pathlib import Path
import shutil
from datetime import datetime


def count_files(source_f: Path) -> int:
    if not source_f.exists() or not source_f.is_dir():
        return 0
    return sum(1 for item in source_f.rglob("*") if item.is_file())


def create_backup(source_f: Path, backup_root: Path) -> Path:
    if not source_f.exists() or not source_f.is_dir():
        raise ValueError("Source folder is not valid.")

    backup_root.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = backup_root / f"{source_f.name}_backup_{timestamp}"
    
    # checks whether that backup folder already exist or not
    counter = 1
    while backup_folder.exists():
        backup_folder = backup_root / f"{source_f.name}_backup_{timestamp}({counter})"
        counter += 1
        
    try:
        shutil.copytree(
            source_f,
            backup_folder,
            ignore=shutil.ignore_patterns("desktop.ini", "Thumbs.db"),
        )
    except Exception as e:
        print(f"Backup failed: {e}")
        raise

    return backup_folder
        
        
def create_staging_copy(source_f: Path, staging_root: Path) -> Path:
    if not source_f.exists() or not source_f.is_dir():
        raise ValueError("Source folder is not valid.")

    staging_root.mkdir(parents=True, exist_ok=True)
    staging_folder = staging_root / f"{source_f.name}_staging"

    if staging_folder.exists():
        shutil.rmtree(staging_folder)

    try:
        shutil.copytree(
            source_f,
            staging_folder,
            ignore=shutil.ignore_patterns("desktop.ini", "Thumbs.db"),
        )
    except Exception as e:
        print(f"Creation of statging folder failed: {e}")
        raise
    return staging_folder
                        
def delete_folder(folder : Path):
    if folder.exists() and folder.is_dir():
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print(f"Error occured: {e}")
            raise                       

def prepare_backup_staging(source_path :str,
                           backup_path : str,
                           staging_path :str) -> dict:
    source = Path(source_path)
    backup_root = Path(backup_path)
    staging_root = Path(staging_path)
    
    if not source.exists() or not source.is_dir():
        raise ValueError("Source folder is not valid.")
    
    backup_root.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    
    source_file_count = count_files(source)
    
    if source_file_count == 0:
        return {
            "status" : "EMPTY",
            "source_files" : 0
        }
        
    backup_folder = create_backup(source, backup_root)
    staging_folder = create_staging_copy(source, staging_root)
    
    return {
        "status": "READY",
        "source_files": source_file_count,
        "backup_folder": backup_folder,
        "staging_folder": staging_folder
    }
    
    
    
    
if __name__ == "__main__":
    
    # Can be blank or whatever you like 
    result = prepare_backup_staging(
        "D:/Downloads",
        "D:/Backup",
        "D:/temp/Staging"
    )
    print(result)