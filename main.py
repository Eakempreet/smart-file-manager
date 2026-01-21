from pathlib import Path
from backup import prepare_backup_staging, count_files
from organizer import file_organizer
from apply import apply_to_original, rollback_from_backup, clear_folder_contents
from logger import log_info, log_error, log_warning
import cancel_state
from cancel_state import reset_cancel
import shutil

SOURCE_FOLDER = "D:/Downloads"
BACKUP_FOLDER = "D:/SFM/Backup_SFM"

def cleanup_staging_and_exit(staging_folder, reason="cancelation"):
    """Clean up staging folder after cancellation"""
    sf = Path(staging_folder)
    # If staging was already deleted (e.g., apply_to_original removed it), skip quietly.
    if not sf.exists():
        log_info(f"Staging folder already removed; no cleanup needed after {reason}")
        return
    
    print(f"🗑️ Attempting to delete staging folder: {sf}")
    try:
        # Use rmtree directly to remove folder and all contents
        shutil.rmtree(sf)
        
        # Verify deletion
        if not sf.exists():
            print(f"✅ Staging folder cleaned up: {sf}")
            log_info(f"Staging folder deleted after {reason}: {sf}")
        else:
            print(f"⚠️ Folder still exists after cleanup attempt: {sf}")
            log_warning(f"Staging folder still exists after rmtree: {sf}")
    except PermissionError as e:
        print(f"⚠️ Permission denied (folder may be locked by Windows): {sf}")
        print(f"   You can manually delete: {sf}")
        log_warning(f"PermissionError deleting staging folder: {sf} :: {e}")
    except Exception as e:
        print(f"⚠️ Could not delete staging folder: {e}")
        print(f"   Path: {sf}")
        log_warning(f"Could not delete staging folder: {sf} :: {e}")

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
        # Clean up any partial staging that might exist
        if staging_path.exists():
            cleanup_staging_and_exit(staging_path, "cancelation during backup/staging")
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
    