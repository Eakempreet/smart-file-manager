from pathlib import Path
import shutil


FILE_CATEGORIES = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"
    ],

    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".ppt", ".pptx", ".xls", ".xlsx", ".csv"
    ],

    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"
    ],

    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"
    ],

    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz"
    ],

    "Code": [
        ".py", ".java", ".cpp", ".c", ".js", ".html",
        ".css", ".json", ".xml", ".yml", ".yaml"
    ],

    "Executables": [
        ".exe", ".msi", ".bat", ".sh"
    ]
}

def file_organizer(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError("Provided path is not a valid folder")

    for f in folder.iterdir():
        if f.is_file():    
            suffix = f.suffix.lower()
            found = False
    
            for category, extensions in FILE_CATEGORIES.items():
                if suffix in extensions:
                    destination_folder = folder / category
                    destination_folder.mkdir(exist_ok=True)
                
                    destination_path = destination_folder / f.name
                    shutil.move(f, destination_path)
                
                    found = True
                    break

            if not found:
                destination_folder = folder / 'Others'
                destination_folder.mkdir(exist_ok=True)
            
                destination_path = destination_folder / f.name
                shutil.move(f, destination_path)
            
            
            
            
            
if __name__ == "__main__":
    file_organizer('D:/Downloads')  # or whatever folder you want
            

    