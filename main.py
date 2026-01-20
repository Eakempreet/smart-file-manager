from pathlib import Path
from backup import prepare_backup_staging, count_files
from organizer import file_organizer
from apply import apply_to_original, rollback_from_backup, clear_folder_contents
from logger import log_info, log_error
import cancel_state
from cancel_state import reset_cancel

SOURCE_FOLDER = "D:/Downloads"
BACKUP_FOLDER = "D:/SFM/Backup_SFM"

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

def run_backend(source_Folder, backup_Folder):
    # resetting the cancel attribute
    reset_cancel()
    log_info("=" * 100)
    log_info("Program Started")
    
    # Convert to Path objects for consistency
    source_path = Path(source_Folder)
    backup_path = Path(backup_Folder)
    staging_path = backup_path.parent / "Staging"
    
    try:
        result = prepare_backup_staging(
            str(source_path),
            str(backup_path),
            str(staging_path)
        )
    except Exception as e:
        print(f"Setup failed: {e}")
        log_error(f"Setup failed: {e}")
        return "SETUP_FAILED"
    
    if result["status"] == "CANCELLED":
        print("Operation cancelled during backup/staging.")
        log_info("Cancelled during backup/staging phase")
        return "CANCELLED"
    
    if result["status"] == "EMPTY":
        print("Nothing to work on. The source folder is empty")
        log_info("Source folder is empty, nothing to organize")
        return "EMPTY"
    
    
    backup_folder = Path(result["backup_folder"])
    log_info(f"Backup created at {backup_folder}")
    
    staging_folder = Path(result["staging_folder"])
    log_info(f"Staging created at {staging_folder}")
    
    print("Organizing files in staging...")
    log_info("Organizing files in staging...")
    status = file_organizer(str(staging_folder))
    
    # Cancel before apply 
    if status == "CANCELLED":
        print("Operation cancelled by user during organizing.")
        log_info("Operation cancelled by the user during organizing")
        cleanup_staging_and_exit(staging_folder, "cancelation during organizing")
        return "CANCELLED"       
              
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
    
    try:
        if cancel_state.cancel_requested:
            print("Operation cancelled just before apply phase.")
            log_info("Cancelled just before apply phase")
            cleanup_staging_and_exit(staging_folder, "cancelation before apply")
            return "CANCELLED"
         
        print("Applying organized folder to original folder...")
        log_info("Applying staging to original")
        apply_to_original(source_path, staging_folder)
        print("✅ Files applied successfully.")
        log_info("Files applied succesfully to the original")
        cleanup_staging_and_exit(staging_folder, "success")
        return "SUCCESS"
    except Exception as e:
        print(f"❌ Apply failed: {e}")
        print("↩️ Rolling back from backup...")
        log_error("Apply failed, rollback triggered")
        rollback_from_backup(source_path, backup_folder)
        print("✅ Rollback completed. Original restored.")
        log_info("Rollback Completed")
        return "FAILED"

    
def main():
    run_backend(
        SOURCE_FOLDER,
        BACKUP_FOLDER
    )

    

if __name__ == "__main__":
    main()
    