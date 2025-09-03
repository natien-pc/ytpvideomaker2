"""
utils.py — helper utilities for the project
"""
import json
import os
import subprocess
import sys
import tempfile

def run_cmd(cmd):
    print("RUN:", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if p.returncode != 0:
        print("ffmpeg error output:\n", p.stdout)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p.stdout

def safe_makedirs(path):
    os.makedirs(path, exist_ok=True)

def load_config(path):
    # default config structure
    default = {
        "effects": {
            "invert": {"enabled": True, "probability": 0.25, "max_level": 1},
            "mirror": {"enabled": True, "probability": 0.2},
            "reverse": {"enabled": True, "probability": 0.15},
            "stutter_loop": {"enabled": True, "probability": 0.2},
            "frame_shuffle": {"enabled": True, "probability": 0.1},
            "chorus": {"enabled": True, "probability": 0.1},
            "earrape": {"enabled": True, "probability": 0.05},
            "rainbow_overlay": {"enabled": True, "probability": 0.15}
        },
        "paths": {
            "sources": "sources",
            "assets": "assets",
            "temp": "temp"
        }
    }
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(default, fh, indent=2)
        return default
    try:
        with open(path, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        # merge defaults for missing keys
        for k, v in default.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception:
        return default

def save_project(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)

def open_with_wmp(path):
    """
    Try to open path with Windows Media Player COM object for native WMP playback.
    Fallback to os.startfile if COM is not available or fails.
    """
    try:
        if sys.platform != "win32":
            raise RuntimeError("Not Windows")
        # attempt COM control
        try:
            import comtypes.client
            wmp = comtypes.client.CreateObject("WMPlayer.OCX")
            media = wmp.newMedia(path)
            playlist = wmp.newPlaylist("preview", "")
            playlist.appendItem(media)
            wmp.currentPlaylist = playlist
            wmp.controls.play()
            print("Playing in embedded Windows Media Player (COM).")
            return path
        except Exception as e:
            print("Embedded WMP failed:", e)
    except Exception:
        pass
    # fallback to default app (likely Windows Media Player)
    try:
        os.startfile(path)
    except Exception as e:
        print("Could not start file:", e)
    return path