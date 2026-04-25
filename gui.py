import customtkinter as ctk
from tkinter import filedialog
import threading
import sys
import os
import json
from datetime import datetime
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONVERSIONS = {
    "PNG":  ["JPG", "PDF", "WEBP"],
    "JPG":  ["PNG", "PDF"],
    "JPEG": ["PNG", "PDF"],
    "WEBP": ["PNG", "JPG"],
    "PDF":  ["DOCX"],   
    "CSV":  ["JSON"],
}

ACCENT   = "#3B82F6"
BG_CARD  = "#1E1E2E"
BG_CHIP  = "#2A2A3D"
BG_CHIP_ACTIVE = "#3B82F6"

# File for storing recent files
RECENT_FILE = Path.home() / ".convertix_recent.json"


class SimpleDialog(ctk.CTkToplevel):
    """Simple dialog for showing messages"""
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.configure(fg_color="#13131F")
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        ctk.CTkLabel(self, text=message, wraplength=350, font=("Segoe UI", 12)).pack(pady=20, padx=20)
        
        btn = ctk.CTkButton(self, text="OK", command=self.destroy, fg_color=ACCENT, width=100)
        btn.pack(pady=10)
        
        # Wait for window to close
        self.wait_window()


class ConvertixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Convertix")
        self.geometry("620x650")
        self.resizable(False, False)
        self.configure(fg_color="#13131F")

        self.input_file  = ""
        self.output_file = ""
        self.from_fmt    = "PNG"
        self.to_fmt      = "JPG"
        
        # For cancellation
        self.conversion_thread = None
        self.cancel_requested = False

        self._build_ui()
        self._load_recent_files()

    def _build_ui(self):
        # ── Title ──────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Convertix",
            font=("Segoe UI", 28, "bold"), text_color="white"
        ).pack(pady=(28, 4))

        ctk.CTkLabel(
            self, text="Fast file conversion",
            font=("Segoe UI", 12), text_color="#6B7280"
        ).pack(pady=(0, 18))

        # ── Conversion card ────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16)
        card.pack(padx=30, fill="x")

        ctk.CTkLabel(
            card, text="FROM", font=("Segoe UI", 10, "bold"),
            text_color="#6B7280"
        ).pack(anchor="w", padx=18, pady=(16, 6))

        self.from_row = ctk.CTkFrame(card, fg_color="transparent")
        self.from_row.pack(padx=18, fill="x", pady=(0, 14))
        self._build_chips(self.from_row, list(CONVERSIONS.keys()), self.from_fmt, self._select_from)

        ctk.CTkFrame(card, height=1, fg_color="#2D2D42").pack(fill="x", padx=18)

        ctk.CTkLabel(
            card, text="TO", font=("Segoe UI", 10, "bold"),
            text_color="#6B7280"
        ).pack(anchor="w", padx=18, pady=(14, 6))

        self.to_row = ctk.CTkFrame(card, fg_color="transparent")
        self.to_row.pack(padx=18, fill="x", pady=(0, 16))
        self._build_chips(self.to_row, CONVERSIONS[self.from_fmt], self.to_fmt, self._select_to)

        # ── File pickers ───────────────────────────────────────
        picker_frame = ctk.CTkFrame(self, fg_color="transparent")
        picker_frame.pack(padx=30, pady=14, fill="x")
        picker_frame.columnconfigure(0, weight=1)
        picker_frame.columnconfigure(1, weight=2)

        self._file_row(picker_frame, "Input",  self._choose_input,  0)
        self._file_row(picker_frame, "Output", self._choose_output, 1)

        # ── Progress bar (hidden initially) ────────────────────
        self.progress = ctk.CTkProgressBar(self, height=8, corner_radius=4)
        self.progress.pack(padx=30, pady=(10, 0))
        self.progress.set(0)
        self.progress.pack_forget()

        # ── Cancel button (hidden initially) ───────────────────
        self.cancel_btn = ctk.CTkButton(
            self, text="Cancel", height=36,
            font=("Segoe UI", 12),
            fg_color="#EF4444", hover_color="#DC2626",
            corner_radius=8, command=self._cancel_conversion,
            state="disabled"
        )
        self.cancel_btn.pack(padx=30, pady=(5, 0))
        self.cancel_btn.pack_forget()

        # ── Convert button ─────────────────────────────────────
        self.convert_btn = ctk.CTkButton(
            self, text="Convert", height=44,
            font=("Segoe UI", 14, "bold"),
            fg_color=ACCENT, hover_color="#2563EB",
            corner_radius=12, command=self._start_conversion
        )
        self.convert_btn.pack(padx=30, fill="x", pady=(10, 0))

        self.status_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.status_label.pack(pady=(10, 0))

        # ── Recent files section ───────────────────────────────
        recent_frame = ctk.CTkFrame(self, fg_color="transparent")
        recent_frame.pack(padx=30, pady=(15, 10), fill="x")

        ctk.CTkLabel(
            recent_frame, text="📁 Recent files", 
            font=("Segoe UI", 10, "bold"), text_color="#6B7280"
        ).pack(anchor="w")

        self.recent_container = ctk.CTkFrame(recent_frame, fg_color="transparent")
        self.recent_container.pack(fill="x", pady=(5, 0))

    # ── Chip helpers ───────────────────────────────────────────
    def _build_chips(self, parent, options, active, callback):
        for w in parent.winfo_children():
            w.destroy()
        for opt in options:
            is_active = opt == active
            btn = ctk.CTkButton(
                parent, text=opt, width=70, height=32,
                font=("Segoe UI", 12, "bold" if is_active else "normal"),
                fg_color=BG_CHIP_ACTIVE if is_active else BG_CHIP,
                hover_color="#2563EB" if is_active else "#33334A",
                corner_radius=8,
                command=lambda o=opt: callback(o)
            )
            btn.pack(side="left", padx=(0, 8))

    def _select_from(self, fmt):
        self.from_fmt = fmt
        options = CONVERSIONS.get(fmt, [])
        if options:
            self.to_fmt = options[0]
        self._build_chips(self.from_row, list(CONVERSIONS.keys()), self.from_fmt, self._select_from)
        self._build_chips(self.to_row, options, self.to_fmt, self._select_to)
        
        # Reset file selection when format changes
        if self.input_file:
            self.input_file = ""
            self.input_label.configure(text="No file selected", text_color="#6B7280")

    def _select_to(self, fmt):
        self.to_fmt = fmt
        self._build_chips(self.to_row, CONVERSIONS.get(self.from_fmt, []), self.to_fmt, self._select_to)

    # ── File row helper ────────────────────────────────────────
    def _file_row(self, parent, label, command, row):
        ctk.CTkButton(
            parent, text=f"Select {label}", width=110, height=35,
            font=("Segoe UI", 12), corner_radius=8,
            fg_color=BG_CHIP, hover_color="#33334A",
            command=command
        ).grid(row=row, column=0, sticky="w", pady=6)

        lbl = ctk.CTkLabel(
            parent, text="No file selected",
            font=("Segoe UI", 11), text_color="#6B7280",
            wraplength=350, anchor="w"
        )
        lbl.grid(row=row, column=1, sticky="w", padx=(12, 0))

        if label == "Input":
            self.input_label = lbl
        else:
            self.output_label = lbl

    # ── File picking with info display ─────────────────────────
    def _choose_input(self):
        fmt = self.from_fmt.lower()
        path = filedialog.askopenfilename(
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}"), ("All files", "*.*")]
        )
        if path:
            self.input_file = path
            self._show_file_info(path, self.input_label, is_input=True)
            self._add_to_recent(path)

    def _choose_output(self):
        fmt = self.to_fmt.lower()
        # Suggest output filename based on input
        default_name = ""
        if self.input_file:
            base = os.path.splitext(os.path.basename(self.input_file))[0]
            default_name = f"{base}_converted.{fmt}"
        
        path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            initialfile=default_name,
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")]
        )
        if path:
            self.output_file = path
            self._show_file_info(path, self.output_label, is_input=False)

    def _show_file_info(self, path, label, is_input=True):
        """Display file size and additional info"""
        if not os.path.exists(path):
            label.configure(text="File not found", text_color="#EF4444")
            return
        
        size = os.path.getsize(path) / (1024 * 1024)  # MB
        filename = os.path.basename(path)
        
        # Truncate long filenames
        if len(filename) > 40:
            filename = filename[:37] + "..."
        
        # For input images, try to get dimensions
        info_text = filename
        if is_input and self.from_fmt.lower() in ['png', 'jpg', 'jpeg', 'webp', 'bmp']:
            try:
                from PIL import Image
                with Image.open(path) as img:
                    info_text += f"  ({img.width}×{img.height}, {size:.1f}MB)"
            except:
                info_text += f"  ({size:.1f}MB)"
        else:
            info_text += f"  ({size:.1f}MB)"
        
        label.configure(text=info_text, text_color="white")
        
        # Warn if file is large
        if is_input and size > 100:
            self._set_status(f"⚠️ Large file ({size:.1f}MB) - may take a while", "#F59E0B")

    # ── Recent files ───────────────────────────────────────────
    def _load_recent_files(self):
        """Load recent files from JSON file"""
        try:
            if RECENT_FILE.exists():
                with open(RECENT_FILE, 'r') as f:
                    self.recent_files = json.load(f)
                self._update_recent_display()
            else:
                self.recent_files = []
        except Exception as e:
            self.recent_files = []

    def _save_recent_files(self):
        """Save recent files to JSON file"""
        try:
            with open(RECENT_FILE, 'w') as f:
                json.dump(self.recent_files[:10], f)  # Keep last 10
        except Exception as e:
            pass

    def _add_to_recent(self, filepath):
        """Add file to recent list"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:10]
        self._save_recent_files()
        self._update_recent_display()

    def _update_recent_display(self):
        """Update the recent files UI"""
        for w in self.recent_container.winfo_children():
            w.destroy()
        
        if not self.recent_files:
            lbl = ctk.CTkLabel(
                self.recent_container, 
                text="No recent files", 
                font=("Segoe UI", 10), 
                text_color="#4B5563"
            )
            lbl.pack(anchor="w", pady=2)
            return
        
        for filepath in self.recent_files[:5]:  # Show last 5
            if not os.path.exists(filepath):
                continue
            
            # Create frame for each recent file
            row = ctk.CTkFrame(self.recent_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # File name button
            filename = os.path.basename(filepath)
            if len(filename) > 50:
                filename = filename[:47] + "..."
            
            btn = ctk.CTkButton(
                row, text=filename, height=24,
                font=("Segoe UI", 10),
                fg_color="transparent", hover_color="#2A2A3D",
                anchor="w", corner_radius=4,
                command=lambda p=filepath: self._use_recent_file(p)
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Clear button
            clear_btn = ctk.CTkButton(
                row, text="✕", width=24, height=24,
                font=("Segoe UI", 10),
                fg_color="transparent", hover_color="#EF4444",
                corner_radius=4,
                command=lambda p=filepath: self._remove_recent(p)
            )
            clear_btn.pack(side="right")

    def _use_recent_file(self, filepath):
        """Use a recent file as input"""
        ext = os.path.splitext(filepath)[1][1:].upper()
        if ext in CONVERSIONS:
            self._select_from(ext)
        self.input_file = filepath
        self._show_file_info(filepath, self.input_label, is_input=True)

    def _remove_recent(self, filepath):
        """Remove file from recent list"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
            self._save_recent_files()
            self._update_recent_display()

    # ── Conversion with progress and cancel ────────────────────
    def _start_conversion(self):
        if not self.input_file or not self.output_file:
            self._set_status("Please select both files first.", "#EF4444")
            return
        
        if not os.path.exists(self.input_file):
            self._set_status("Input file no longer exists.", "#EF4444")
            return
        
        self.cancel_requested = False
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.progress.pack()
        self.cancel_btn.pack()
        self.cancel_btn.configure(state="normal")
        self.progress.set(0)
        self._set_status("Converting...", "#3B82F6")
        
        self.conversion_thread = threading.Thread(target=self._run_conversion, daemon=True)
        self.conversion_thread.start()
        
        # Start progress animation
        self._animate_progress()

    def _animate_progress(self):
        """Animate progress bar while converting"""
        if self.conversion_thread and self.conversion_thread.is_alive():
            current = self.progress.get()
            if current < 0.9 and not self.cancel_requested:
                self.progress.set(current + 0.02)
            self.after(100, self._animate_progress)

    def _cancel_conversion(self):
        """Request cancellation"""
        self.cancel_requested = True
        self._set_status("Cancelling...", "#F59E0B")
        self.cancel_btn.configure(state="disabled")
        self.convert_btn.configure(text="Cancelling...")

    def _run_conversion(self):
        try:
            from cli import convert_file
            
            # Run the conversion
            convert_file(self.input_file, self.output_file)
            
            if self.cancel_requested:
                self.after(0, self._on_cancelled)
            else:
                self.after(0, self._on_success)
            
        except FileNotFoundError as e:
            self.after(0, self._on_failure, str(e))
        except NotImplementedError as e:
            self.after(0, self._on_failure, f"Conversion not supported: {e}")
        except Exception as e:
            self.after(0, self._on_failure, str(e))

    def _on_success(self):
        self.progress.set(1.0)
        self._set_status("✓ Conversion successful!", "#22C55E")
        self._reset_button()
        
        # Show success dialog
        self.after(100, lambda: SimpleDialog(
            self, "Success", 
            f"File saved to:\n{os.path.dirname(self.output_file)}"
        ))

    def _on_cancelled(self):
        self._set_status("⚠️ Conversion cancelled", "#F59E0B")
        self._reset_button()
        
        # Clean up partial output if exists
        if self.output_file and os.path.exists(self.output_file):
            try:
                os.remove(self.output_file)
            except:
                pass

    def _on_failure(self, msg):
        self._set_status(f"✕ {msg}", "#EF4444")
        self._reset_button()

    def _reset_button(self):
        """Reset UI after conversion"""
        self.convert_btn.configure(state="normal", text="Convert")
        self.progress.pack_forget()
        self.cancel_btn.pack_forget()
        self.progress.set(0)
        
        # Add output to recent if it exists
        if self.output_file and os.path.exists(self.output_file):
            self._add_to_recent(self.output_file)

    def _set_status(self, msg, color):
        """Update status label"""
        self.status_label.configure(text=msg, text_color=color)
        
        # Auto-clear success/error messages after 5 seconds
        if color != "#3B82F6":  # Not the "Converting..." message
            self.after(5000, lambda: self.status_label.configure(text="") if self.status_label.cget("text") == msg else None)


if __name__ == "__main__":
    app = ConvertixApp()
    app.mainloop()