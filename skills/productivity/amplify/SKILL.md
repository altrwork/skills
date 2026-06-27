# Amplify

Build a before/after (or multi-phase) compilation video from raw footage folders.
Designed for content creators, tradespeople, and anyone documenting a transformation.

## Inputs

- A folder of raw clips organized as `before/` and `after/` subfolders (or user specifies which files are which)
- Optional: background music file path
- Optional: output format (9:16 TikTok/Reels, 16:9 YouTube, 1:1 Instagram) — default 9:16
- Optional: title card text (default: "BEFORE" / "AFTER")
- Optional: target total duration (default: 20–30s)

## Tooling

- **ffmpeg:** `-hwaccel videotoolbox` for decode, `-preset fast`, `-c:v libx264 -crf 20` for output
- **Python scripts in `<skill-dir>/scripts/`:**
  - `score_frames.py` — rate extracted frames by blur and brightness
  - `assemble.py` — build and render the final video from a manifest
- **Working dir:** `/tmp/amplify/` (mkdir at start, leave artifacts for debugging)

---

## Workflow

### Step 1 — Understand the input

```bash
mkdir -p /tmp/amplify/frames
```

Ask the user (skip any already answered):
1. Where is the footage? (folder path, or use `~/Documents/amplify/input/`)
2. Are files already split into `before/` and `after/` subfolders, or should we sort them together?
3. Target format? (default 9:16)
4. Background music file? (optional — skip if none)
5. Title card text? (default "BEFORE" / "AFTER")

### Step 2 — Probe every clip

For each video file in `before/` and `after/`:

```bash
ffprobe -v quiet -print_format json -show_streams "$FILE"
```

Collect: resolution, duration, fps, has_audio. Print a summary table.
Warn if:
- Any clip is under 3 seconds (too short to trim from)
- Resolutions are mixed (will need scale normalization)
- No audio found (will need silent audio track added before concat)

### Step 3 — Extract candidate frames

Sample 3 frames per clip at 20%, 50%, 80% of its duration:

```bash
ffmpeg -y -ss "$T" -i "$CLIP" -frames:v 1 -q:v 2 /tmp/amplify/frames/${CLIP_ID}_${N}.jpg
```

### Step 4 — Score frames for visual quality

```bash
python3 <skill-dir>/scripts/score_frames.py /tmp/amplify/frames/ > /tmp/amplify/scores.json
```

`score_frames.py` measures blur (Laplacian variance) and brightness for each frame.
For each clip, identify the best-scoring time window (start = timestamp of best frame − 1s).

### Step 5 — Read scored frames and show the user

Read `/tmp/amplify/scores.json`. For each clip, show:
- Clip filename, phase (before/after), best frame score, recommended trim window
- Flag any clip with very low blur score (< 50) as "possibly shaky/blurry"

Then propose a narrative structure. Default template:

```
[TITLE CARD: "BEFORE"  —  1.5s]
  before_clip_1:  best window, ~5s
  before_clip_2:  best window, ~5s   (if available)
[TITLE CARD: "AFTER"   —  1.5s]
  after_clip_1:   best window, ~5s
  after_clip_2:   best window, ~5s   (if available)
[TOTAL: ~20s]
```

Show the structure and let the user confirm, reorder, swap clips, or adjust durations.

### Step 6 — Trim approved clips

For each confirmed clip segment:

```bash
ffmpeg -y -ss "$START" -t "$DURATION" -i "$CLIP" -c copy /tmp/amplify/trim_${N}.mp4
```

If clips have no audio track, add a silent one:

```bash
ffmpeg -y -i /tmp/amplify/trim_${N}.mp4 \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -c:v copy -c:a aac -b:a 128k -shortest \
  /tmp/amplify/trim_audio_${N}.mp4
```

### Step 7 — Apply 9:16 crop (if output is 9:16 and source is 16:9)

Detect source aspect with ffprobe. If 16:9 source and 9:16 output:
- Extract a probe frame: `ffmpeg -ss "$MID" -i "$CLIP" -frames:v 1 /tmp/amplify/probe_${N}.jpg`
- Read the frame to identify where the main subject is
- Crop 608×1080 centered on the subject, scale to 1080×1920

For static scenes with no moving subject, center crop is fine (x = (1920−608)/2 = 656).

### Step 8 — Build the assembly manifest

Write `/tmp/amplify/manifest.json`:

```json
[
  {"type": "title", "text": "BEFORE", "duration": 1.5, "w": 1080, "h": 1920},
  {"type": "clip",  "path": "/tmp/amplify/trim_0.mp4", "duration": 5.0},
  {"type": "clip",  "path": "/tmp/amplify/trim_1.mp4", "duration": 5.0},
  {"type": "title", "text": "AFTER",  "duration": 1.5, "w": 1080, "h": 1920},
  {"type": "clip",  "path": "/tmp/amplify/trim_2.mp4", "duration": 5.0},
  {"type": "clip",  "path": "/tmp/amplify/trim_3.mp4", "duration": 5.0}
]
```

### Step 9 — Assemble final video

```bash
python3 <skill-dir>/scripts/assemble.py /tmp/amplify/manifest.json /tmp/amplify/final_raw.mp4
```

`assemble.py` generates title card clips on the fly, then concatenates everything using
`ffmpeg -f concat` demuxer. All clips must share the same resolution and frame rate —
the script normalizes them with a scale+fps filter if needed.

### Step 10 — Add music bed (if provided)

```bash
# Get duration of assembled video
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 /tmp/amplify/final_raw.mp4)
FADE_START=$(python3 -c "print($DURATION - 2)")

ffmpeg -y -i /tmp/amplify/final_raw.mp4 -i "$MUSIC" \
  -filter_complex "[1:a]volume=0.35,afade=t=out:st=${FADE_START}:d=2[a]" \
  -map 0:v -map "[a]" -shortest \
  -c:v copy -c:a aac -b:a 192k \
  /tmp/amplify/final_music.mp4
```

### Step 11 — Deliver

Save final output to `<source_dir>/../output/` (or `~/Documents/amplify/output/`).
Filename: `amplify_<phase1>_<phase2>_<timestamp>.mp4`

Print: clip count, total duration, output path.
Open with `open <output_path>`.
Offer to iterate: swap a clip, adjust timing, change title text, add/remove music.

---

## Pitfalls

- **Always confirm before/after grouping** — never assume file order or naming.
- **Mixed resolutions break concat** — scale all clips to target resolution before assembly.
- **No audio track in source** — add silent AAC before concat or the filter graph errors.
- **Title card font on macOS** — use `/System/Library/Fonts/Supplemental/Arial Bold.ttf`; fall back to default font if path not found.
- **Short clips (< 3s)** — warn the user; trimming a 2s clip to 5s is impossible.
- **4K source** — downscale to 1920×1080 first for speed, then crop.
- **Static camera = center crop is fine.** Don't waste time on ROI analysis for a tripod-mounted phone video.
