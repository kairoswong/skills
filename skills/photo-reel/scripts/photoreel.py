import argparse, json, os, re, shutil, subprocess, sys, tempfile, wave

try:
    import numpy as np
except Exception:
    np = None
try:
    import scipy.io.wavfile as wavfile
except Exception:
    wavfile = None
try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
except Exception:
    Image = None
try:
    import librosa
except Exception:
    librosa = None

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = {
    "width": 1080, "height": 1920, "fps": 30,
    "hold": 4.9, "xfade": 0.8, "fit": "contain",
    "frame_w": 960, "frame_h": 1440, "shift": -60,
    "credit": "",
    "start": 0.0, "duration": 0.0,
    "music": "music/music.mp3",
    "guide": "music/guide.wav",
    "bpm": 120.0,
    "crf": 18, "preset": "medium",
}

AUDIO_EXT = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg")
PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
RADIUS = 40
FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf", "helveticaneue.ttf", "DejaVuSans.ttf")


def natural(s):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", s)]


def load_config(project):
    cfg = dict(DEFAULTS)
    p = os.path.join(project, "config.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def require_deps():
    missing = []
    if np is None:
        missing.append("numpy")
    if wavfile is None:
        missing.append("scipy")
    if Image is None:
        missing.append("pillow")
    if missing:
        raise SystemExit("missing python packages: %s\ninstall with:  \"%s\" -m pip install %s"
                         % (", ".join(missing), sys.executable, " ".join(missing)))
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found on PATH; install ffmpeg or add its bin folder to PATH")


REEXEC_FLAG = "PHOTOREEL_REEXEC"
NEEDED_MODULES = "numpy,scipy,PIL"
CONDA_DIR_NAMES = ("anaconda3", "miniconda3", "anaconda", "miniconda",
                   "miniforge3", "mambaforge", "micromamba")


def env_python(prefix):
    if os.name == "nt":
        p = os.path.join(prefix, "python.exe")
    else:
        p = os.path.join(prefix, "bin", "python")
    return p if os.path.isfile(p) else None


def deps_ok(python):
    if not python or not os.path.isfile(python):
        return False
    try:
        p = subprocess.run([python, "-c", "import " + NEEDED_MODULES],
                           capture_output=True, timeout=120)
        return p.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def disk_prefixes():
    """Conda-style installs reachable from env vars, standard locations and drives."""
    roots = [os.environ.get(v) for v in ("CONDA_PREFIX", "CONDA_ROOT", "MAMBA_ROOT_PREFIX")]
    bases = [r for r in roots if r]
    bases += [os.path.expanduser("~"), os.environ.get("LOCALAPPDATA", ""),
              os.environ.get("ProgramData", r"C:\ProgramData")]
    if os.name == "nt":
        bases += [d + ":\\" for d in "CDEFGH" if os.path.isdir(d + ":\\")]
    for base in bases:
        if base and os.path.isdir(base):
            for name in CONDA_DIR_NAMES:
                p = os.path.join(base, name)
                if os.path.isdir(p):
                    roots.append(p)
    prefixes = []
    for root in roots:
        if not root:
            continue
        prefixes.append(root)
        envs = os.path.join(root, "envs")
        if os.path.isdir(envs):
            prefixes += [os.path.join(envs, e) for e in sorted(os.listdir(envs))]
    return prefixes


def candidate_pythons(project):
    """Every interpreter worth trying, best first, de-duplicated."""
    cands = [os.environ.get("PHOTOREEL_PYTHON"), sys.executable]
    cands += [shutil.which(n) for n in ("python", "python3")]
    cands += [env_python(os.path.join(project, v)) for v in (".venv", "venv", "env")]
    cands += [env_python(p) for p in disk_prefixes()]
    seen, out = set(), []
    for p in cands:
        if p and os.path.isfile(p):
            key = os.path.normcase(os.path.abspath(p))
            if key not in seen:
                seen.add(key)
                out.append(os.path.abspath(p))
    return out


def ensure_interpreter(project, explicit=None):
    """Re-run this script with an interpreter that has numpy/scipy/pillow."""
    if explicit:
        if not deps_ok(explicit):
            raise SystemExit("%s cannot import %s" % (explicit, NEEDED_MODULES))
        if os.path.normcase(os.path.abspath(explicit)) != os.path.normcase(sys.executable):
            return relaunch(explicit)
        return
    if os.environ.get(REEXEC_FLAG) or deps_ok(sys.executable):
        return
    for cand in candidate_pythons(project):
        if os.path.normcase(cand) == os.path.normcase(sys.executable):
            continue
        if deps_ok(cand):
            print("using python %s" % cand, flush=True)
            return relaunch(cand)
    raise SystemExit(
        "no python with %s found.\n"
        "checked: %s\n"
        "install them with:  \"%s\" -m pip install numpy scipy pillow librosa\n"
        "or point PHOTOREEL_PYTHON at a ready interpreter."
        % (NEEDED_MODULES, "\n         ".join(candidate_pythons(project)), sys.executable))


def relaunch(python):
    env = os.environ.copy()
    env[REEXEC_FLAG] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    sys.exit(subprocess.call([python, os.path.abspath(__file__)] + sys.argv[1:], env=env))


def photo_files(folder):
    if not os.path.isdir(folder):
        raise SystemExit("photo folder not found: " + folder)
    files = [f for f in os.listdir(folder) if f.lower().endswith(PHOTO_EXT)]
    files.sort(key=natural)
    if not files:
        raise SystemExit("no photos in " + folder)
    return files


def find_music(project, cfg, force_guide):
    if force_guide:
        return ensure_guide(project, cfg)
    p = cfg.get("music") or ""
    if not os.path.isabs(p):
        p = os.path.join(project, p)
    if os.path.exists(p):
        return p
    base = os.path.splitext(p)[0]
    for ext in AUDIO_EXT:
        if os.path.exists(base + ext):
            return base + ext
    return ensure_guide(project, cfg)


def write_guide(out, dur=55.0, bpm=120.0):
    """Synthesize a demo track (pad + pluck + light drums) for beat-sync testing.

    Only used when the configured music file is missing; swap in licensed
    music for anything public.
    """
    sr = 48000
    beat = 60.0 / bpm
    eighth = beat / 2
    bar = eighth * 6
    buf = np.zeros((int(dur * sr), 2))

    def add(t, sig, gain=1.0, pan=0.0):
        i = int(t * sr)
        if i >= buf.shape[0]:
            return
        sig = np.asarray(sig)[:buf.shape[0] - i] * gain
        buf[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2) * 1.414
        buf[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2) * 1.414

    def tone(midi, kind, dur_s):
        f = 440.0 * 2 ** ((midi - 69) / 12.0)
        t = np.arange(int(dur_s * sr)) / sr
        if kind == "pad":
            x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t)
                 + 0.35 * np.sin(2 * np.pi * f * 0.996 * t))
            x *= np.minimum(1, t / 0.35) * np.exp(-t * 0.35)
        elif kind == "pluck":
            x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t)
                 + 0.12 * np.sin(2 * np.pi * f * 3 * t))
            x *= np.exp(-t * 2.6)
        elif kind == "kick":
            freq = 55 * np.exp(-t * 16) + 34
            x = np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-t * 12)
        elif kind == "snare":
            x = (np.random.default_rng(7).standard_normal(len(t)) * np.exp(-t * 24) * 0.7
                 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.45)
        else:  # hat
            x = np.random.default_rng(11).standard_normal(len(t)) * np.exp(-t * 90)
        return x

    prog = [[54, 58, 61], [51, 54, 58], [47, 51, 54], [49, 53, 56]]
    bars = int(np.ceil(dur / bar))
    for b in range(bars):
        t0 = b * bar
        chord = prog[b % len(prog)]
        for k, m in enumerate(chord):
            add(t0, tone(m + 12, "pad", bar * 1.05), 0.035, -0.3 + 0.3 * k)
            add(t0 + k * eighth, tone(m + 24, "pluck", 0.9), 0.045, -0.2 + 0.2 * k)
        if b >= 2:
            for e in range(6):
                te = t0 + e * eighth
                if e in (0, 3):
                    add(te, tone(0, "kick", 0.28), 0.55)
                    add(te, tone(chord[0] - 12, "pluck", 0.6), 0.16)
                if e == 4:
                    add(te, tone(0, "snare", 0.2), 0.28, 0.12)
                add(te, tone(0, "hat", 0.05), 0.10 if e % 2 == 0 else 0.06, 0.18)
        if b == bars - 3:
            for k, m in enumerate(chord):
                add(t0 + k * 2 * eighth, tone(m + 12, "pluck", 1.2), 0.06)

    fade = int(1.2 * sr)
    buf[:fade] *= np.linspace(0, 1, fade)[:, None]
    buf[-fade:] *= np.linspace(1, 0, fade)[:, None]
    buf = buf / (float(np.max(np.abs(buf))) or 1) * 0.88
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.clip(buf * 32767, -32768, 32767).astype(np.int16).tobytes())
    print("guide ->", out, "%.0fs @ %.0f BPM" % (dur, bpm), flush=True)


def ensure_guide(project, cfg):
    p = cfg.get("guide") or "music/guide.wav"
    if not os.path.isabs(p):
        p = os.path.join(project, p)
    if not os.path.exists(p):
        print("no music file found; making a %.0f BPM guide track" % cfg["bpm"], flush=True)
        write_guide(p, 55.0, cfg["bpm"])
    return p


def decode_mono(music, start, duration):
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start)]
        if duration > 0:
            cmd += ["-t", str(duration)]
        cmd += ["-i", music, "-ac", "1", "-ar", "22050", "-f", "wav", tmp]
        subprocess.run(cmd, check=True)
        sr, y = wavfile.read(tmp)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    scale = {np.dtype(np.int16): 32768.0, np.dtype(np.int32): 2147483648.0}.get(y.dtype)
    y = y.astype(np.float32)
    if scale:
        y /= scale
    elif y.dtype == np.uint8:
        y = (y - 128.0) / 128.0
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y, sr


def detect_beats(music, start, duration, bpm):
    y, sr = decode_mono(music, start, duration)
    audio_dur = len(y) / float(sr)
    fallback = 60.0 / float(bpm or 145.0)
    if librosa is not None:
        try:
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", trim=False)
            beats = np.array([float(x) for x in beats], dtype=float)
            tempo = float(np.atleast_1d(tempo)[0])
            if len(beats) >= 4:
                interval = float(np.median(np.diff(beats)))
                if interval > 0.05:
                    return beats, interval, tempo, audio_dur
        except Exception as exc:
            print("librosa beat tracking unavailable (%s)" % exc, flush=True)
    offset = onset_phase(y, sr)
    print("using a %.0f BPM grid (phase %.3fs)" % (bpm or 145.0, offset), flush=True)
    beats = np.arange(offset, audio_dur, fallback)
    return beats, fallback, float(bpm or 145.0), audio_dur


def onset_phase(y, sr):
    """Offset of the first strong onset, used to align a fixed tempo grid."""
    hop = 512
    n = len(y) // hop
    if n < 8:
        return 0.0
    frames = y[:n * hop].reshape(n, hop)
    energy = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    flux = np.maximum(0.0, np.diff(energy, prepend=energy[0]))
    if flux.max() <= 0:
        return 0.0
    flux = flux / flux.max()
    fps = sr / float(hop)
    window = max(1, int(fps * 2.0))
    peak = int(np.argmax(flux[:window]))
    return peak / fps if flux[peak] > 0.25 else 0.0


def snap_step(target, interval):
    """Seconds-per-photo target -> integer beats, keeping every segment >= 2.5 s."""
    step = max(1, int(round(target / interval)))
    while step * interval < 2.5:
        step += 1
    return step


def build_cuts(beats, interval, n, hold, duration, audio_dur):
    target = hold if duration <= 0 else min(hold, max(2.5, duration / max(1, n)))
    step = snap_step(target, interval)
    i0 = int(np.argmin(np.abs(beats)))
    cuts = [0.0]
    for k in range(1, n + 1):
        idx = i0 + k * step
        if idx < len(beats):
            cuts.append(float(beats[idx]))
        else:
            cuts.append(cuts[-1] + step * interval)
    if duration > 0:
        cuts = [min(c, duration) for c in cuts]
    for i in range(1, len(cuts)):
        cuts[i] = max(cuts[i], cuts[i - 1] + 1.2)
    if cuts[-1] > audio_dur:
        print("warning: requested photos exceed the music; last photo will be cut short", flush=True)
        cuts[-1] = max(cuts[0] + 1.2, audio_dur)
    return [round(c, 3) for c in cuts], step


def plan_timeline(cfg, photos, beats, interval, audio_dur):
    """Pick how many slots the music needs and where the cuts land.

    Returns (used, cuts, dur, step). `used` cycles `photos` when there are
    fewer of them than the music needs.
    """
    target_dur = min(audio_dur, cfg["duration"]) if cfg["duration"] > 0 else audio_dur
    step = snap_step(cfg["hold"], interval)
    n = max(1, int(np.ceil(target_dur / (step * interval))))
    used = [photos[i % len(photos)] for i in range(n)]
    cuts, step = build_cuts(beats, interval, n, cfg["hold"], cfg["duration"], audio_dur)
    return used, cuts, cuts[-1], step


def fit_photo(w, h, cfg):
    """Scale a photo to fit inside the frame box without cropping."""
    s = min(cfg["frame_w"] / float(w), cfg["frame_h"] / float(h))
    return max(2, int(round(w * s))), max(2, int(round(h * s)))


def build_timeline(cfg, project, photos, cuts, dur):
    """Per-photo frame sizes plus the segment list the renderer consumes."""
    photo_rows = []
    for f in photos:
        with Image.open(os.path.join(project, "photos", f)) as im:
            # 按 EXIF 方向旋转后的真实尺寸计算取景框，与 build_layers 一致；
            # 否则带 Orientation 标记的照片会被压扁/拉伸。
            w, h = ImageOps.exif_transpose(im).size
        fw, fh = fit_photo(w, h, cfg)
        photo_rows.append({"name": f, "fw": fw, "fh": fh})
    segs = [{"t0": cuts[i], "name": p["name"], "fw": p["fw"], "fh": p["fh"]}
            for i, p in enumerate(photo_rows)]
    return {
        "width": cfg["width"], "height": cfg["height"], "fps": cfg["fps"],
        "dur": dur, "xfade": cfg["xfade"],
        "shift": cfg.get("shift", 0),
        "credit": cfg.get("credit", ""),
        "segs": segs,
    }


def load_font(size):
    root = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for name in FONT_CANDIDATES:
        p = os.path.join(root, name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def fmt(sec):
    total = max(0, int(round(sec)))
    return "%d:%02d" % (total // 60, total % 60)


def smooth(x):
    x = 0.0 if x < 0 else 1.0 if x > 1 else x
    return x * x * (3 - 2 * x)


def draw_tracked(draw, xy, text, font, fill, tracking=0.0, center=False):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = xy[0] - total / 2.0 if center else xy[0]
    for ch, w in zip(text, widths):
        draw.text((x, xy[1]), ch, font=font, fill=fill)
        x += w + tracking


def build_vignette(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w * 0.5, h * 0.42
    r = np.sqrt(((xx - cx) / (w * 0.5)) ** 2 + ((yy - cy) / (h * 0.5)) ** 2)
    a1 = np.clip((r - 0.4) / 0.6, 0.0, 1.0)
    a1 = a1 * a1 * (3 - 2 * a1) * 0.52
    t = yy / max(1.0, h - 1.0)
    a2 = np.where(t < 0.26, 0.26 * (1 - t / 0.26),
                  np.where(t > 0.74, 0.42 * (t - 0.74) / 0.26, 0.0))
    a = 1.0 - (1.0 - a1) * (1.0 - a2)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def build_bg(im, w, h):
    bg = ImageOps.fit(im, (w, h), Image.LANCZOS)
    bg = bg.resize((int(w * 1.06), int(h * 1.06)), Image.LANCZOS)
    left, top = (bg.width - w) // 2, (bg.height - h) // 2
    bg = bg.crop((left, top, left + w, top + h))
    bg = bg.filter(ImageFilter.GaussianBlur(16))
    bg = ImageEnhance.Brightness(bg).enhance(0.68)
    return ImageEnhance.Color(bg).enhance(1.18)


def rounded_mask(w, h, radius):
    s = 4
    m = Image.new("L", (w * s, h * s), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * s - 1, h * s - 1], radius=radius * s, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def build_photo_layer(im, fw, fh, fit):
    if fit == "cover":
        ph = ImageOps.fit(im, (fw, fh), Image.LANCZOS)
    else:
        ph = im.resize((fw, fh), Image.LANCZOS)
    ph = ImageEnhance.Color(ph).enhance(1.03)
    ph = ImageEnhance.Contrast(ph).enhance(1.02)
    layer = ph.convert("RGBA")
    r = min(RADIUS, min(fw, fh) // 2)
    layer.putalpha(rounded_mask(fw, fh, r))
    return layer


def build_layers(project, cfg, data):
    w, h = cfg["width"], cfg["height"]
    vig = build_vignette(w, h)
    layers = []
    layers_by_photo = {}
    for seg in data["segs"]:
        name = seg["name"]
        if name not in layers_by_photo:
            with Image.open(os.path.join(project, "photos", name)) as raw:
                im = ImageOps.exif_transpose(raw).convert("RGB")
            bg = Image.alpha_composite(build_bg(im, w, h).convert("RGBA"), vig).convert("RGBA")
            fw, fh = seg["fw"], seg["fh"]
            layers_by_photo[name] = {
                "bg": bg, "fw": fw, "fh": fh,
                "photo": build_photo_layer(im, fw, fh, cfg["fit"]),
            }
        layers.append(layers_by_photo[name])
    return layers


def build_chrome(cfg, dur):
    w, h = cfg["width"], cfg["height"]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bar_y = h - 62
    labels, pos, tw = build_time_labels(cfg, dur, bar_y)
    bar_x0 = 60
    bar_x1 = 60 + 960 - tw - 32
    d.rectangle([bar_x0, bar_y, bar_x1, bar_y + 2], fill=(255, 255, 255, 38))
    credit = cfg.get("credit") or ""
    if credit:
        draw_tracked(d, (w / 2.0, h - 156), credit, load_font(28),
                     (255, 255, 255, 148), tracking=2.8, center=True)
    return {"static": img, "labels": labels, "pos": pos,
            "bar": (bar_x0, bar_x1, bar_y)}


def build_time_labels(cfg, dur, bar_y):
    """Pre-render every elapsed/total label, ink-centred on the progress bar line."""
    w, h = cfg["width"], cfg["height"]
    font = load_font(30)
    total = fmt(dur)
    texts = ["%s/%s" % (fmt(i), total) for i in range(int(dur) + 2)]
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    widths = [probe.textlength(s, font=font) for s in texts]
    tw = int(max(widths)) + 2
    th = 44
    labels = []
    for s, sw in zip(texts, widths):
        tmp = Image.new("RGBA", (tw, th * 3), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((tw - sw, th), s, font=font,
                                 fill=(255, 255, 255, 158), anchor="lm")
        ink = tmp.getbbox()
        im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        im.alpha_composite(tmp, (0, int(round(th / 2.0 - (ink[1] + ink[3]) / 2.0))))
        labels.append(im)
    x = 60 + 960 - tw
    y = int(round(bar_y + 1 - th / 2.0))
    return labels, (x, y), tw


def seg_index(segs, t, xfade):
    j = 0
    for i, s in enumerate(segs):
        if t >= s["t0"] - xfade / 2.0:
            j = i
    return j


def paste_photo(frame, layer, alpha, shift=0):
    if alpha <= 0.002:
        return
    fw, fh = layer["fw"], layer["fh"]
    x = (frame.width - fw) // 2
    # tall photos get the full offset, short ones stay near centre
    y = (frame.height - fh) // 2 + int(round(shift * fh / float(frame.height)))
    if alpha >= 0.998:
        frame.paste(layer["photo"], (x, y), layer["photo"])
    else:
        frame.paste(layer["photo"], (x, y),
                    layer["photo"].getchannel("A").point(lambda v: int(v * alpha)))


def render_frame(t, data, layers, chrome, black):
    segs = data["segs"]
    xf = max(data["xfade"], 0.001)
    t = min(max(t, 0.0), data["dur"] - 1e-4)
    j = seg_index(segs, t, data["xfade"])
    seg = segs[j]
    prev = segs[j - 1] if j > 0 else None
    p = smooth((t - (seg["t0"] - xf / 2.0)) / xf) if prev else 1.0
    shift = data.get("shift", 0)

    if prev and p < 0.998:
        previous = layers[j - 1]["bg"].copy()
        paste_photo(previous, layers[j - 1], 1.0, shift)
        current = layers[j]["bg"].copy()
        paste_photo(current, layers[j], 1.0, shift)
        frame = Image.blend(previous, current, p)
    else:
        frame = layers[j]["bg"].copy()
        paste_photo(frame, layers[j], 1.0, shift)

    frame = Image.alpha_composite(frame, chrome["static"])

    bar_x0, bar_x1, bar_y = chrome["bar"]
    span = bar_x1 - bar_x0
    prog = min(max(t / data["dur"], 0.0), 1.0)
    bar = Image.new("RGBA", (span + 16, 24), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([8, 12, 8 + int(span * prog), 14], fill=(255, 255, 255, 184))
    cx = 8 + int(span * prog)
    bd.ellipse([cx - 4, 8, cx + 4, 16], fill=(255, 255, 255, 217))
    frame.alpha_composite(bar, (bar_x0 - 8, bar_y - 12))

    labels = chrome["labels"]
    idx = min(len(labels) - 1, max(0, int(t)))
    frame.alpha_composite(labels[idx], chrome["pos"])

    fade_duration = min(2.0, data["dur"])
    fade = 1.0 - smooth((data["dur"] - t) / fade_duration)
    out = frame.convert("RGB")
    if fade > 0.002:
        out = Image.blend(out, black, fade)
    return out


def render_video(project, cfg, data, layers, chrome, music, start):
    w, h, fps = cfg["width"], cfg["height"], cfg["fps"]
    out = os.path.join(project, "photo_reel.mp4")
    nframes = max(1, int(round(data["dur"] * fps)))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    audio_fade = min(2.0, data["dur"] / 4)
    af = "afade=t=in:st=0:d=%.2f,afade=t=out:st=%.2f:d=%.2f,loudnorm=I=-14:TP=-1.5:LRA=11" % (
        audio_fade, max(0, data["dur"] - audio_fade), audio_fade)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (w, h),
           "-r", str(fps), "-i", "-",
           "-ss", str(start), "-t", str(data["dur"]), "-i", music,
           "-map", "0:v:0", "-map", "1:a:0", "-map_chapters", "-1",
           "-c:v", "libx264", "-preset", str(cfg["preset"]), "-crf", str(cfg["crf"]),
           "-pix_fmt", "yuv420p", "-af", af, "-ar", "48000", "-ac", "2",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    print("+ ffmpeg -> %s (%d frames)" % (out, nframes), flush=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(nframes):
            proc.stdin.write(render_frame(i / float(fps), data, layers, chrome, black).tobytes())
            if i and i % (fps * 5) == 0:
                print("  frame %d/%d" % (i, nframes), flush=True)
        proc.stdin.close()
    except BrokenPipeError:
        pass
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed while encoding video")
    print("video ->", out, flush=True)


def probe(project):
    out = os.path.join(project, "photo_reel.mp4")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,codec_name,width,height,sample_rate,channels",
                        "-of", "json", out], capture_output=True, text=True)
    print(p.stdout.strip(), flush=True)


def cmd_stats(photos_dir):
    """Print size/brightness/colour per photo so they can be grouped into chapters."""
    print("%-22s %-11s %6s %5s %5s %6s %6s %5s" %
          ("file", "size", "bright", "dark", "sat", "green", "warm", "sky"))
    for f in photo_files(photos_dir):
        with Image.open(os.path.join(photos_dir, f)) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            w, h = im.size
            im.thumbnail((400, 400))
            a = np.asarray(im).astype(np.float32)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        mx = a.max(axis=2)
        sat = np.where(mx > 0, (mx - a.min(axis=2)) / np.maximum(mx, 1e-6), 0)
        sky = ((b > r + 15) & (b > g + 5) & (mx > 120)).mean()
        print("%-22s %-11s %6.0f %5.2f %5.2f %+6.0f %+6.0f %5.2f%s"
              % (f, "%dx%d" % (w, h), mx.mean(), (mx < 50).mean(), sat.mean(),
                 (g - (r + b) / 2).mean(), (r - b).mean(), sky,
                 "  night" if (mx < 50).mean() > 0.5 else ""))


def cmd_check(photos_dir):
    """Report numbering gaps and unnumbered files."""
    fs = photo_files(photos_dir)
    numbered = {f: int(f.split(".")[0]) for f in fs if re.fullmatch(r"\d+\.\w+", f)}
    loose = [f for f in fs if f not in numbered]
    nums = sorted(numbered.values())
    gaps = [i for i in range(nums[0], nums[-1] + 1) if i not in nums] if nums else []
    print("%d files, numbering %s" % (len(fs), "%d..%d" % (nums[0], nums[-1]) if nums else "none"))
    print("gaps: %s" % (gaps or "none"))
    print("unnumbered: %s" % (loose or "none"))
    return 0 if not gaps and not loose else 1


def cmd_plan(spec, photos_dir):
    """Renumber photos into 01.jpg, 02.jpg ... following the given old order.

    SPEC is comma-separated old numbers, or a file listing one per line.
    Copies to a staging folder first, so an aborted run never loses photos.
    """
    tmp = os.path.join(HERE, "_tmp_reorder")
    existing = set(photo_files(photos_dir))
    if os.path.exists(spec):
        tokens = [ln.split("#")[0].strip() for ln in open(spec, encoding="utf-8")]
    else:
        tokens = spec.split(",")

    def resolve(tok):
        if tok in existing:
            return tok
        for cand in ("%s.jpg" % tok, "%02d.jpg" % int(tok), "%d.jpg" % int(tok)):
            if cand in existing:
                return cand
        raise SystemExit("no such photo: " + tok)

    order = [resolve(t) for t in tokens if t]
    if len(order) != len(set(order)):
        raise SystemExit("duplicate entries in the order")
    missing = sorted(existing - set(order))
    if missing:
        raise SystemExit("photos not covered by the order: %s" % missing)

    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    for i, f in enumerate(order, start=1):
        shutil.copy2(os.path.join(photos_dir, f), os.path.join(tmp, "%02d.jpg" % i))
    if len(os.listdir(tmp)) != len(order):
        raise SystemExit("staging count mismatch")
    for f in existing:
        os.remove(os.path.join(photos_dir, f))
    for name in sorted(os.listdir(tmp)):
        shutil.move(os.path.join(tmp, name), os.path.join(photos_dir, name))
    os.rmdir(tmp)
    print("reordered %d photos -> 01.jpg..%02d.jpg" % (len(order), len(order)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=HERE)
    ap.add_argument("--photos", default=None)
    ap.add_argument("--music", default=None)
    ap.add_argument("--start", type=float, default=None)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--hold", type=float, default=None)
    ap.add_argument("--xfade", type=float, default=None)
    ap.add_argument("--fit", choices=["cover", "contain"], default=None)
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--crf", type=int, default=None)
    ap.add_argument("--guide", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--python", default=None, help="interpreter to use for rendering")
    ap.add_argument("--stats", action="store_true", help="print per-photo brightness/colour, then exit")
    ap.add_argument("--check", action="store_true", help="report numbering gaps, then exit")
    ap.add_argument("--plan", metavar="SPEC",
                    help="renumber photos into 01.jpg.. following SPEC (comma-separated old "
                         "numbers, or a file listing one per line), then exit")
    ap.add_argument("--make-guide", metavar="OUT", nargs="?", const="",
                    help="synthesize a demo guide track and exit")
    a = ap.parse_args()

    project = os.path.abspath(a.project)
    ensure_interpreter(project, a.python)
    require_deps()

    photos_dir = os.path.abspath(a.photos) if a.photos else os.path.join(project, "photos")
    if a.stats:
        return cmd_stats(photos_dir)
    if a.check:
        return cmd_check(photos_dir)
    if a.plan:
        return cmd_plan(a.plan, photos_dir)
    if a.make_guide is not None:
        cfg = load_config(project)
        out = a.make_guide or os.path.join(project, cfg["guide"])
        return write_guide(out, 55.0, cfg["bpm"])

    cfg = load_config(project)
    for k in ("hold", "xfade", "fit", "fps", "start", "duration", "crf"):
        v = getattr(a, k)
        if v is not None:
            cfg[k] = v
    if a.music:
        cfg["music"] = a.music
    if photos_dir != os.path.abspath(os.path.join(project, "photos")):
        raise SystemExit("keep photos inside " + os.path.join(project, "photos"))
    photos = photo_files(photos_dir)
    music = find_music(project, cfg, a.guide)
    print("python", sys.executable, flush=True)
    print("photos", len(photos), "music", music, flush=True)
    beats, interval, tempo, audio_dur = detect_beats(music, cfg["start"], cfg["duration"], cfg["bpm"])
    used, cuts, dur, step = plan_timeline(cfg, photos, beats, interval, audio_dur)
    data = build_timeline(cfg, project, used, cuts, dur)
    print("tempo %.1f BPM · beat %.3fs · step %d beats · %d photos (%d source) · %.2fs"
          % (tempo, interval, step, len(used), len(photos), dur), flush=True)
    if a.no_render:
        return
    layers = build_layers(project, cfg, data)
    chrome = build_chrome(cfg, dur)
    render_video(project, cfg, data, layers, chrome, music, cfg["start"])
    probe(project)


if __name__ == "__main__":
    sys.exit(main() or 0)
