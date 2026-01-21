import tkinter as tk
from tkinter import ttk, filedialog
from cancel_state import request_cancel, reset_cancel
import threading
import queue
from main import run_backend
import sys
from pathlib import Path

class SmartFileManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Manager")
        self.root.geometry("800x520")
        self.root.resizable(False, False)
        self.is_dark = True
        self.ui_queue = queue.Queue()
        
        
        # Icons (load safely for both normal runs and packaged .exe)
        self.moon_icon = self._load_icon("assets_ui/half-moon.png")
        self.sun_icon = self._load_icon("assets_ui/sun.png")
        self.folder_icon = self._load_icon("assets_ui/folder.png")
        
        self.setup_style()
        self.build_header()
        self.build_source_section()
        self.build_backup_section()
        self.build_control()
        self.build_progress_section()
        self.build_log_section()
        self.process_ui_queue()
        self.apply_theme()
    
    
    def _build_folder_section(self, label_text, browse_command):
        frame = ttk.Frame(self.root, padding=(20, 10), style="Dark.TFrame")
        frame.pack(fill="x")
        
        frame.columnconfigure(0, weight=1)
        
        label = ttk.Label(frame, text=label_text, style="Dark.TLabel")
        label.grid(row=0, column=0, sticky="w")
        
        path_var = tk.StringVar()
        
        entry = ttk.Entry(frame, textvariable=path_var, state="readonly", style="Dark.TEntry")
        entry.grid(row=1, column=0, sticky="ew", pady=5)
        
        if self.folder_icon is not None:
            button = ttk.Button(frame, image=self.folder_icon, command=browse_command, style="Dark.TButton")
        else:
            button = ttk.Button(frame, text="Browse", command=browse_command, style="Dark.TButton")
        button.grid(row=1, column=1, padx=5, pady=5)
        
        # Returning widgets explicitly to allow future customization
        return frame, label, path_var, entry, button    
        
    def build_header(self):
        header = ttk.Frame(self.root, padding=(20, 15), style="Dark.TFrame")
        header.pack(fill="x")
        
        header.columnconfigure(0, weight=1)
        
        title = ttk.Label(
            header,
            text="Smart File Manager",
            font=("Segoe UI", 16, "bold"),
            style="Dark.TLabel"
        )
        title.grid(row=0, column=0, sticky="w")
        
        subtitle = ttk.Label(
            header,
            text="Safe file organization",
            font=("Segoe UI", 9),
            style="Dark.TLabel"
        )
        subtitle.grid(row=1, column=0, sticky="w")
        
        if self.moon_icon is not None:
            self.theme_btn = ttk.Button(
                header,
                image=self.moon_icon,
                command=self.toggle_theme,
                style="Dark.TButton"
            )
        else:
            self.theme_btn = ttk.Button(
                header,
                text="Theme",
                command=self.toggle_theme,
                style="Dark.TButton"
            )
        self.theme_btn.grid(row=0, column=1, rowspan=2, sticky="e")

    def _resource_path(self, relative_path: str) -> Path:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        return base / relative_path

    def _load_icon(self, relative_path: str):
        path = self._resource_path(relative_path)
        try:
            if path.exists():
                return tk.PhotoImage(file=str(path))
        except tk.TclError:
            pass
        return None
        
    
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()
            
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
            self.update_controls_state()
            
            
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
            self.update_controls_state()
        
    def build_control(self):
        control_frame = ttk.Frame(self.root, padding=(20, 20), style="Dark.TFrame")
        control_frame.pack()
        
        self.run_btn = ttk.Button(
            control_frame,
            text="Run",
            state="disabled",
            command=self.on_run,
            style="Dark.TButton"
        )
        self.run_btn.pack(side="left", padx=10)
        
        self.cancel_btn = ttk.Button(
            control_frame,
            text = "Cancel",
            state = "disabled",
            command=self.on_cancel,
            style="Dark.TButton"
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        self.reset_btn = ttk.Button(
            control_frame,
            text="Reset",
            state="disabled",
            command=self.on_reset,
            style="Dark.TButton"
        )
        self.reset_btn.pack(side="left", padx=10)
    
    def update_controls_state(self):
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
        
        thread = threading.Thread(
            target=self._background_task,
            daemon=True
        )
        thread.start()
        
    
    def on_cancel(self):
        request_cancel()
        print("Cancel clicked")
        self.log("Cancel requested by the User")
        self.cancel_btn.config(state="disabled")
        self.status_text.set("Cancelling...")
        
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
        progress_frame = ttk.Frame(self.root, padding=(20, 10), style="Dark.TFrame")
        progress_frame.pack(fill="x")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient= "horizontal",
            mode="determinate",
            style="Dark.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x")
        
        self.status_text = tk.StringVar(value="Idle")
        
        status_label = ttk.Label(
            progress_frame,
            textvariable= self.status_text,
            anchor="w",
            style="Dark.TLabel"
        )
        status_label.pack(fill="x", pady=(5,0))
        
    def build_log_section(self):
        log_frame = ttk.Frame(self.root, padding=(20,10), style="Dark.TFrame")
        log_frame.pack(fill="both", expand=True)
        
        log_label = ttk.Label(log_frame, text="Logs", style="Dark.TLabel")
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
        
    def _background_task(self):
        try:
            self.ui_queue.put(("log", "Backend Started"))
            self.ui_queue.put(("status", "Running"))
        
            result = run_backend(
                self.source_path.get(),
                self.backup_path.get(),
                self.report_progress
                )
        
            if result == "SUCCESS":
                self.ui_queue.put(("done", "Completed successfully"))
            elif result == "CANCELLED":
                self.ui_queue.put(("cancelled", "Operation cancelled by User"))
            elif result == "EMPTY":
                self.ui_queue.put(("done", "Nothing to organize (Empty Folder)"))
            elif result == "SETUP_FAILED":
                self.ui_queue.put(("failed", "Cannot stage the folders"))
            elif result == "FAILED":
                self.ui_queue.put(("failed", "Apply failed on source folder"))
            else:
                self.ui_queue.put(("done", "Completed"))
        
        except Exception as e:
            self.ui_queue.put(("error", str(e)))
        
    def process_ui_queue(self):
        try:
            while True:
                msg_type, payload = self.ui_queue.get_nowait()
            
                if msg_type == "log":
                    self.log(payload)
                    
                elif msg_type == "status":
                    self.status_text.set(payload)
                
                elif msg_type == "done":
                    self.log(payload)
                    self.status_text.set("Completed")
                    self.run_btn.config(state="disabled")
                    self.cancel_btn.config(state="disabled")
                    self.reset_btn.config(state="normal")
                    
                    
                elif msg_type == "cancelled":
                    self.log(payload)
                    self.status_text.set("Cancelled")
                    self.run_btn.config(state="disabled")
                    self.cancel_btn.config(state="disabled")
                    self.reset_btn.config(state="normal")
                    
                elif msg_type == "failed" or msg_type == "error":
                    self.log(payload)
                    self.status_text.set("Failed")
                    self.run_btn.config(state="disabled")
                    self.cancel_btn.config(state="disabled")
                    self.reset_btn.config(state="normal")
                    
                elif msg_type == "progress":
                    current, total, phase = payload
                    current = int(current)
                    total = int(total)
                    
                    if total == 0:
                        self.status_text.set(f"{phase}...")
                        continue
                    
                    percent = (current/ total) * 100
                    if int(self.progress_bar["maximum"]) != total:
                        self.progress_bar["maximum"] = total
                    self.progress_bar["value"] = current
                    self.status_text.set(f"{phase}: {percent:.1f}% ({current}/{total})")
                    
                elif msg_type == "apply_start":
                    self.cancel_btn.config(state="disabled")
                    self.reset_btn.config(state="disabled")
                    self.run_btn.config(state="disabled")
                    self.status_text.set("Applying changes (do not close the window...)")                      
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_ui_queue)
        
    def report_progress(self, current, total, phase):
        if phase == "APPLY_START":
            self.ui_queue.put(("apply_start", None))
        else:
            self.ui_queue.put(("progress", (current, total, phase)))
            
    def setup_style(self):
        self.style = ttk.Style()

        # Use a theme that respects colors on Windows.
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            self.style.theme_use("default")

        # Light palette
        light_bg = "#f5f5f5"
        light_fg = "#111111"
        light_entry_bg = "#ffffff"
        light_border = "#d0d0d0"
        light_btn_bg = "#ffffff"
        light_btn_active = "#eaeaea"
        light_accent = "#2563eb"

        self.style.configure("Light.TFrame", background=light_bg)
        self.style.configure("Light.TLabel", background=light_bg, foreground=light_fg)
        self.style.configure(
            "Light.TButton",
            padding=(14, 8),
            background=light_btn_bg,
            foreground=light_fg,
            borderwidth=0,
            relief="flat",
            bordercolor=light_border,
            focusthickness=1,
            focuscolor=light_accent,
        )
        self.style.map(
            "Light.TButton",
            background=[("active", light_btn_active), ("pressed", light_btn_active)],
        )

        self.style.configure(
            "Light.TEntry",
            fieldbackground=light_entry_bg,
            foreground=light_fg,
            background=light_entry_bg,
            bordercolor=light_border,
            lightcolor=light_border,
            darkcolor=light_border,
        )
        self.style.map(
            "Light.TEntry",
            fieldbackground=[("readonly", light_entry_bg)],
            foreground=[("readonly", light_fg)],
        )

        self.style.configure(
            "Light.Horizontal.TProgressbar",
            troughcolor=light_border,
            background=light_accent,
        )

        # Dark palette
        dark_bg = "#1e1e1e"
        dark_fg = "#eeeeee"
        dark_entry_bg = "#2a2a2a"
        dark_border = "#3a3a3a"
        dark_btn_bg = "#2a2a2a"
        dark_btn_active = "#333333"
        dark_accent = "#3b82f6"

        self.style.configure("Dark.TFrame", background=dark_bg)
        self.style.configure("Dark.TLabel", background=dark_bg, foreground=dark_fg)
        self.style.configure(
            "Dark.TButton",
            padding=(14, 8),
            background=dark_btn_bg,
            foreground=dark_fg,
            borderwidth=0,
            relief="flat",
            bordercolor=dark_border,
            focusthickness=1,
            focuscolor=dark_accent,
        )
        self.style.map(
            "Dark.TButton",
            background=[("active", dark_btn_active), ("pressed", dark_btn_active)],
        )

        self.style.configure(
            "Dark.TEntry",
            fieldbackground=dark_entry_bg,
            foreground=dark_fg,
            background=dark_entry_bg,
            bordercolor=dark_border,
            lightcolor=dark_border,
            darkcolor=dark_border,
        )
        self.style.map(
            "Dark.TEntry",
            fieldbackground=[("readonly", dark_entry_bg)],
            foreground=[("readonly", dark_fg)],
        )

        self.style.configure(
            "Dark.Horizontal.TProgressbar",
            troughcolor=dark_border,
            background=dark_accent,
        )
        
    def apply_theme(self):
        theme = "Dark" if self.is_dark else "Light"

        # Window + non-ttk widgets
        if theme == "Dark":
            self.root.configure(bg="#1e1e1e")
            self.log_text.configure(bg="#1e1e1e", fg="#eeeeee", insertbackground="#eeeeee")
        else:
            self.root.configure(bg="#f5f5f5")
            self.log_text.configure(bg="#ffffff", fg="#111111", insertbackground="#111111")
        
        for widget in self.root.winfo_children():
            self._apply_theme_recursive(widget, theme)
            
        self.theme_btn.config(
            image=self.moon_icon if self.is_dark else self.sun_icon
        )
        
    def _apply_theme_recursive(self, widget, theme):
        try:
            if isinstance(widget, ttk.Frame):
                widget.configure(style=f"{theme}.TFrame")
            elif isinstance(widget, ttk.Label):
                widget.configure(style=f"{theme}.TLabel")
            elif isinstance(widget, ttk.Button):
                widget.configure(style=f"{theme}.TButton")
            elif isinstance(widget, ttk.Entry):
                widget.configure(style=f"{theme}.TEntry")
            elif isinstance(widget, ttk.Progressbar):
                widget.configure(style=f"{theme}.Horizontal.TProgressbar")
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self._apply_theme_recursive(child, theme)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartFileManagerUI(root)
    root.mainloop()