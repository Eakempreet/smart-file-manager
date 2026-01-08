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

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = backup_root / f"{source_f.name}_backup_{timestamp}"
    
    # w?
    counter = 1
    while backup_folder.exists():
        backup_folder = backup_root / f"{source_f.name}_backup_{timestamp}({counter})"
        counter += 1

    
    shutil.copytree(source_f, backup_folder)
    return backup_folder
        
        
def create_copy(source_f: Path, staging_root: Path) -> Path:
    if not source_f.exists() or not source_f.is_dir():
        raise ValueError("Source folder is not valid.")

    staging_root.mkdir(parents=True, exist_ok=True)
    staging_folder = staging_root / f"{source_f.name}_staging"

    if staging_folder.exists():
        shutil.rmtree(staging_folder)

    shutil.copytree(source_f, staging_folder)
    return staging_folder
                        
                        

def prepare_backup_staging(source_path :str,
                           backup_path : str,
                           staging_path :str):
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
    staging_folder = create_copy(source, staging_root)
    
    return {
        "status": "READY",
        "source_files": source_file_count,
        "backup_folder": backup_folder,
        "staging_folder": staging_folder
    }