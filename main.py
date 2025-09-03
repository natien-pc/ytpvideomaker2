#!/usr/bin/env python3
"""
main.py — YTP Video Maker (beta)
Provides a small CLI and Tkinter GUI to compose quick YTP-style previews using ffmpeg.

Usage (CLI):
  python main.py --add path\to\clip.mp4
  python main.py --list
  python main.py --generate-preview --out preview.mp4

Usage (GUI):
  python main.py --gui
"""
import argparse
import json
import os
import sys
import tempfile
import threading
from tkinter import Tk, Button, Listbox, EXTENDED, filedialog, Label, Scale, HORIZONTAL, Checkbutton, IntVar

from effects import apply_randomized_effects_to_clip, concat_clips_quick
from utils import safe_makedirs, load_config, save_project, open_with_wmp

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCES_DIR = os.path.join(PROJECT_DIR, "sources")
TEMP_DIR = os.path.join(PROJECT_DIR, "temp")
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")

safe_makedirs(SOURCES_DIR)
safe_makedirs(TEMP_DIR)

def cli_main(args):
    config = load_config(CONFIG_PATH)
    if args.add:
        for p in args.add:
            print("Add source (copy reference):", p)
            # just print — user manages sources. Could copy in future.
    if args.list:
        print("Sources in ./sources:")
        for f in os.listdir(SOURCES_DIR):
            print(" -", f)
    if args.generate_preview:
        # pick all files in sources
        sources = [os.path.join(SOURCES_DIR, f) for f in os.listdir(SOURCES_DIR)
                   if os.path.isfile(os.path.join(SOURCES_DIR, f))]
        if not sources:
            print("No sources found in ./sources. Add video files first.")
            return
        out = args.out or os.path.join(TEMP_DIR, "preview.mp4")
        print("Generating preview to", out)
        # simple pipeline: take first source, apply randomized effects, write out
        tmp = apply_randomized_effects_to_clip(sources[0], out, config, preview=True)
        print("Preview ready:", tmp)
        open_with_wmp(tmp)

def run_gui():
    root = Tk()
    root.title("YTP Video Maker — Beta (preview)")
    root.geometry("700x420")

    lbl = Label(root, text="Sources (double-click to open folder)")
    lbl.pack()

    listbox = Listbox(root, selectmode=EXTENDED, width=80, height=10)
    listbox.pack()

    def refresh_sources():
        listbox.delete(0, "end")
        for f in os.listdir(SOURCES_DIR):
            if os.path.isfile(os.path.join(SOURCES_DIR, f)):
                listbox.insert("end", f)
    refresh_sources()

    def add_files():
        files = filedialog.askopenfilenames(title="Add video/audio sources")
        for f in files:
            # simply copy into sources folder for convenience
            import shutil
            dest = os.path.join(SOURCES_DIR, os.path.basename(f))
            try:
                shutil.copy2(f, dest)
            except Exception:
                # if same file, ignore
                pass
        refresh_sources()

    def remove_selected():
        sel = listbox.curselection()
        for i in reversed(sel):
            fname = listbox.get(i)
            try:
                os.remove(os.path.join(SOURCES_DIR, fname))
            except Exception as e:
                print("Remove error:", e)
        refresh_sources()

    btn_add = Button(root, text="Add Files", command=add_files)
    btn_add.pack()
    btn_remove = Button(root, text="Remove Selected", command=remove_selected)
    btn_remove.pack()

    # Simple effect toggles
    cfg = load_config(CONFIG_PATH)
    effect_vars = {}
    for effect in ["invert", "reverse", "stutter_loop", "frame_shuffle", "mirror", "rainbow_overlay", "earrape"]:
        var = IntVar(value=1 if cfg.get("effects", {}).get(effect, {}).get("enabled", True) else 0)
        chk = Checkbutton(root, text=effect.replace("_", " ").title(), variable=var)
        chk.pack(anchor="w")
        effect_vars[effect] = var

    def generate_preview_gui():
        selected = listbox.curselection()
        if not selected:
            print("Select a source in the list first.")
            return
        chosen = listbox.get(selected[0])
        source_path = os.path.join(SOURCES_DIR, chosen)
        out = os.path.join(TEMP_DIR, "preview_gui.mp4")

        # merge toggles into a local config copy
        local_cfg = dict(cfg)
        local_cfg.setdefault("effects", {})
        for k, v in effect_vars.items():
            local_cfg["effects"].setdefault(k, {})
            local_cfg["effects"][k]["enabled"] = bool(v.get())

        def job():
            print("Rendering preview — this may take a short while...")
            res = apply_randomized_effects_to_clip(source_path, out, local_cfg, preview=True)
            print("Preview written:", res)
            open_with_wmp(res)

        threading.Thread(target=job, daemon=True).start()

    btn_preview = Button(root, text="Generate Preview (selected)", command=generate_preview_gui)
    btn_preview.pack(pady=10)

    def save_proj():
        proj = {"sources": os.listdir(SOURCES_DIR), "effects": cfg.get("effects", {})}
        save_project(os.path.join(PROJECT_DIR, "last_project.json"), proj)
        print("Project saved to last_project.json")

    btn_save = Button(root, text="Save Project", command=save_proj)
    btn_save.pack()

    root.mainloop()

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--add", nargs="+", help="Add files to sources (copies)")
    p.add_argument("--list", action="store_true", help="List source files")
    p.add_argument("--generate-preview", action="store_true", help="Generate a quick preview from first source")
    p.add_argument("--out", help="Output path for preview")
    p.add_argument("--gui", action="store_true", help="Run the simple Tk GUI")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.gui:
        run_gui()
    else:
        cli_main(args)