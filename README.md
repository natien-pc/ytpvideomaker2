# YTP Video Maker (beta) (2010s) — Python + FFmpeg (Windows 8.1 target)

A small proof-of-concept YouTube Poop (YTP) style video maker written in Python that drives ffmpeg to apply a set of randomized/controlled effects and produce quick previews. This is a beta scaffold — intended as a starting point to expand effects and GUI features.

Features
- Effects implemented (sample set):
  - Invert — color inversion
  - Rainbow Overlay — overlay PNG/GIF (user-provided)
  - Mirror — horizontal flip
  - Sus — clip followed by reversed copy
  - Stutter Loop — duplicate clip 2–4 times
  - Loop Frames — short frame-precise loop (2–9 frames)
  - Shuffle Frames — randomly scramble frames (simple implementation)
  - Reverse Clip (video & audio)
  - Speed Up / Slow Down
  - Chorus Effect (approx via aecho)
  - Vibrato / Pitch Bend (asetrate + atempo approximation)
  - Earrape Mode — large gain
  - Meme Injection — overlay image/audio
- Per-effect toggles, probability, and max levels via `config.json`
- Quick low-res preview generation for fast iteration
- Command-line and simple Tkinter UI
- Attempts to open preview in Windows Media Player (COM) or via default program

Requirements
- Windows 8.1 or newer
- Python 3.6+
- ffmpeg in PATH (recommended build with common filters)
- Optional Python packages: pywin32, comtypes, Pillow (for some overlay handling)

Install
1. Ensure ffmpeg is installed and accessible via your PATH.
2. Create and activate a virtualenv (recommended).
3. Install Python deps:
   pip install -r requirements.txt

Quick usage (CLI)
- Add some source clips into the `sources/` folder (or pick files from anywhere).
- Run:
    python main.py --add "path\to\clip.mp4"
    python main.py --generate-preview --out preview.mp4

Quick usage (GUI)
    python main.py --gui
- Use the GUI to add clips, enable effects, set probabilities, and click "Generate Preview".
- The preview is opened in Windows Media Player if available, otherwise uses the default file opener.

Project layout
- main.py — CLI + Tkinter GUI entry point
- effects.py — effect implementations (calls ffmpeg)
- utils.py — helper functions and temp-file management
- config.json — default effect toggles, probabilities, and other settings
- templates/sample_project.json — simple saved project format
- sources/ — raw input clips (not included)
- assets/ — placeholder for overlay images & audio (user-provided)
- temp/ — temporary files and autosave (created at runtime)

Disclaimer
This tool is experimental. Many effects are approximate and use ffmpeg filters or simple frame manipulation. Auto-Tune Chaos and some advanced transforms are placeholders and need more sophisticated third-party tools.

License
MIT — adapt the code, expand effects, and have fun making chaotic edits.
