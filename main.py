from pathlib import Path
from backup import prepare_backup_staging, count_files
from organizer import file_organizer
from apply import apply_to_original, rollback_from_backup
from logger import log_info, log_error

SOURCE_FOLDER = "D:/Downloads"
BACKUP_FOLDER = "D:/SFM/Backup_SFM"
STAGING_FOLDER = "D:/SFM/temp/Staging"

def main():
    log_info("=" * 100)
    log_info("Program Started")
    try:
        result = prepare_backup_staging(
            SOURCE_FOLDER,
            BACKUP_FOLDER,
            STAGING_FOLDER
        )
    except Exception as e:
        print(f"Setup failed: {e}")
        log_error(f"Setup failed: {e}")
        return
    
    
    if result["status"] == "EMPTY":
        print("Nothing to work on. The source folder is empty")
        log_info("Source folder is empty, nothing to organize")
        return
    
    
    backup_folder = result["backup_folder"]
    log_info(f"Backup created at {backup_folder}")
    
    staging_folder = result["staging_folder"]
    log_info(f"Staging created at {staging_folder}")
    
    print("Organizing files in staging...")
    log_info("Organizing files in staging...")
    file_organizer(str(staging_folder))
    
    # sanity check: files still exist
    if count_files(staging_folder) == 0:
        log_error("Staging folder is empty after organizing - no files found")
        raise RuntimeError("Staging folder is empty after organizing - no files found")
    
    # sanity check: category folders created
    if not any(staging_folder.glob("*/")):
        log_error("File organizing failed - no category folders created")
        raise RuntimeError("File organizing failed - no category folders created")
    
    print("Staging organized successfully.")
    log_info("Staging organized succesfully")
    original_folder = Path(SOURCE_FOLDER)
    
    
    try:
        print("Applying organized folder to original folder...")
        log_info("Applying staging to original")
        apply_to_original(original_folder, staging_folder)
        print("✅ Files applied successfully.")
        log_info("Files applied succesfully to the original")
    except Exception as e:
        print(f"❌ Apply failed: {e}")
        print("↩️ Rolling back from backup...")
        log_error("Apply failed, rollback triggered")
        rollback_from_backup(original_folder, backup_folder)
        print("✅ Rollback completed. Original restored.")
        log_info("Rollback Completed")

    
    

if __name__ == "__main__":
    main()
    