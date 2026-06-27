#!/usr/bin/env python3
"""
Score extracted frames for visual quality.

Metrics:
  blur_score      — Laplacian variance (higher = sharper)
  brightness      — mean pixel value 0-255
  brightness_ok   — 1.0 if well-exposed, < 1.0 if too dark or blown out
  overall         — weighted composite (70% blur, 30% brightness)

Usage:
  python3 score_frames.py <frames_dir> > scores.json
  python3 score_frames.py <frames_dir> --clip-summary > summary.json

Output (default):
  { "filename.jpg": { "blur_score": 312.4, "brightness": 118.2, ... }, ... }

Output (--clip-summary):
  Groups frames by clip_id (filename prefix before last underscore + digit).
  Returns best frame per clip and its timestamp index (0=20%, 1=50%, 2=80%).
"""
import os, sys, json, subprocess
import numpy as np

SAMPLE_POSITIONS = [0.2, 0.5, 0.8]  # matches Step 3 in SKILL.md


def decode_frame(path: str, width: int = 320, height: int = 180) -> np.ndarray | None:
    """Decode a JPEG to a grayscale numpy array via ffmpeg pipe."""
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", path,
        "-vf", f"scale={width}:{height},format=gray",
        "-f", "rawvideo", "-"
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0 or len(result.stdout) != width * height:
        return None
    return np.frombuffer(result.stdout, dtype=np.uint8).reshape(height, width)


def laplacian_variance(arr: np.ndarray) -> float:
    """Measure sharpness: variance of the Laplacian response."""
    f = arr.astype(np.float32)
    # Laplacian kernel: edges → high variance = sharp; low = blurry
    lap = (
        np.roll(f, -1, axis=0) + np.roll(f, 1, axis=0) +
        np.roll(f, -1, axis=1) + np.roll(f, 1, axis=1) -
        4 * f
    )
    return float(np.var(lap))


def brightness_score(arr: np.ndarray) -> tuple[float, float]:
    """Return (mean_brightness, score). Score peaks at 128 (neutral exposure)."""
    mean = float(np.mean(arr))
    score = 1.0 - abs(mean - 128.0) / 128.0
    return mean, score


def score_frame(path: str) -> dict | None:
    arr = decode_frame(path)
    if arr is None:
        return None
    blur = laplacian_variance(arr)
    brightness, b_score = brightness_score(arr)
    overall = blur * 0.7 + b_score * 100.0 * 0.3
    return {
        "blur_score":      round(blur, 2),
        "brightness":      round(brightness, 2),
        "brightness_ok":   round(b_score, 3),
        "overall":         round(overall, 2),
    }


def clip_id_from_filename(filename: str) -> str:
    """'kitchen_before_2_1.jpg' → 'kitchen_before_2'  (strip last _N)."""
    stem = filename.rsplit(".", 1)[0]
    parts = stem.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else stem


def main():
    frames_dir = sys.argv[1]
    clip_summary = "--clip-summary" in sys.argv

    files = sorted(
        f for f in os.listdir(frames_dir)
        if f.lower().endswith(".jpg")
    )

    scores: dict[str, dict] = {}
    for fname in files:
        path = os.path.join(frames_dir, fname)
        s = score_frame(path)
        if s:
            scores[fname] = s
        else:
            sys.stderr.write(f"WARN: could not decode {fname}\n")

    if not clip_summary:
        print(json.dumps(scores, indent=2))
        return

    # Group by clip, pick best frame per clip
    clips: dict[str, list] = {}
    for fname, s in scores.items():
        cid = clip_id_from_filename(fname)
        clips.setdefault(cid, []).append({"filename": fname, **s})

    summary = {}
    for cid, frames in clips.items():
        best = max(frames, key=lambda x: x["overall"])
        # Sample index: last digit of filename before extension
        stem = best["filename"].rsplit(".", 1)[0]
        sample_idx = int(stem.rsplit("_", 1)[-1])
        summary[cid] = {
            "best_frame":   best["filename"],
            "sample_index": sample_idx,
            "position":     SAMPLE_POSITIONS[sample_idx],
            "scores":       {k: best[k] for k in ("blur_score", "brightness", "brightness_ok", "overall")},
            "all_frames":   frames,
        }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
