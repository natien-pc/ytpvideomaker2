"""
effects.py — provides functions that invoke ffmpeg to apply YTP-like effects.

These implementations are intentionally simple and use ffmpeg CLI via subprocess.
They produce files in the same container/codec as ffmpeg defaults (H.264/AAC recommended if ffmpeg build supports it).

Note: Requires ffmpeg in PATH.
"""
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from utils import run_cmd, safe_makedirs

TEMP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
safe_makedirs(TEMP_DIR)

def ffmpeg_exists():
    return shutil.which("ffmpeg") is not None

def apply_invert(input_path, output_path):
    # Simple invert using negate filter
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "negate", "-c:a", "copy", output_path]
    run_cmd(cmd)
    return output_path

def apply_mirror(input_path, output_path):
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "hflip", "-c:a", "copy", output_path]
    run_cmd(cmd)
    return output_path

def apply_reverse(input_path, output_path):
    # reverse both video and audio
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "reverse", "-af", "areverse", output_path]
    run_cmd(cmd)
    return output_path

def apply_speed_change(input_path, output_path, speed=1.0):
    # speed >1.0 => faster, <1.0 => slower. Video setpts and audio atempo (limited 0.5-2.0)
    # If required factor is outside atempo range, chain atempo filters.
    setpts = f"setpts=PTS/{speed}"
    # compute atempo chain
    atempo = []
    factor = speed
    if factor <= 0:
        factor = 1.0
    # ffmpeg atempo supports between 0.5 and 2.0 per filter; chain if necessary
    atempo_filters = []
    remaining = 1.0 / factor  # because changing video PTS by /speed, audio needs atempo=speed
    # alternative: use atempo=speed directly when speed between 0.5 and 2
    audio_filter = None
    if 0.5 <= factor <= 2.0:
        audio_filter = f"atempo={factor}"
    else:
        # chain approximate by breaking factor into multiple multipliers within [0.5,2.0]
        val = factor
        parts = []
        while val > 2.0:
            parts.append(2.0)
            val /= 2.0
        while val < 0.5:
            parts.append(0.5)
            val /= 0.5
        parts.append(val)
        audio_filter = ",".join([f"atempo={p}" for p in parts])
    cmd = ["ffmpeg", "-y", "-i", input_path, "-filter_complex", f"[0:v]{setpts}[v];[0:a]{audio_filter}[a]", "-map", "[v]", "-map", "[a]", output_path]
    run_cmd(cmd)
    return output_path

def apply_earrape(input_path, output_path, gain_db=20):
    # Apply very large gain — clipping will occur (earrape)
    cmd = ["ffmpeg", "-y", "-i", input_path, "-af", f"volume={gain_db}dB", "-c:v", "copy", output_path]
    run_cmd(cmd)
    return output_path

def apply_chorus_like(input_path, output_path):
    # Use aecho to simulate chorus-ish effect (not real chorus)
    # Parameters are example: in_GAIN out_GAIN delays decays
    cmd = ["ffmpeg", "-y", "-i", input_path, "-af", "aecho=0.8:0.9:100:0.3", "-c:v", "copy", output_path]
    run_cmd(cmd)
    return output_path

def apply_frame_shuffle(input_path, output_path, max_frames=500):
    # Simple frame shuffle: extract frames to a temp dir, shuffle file order, reassemble
    tmpd = tempfile.mkdtemp(prefix="frames_")
    try:
        # extract frames as PNG
        frame_pattern = os.path.join(tmpd, "frame_%06d.png")
        cmd1 = ["ffmpeg", "-y", "-i", input_path, "-vsync", "0", frame_pattern]
        run_cmd(cmd1)
        frames = sorted([os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith(".png")])
        if not frames:
            raise RuntimeError("No frames extracted.")
        if len(frames) > max_frames:
            frames = frames[:max_frames]
        random.shuffle(frames)
        # write a temporary file list for ffmpeg
        listfile = os.path.join(tmpd, "list.txt")
        with open(listfile, "w", encoding="utf-8") as fh:
            for f in frames:
                fh.write(f"file '{f}'\n")
        # reassemble into video (assume 25 fps)
        cmd2 = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
        run_cmd(cmd2)
    finally:
        # keep temp dir for debugging if needed; user may clear temp/ later
        pass
    return output_path

def apply_stutter_loop(input_path, output_path, repeats=3):
    # Create a concat-list file that references the same file multiple times and concat
    tmpd = tempfile.mkdtemp(prefix="stutter_")
    try:
        listfile = os.path.join(tmpd, "list.txt")
        with open(listfile, "w", encoding="utf-8") as fh:
            for i in range(repeats):
                fh.write(f"file '{os.path.abspath(input_path)}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", output_path]
        run_cmd(cmd)
    finally:
        pass
    return output_path

def overlay_image(input_path, overlay_path, output_path, x=0, y=0):
    # Overlay an image/gif onto the video
    cmd = ["ffmpeg", "-y", "-i", input_path, "-i", overlay_path,
           "-filter_complex", f"[0:v][1:v] overlay={x}:{y}:format=auto", "-c:a", "copy", output_path]
    run_cmd(cmd)
    return output_path

def concat_clips_quick(clips, output_path):
    # Quick concat using intermediate list file. Clips should have compatible codecs.
    tmpd = tempfile.mkdtemp(prefix="concat_")
    try:
        listfile = os.path.join(tmpd, "list.txt")
        with open(listfile, "w", encoding="utf-8") as fh:
            for c in clips:
                fh.write(f"file '{os.path.abspath(c)}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", output_path]
        run_cmd(cmd)
    finally:
        pass
    return output_path

def apply_randomized_effects_to_clip(input_path, output_path, config=None, preview=False):
    """
    Given an input clip, randomly apply some effects based on config and write to output_path.
    If preview=True, produce a faster low-res preview (scale down).
    """
    if config is None:
        config = {}
    working = input_path
    steps = []
    effects_cfg = config.get("effects", {})

    # copy to initial temp
    base_tmp = os.path.join(TEMP_DIR, f"step_0{Path(input_path).suffix}")
    shutil.copy2(input_path, base_tmp)
    working = base_tmp

    def apply_step(fn, *args, **kwargs):
        nonlocal working
        idx = len(steps) + 1
        out = os.path.join(TEMP_DIR, f"step_{idx}{Path(working).suffix}")
        fn(working, out, *args, **kwargs) if kwargs else fn(working, out)
        steps.append(out)
        working = out

    # Helper to decide whether to run an effect
    def chance(effect_name, default_prob=0.5):
        e = effects_cfg.get(effect_name, {})
        if not e.get("enabled", True):
            return False
        prob = e.get("probability", default_prob)
        return random.random() < prob

    # Example ordering of some effects, applied if chosen
    if chance("invert", 0.25):
        apply_step(apply_invert)

    if chance("mirror", 0.25):
        apply_step(apply_mirror)

    if chance("reverse", 0.15):
        apply_step(apply_reverse)

    if chance("speed_change", 0.25):
        # random speed 0.5x - 2x
        speed = random.choice([0.5, 0.75, 1.25, 1.5, 2.0])
        apply_step(apply_speed_change, speed=speed)

    if chance("stutter_loop", 0.20):
        repeats = random.randint(2, 4)
        apply_step(apply_stutter_loop, repeats=repeats)

    if chance("frame_shuffle", 0.10):
        apply_step(apply_frame_shuffle)

    if chance("chorus", 0.10):
        apply_step(apply_chorus_like)

    if chance("earrape", 0.05):
        apply_step(apply_earrape, gain_db=18)

    # Rainbow overlay: only if overlay asset exists in assets/
    overlay_asset = os.path.join(os.path.dirname(__file__), "assets", "rainbow_overlay.png")
    if os.path.exists(overlay_asset) and chance("rainbow_overlay", 0.15):
        apply_step(overlay_image, overlay_asset)

    # Final step: if preview, scale down for fast rendering
    if preview:
        out_preview = output_path
        cmd = ["ffmpeg", "-y", "-i", working, "-vf", "scale=640:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "96k", out_preview]
        run_cmd(cmd)
        return out_preview
    else:
        # simply copy (or re-encode)
        shutil.copy2(working, output_path)
        return output_path