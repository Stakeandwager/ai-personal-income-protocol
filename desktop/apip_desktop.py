"""APIP desktop starter: local opportunity tracker (no network crawling yet)."""
from __future__ import annotations

import csv
import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_NAME = "APIP"
APP_VERSION = "0.1.0"


def data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        folder = base / "APIP"
    else:
        folder = Path.home() / ".local" / "share" / "APIP"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


DB_PATH = data_dir() / "apip.sqlite3"


class APIPApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — Opportunity Engine {APP_VERSION}")
        self.geometry("1100x680")
        self.minsize(820, 520)
        self.configure(padx=14, pady=12)
        self._init_db()
        self._build_ui()
        self.refresh()

    def _connect(self):
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    problem TEXT NOT NULL,
                    source_url TEXT NOT NULL DEFAULT '',
                    evidence TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'NEW',
                    created_at TEXT NOT NULL
                )
            """)

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="APIP", font=("Segoe UI", 22, "bold")).pack(side="left")
        ttk.Label(header, text="Problem discovery → earning opportunities",
                  font=("Segoe UI", 11)).pack(side="left", padx=16, pady=(7, 0))
        ttk.Label(header, text="LOCAL DESKTOP • v0.1.0",
                  foreground="#55705b").pack(side="right", pady=(8, 0))

        status = ttk.LabelFrame(self, text="Current status")
        status.pack(fill="x", pady=(0, 10))
        ttk.Label(status, text="Local database:").grid(row=0, column=0, sticky="w", padx=10, pady=7)
        ttk.Label(status, text=str(DB_PATH)).grid(row=0, column=1, sticky="w", padx=4, pady=7)
        self.count_label = ttk.Label(status, text="Saved opportunities: 0")
        self.count_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 7))
        ttk.Label(status, text="Discovery crawler: NOT CONNECTED (this starter does not invent live results)",
                  foreground="#8a5a00").grid(row=1, column=1, sticky="w", padx=4, pady=(0, 7))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, padding=(0, 0, 10, 0))
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(left, weight=3)
        body.add(right, weight=2)

        ttk.Label(left, text="Opportunity queue", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 7))
        columns = ("id", "title", "status", "created")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        for col, label, width in [
            ("id", "ID", 45), ("title", "Opportunity", 270),
            ("status", "Status", 110), ("created", "Created (UTC)", 145)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_selected)

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(actions, text="Export CSV", command=self.export_csv).pack(side="left", padx=6)
        ttk.Button(actions, text="Change status", command=self.change_status).pack(side="left")

        ttk.Label(right, text="Add an opportunity", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 7))
        ttk.Label(right, text="Record a real finding and its source. Demo ideas should be labelled as hypotheses.").pack(anchor="w", pady=(0, 10))
        ttk.Label(right, text="Title").pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.title_var).pack(fill="x", pady=(3, 8))
        ttk.Label(right, text="Problem / need").pack(anchor="w")
        self.problem_text = tk.Text(right, height=5, wrap="word")
        self.problem_text.pack(fill="x", pady=(3, 8))
        ttk.Label(right, text="Source URL (optional)").pack(anchor="w")
        self.url_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.url_var).pack(fill="x", pady=(3, 8))
        ttk.Label(right, text="Evidence / why someone might pay").pack(anchor="w")
        self.evidence_text = tk.Text(right, height=5, wrap="word")
        self.evidence_text.pack(fill="both", expand=True, pady=(3, 8))
        ttk.Button(right, text="Save opportunity", command=self.save_opportunity).pack(anchor="e")

        footer = ttk.Label(self, text="Income is counted only after evidence of payment is recorded. No spending, outreach, or payment actions occur here.")
        footer.pack(fill="x", pady=(10, 0))

    def save_opportunity(self):
        title = self.title_var.get().strip()
        problem = self.problem_text.get("1.0", "end").strip()
        if not title or not problem:
            messagebox.showwarning("Missing information", "Enter both a title and a problem description.")
            return
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as con:
            con.execute(
                "INSERT INTO opportunities (title, problem, source_url, evidence, status, created_at) VALUES (?, ?, ?, ?, 'NEW', ?)",
                (title, problem, self.url_var.get().strip(), self.evidence_text.get("1.0", "end").strip(), created)
            )
        self.title_var.set("")
        self.problem_text.delete("1.0", "end")
        self.url_var.set("")
        self.evidence_text.delete("1.0", "end")
        self.refresh()
        messagebox.showinfo("Saved", "Opportunity saved to your local APIP database.")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        with self._connect() as con:
            rows = con.execute("SELECT id, title, status, created_at FROM opportunities ORDER BY id DESC").fetchall()
        for row in rows:
            created = row["created_at"].replace("T", " ")[:19]
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["id"], row["title"], row["status"], created))
        self.count_label.configure(text=f"Saved opportunities: {len(rows)}")

    def show_selected(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        with self._connect() as con:
            row = con.execute("SELECT * FROM opportunities WHERE id = ?", (int(selection[0]),)).fetchone()
        if not row:
            return
        details = (
            f"Title: {row['title']}\n\nProblem: {row['problem']}\n\n"
            f"Source: {row['source_url'] or '(not supplied)'}\n\n"
            f"Evidence: {row['evidence'] or '(not supplied)'}\n\nStatus: {row['status']}"
        )
        messagebox.showinfo(f"Opportunity #{row['id']}", details)

    def change_status(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select an opportunity", "Select a row first.")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Change opportunity status")
        dialog.transient(self)
        dialog.grab_set()
        ttk.Label(dialog, text="Choose a status:").pack(padx=16, pady=(14, 6))
        status_var = tk.StringVar(value="RESEARCH")
        choices = ("NEW", "RESEARCH", "VALIDATED_DEMAND", "OFFER_PREPARED", "OFFER_SENT", "WORK_DELIVERED", "PAYMENT_VERIFIED", "REJECTED")
        ttk.Combobox(dialog, textvariable=status_var, values=choices, state="readonly", width=24).pack(padx=16, pady=6)

        def apply():
            with self._connect() as con:
                con.execute("UPDATE opportunities SET status = ? WHERE id = ?", (status_var.get(), int(selection[0])))
            dialog.destroy()
            self.refresh()
        ttk.Button(dialog, text="Save status", command=apply).pack(pady=(6, 14))

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export APIP opportunities", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], initialfile="apip-opportunities.csv"
        )
        if not path:
            return
        with self._connect() as con:
            rows = con.execute("SELECT id, title, problem, source_url, evidence, status, created_at FROM opportunities ORDER BY id").fetchall()
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(("id", "title", "problem", "source_url", "evidence", "status", "created_at_utc"))
            writer.writerows([tuple(row) for row in rows])
        messagebox.showinfo("Export complete", f"Exported {len(rows)} opportunities to:\n{path}")


if __name__ == "__main__":
    try:
        APIPApp().mainloop()
    except Exception as exc:
        messagebox.showerror("APIP could not start", f"{exc}\n\nDatabase: {DB_PATH}")
        raise
