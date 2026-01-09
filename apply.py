from pathlib import Path
import shutil

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
    
    for item in staging.iterdir():
        try:
            shutil.move(item, original / item.name)
        except Exception as e:
            print(f"Error Occurred: {e}")
            raise
            
    try:
        shutil.rmtree(staging)
    except Exception as e:
        print(f"Error occur while removing Staging folder: {e}")
        raise
        
        
        
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
