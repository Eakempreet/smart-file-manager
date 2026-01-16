from datetime import datetime
from pathlib import Path

LOG_FILE = Path("smart_file_manager.log")

def _write_log(level: str, message : str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {level.upper} | {message}\n"
    
    with open(LOG_FILE, mode="a", encoding="utf-8") as f:
        f.write(line)
        

def log_info(message : str):
    _write_log("INFO", message)
    
def log_warning(message : str):
    _write_log("WARNING", message)
    
def log_error(message : str):
    _write_log("ERROR", message)
    
