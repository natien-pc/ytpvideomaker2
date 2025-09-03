```markdown
# assets/ — Asset pack for YTP Video Maker (beta)

This folder holds user-provided overlays, audio SFX, memes, and other media used by the YTP Video Maker project.

Contents (what you should add)
- overlays/ — PNG/GIF overlays (transparent PNGs or animated GIFs). Example filenames:
  - rainbow_overlay.png
  - meme_transparent.png
  - explosion_*.png
- sounds/ — short sound effects (WAV or MP3). Example filenames:
  - boop.wav
  - stinger.wav
  - error_buzz.wav
- music/ — background tracks, loops, meme songs (longer MP3/WAV)
- ads/ — mock commercial audio/video
- errors/ — short computer/console error clips
- templates/ — intro/outro templates as short videos or image sequences

Place your custom assets in the subfolders above. The project will look for:
- assets/rainbow_overlay.png (used by default pipeline if present)
- assets/memes/ (optional, for meme injection)
- assets/sounds/ (random overlays and UI sounds)

Quick helper
If you don't have assets yet, run the helper script `generate_placeholders.py` in this folder to create a small set of demo assets (transparent overlays and short WAV SFX) that you can use to test the project.

License / attribution
These placeholder assets are generated programmatically and are intended for testing only. Replace them with your own media for production or distribution. Use licensed or public-domain media for any public uploads.
```