import tkinter as tk
from tkinter import ttk, filedialog
from cancel_state import request_cancel, reset_cancel

class SmartFileManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Manager")
        self.root.geometry("800x520")
        self.root.resizable(False, False)
        self.is_dark = True
        
        
        # Icons
        self.moon_icon = tk.PhotoImage(file="assets_ui/half-moon.png")
        self.sun_icon = tk.PhotoImage(file="assets_ui/sun.png")
        self.folder_icon = tk.PhotoImage(file="assets_ui/folder.png")
        
        self.build_header()
        self.build_source_section()
        self.build_backup_section()
        self.build_control()
        self.build_progress_section()
        self.build_log_section()
    
    
    def _build_folder_section(self, label_text, browse_command):
        frame = ttk.Frame(self.root, padding=(20, 10))
        frame.pack(fill="x")
        
        frame.columnconfigure(0, weight=1)
        
        label = ttk.Label(frame, text=label_text)
        label.grid(row=0, column=0, sticky="w")
        
        path_var = tk.StringVar()
        
        entry = ttk.Entry(frame, textvariable=path_var, state="readonly")
        entry.grid(row=1, column=0, sticky="ew", pady=5)
        
        button = ttk.Button(frame, image=self.folder_icon, command=browse_command)
        button.grid(row=1, column=1, padx=5, pady=5)
        
        # Returning widgets explicitly to allow future customization
        return frame, label, path_var, entry, button    
        
    def build_header(self):
        header = ttk.Frame(self.root, padding=(20, 15))
        header.pack(fill="x")
        
        header.columnconfigure(0, weight=1)
        
        title = ttk.Label(
            header,
            text="Smart File Manager",
            font=("Segoe UI", 16, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        subtitle = ttk.Label(
            header,
            text="Safe file organization",
            font=("Segoe UI", 9)
        )
        subtitle.grid(row=1, column=0, sticky="w")
        
        self.theme_btn = ttk.Button(
            header,
            image=self.moon_icon,
            command=self.toggle_theme
        )
        self.theme_btn.grid(row=0, column=1, rowspan=2, sticky="e")
        
    
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        
        if self.is_dark:
            self.theme_btn.config(image=self.moon_icon)
        else:
            self.theme_btn.config(image=self.sun_icon)
            
    def build_source_section(self):
        self.source_frame, self.source_label, self.source_path, self.source_entry, self.source_button = self._build_folder_section(
            "Source Folder",
            self.browse_source
        )
        
    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)
            self.log(f"Source folder selected: {path}")
            self.validation_ready()
            
            
    def build_backup_section(self):
        self.backup_frame, self.backup_label, self.backup_path, self.backup_entry, self.backup_button = self._build_folder_section(
            "Backup Location",
            self.browse_backup
        )


    def browse_backup(self):
        path = filedialog.askdirectory()
        if path:
            self.backup_path.set(path)
            self.log(f"Backup folder selected: {path}")
            self.validation_ready()
        
    def build_control(self):
        control_frame = ttk.Frame(self.root, padding=(20, 20))
        control_frame.pack()
        
        self.run_btn = ttk.Button(
            control_frame,
            text="Run",
            state="disabled",
            command=self.on_run
        )
        self.run_btn.pack(side="left", padx=10)
        
        self.cancel_btn = ttk.Button(
            control_frame,
            text = "Cancel",
            state = "disabled",
            command=self.on_cancel
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        self.reset_btn = ttk.Button(
            control_frame,
            text="Reset",
            state="disabled",
            command=self.on_reset
        )
        self.reset_btn.pack(side="left", padx=10)
    
    def validation_ready(self):
        src = self.source_path.get()
        bkp = self.backup_path.get()
        
        if src and bkp and src != bkp:
            self.run_btn.config(state="normal")
    
        if src or bkp:  # Enable reset if ANY path selected
            self.reset_btn.config(state="normal")
        else:
            self.reset_btn.config(state="disabled")
            
    def on_run(self):
        reset_cancel()
        print("Run clicked")
        self.log("Run Started")
        self.run_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.reset_btn.config(state="disabled")
        self.status_text.set("Running...")
        
    
    def on_cancel(self):
        request_cancel()
        print("Cancel clicked")
        self.log("Operation canceled by the User")
        self.status_text.set("Cancelled")
        self.cancel_btn.config(state="disabled")
        
    def on_reset(self):
        reset_cancel()
        self.log("UI reset... Select the Folders")
        self.source_path.set("")
        self.backup_path.set("")
        self.progress_bar["value"] = 0
        self.status_text.set("Idle")
        
        self.run_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")
        
    def build_progress_section(self):
        progress_frame = ttk.Frame(self.root, padding=(20, 10))
        progress_frame.pack(fill="x")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient= "horizontal",
            mode="determinate"
        )
        self.progress_bar.pack(fill="x")
        
        self.status_text = tk.StringVar(value="Idle")
        
        status_label = ttk.Label(
            progress_frame,
            textvariable= self.status_text,
            anchor="w"
        )
        status_label.pack(fill="x", pady=(5,0))
        
    def build_log_section(self):
        log_frame = ttk.Frame(self.root, padding=(20,10))
        log_frame.pack(fill="both", expand=True)
        
        log_label = ttk.Label(log_frame, text="Logs")
        log_label.pack(anchor="w")
        
        self.log_text = tk.Text(
            log_frame,
            height = 8,
            state = "disabled",
            font = ("Consolas", 9),
            wrap = "word"
        )
        self.log_text.pack(fill="both", expand = True, pady = (5,0))

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartFileManagerUI(root)
    root.mainloop()