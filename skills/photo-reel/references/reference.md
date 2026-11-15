# photo-reel options and design reference

`scripts/photoreel.py` is the only script: rendering, encoding, photo tools and guide-track
synthesis all live in it. This document lists every config field, CLI flag and internal
mechanism, for when the default look needs adjusting.

## Every `config.json` field

| Field | Default | Meaning |
|-------|---------|---------|
| `music` | `music/music.mp3` | Music path (relative to the project). Missing file → a demo guide track is synthesized |
| `start` | `0.0` | Offset into the music, seconds |
| `duration` | `0.0` | How much music to use (0 = to the end) |
| `hold` | `4.9` | Target seconds per photo (snapped to the nearest beat) |
| `xfade` | `0.8` | Crossfade duration; spread ±half around each cut |
| `fit` | `contain` | `contain` shows the whole photo uncropped; `cover` crops to fill the viewfinder |
| `frame_w` / `frame_h` | `960` / `1440` | Viewfinder size (2:3); photos scale inside it |
| `shift` | `-60` | Vertical photo offset, proportional to photo height; negative moves up |
| `fps` | `30` | Frame rate (60 doubles render time) |
| `crf` | `18` | x264 quality (lower is better; 16 ≈ near-lossless) |
| `preset` | `medium` | x264 preset |
| `bpm` | `120.0` | Fixed beat grid used when librosa is unavailable |
| `credit` | `""` | Bottom credit line; empty string hides it |
| `title` | `PHOTO REEL` | Reserved field (not rendered yet) |
| `guide` | `music/guide.wav` | Where the synthesized demo track is written |

## CLI flags (override `config.json`)

| Flag | Effect |
|------|--------|
| `--project DIR` | Project directory (contains `photos/`, `config.json`); default = script's own folder |
| `--photos DIR` | Photo folder (must be inside `<project>/photos`) |
| `--music FILE` | Music path override |
| `--start S` / `--duration S` | Music slice |
| `--hold S` / `--xfade S` | Seconds per photo / crossfade length |
| `--fit contain\|cover` | Scaling mode |
| `--fps N` / `--crf N` | Frame rate / quality |
| `--guide` | Force the synthesized guide track |
| `--no-render` | Analyse beats and cuts, print the plan, exit |
| `--python EXE` | Use this interpreter for rendering |

## Subcommands (tools besides rendering)

| Command | Effect |
|---------|--------|
| `--stats` | Per-photo size/brightness/dark/saturation and green/warm/sky bias, for grouping into chapters |
| `--check` | Numbering continuity: reports gaps and unnumbered files (non-zero exit = problems) |
| `--plan 1,2,5,3,4` | Reorder by old numbers and renumber to `01.jpg…`; also accepts a file with one number per line |
| `--make-guide [OUT]` | Synthesize the demo guide track and exit |

`--plan` copies everything to a staging folder first and only clears `photos/` after the count
checks out, so an aborted run never loses photos. All subcommands accept `--photos DIR`.

## Beat and cut mechanics

- With `librosa` installed → `librosa.beat.beat_track` detects beats; otherwise a fixed grid at
  `bpm` is used, phase-aligned to the first strong onset found via an energy-flux peak
  (`onset_phase`).
- Cuts must land on beats: `hold` converts to an integer beat count `step = round(hold /
  interval)`, with each segment forced to ≥ 2.5 s (`step_beats * interval < 2.5` → increment).
- Adjacent cuts are kept ≥ 1.2 s apart; when there are fewer photos than slots, photos cycle in
  filename order.
- Number of slots needed: `n = ceil(duration / (step * interval))`.

## Render pipeline

1. **Layers**: per photo, a blurred background (same photo, cover-crop, upscaled 1.06, Gaussian
   blur 16, darkened 0.68, saturated 1.18) + a rounded photo layer (radius 40 px, 4× supersampled
   mask) + a vignette. EXIF orientation is applied before measuring sizes.
2. **Viewfinder**: in `contain` mode the photo's longest edge ≤ `frame_h` and width ≤ `frame_w`;
   landscape and portrait photos get different rounded sizes. `cover` uses `ImageOps.fit`.
3. **Transitions**: `render_frame` smoothstep-blends the two layers within `xfade/2` either side
   of each cut.
4. **Static chrome**: bottom progress bar + all timecode labels pre-rendered
   (`0:12/0:50`, ink-centred on the bar line).
5. **Encoding**: frames piped to ffmpeg as rawvideo rgb24, libx264 + AAC; audio gets
   `afade` in/out (`min(2, dur/4)` s) + `loudnorm`; `+faststart` for streaming.
6. **Ending**: the last 2 seconds fade to black; the video starts directly on frame one (no
   fade-in).

## Dependency bootstrap (Windows-friendly)

The script re-execs itself with the first interpreter that can import numpy/scipy/pillow,
searching in order: `PHOTOREEL_PYTHON` → current interpreter → `python`/`python3` on PATH →
project-local `.venv/venv/env` → every conda/mamba/micromamba env (including a scan of common
install locations on disk).

`ffmpeg`/`ffprobe` must be on PATH. `librosa` is optional (better beat tracking).

```powershell
python -m pip install numpy scipy pillow librosa
```

## Performance and limits

- Rendering draws each frame in Python: expect minutes to tens of minutes for a minute-scale
  video. Adding/removing/reordering photos shifts every cut point — the whole video must be
  re-rendered (`photo_reel.mp4` is the only artifact; no intermediate files).
- Fonts: `segoeui → arial → helveticaneue → DejaVuSans` under `%WINDIR%\Fonts`, falling back to
  PIL's bitmap font; non-Latin credit text will render as boxes — keep `credit` in Latin.
- Copyright: `credit` should name the actual author; confirm you have the rights to the music.
