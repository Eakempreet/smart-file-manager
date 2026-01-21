import tkinter as tk
from ui import SmartFileManagerUI

def main():
    root = tk.Tk()
    app = SmartFileManagerUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()