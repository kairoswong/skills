---
name: photo-reel
description: |
  Render a folder of photos plus a music track into a beat-synced vertical
  (1080×1920) photo-reel video with Python/Pillow + ffmpeg — blurred photo
  background, rounded contain-fit photos, crossfades on detected beats, and a
  progress bar / timecode overlay. Use when the user asks to 把照片做成视频,
  photo slideshow with music, 照片卡点视频, photo reel, beat-synced photo
  video, or says "photo-reel". Not for editing existing footage, adding
  motion/animation to photos, or text-to-film pipelines (use story2film).
---

# photo-reel

One photo folder + one music track in, one `photo_reel.mp4` out. Photos keep their aspect
ratio (no crop) inside a 960×1440 viewfinder, over a blurred version of the same photo; cuts
land on music beats (librosa when available, else a fixed BPM grid) with short crossfades; a
bottom timeline and running timecode give it the feel of a photo-app export.

Script: `scripts/photoreel.py` (single file — rendering, encoding, photo tools, guide-track
synthesis). All options and internals: `references/reference.md`. No browser, no Node.

## Rules

- **Photos stay in the project's `photos/` folder**, sorted by filename
  (`01.jpg`, `02.jpg`, …; jpg/png/webp/bmp). Music defaults to `music/music.mp3`.
- **Never modify user photos in place**; `--plan` is the only reordering command and it
  stages to a temp folder first.
- **One round of questions**, then work: which music (and start/duration), credit text,
  portrait or square output. Defaults: whole track, no credit, 1080×1920, contain fit.
- **Copyright**: only use music the user has rights to; without music the script
  synthesizes a 55 s guide track for testing cuts (clearly labelled, not for publishing).
- Changing photos, order, hold, or music shifts every cut point — re-render the whole video.

## 1. Check the machine

```
python "<skill>/scripts/photoreel.py" --no-render --project "<project>"
```

Needs python + numpy/scipy/pillow (script auto-finds a suitable interpreter, including conda
envs) and ffmpeg/ffprobe on PATH; librosa optional (better beats). Report what is missing;
install pip packages if the user agrees, do not install system software yourself.

## 2. Set up the project

Create a project folder with `photos/` (numbered files) and `config.json` (copy from
`template/config.json`). Drop the music at `music/music.mp3` or point `music` at another path.

Useful checks before rendering:

```
python "<skill>/scripts/photoreel.py" --stats  --project "<project>"   # size/brightness/tone per photo
python "<skill>/scripts/photoreel.py" --check --project "<project>"    # numbering gaps
python "<skill>/scripts/photoreel.py" --plan 1,2,5,3,4 --project "<project>"  # reorder + renumber
python "<skill>/scripts/photoreel.py" --no-render --project "<project>"       # cut plan only
```

`--no-render` prints tempo, beat interval, seconds per photo, photo count and total duration —
sanity-check the plan (roughly `duration / hold` photos needed) before committing to a long
render.

## 3. Render

```
python "<skill>/scripts/photoreel.py" --project "<project>"
```

Frame-by-frame Pillow rendering piped into ffmpeg: a minute-scale video takes minutes to tens
of minutes — run it in the background, report progress, don't poll busy-loop. Tune with
`--start/--duration/--hold/--xfade/--fit/--fps/--crf` (all documented in
`references/reference.md`).

## 4. Verify and deliver

- `ffprobe` the output: video stream `1080x1920 h264`, audio `aac 48000 Hz stereo`, duration
  ≈ the planned duration (or `--duration`).
- Spot-check frames near the first and last cut points (extract with ffmpeg) to confirm the
  crossfade and the timecode overlay look right.
- Deliver `<project>/photo_reel.mp4`; tell the user the path, the cut plan (tempo, seconds per
  photo), and that changing photos/order/hold requires a full re-render.
