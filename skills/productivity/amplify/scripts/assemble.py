#!/usr/bin/env python3
"""
Assemble a before/after compilation from a manifest JSON.

Manifest format (list of items in display order):
[
  {"type": "title", "text": "BEFORE", "duration": 1.5, "w": 1080, "h": 1920},
  {"type": "clip",  "path": "/tmp/amplify/trim_0.mp4",  "duration": 5.0},
  {"type": "clip",  "path": "/tmp/amplify/trim_1.mp4",  "duration": 5.0},
  {"type": "title", "text": "AFTER",  "duration": 1.5, "w": 1080, "h": 1920},
  {"type": "clip",  "path": "/tmp/amplify/trim_2.mp4",  "duration": 5.0}
]

Usage:
  python3 assemble.py manifest.json output.mp4 [--fps 30] [--width 1080] [--height 1920]
"""
import json, sys, os, subprocess, tempfile, shutil

# ── CLI args ──────────────────────────────────────────────────────────────────
manifest_path = sys.argv[1]
output_path   = sys.argv[2]

TARGET_FPS    = 30
TARGET_W      = 1080
TARGET_H      = 1920
for i, arg in enumerate(sys.argv):
    if arg == "--fps":    TARGET_FPS = int(sys.argv[i+1])
    if arg == "--width":  TARGET_W   = int(sys.argv[i+1])
    if arg == "--height": TARGET_H   = int(sys.argv[i+1])

manifest = json.load(open(manifest_path))
work_dir  = os.path.dirname(manifest_path)

# ── Helpers ───────────────────────────────────────────────────────────────────

MACOS_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]

def find_font() -> str:
    for p in MACOS_FONTS:
        if os.path.exists(p):
            return p
    return ""  # ffmpeg will use its built-in default


def run(cmd: list[str], label: str = "") -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"ERROR{' (' + label + ')' if label else ''}:\n{result.stderr[-2000:]}\n")
        sys.exit(1)


def make_title_card(text: str, duration: float, w: int, h: int, out_path: str) -> None:
    """Generate a solid-black title card with centered white text."""
    font_arg = find_font()
    font_clause = f":fontfile='{font_arg}'" if font_arg else ""

    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"color=black:size={w}x{h}:rate={TARGET_FPS}:duration={duration}",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", (
            f"drawtext=text='{text}'"
            f":fontcolor=white"
            f":fontsize={int(h * 0.08)}"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
            f"{font_clause}"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration),
        out_path,
    ], label=f"title card: {text}")


def normalize_clip(src: str, out: str, idx: int) -> None:
    """Scale, pad, set fps, ensure audio track — output to out."""
    # Check whether source has an audio stream
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", src],
        capture_output=True, text=True
    )
    import json as _json
    streams = _json.loads(probe.stdout).get("streams", [])
    has_audio = any(s["codec_type"] == "audio" for s in streams)

    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={TARGET_FPS},format=yuv420p"
    )

    if has_audio:
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src,
            "-vf", vf,
            "-af", "aformat=sample_rates=44100:channel_layouts=stereo",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            out,
        ], label=f"normalize clip {idx}")
    else:
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            out,
        ], label=f"normalize clip {idx} (add silent audio)")


# ── Build each segment ────────────────────────────────────────────────────────

segments: list[str] = []

for i, item in enumerate(manifest):
    seg_path = os.path.join(work_dir, f"seg_{i:02d}.mp4")

    if item["type"] == "title":
        w = item.get("w", TARGET_W)
        h = item.get("h", TARGET_H)
        make_title_card(item["text"], item["duration"], w, h, seg_path)
        sys.stderr.write(f"  [{i}] title card '{item['text']}' ({item['duration']}s)\n")

    elif item["type"] == "clip":
        normalize_clip(item["path"], seg_path, i)
        dur = item.get("duration", "?")
        sys.stderr.write(f"  [{i}] clip {os.path.basename(item['path'])} ({dur}s)\n")

    else:
        sys.stderr.write(f"  [{i}] unknown type '{item['type']}' — skipping\n")
        continue

    segments.append(seg_path)

# ── Concatenate ───────────────────────────────────────────────────────────────

concat_list = os.path.join(work_dir, "concat_list.txt")
with open(concat_list, "w") as f:
    for p in segments:
        f.write(f"file '{p}'\n")

run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy",
    output_path,
], label="final concat")

total = sum(item.get("duration", 0) for item in manifest if item["type"] in ("title", "clip"))
sys.stderr.write(f"\nDone — {len(segments)} segments, ~{total:.0f}s → {output_path}\n")
