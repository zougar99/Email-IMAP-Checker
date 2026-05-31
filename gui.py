#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email IMAP Checker - Professional GUI Application
Modern, Feature-Rich Interface for Email Validation
Version 3.5 - Enhanced Edition
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import queue
import json
import re
from datetime import datetime
from pathlib import Path

class ModernStyle:
    """Professional color themes"""
    
    THEMES = {
        "dark": {
            "bg": "#0d1117",
            "bg_secondary": "#161b22",
            "bg_tertiary": "#21262d",
            "fg": "#c9d1d9",
            "fg_secondary": "#8b949e",
            "accent": "#58a6ff",
            "accent_hover": "#79b8ff",
            "success": "#3fb950",
            "success_hover": "#56d364",
            "error": "#f85149",
            "error_hover": "#ff6e6a",
            "warning": "#d29922",
            "border": "#30363d",
            "input_bg": "#0d1117",
            "button_bg": "#21262d",
            "highlight": "#388bfd"
        },
        "light": {
            "bg": "#ffffff",
            "bg_secondary": "#f6f8fa",
            "bg_tertiary": "#e6eaef",
            "fg": "#24292f",
            "fg_secondary": "#57606a",
            "accent": "#0969da",
            "accent_hover": "#0550ae",
            "success": "#1a7f37",
            "success_hover": "#2da44e",
            "error": "#cf222e",
            "error_hover": "#a40e26",
            "warning": "#9a6700",
            "border": "#d0d7de",
            "input_bg": "#ffffff",
            "button_bg": "#f6f8fa",
            "highlight": "#0969da"
        },
        "blue": {
            "bg": "#0a1929",
            "bg_secondary": "#0d2137",
            "bg_tertiary": "#132f4c",
            "fg": "#b2bac2",
            "fg_secondary": "#6f7e8c",
            "accent": "#5090d3",
            "accent_hover": "#66b2ff",
            "success": "#1db954",
            "success_hover": "#1ed760",
            "error": "#eb5757",
            "error_hover": "#ff6b6b",
            "warning": "#f0b429",
            "border": "#1e4976",
            "input_bg": "#0a1929",
            "button_bg": "#132f4c",
            "highlight": "#5090d3"
        },
        "purple": {
            "bg": "#1a1625",
            "bg_secondary": "#231d2e",
            "bg_tertiary": "#2d2640",
            "fg": "#e0d6f2",
            "fg_secondary": "#9d8cb8",
            "accent": "#a78bfa",
            "accent_hover": "#c4b5fd",
            "success": "#34d399",
            "success_hover": "#6ee7b7",
            "error": "#f87171",
            "error_hover": "#fca5a5",
            "warning": "#fbbf24",
            "border": "#3d3554",
            "input_bg": "#1a1625",
            "button_bg": "#2d2640",
            "highlight": "#a78bfa"
        }
    }


class EmailCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email IMAP Checker Pro v3.5")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        
        # Current theme
        self.current_theme = "dark"
        self.colors = ModernStyle.THEMES[self.current_theme]
        
        # Variables
        self.input_file = tk.StringVar(value="input.txt")
        self.threads = tk.StringVar(value="500")
        self.timeout = tk.StringVar(value="5")
        self.check_unknown = tk.BooleanVar(value=True)
        self.save_invalid = tk.BooleanVar(value=True)
        self.grab_emails = tk.BooleanVar(value=False)
        
        # Statistics
        self.valid_count = tk.IntVar(value=0)
        self.invalid_count = tk.IntVar(value=0)
        self.total_count = tk.IntVar(value=0)
        self.progress_var = tk.DoubleVar(value=0)
        self.speed_var = tk.StringVar(value="0/s")
        self.eta_var = tk.StringVar(value="--:--")
        
        self.process = None
        self.is_running = False
        self.output_queue = queue.Queue()
        self.start_time = None
        
        # Configure root
        self.root.configure(bg=self.colors["bg"])
        
        # Create main layout
        self.create_widgets()
        self.check_output_queue()
        self.update_statistics()
        
        # Center window
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def apply_theme(self):
        """Apply current theme to all widgets"""
        self.colors = ModernStyle.THEMES[self.current_theme]
        self.root.configure(bg=self.colors["bg"])
        # Recreate widgets with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # ===== HEADER =====
        self.create_header(main_container)
        
        # ===== STATISTICS CARDS =====
        self.create_stats_cards(main_container)
        
        # ===== SETTINGS PANEL =====
        self.create_settings_panel(main_container)
        
        # ===== CONTROL BUTTONS =====
        self.create_control_buttons(main_container)
        
        # ===== PROGRESS BAR =====
        self.create_progress_bar(main_container)
        
        # ===== OUTPUT LOG =====
        self.create_output_log(main_container)
        
        # ===== FOOTER =====
        self.create_footer(main_container)
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side - Title
        left_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        left_frame.pack(side=tk.LEFT)
        
        title = tk.Label(
            left_frame,
            text="Email IMAP Checker Pro",
            font=("Segoe UI", 26, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        )
        title.pack(anchor="w")
        
        subtitle = tk.Label(
            left_frame,
            text="Professional Email Validation Tool | 1,833 Global Providers",
            font=("Segoe UI", 11),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        )
        subtitle.pack(anchor="w")
        
        # Right side - Theme selector
        right_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        right_frame.pack(side=tk.RIGHT)
        
        theme_label = tk.Label(
            right_frame,
            text="Theme:",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 5))
        
        for theme_name in ["dark", "light", "blue", "purple"]:
            btn = tk.Button(
                right_frame,
                text=theme_name.capitalize()[:1],
                font=("Segoe UI", 9, "bold"),
                width=3,
                bg=ModernStyle.THEMES[theme_name]["accent"],
                fg="#ffffff" if theme_name != "light" else "#000000",
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda t=theme_name: self.change_theme(t)
            )
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_stats_cards(self, parent):
        cards_frame = tk.Frame(parent, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configure grid columns to be equal
        for i in range(5):
            cards_frame.columnconfigure(i, weight=1)
            
        # Stats data
        stats = [
            ("Total", self.total_count, self.colors["accent"], "file-text"),
            ("Valid", self.valid_count, self.colors["success"], "check-circle"),
            ("Invalid", self.invalid_count, self.colors["error"], "x-circle"),
            ("Speed", self.speed_var, self.colors["warning"], "zap"),
            ("ETA", self.eta_var, self.colors["fg_secondary"], "clock")
        ]
        
        self.stat_labels = {}
        
        for i, (name, var, color, icon) in enumerate(stats):
            card = tk.Frame(
                cards_frame,
                bg=self.colors["bg_secondary"],
                highlightbackground=self.colors["border"],
                highlightthickness=1
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            # Card inner padding
            inner = tk.Frame(card, bg=self.colors["bg_secondary"])
            inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
            
            # Title
            title_lbl = tk.Label(
                inner,
                text=name.upper(),
                font=("Segoe UI", 9, "bold"),
                bg=self.colors["bg_secondary"],
                fg=self.colors["fg_secondary"]
            )
            title_lbl.pack(anchor="w")
            
            # Value
            if isinstance(var, tk.StringVar):
                value_lbl = tk.Label(
                    inner,
                    textvariable=var,
                    font=("Segoe UI", 22, "bold"),
                    bg=self.colors["bg_secondary"],
                    fg=color
                )
            else:
                value_lbl = tk.Label(
                    inner,
                    textvariable=var,
                    font=("Segoe UI", 22, "bold"),
                    bg=self.colors["bg_secondary"],
                    fg=color
                )
            value_lbl.pack(anchor="w")
            self.stat_labels[name] = value_lbl
            
    def create_settings_panel(self, parent):
        settings_frame = tk.Frame(
            parent,
            bg=self.colors["bg_secondary"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner = tk.Frame(settings_frame, bg=self.colors["bg_secondary"])
        inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Title
        tk.Label(
            inner,
            text="CONFIGURATION",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Row 1: File input
        row1 = tk.Frame(inner, bg=self.colors["bg_secondary"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="Input File:",
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.file_entry = tk.Entry(
            row1,
            textvariable=self.input_file,
            font=("Segoe UI", 10),
            bg=self.colors["input_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=50
        )
        self.file_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=6)
        
        browse_btn = tk.Button(
            row1,
            text="Browse",
            font=("Segoe UI", 9),
            bg=self.colors["button_bg"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.browse_file
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Row 2: Parameters
        row2 = tk.Frame(inner, bg=self.colors["bg_secondary"])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="Threads:",
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        threads_entry = tk.Entry(
            row2,
            textvariable=self.threads,
            font=("Segoe UI", 10),
            bg=self.colors["input_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=10
        )
        threads_entry.pack(side=tk.LEFT, padx=(0, 20), ipady=6)
        
        tk.Label(
            row2,
            text="Timeout (sec):",
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"]
        ).pack(side=tk.LEFT)
        
        timeout_entry = tk.Entry(
            row2,
            textvariable=self.timeout,
            font=("Segoe UI", 10),
            bg=self.colors["input_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=10
        )
        timeout_entry.pack(side=tk.LEFT, padx=(5, 0), ipady=6)
        
        # Row 3: Checkboxes
        row3 = tk.Frame(inner, bg=self.colors["bg_secondary"])
        row3.pack(fill=tk.X, pady=10)
        
        style = ttk.Style()
        style.configure(
            "Custom.TCheckbutton",
            background=self.colors["bg_secondary"],
            foreground=self.colors["fg"]
        )
        
        chk1 = tk.Checkbutton(
            row3,
            text="Check Unknown Hosts",
            variable=self.check_unknown,
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["fg"]
        )
        chk1.pack(side=tk.LEFT, padx=(0, 20))
        
        chk2 = tk.Checkbutton(
            row3,
            text="Save Invalid Emails",
            variable=self.save_invalid,
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["fg"]
        )
        chk2.pack(side=tk.LEFT, padx=(0, 20))
        
        chk3 = tk.Checkbutton(
            row3,
            text="Grab Email Contents",
            variable=self.grab_emails,
            font=("Segoe UI", 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["fg"]
        )
        chk3.pack(side=tk.LEFT)
        
    def create_control_buttons(self, parent):
        buttons_frame = tk.Frame(parent, bg=self.colors["bg"])
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Start button
        self.start_btn = tk.Button(
            buttons_frame,
            text="▶  START CHECKING",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["success"],
            fg="#ffffff",
            activebackground=self.colors["success_hover"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=20,
            height=2,
            command=self.start_checking
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            buttons_frame,
            text="⏹  STOP",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["error"],
            fg="#ffffff",
            activebackground=self.colors["error_hover"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=12,
            height=2,
            state=tk.DISABLED,
            command=self.stop_checking
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open Output button
        self.open_btn = tk.Button(
            buttons_frame,
            text="📂  OUTPUT FOLDER",
            font=("Segoe UI", 11),
            bg=self.colors["button_bg"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=16,
            height=2,
            command=self.open_output_folder
        )
        self.open_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Statistics button
        self.stats_btn = tk.Button(
            buttons_frame,
            text="📊  STATISTICS",
            font=("Segoe UI", 11),
            bg=self.colors["button_bg"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=14,
            height=2,
            command=self.show_statistics
        )
        self.stats_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Log button
        self.clear_btn = tk.Button(
            buttons_frame,
            text="🗑  CLEAR LOG",
            font=("Segoe UI", 11),
            bg=self.colors["button_bg"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=12,
            height=2,
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_frame = tk.Frame(buttons_frame, bg=self.colors["bg"])
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Label(
            self.status_frame,
            text="●",
            font=("Segoe UI", 14),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        )
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=("Segoe UI", 11),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        )
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
    def create_progress_bar(self, parent):
        progress_frame = tk.Frame(parent, bg=self.colors["bg"])
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar with custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=self.colors["accent"],
            troughcolor=self.colors["bg_secondary"],
            borderwidth=0,
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"]
        )
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style="Custom.Horizontal.TProgressbar",
            length=400
        )
        self.progress_bar.pack(fill=tk.X, ipady=3)
        
        # Progress label
        self.progress_label = tk.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 9),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        )
        self.progress_label.pack(pady=(5, 0))
        
    def create_output_log(self, parent):
        log_frame = tk.Frame(
            parent,
            bg=self.colors["bg_secondary"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Header
        header = tk.Frame(log_frame, bg=self.colors["bg_tertiary"])
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="  OUTPUT LOG",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_tertiary"],
            fg=self.colors["fg"],
            pady=8
        ).pack(side=tk.LEFT)
        
        # Output text
        self.output_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored output
        self.output_text.tag_config("info", foreground=self.colors["accent"])
        self.output_text.tag_config("success", foreground=self.colors["success"])
        self.output_text.tag_config("error", foreground=self.colors["error"])
        self.output_text.tag_config("warning", foreground=self.colors["warning"])
        self.output_text.tag_config("timestamp", foreground=self.colors["fg_secondary"])
        
        # Initial message
        self.log_output("Welcome to Email IMAP Checker Pro v3.5", "info")
        self.log_output(f"Loaded 1,833 email providers from hoster.dat", "info")
        self.log_output("Ready to start checking...", "info")
        
    def create_footer(self, parent):
        footer_frame = tk.Frame(parent, bg=self.colors["bg"])
        footer_frame.pack(fill=tk.X)
        
        tk.Label(
            footer_frame,
            text="Email IMAP Checker Pro v3.5 | Supports 1,833+ Global Email Providers | Telegram: @werlist99",
            font=("Segoe UI", 9),
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"]
        ).pack()
        
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Count lines
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for line in f if line.strip())
                self.total_count.set(lines)
                self.log_output(f"Loaded {lines} email(s) from {os.path.basename(filename)}", "info")
            except Exception as e:
                self.log_output(f"Error reading file: {e}", "error")
                
    def log_output(self, message, tag=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        
    def clear_log(self):
        self.output_text.delete(1.0, tk.END)
        self.log_output("Log cleared", "info")
        
    def start_checking(self):
        if self.is_running:
            return
            
        input_file = self.input_file.get()
        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"Input file not found: {input_file}")
            return
            
        # Reset statistics
        self.valid_count.set(0)
        self.invalid_count.set(0)
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        
        # Count total emails
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                total = sum(1 for line in f if line.strip() and ':' in line)
            self.total_count.set(total)
        except:
            self.total_count.set(0)
            
        self.is_running = True
        self.start_time = datetime.now()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_indicator.config(fg=self.colors["success"])
        self.status_label.config(text="Running...", fg=self.colors["success"])
        
        self.log_output("=" * 60, "info")
        self.log_output("Starting email validation...", "info")
        self.log_output(f"Input: {input_file}", "info")
        self.log_output(f"Threads: {self.threads.get()}, Timeout: {self.timeout.get()}s", "info")
        self.log_output("=" * 60, "info")
        
        # Build command
        cmd = [
            sys.executable, "atr3.py",
            "-i", input_file,
            "-t", self.threads.get(),
            "-to", self.timeout.get()
        ]
        
        if not self.check_unknown.get():
            cmd.extend(["-uh", "False"])
        if not self.save_invalid.get():
            cmd.extend(["-iu", "False"])
        if self.grab_emails.get():
            cmd.extend(["-g", "True"])
            
        # Start process in thread
        thread = threading.Thread(target=self.run_process, args=(cmd,), daemon=True)
        thread.start()
        
    def run_process(self, cmd):
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_queue.put(line.strip())
                    
            self.process.wait()
            self.output_queue.put("__DONE__")
            
        except Exception as e:
            self.output_queue.put(f"[ERROR] {str(e)}")
            self.output_queue.put("__DONE__")
            
    def check_output_queue(self):
        try:
            while True:
                message = self.output_queue.get_nowait()
                if message == "__DONE__":
                    self.on_process_complete()
                else:
                    # Parse and update statistics
                    self.parse_output(message)
                    
                    # Determine tag based on message content
                    tag = None
                    if "[INFO]" in message or "[OK]" in message:
                        tag = "info"
                    elif "Valid" in message or "valid" in message:
                        tag = "success"
                    elif "[ERROR]" in message or "Error" in message:
                        tag = "error"
                    elif "WARNING" in message:
                        tag = "warning"
                    self.log_output(message, tag)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_output_queue)
            
    def parse_output(self, message):
        """Parse output to update statistics"""
        # Try to extract valid count from messages
        if "Valid" in message and ":" in message:
            try:
                valid = int(re.search(r'(\d+)', message.split("Valid")[-1]).group(1))
                self.valid_count.set(valid)
            except:
                pass
                
    def update_statistics(self):
        """Update statistics periodically"""
        if self.is_running and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            total = self.total_count.get()
            valid = self.valid_count.get()
            invalid = self.invalid_count.get()
            processed = valid + invalid
            
            if elapsed > 0 and processed > 0:
                speed = processed / elapsed
                self.speed_var.set(f"{speed:.1f}/s")
                
                if total > 0 and speed > 0:
                    remaining = total - processed
                    eta_seconds = remaining / speed
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    self.eta_var.set(f"{eta_min:02d}:{eta_sec:02d}")
                    
                    progress = (processed / total) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"{progress:.1f}%")
                    
        self.root.after(1000, self.update_statistics)
        
    def on_process_complete(self):
        self.is_running = False
        self.process = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_indicator.config(fg=self.colors["accent"])
        self.status_label.config(text="Completed", fg=self.colors["accent"])
        self.progress_var.set(100)
        self.progress_label.config(text="100%")
        
        self.log_output("=" * 60, "success")
        self.log_output("Process completed successfully!", "success")
        
        # Calculate and show summary
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.log_output(f"Total time: {elapsed:.1f} seconds", "info")
        self.log_output(f"Valid emails: {self.valid_count.get()}", "success")
        self.log_output(f"Invalid emails: {self.invalid_count.get()}", "error")
        self.log_output("=" * 60, "success")
        
    def stop_checking(self):
        if self.process:
            self.process.terminate()
            self.log_output("Process stopped by user", "warning")
            self.on_process_complete()
            
    def open_output_folder(self):
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "M-P-V-I")
        if os.path.exists(output_folder):
            # Open the most recent folder
            folders = sorted(Path(output_folder).iterdir(), key=os.path.getmtime, reverse=True)
            if folders:
                os.startfile(str(folders[0]))
            else:
                os.startfile(output_folder)
        else:
            messagebox.showinfo("Info", "Output folder not found. Run the checker first.")
            
    def show_statistics(self):
        """Show detailed statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("500x400")
        stats_window.configure(bg=self.colors["bg"])
        
        # Read results
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "M-P-V-I")
        
        content = tk.Text(
            stats_window,
            font=("Consolas", 11),
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            relief=tk.FLAT,
            padx=20,
            pady=20
        )
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Gather statistics
        stats_text = "=" * 40 + "\n"
        stats_text += "      EMAIL CHECKER STATISTICS\n"
        stats_text += "=" * 40 + "\n\n"
        stats_text += f"Total Emails:    {self.total_count.get()}\n"
        stats_text += f"Valid Emails:    {self.valid_count.get()}\n"
        stats_text += f"Invalid Emails:  {self.invalid_count.get()}\n"
        stats_text += f"\n"
        stats_text += f"Current Speed:   {self.speed_var.get()}\n"
        stats_text += f"ETA:             {self.eta_var.get()}\n"
        stats_text += f"\n"
        stats_text += "=" * 40 + "\n"
        stats_text += "  ISP/BOITE DISTRIBUTION\n"
        stats_text += "=" * 40 + "\n\n"
        
        # Read ISP stats
        isp_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isp+boite")
        if os.path.exists(isp_folder):
            isp_counts = []
            for f in os.listdir(isp_folder):
                if f.startswith("mail_") and f.endswith(".txt"):
                    try:
                        with open(os.path.join(isp_folder, f), 'r', encoding='utf-8') as file:
                            count = sum(1 for _ in file)
                        isp_name = f[5:-4]  # Remove "mail_" and ".txt"
                        isp_counts.append((isp_name, count))
                    except:
                        pass
                        
            # Sort by count
            isp_counts.sort(key=lambda x: x[1], reverse=True)
            
            for isp, count in isp_counts[:20]:  # Top 20
                stats_text += f"{isp:30} {count:5}\n"
        else:
            stats_text += "No ISP data available yet.\n"
            
        content.insert(tk.END, stats_text)
        content.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    
    # Set icon if available
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
        
    app = EmailCheckerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
