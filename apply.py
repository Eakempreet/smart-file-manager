from pathlib import Path
import shutil
import time
import tempfile
from logger import log_warning

def clear_folder_contents(folder: Path):
    if not folder.exists() or not folder.is_dir():
        raise ValueError("Target must be existing directory")
    try:
        for item in folder.iterdir():
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)
    except Exception as e:
        print(f"Error occurred: {e}")
        raise
    
    
def apply_to_original(original : Path, staging : Path):
    if not original.exists() or not staging.exists():
        raise ValueError("Original or Staging folder does not exist.")
    
    clear_folder_contents(original)
    
    items = list(staging.iterdir())
    for item in items:
        try:
            shutil.move(str(item), original / item.name)
        except Exception as e:
            print(f"Error Occurred: {e}")
            raise
            
    try:
        del items
        time.sleep(0.5)
        shutil.rmtree(staging)
        print("✅ Staging folder deleted successfully")
    except PermissionError:
        try:
            trash_folder = Path(tempfile.gettempdir()) / "SmartFileManager_Trash"
            trash_folder.mkdir(exist_ok=True)
            shutil.move(str(staging), trash_folder / staging.name)
            print(f"✅ Staging folder moved to system temp (auto-cleanup in few days)")
        except Exception as e:
            # If even moving fails, just warn user
            print(f"⚠️ Warning: Could not clean staging folder: {e}")
            print(f"   You can manually delete: {staging}")
            log_warning(f"Could not delete or move staging folder: {staging}. Error: {e}")    
        
        
def rollback_from_backup(original: Path, backup: Path):
    if not original.exists() or not original.is_dir():
        raise ValueError("Original must be a valid directory")
    
    if not backup.exists():
        raise FileNotFoundError("Backup does not exists. Cannot roll back.")
    
    clear_folder_contents(original)
    
    for item in backup.iterdir():
        try:
            if item.is_file():
                shutil.copy2(item, original / item.name)
            else:
                shutil.copytree(item, original / item.name)
        except Exception as e:
            print(f"Error while copying {item.name}: {e}")
            raise
