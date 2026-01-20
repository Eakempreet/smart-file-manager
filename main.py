from pathlib import Path
from backup import prepare_backup_staging, count_files
from organizer import file_organizer
from apply import apply_to_original, rollback_from_backup, clear_folder_contents
from logger import log_info, log_error
from cancel_state import cancel_requested, reset_cancel
import shutil

SOURCE_FOLDER = "D:/Downloads"
BACKUP_FOLDER = "D:/SFM/Backup_SFM"
STAGING_FOLDER = "D:/SFM/temp/Staging"

def cleanup_staging_and_exit(staging_folder, reason="cancelation"):
    """Clean up staging folder after cancellation"""
    try:
        clear_folder_contents(staging_folder)
        staging_folder.rmdir()
        print("✅ Staging folder cleaned up.")
        log_info(f"Staging folder deleted after {reason}")
    except Exception as e:
        print(f"⚠️ Warning: Could not delete staging folder: {e}")
        log_error(f"Could not delete staging folder: {e}")

def run_backend(source_Folder, backup_Folder, staging_Folder):
    # resetting the cancel attribute
    reset_cancel()
    log_info("=" * 100)
    log_info("Program Started")
    try:
        result = prepare_backup_staging(
            source_Folder,
            backup_Folder,
            staging_Folder
        )
    except Exception as e:
        print(f"Setup failed: {e}")
        log_error(f"Setup failed: {e}")
        return
    
    if result["status"] == "CANCELLED":
        print("Operation cancelled during backup/staging.")
        log_info("Cancelled during backup/staging phase")
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
    status = file_organizer(str(staging_folder))
    
    # Cancel before apply 
    if status == "CANCELLED":
        print("Operation cancelled by user during organizing.")
        log_info("Operation cancelled by the user during organizing")
        cleanup_staging_and_exit(staging_folder, "cancelation during organizing")
        return       
              
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
        if cancel_requested:
            print("Operation cancelled just before apply phase.")
            log_info("Cancelled just before apply phase")
            cleanup_staging_and_exit(staging_folder, "cancelation before apply")
            return
         
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

    
def main():
    run_backend(
        SOURCE_FOLDER,
        BACKUP_FOLDER,
        STAGING_FOLDER
    )

    

if __name__ == "__main__":
    main()
    