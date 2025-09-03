#!/usr/bin/env python3
"""
generate_placeholders.py

Creates simple placeholder assets for development and testing:
- overlays/rainbow_overlay.png : semi-transparent rainbow overlay
- overlays/meme_transparent.png : simple "MEME" transparent PNG
- sounds/boop.wav : short sine blip
- sounds/startup.wav : rising tone sequence
- sounds/shutdown.wav : falling tone sequence

Run from the repository root:
    python assets/generate_placeholders.py
"""
import os
import math
import wave
import struct
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OVERLAYS = os.path.join(OUT_DIR, "overlays")
SOUNDS = os.path.join(OUT_DIR, "sounds")

os.makedirs(OVERLAYS, exist_ok=True)
os.makedirs(SOUNDS, exist_ok=True)

def make_rainbow_overlay(path, size=(1280, 720), alpha=96):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # create horizontal rainbow gradient
    bands = [
        (148, 0, 211),  # violet
        (75, 0, 130),   # indigo
        (0, 0, 255),    # blue
        (0, 255, 0),    # green
        (255, 255, 0),  # yellow
        (255, 127, 0),  # orange
        (255, 0, 0)     # red
    ]
    band_h = size[1] // len(bands) + 1
    for i, col in enumerate(bands):
        y0 = i * band_h
        y1 = y0 + band_h
        draw.rectangle([0, y0, size[0], y1], fill=(col[0], col[1], col[2], alpha))
    # add subtle diagonal stripe
    stripe = Image.new("RGBA", size, (255,255,255,0))
    sd = ImageDraw.Draw(stripe)
    for x in range(-size[1], size[0], 40):
        sd.line([(x,0),(x+size[1],size[1])], fill=(255,255,255,20), width=8)
    img = Image.alpha_composite(img, stripe)
    img.save(path)
    print("Wrote:", path)

def make_meme_overlay(path, size=(640,160), alpha_bg=64):
    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # semi-transparent black rectangle
    draw.rectangle([0,0,size[0],size[1]], fill=(0,0,0,alpha_bg))
    # text "MEME" in white with black stroke
    try:
        font = ImageFont.truetype("arial.ttf", 96)
    except Exception:
        font = ImageFont.load_default()
    text = "MEME"
    w,h = draw.textsize(text, font=font)
    x = (size[0]-w)//2
    y = (size[1]-h)//2
    # stroke
    draw.text((x-2,y-2), text, font=font, fill=(0,0,0,255))
    draw.text((x+2,y+2), text, font=font, fill=(0,0,0,255))
    draw.text((x,y), text, font=font, fill=(255,255,255,255))
    img.save(path)
    print("Wrote:", path)

def write_wav(path, freq=440.0, duration=0.25, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    nchannels = 1
    sampwidth = 2  # bytes
    max_amp = 32767 * volume
    with wave.open(path, 'w') as wf:
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = int(max_amp * math.sin(2.0 * math.pi * freq * t))
            data = struct.pack('<h', value)
            wf.writeframesraw(data)
    print("Wrote:", path)

def make_startup(path):
    # ascending tones
    freqs = [220, 330, 440, 660]
    combined = os.path.join(SOUNDS, "startup_temp.wav")
    # write small segments and append manually
    for i,f in enumerate(freqs):
        write_wav(os.path.join(SOUNDS, f"seg_{i}.wav"), freq=f, duration=0.12, volume=0.45)
    # Simple concatenation by reading frames (since all same params)
    segs = [os.path.join(SOUNDS, f"seg_{i}.wav") for i in range(len(freqs))]
    with wave.open(path, 'w') as out:
        with wave.open(segs[0], 'r') as ref:
            out.setparams(ref.getparams())
        for s in segs:
            with wave.open(s, 'r') as r:
                frames = r.readframes(r.getnframes())
                out.writeframes(frames)
    # cleanup segs
    for s in segs:
        os.remove(s)
    print("Wrote:", path)

def make_shutdown(path):
    freqs = [660, 440, 330, 220]
    segs = []
    for i,f in enumerate(freqs):
        write_wav(os.path.join(SOUNDS, f"sd_{i}.wav"), freq=f, duration=0.12, volume=0.45)
        segs.append(os.path.join(SOUNDS, f"sd_{i}.wav"))
    with wave.open(path, 'w') as out:
        with wave.open(segs[0], 'r') as ref:
            out.setparams(ref.getparams())
        for s in segs:
            with wave.open(s, 'r') as r:
                out.writeframes(r.readframes(r.getnframes()))
    for s in segs:
        os.remove(s)
    print("Wrote:", path)

def make_boop(path):
    write_wav(path, freq=1000.0, duration=0.08, volume=0.7)

if __name__ == "__main__":
    make_rainbow_overlay(os.path.join(OVERLAYS, "rainbow_overlay.png"))
    make_meme_overlay(os.path.join(OVERLAYS, "meme_transparent.png"))
    make_boop(os.path.join(SOUNDS, "boop.wav"))
    make_startup(os.path.join(SOUNDS, "startup.wav"))
    make_shutdown(os.path.join(SOUNDS, "shutdown.wav"))
    print("Placeholder asset generation completed. Check the 'overlays' and 'sounds' subfolders.")