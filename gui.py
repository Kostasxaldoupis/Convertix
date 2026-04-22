import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONVERSIONS = {
    "PNG":  ["JPG", "PDF", "WEBP"],
    "JPG":  ["PNG", "PDF"],
    "PDF":  ["DOCX"],   
    "CSV":  ["JSON"],
}

ACCENT   = "#3B82F6"
BG_CARD  = "#1E1E2E"
BG_CHIP  = "#2A2A3D"
BG_CHIP_ACTIVE = "#3B82F6"


class ConvertixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Convertix")
        self.geometry("580x500")
        self.resizable(False, False)
        self.configure(fg_color="#13131F")

        self.input_file  = ""
        self.output_file = ""
        self.from_fmt    = "PNG"
        self.to_fmt      = "JPEG"

        self._build_ui()

    def _build_ui(self):
        # ── Title ──────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Convertix",
            font=("Segoe UI", 26, "bold"), text_color="white"
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

        self._file_row(picker_frame, "Input",  self._choose_input,  0)
        self._file_row(picker_frame, "Output", self._choose_output, 1)

        # ── Convert button ─────────────────────────────────────
        self.convert_btn = ctk.CTkButton(
            self, text="Convert", height=44,
            font=("Segoe UI", 14, "bold"),
            fg_color=ACCENT, hover_color="#2563EB",
            corner_radius=12, command=self._start_conversion
        )
        self.convert_btn.pack(padx=30, fill="x")

        self.status_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.status_label.pack(pady=(10, 0))

    # ── Chip helpers ───────────────────────────────────────────
    def _build_chips(self, parent, options, active, callback):
        for w in parent.winfo_children():
            w.destroy()
        for opt in options:
            is_active = opt == active
            btn = ctk.CTkButton(
                parent, text=opt, width=64, height=30,
                font=("Segoe UI", 12, "bold" if is_active else "normal"),
                fg_color=BG_CHIP_ACTIVE if is_active else BG_CHIP,
                hover_color="#2563EB" if is_active else "#33334A",
                corner_radius=8,
                command=lambda o=opt: callback(o)
            )
            btn.pack(side="left", padx=(0, 8))

    def _select_from(self, fmt):
        self.from_fmt = fmt
        options = CONVERSIONS[fmt]
        self.to_fmt = options[0]
        self._build_chips(self.from_row, list(CONVERSIONS.keys()), self.from_fmt, self._select_from)
        self._build_chips(self.to_row,   options,                   self.to_fmt,   self._select_to)

    def _select_to(self, fmt):
        self.to_fmt = fmt
        self._build_chips(self.to_row, CONVERSIONS[self.from_fmt], self.to_fmt, self._select_to)

    # ── File row helper ────────────────────────────────────────
    def _file_row(self, parent, label, command, row):
        ctk.CTkButton(
            parent, text=f"Select {label}", width=110, height=32,
            font=("Segoe UI", 12), corner_radius=8,
            fg_color=BG_CHIP, hover_color="#33334A",
            command=command
        ).grid(row=row, column=0, sticky="w", pady=4)

        lbl = ctk.CTkLabel(
            parent, text="No file selected",
            font=("Segoe UI", 11), text_color="#6B7280",
            wraplength=280, anchor="w"
        )
        lbl.grid(row=row, column=1, sticky="w", padx=(10, 0))

        if label == "Input":
            self.input_label = lbl
        else:
            self.output_label = lbl

    # ── File picking ───────────────────────────────────────────
    def _choose_input(self):
        fmt = self.from_fmt.lower()
        path = filedialog.askopenfilename(filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")])
        if path:
            self.input_file = path
            self.input_label.configure(text=self._truncate(path), text_color="white")

    def _choose_output(self):
        fmt = self.to_fmt.lower()
        path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")]
        )
        if path:
            self.output_file = path
            self.output_label.configure(text=self._truncate(path), text_color="white")

    # ── Conversion ─────────────────────────────────────────────
    def _start_conversion(self):
        if not self.input_file or not self.output_file:
            self._set_status("Please select both files first.", "red")
            return
        self.convert_btn.configure(state="disabled", text="Converting...")
        self._set_status("", "white")
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            subprocess.run(
            [sys.executable, "cli.py",
            self.input_file, self.output_file],
            )
            self.after(0, self._on_success)
        except subprocess.CalledProcessError as e:
            self.after(0, self._on_failure, e.stderr.strip() or "Unknown error")
        except Exception as e:
            self.after(0, self._on_failure, str(e))

    def _on_success(self):
        self._set_status("✓  Conversion successful!", "#22C55E")
        self._reset_button()

    def _on_failure(self, msg):
        self._set_status(f"✕  {msg}", "#EF4444")
        self._reset_button()

    def _reset_button(self):
        self.convert_btn.configure(state="normal", text="Convert")

    def _set_status(self, msg, color):
        self.status_label.configure(text=msg, text_color=color)

    @staticmethod
    def _truncate(path, max_len=45):
        return f"...{path[-(max_len - 3):]}" if len(path) > max_len else path


if __name__ == "__main__":
    app = ConvertixApp()
    app.mainloop()