#!/usr/bin/env python3
"""Generate the real-world rollout figure (``fig:real_rollout``).

Layout: 2 rows x 6 frames; each row shows two tasks side by side with
3 evenly-spaced keyframes per task and its instruction as the group title.

Usage:
    python scripts/plot_real_rollout.py
Output:
    Figures/real_rollout.pdf

To swap videos or tasks, edit TASKS below and re-run. Each entry:
    (tag, instruction, video_path, crop)
- tag: "(a)" ... used as the label prefix.
- instruction: italic title shown above the 3 keyframes.
- crop: ffmpeg crop "w:h:x:y" to trim off-workspace clutter, or None.
Frames are sampled at FRACS of the video duration (start / middle / end).
"""
import os
import subprocess
import tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))

# ---------------------------------------------------------------- data (edit me)
TASKS = [
    ("(a)", "Put the kiwi into the basket",
     "video/bcb64796c52be3287555a4e06a98d3fd_raw.mp4", "1440:1080:0:0"),
    ("(b)", "Stack the green and then the yellow bowl on the plate",
     "video/a92eb89f0846587a5885ea7dd962a502_raw.mp4", "1440:1080:0:0"),
    ("(c)", "Put the green pepper and then the watermelon into the pan",
     "video/0d8811e101e3588375ab97a6db91652c.mp4", "960:720:0:0"),
    ("(d)", "Lift the pot",
     "video/d5eb6e252a21dfdbd4160c8c3a615611_raw.mp4", "1440:1080:0:0"),
]
FRACS = [0.12, 0.55, 0.95]      # sample points along each video
PER_ROW = 2                     # tasks per row (2 tasks x 3 frames = 6 images)
OUT = os.path.join(ROOT, "Figures", "real_rollout.pdf")
# -----------------------------------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "font.size": 7, "pdf.fonttype": 42,
})


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def grab(path, t, crop, dst):
    vf = (f"crop={crop}," if crop else "") + "scale=800:-1"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path,
         "-frames:v", "1", "-q:v", "2", "-vf", vf, dst, "-y"], check=True)


def main():
    tmp = tempfile.mkdtemp(prefix="rollout_")
    frames = {}
    for tag, _, video, crop in TASKS:
        path = os.path.join(ROOT, video)
        dur = duration(path)
        for k, f in enumerate(FRACS):
            dst = os.path.join(tmp, f"{tag[1]}_{k}.jpg")
            grab(path, dur * f, crop, dst)
            frames[(tag, k)] = dst

    n_rows = (len(TASKS) + PER_ROW - 1) // PER_ROW
    n_cols = PER_ROW * len(FRACS)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(7.0, 1.06 * n_rows))
    for i, (tag, instr, _, _) in enumerate(TASKS):
        row, grp = divmod(i, PER_ROW)
        for k in range(len(FRACS)):
            ax = axes[row][grp * len(FRACS) + k]
            # interpolation="none": embed full-res pixels in the PDF instead of
            # resampling down to the canvas dpi (which blurs the frames)
            ax.imshow(mpimg.imread(frames[(tag, k)]), interpolation="none")
            ax.set_axis_off()
            if k == 1:  # middle frame carries the group title
                ax.set_title(instr, fontsize=10, style="italic", pad=3)
    fig.subplots_adjust(left=0.002, right=0.998, top=0.90, bottom=0.01,
                        wspace=0.03, hspace=0.22)
    fig.savefig(OUT, dpi=600, bbox_inches="tight", pad_inches=0.02)
    # ghostscript pass: JPEG-recompress the embedded frames at 300 DPI so the
    # PDF stays small (a few hundred KB instead of several MB)
    tmp_pdf = OUT + ".tmp"
    subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
         "-dCompatibilityLevel=1.5", "-dAutoFilterColorImages=false",
         "-dColorImageFilter=/DCTEncode", "-dDownsampleColorImages=true",
         "-dColorImageResolution=300", "-dColorImageDownsampleThreshold=1.0",
         "-dJPEGQ=92", "-o", tmp_pdf, OUT], check=True)
    os.replace(tmp_pdf, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
