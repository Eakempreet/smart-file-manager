from pathlib import Path
from backup import prepare_backup_staging, count_files
from organizer import file_organizer
from apply import apply_to_original, rollback_from_backup

SOURCE_FOLDER = "D:/Downloads"
BACKUP_FOLDER = "D:/Backup_SFM"
STAGING_FOLDER = "D:/temp/Staging"

def main():
    try:
        result = prepare_backup_staging(
            SOURCE_FOLDER,
            BACKUP_FOLDER,
            STAGING_FOLDER
        )
    except Exception as e:
        print(f"Setup failed: {e}")
        return
    
    if result["status"] == "EMPTY":
        print("Nothing to work on. The source folder is empty")
        return
    
    staging_folder = result["staging_folder"]
    
    print("Organizing files in staging...")
    file_organizer(str(staging_folder))
    
    # sanity check: files still exist
    if count_files(staging_folder) == 0:
        raise RuntimeError("Staging folder is empty after organizing - no files found")
    
    # sanity check: category folders created
    if not any(staging_folder.glob("*/")):
        raise RuntimeError("File organizing failed - no category folders created")
    
    print("Staging organized successfully.")
    
    original_folder = Path(SOURCE_FOLDER)
    backup_folder = result["backup_folder"]
    
    try:
        print("Applying organized folder to original folder...")
        apply_to_original(original_folder, staging_folder)
        print("✅ Files applied successfully.")
    except Exception as e:
        print(f"❌ Apply failed: {e}")
        print("↩️ Rolling back from backup...")
        rollback_from_backup(original_folder, backup_folder)
        print("✅ Rollback completed. Original restored.")

    
    

if __name__ == "__main__":
    main()
    