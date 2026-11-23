#!/usr/bin/env python3
"""Generate the supplementary real-world rollout figures.

Outputs:
    Figures/supp_height.pdf : one row of 6 keyframes, basket task at an unseen
                              container height.
    Figures/supp_light.pdf  : 2 rows x 6 frames, four tasks under unseen
                              coloured lighting (3 keyframes per task).

To swap videos, edit HEIGHT / LIGHT below and re-run.  Each entry:
    (instruction, video_path)
Frames are sampled at the given fractions of the video duration.
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
# crop = (w_frac, h_frac, x_frac, y_frac) of the source frame
DEFAULT_CROP = (0.62, 0.90, 0.02, 0.10)
HEIGHT = [
    ("Standard", "video/supp/basket_standard.mp4", DEFAULT_CROP),
    ("Raised",   "video/supp/basket_height.mp4",   DEFAULT_CROP),
]
HEIGHT_INSTR = "Put the kiwi into the basket"
HEIGHT_FRACS = [0.05, 0.25, 0.45, 0.62, 0.80, 0.97]

LIGHT = [
    ("Put the kiwi into the basket", "video/supp/basket_light.mp4", (0.52, 0.75, 0.19, 0.25)),
    ("Put the green pepper and then watermelon into the pan", "video/supp/pan_light.mp4", DEFAULT_CROP),
    ("Stack the green and then the yellow bowl on the plate", "video/supp/bowls_light.mp4", DEFAULT_CROP),
    ("Lift the pot", "video/supp/pot_light.mp4", DEFAULT_CROP),
]
LIGHT_FRACS = [0.05, 0.25, 0.45, 0.62, 0.80, 0.97]
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


def grab(path, t, dst, crop):
    cw, ch, cx, cy = crop
    vf = f"crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy},scale=800:-1"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path,
         "-frames:v", "1", "-q:v", "2", "-vf", vf, dst, "-y"],
        check=True)


def compress(out):
    tmp_pdf = out + ".tmp"
    subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
         "-dCompatibilityLevel=1.5", "-dAutoFilterColorImages=false",
         "-dColorImageFilter=/DCTEncode", "-dDownsampleColorImages=true",
         "-dColorImageResolution=300", "-dColorImageDownsampleThreshold=1.0",
         "-dJPEGQ=92", "-o", tmp_pdf, out], check=True)
    os.replace(tmp_pdf, out)


def frames_of(video, fracs, tmp, tag, crop):
    path = os.path.join(ROOT, video)
    dur = duration(path)
    out = []
    for k, f in enumerate(fracs):
        dst = os.path.join(tmp, f"{tag}_{k}.jpg")
        grab(path, dur * f, dst, crop)
        out.append(dst)
    return out


def main():
    tmp = tempfile.mkdtemp(prefix="supp_rollout_")

    # ---- height figure: 2 rows (standard vs unseen height) x 6 frames --------
    # row height matches the 16:9 frames so rows sit close together
    n = len(HEIGHT_FRACS)
    fig, axes = plt.subplots(len(HEIGHT), n, figsize=(7.0, 1.12 * len(HEIGHT)))
    for r, (row_label, video, crop) in enumerate(HEIGHT):
        frames = frames_of(video, HEIGHT_FRACS, tmp, f"h{r}", crop)
        for k in range(n):
            ax = axes[r][k]
            ax.imshow(mpimg.imread(frames[k]), interpolation="none")
            ax.set_axis_off()
        axes[r][0].axis("on")
        axes[r][0].set_xticks([]); axes[r][0].set_yticks([])
        for sp in axes[r][0].spines.values():
            sp.set_visible(False)
        axes[r][0].set_ylabel(row_label, fontsize=8, rotation=90, labelpad=4)
    # match the title-to-image gap of the lighting figure
    fig.text(0.5, 0.897, HEIGHT_INSTR, ha="center", va="bottom",
             fontsize=10, style="italic")
    fig.subplots_adjust(left=0.02, right=0.998, top=0.88, bottom=0.01,
                        wspace=0.006, hspace=0.06)
    out = os.path.join(ROOT, "Figures", "supp_height.pdf")
    fig.savefig(out, dpi=600, bbox_inches="tight", pad_inches=0.02)
    compress(out)
    print("saved", out)

    # ---- lighting figure: one task per row, 6 frames each --------------------
    n = len(LIGHT_FRACS)
    n_rows = len(LIGHT)
    fig, axes = plt.subplots(n_rows, n, figsize=(7.0, 1.19 * n_rows))
    for r, (instr, video, crop) in enumerate(LIGHT):
        frames = frames_of(video, LIGHT_FRACS, tmp, f"l{r}", crop)
        for k in range(n):
            ax = axes[r][k]
            ax.imshow(mpimg.imread(frames[k]), interpolation="none")
            ax.set_axis_off()
    fig.subplots_adjust(left=0.002, right=0.998, top=0.955, bottom=0.005,
                        wspace=0.006, hspace=0.26)
    # centred instruction above each row
    for r, (instr, _, _) in enumerate(LIGHT):
        pos = axes[r][0].get_position()
        fig.text(0.5, pos.y1 + 0.008, instr, ha="center", va="bottom",
                 fontsize=10, style="italic")
    out = os.path.join(ROOT, "Figures", "supp_light.pdf")
    fig.savefig(out, dpi=600, bbox_inches="tight", pad_inches=0.02)
    compress(out)
    print("saved", out)


if __name__ == "__main__":
    main()
