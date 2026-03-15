# video_creator.py
"""
Builds the final workout video with perfect audio-video sync.
- No ImageMagick needed (all text via Pillow)
- Pillow 10+ ANTIALIAS patch included
- Each segment duration = real measured audio duration (no blank tail)
- Intro card design randomizes every run (5 different styles)
"""

import os
import math
import time
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Pillow 10+ removed ANTIALIAS — patch before MoviePy imports it
from PIL import Image as _PIL
if not hasattr(_PIL, "ANTIALIAS"):
    _PIL.ANTIALIAS = _PIL.LANCZOS

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
)

# ── Constants ─────────────────────────────────────────────
FPS            = 30
OUTPUT_SIZE    = (1920, 1080)
W, H           = OUTPUT_SIZE
AUDIO_PAD_SECS = 0.35   # tiny breath gap after each segment


# ── Font loader ───────────────────────────────────────────

def _load_font(size: int):
    for path in [
        "C:/Windows/Fonts/impact.ttf",       # punchy fitness font
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ── Shared drawing helpers ────────────────────────────────

def _cx(draw, text, font):
    """Horizontal center x for given text."""
    bb = draw.textbbox((0, 0), text, font=font)
    return (W - (bb[2] - bb[0])) // 2


def _outline(draw, pos, text, font, fill, outline=(0,0,0), r=5):
    x, y = pos
    for dx in [-r, 0, r]:
        for dy in [-r, 0, r]:
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def _gradient(draw, top_color, bot_color):
    for y in range(H):
        t = y / H
        r = int(top_color[0]*(1-t) + bot_color[0]*t)
        g = int(top_color[1]*(1-t) + bot_color[1]*t)
        b = int(top_color[2]*(1-t) + bot_color[2]*t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


# ── 5 Randomized intro card designs ──────────────────────

def _intro_style_red(title, sub):
    """Classic red → black gradient with stripe."""
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    _gradient(d, (160, 0, 0), (10, 10, 10))
    d.polygon([(int(W*.55),0),(W,0),(W,int(H*.40)),(int(W*.68),0)], fill=(210,30,30))
    ft = _load_font(118); fs = _load_font(52)
    _outline(d, (_cx(d,title,ft), int(H*.22)), title, ft, (255,255,255), r=6)
    d.text((_cx(d,sub,fs), int(H*.58)), sub, font=fs, fill=(255,204,0))
    d.text((_cx(d,">> GET READY <<",fs), int(H*.74)), ">> GET READY <<", font=fs, fill=(255,90,0))
    return img


def _intro_style_dark_gold(title, sub):
    """Dark charcoal with gold accents."""
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    _gradient(d, (20, 20, 20), (5, 5, 5))
    # Gold bar at top
    d.rectangle([0, 0, W, 12], fill=(255, 200, 0))
    d.rectangle([0, H-12, W, H], fill=(255, 200, 0))
    ft = _load_font(130); fs = _load_font(55)
    _outline(d, (_cx(d,title,ft), int(H*.20)), title, ft, (255,210,0), outline=(0,0,0), r=7)
    d.text((_cx(d,sub,fs), int(H*.60)), sub, font=fs, fill=(200,200,200))
    ready = "ARE YOU READY?"
    d.text((_cx(d,ready,fs), int(H*.76)), ready, font=fs, fill=(255,80,0))
    return img


def _intro_style_blue_electric(title, sub):
    """Electric blue energy style."""
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    _gradient(d, (0, 20, 80), (0, 5, 20))
    # Diagonal stripes
    for i in range(0, W, 120):
        d.polygon([(i,0),(i+60,0),(i+60-H,H),(i-H,H)], fill=(0,30,100))
    ft = _load_font(118); fs = _load_font(52)
    _outline(d, (_cx(d,title,ft), int(H*.20)), title, ft, (0,210,255), outline=(0,0,0), r=6)
    d.text((_cx(d,sub,fs), int(H*.58)), sub, font=fs, fill=(255,255,255))
    tag = "BURN  *  SWEAT  *  REPEAT"
    d.text((_cx(d,tag,fs), int(H*.74)), tag, font=fs, fill=(0,210,255))
    return img


def _intro_style_fire_orange(title, sub):
    """Fire orange — intense energy."""
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    _gradient(d, (180, 60, 0), (10, 5, 0))
    d.polygon([(0,int(H*.55)),(0,H),(int(W*.45),H)], fill=(220,80,0))
    ft = _load_font(120); fs = _load_font(52)
    _outline(d, (_cx(d,title,ft), int(H*.18)), title, ft, (255,255,255), outline=(80,0,0), r=7)
    d.text((_cx(d,sub,fs), int(H*.58)), sub, font=fs, fill=(255,220,100))
    tag = "LET'S BURN SOME CALORIES!"
    d.text((_cx(d,tag,fs), int(H*.74)), tag, font=fs, fill=(255,150,0))
    return img


def _intro_style_minimal_white(title, sub):
    """Clean minimal white on dark — modern look."""
    img = Image.new("RGB", (W, H), (15, 15, 15))
    d   = ImageDraw.Draw(img)
    # Red accent bar left side
    d.rectangle([0, int(H*.15), 18, int(H*.85)], fill=(220, 0, 0))
    ft = _load_font(125); fs = _load_font(54)
    _outline(d, (_cx(d,title,ft), int(H*.22)), title, ft, (255,255,255), outline=(50,0,0), r=5)
    d.text((_cx(d,sub,fs), int(H*.60)), sub, font=fs, fill=(180,180,180))
    tag = "NO EQUIPMENT  |  ALL LEVELS  |  BURN FAT"
    d.text((_cx(d,tag,fs), int(H*.76)), tag, font=fs, fill=(220,0,0))
    return img


INTRO_STYLES = [
    _intro_style_red,
    _intro_style_dark_gold,
    _intro_style_blue_electric,
    _intro_style_fire_orange,
    _intro_style_minimal_white,
]


def _make_intro_card(duration: float) -> ImageClip:
    title = "FAT BURN WORKOUT"
    sub   = "No Equipment  *  Full Body  *  Burn Fat"
    style = random.choice(INTRO_STYLES)
    img   = style(title, sub)
    return ImageClip(np.array(img)).set_duration(duration).set_fps(FPS)


def _make_rest_card(duration: float) -> ImageClip:
    img  = Image.new("RGB", (W, H), (13, 13, 13))
    d    = ImageDraw.Draw(img)
    fb   = _load_font(140)
    fs   = _load_font(60)
    text = "REST"
    bb   = d.textbbox((0,0), text, font=fb)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx   = (W - tw) // 2
    ty   = (H - th) // 2 - 30
    _outline(d, (tx, ty), text, fb, fill=(255,204,0), r=6)
    sub  = "Shake it out!"
    d.text((_cx(d, sub, fs), ty + th + 20), sub, font=fs, fill=(170,170,170))
    return ImageClip(np.array(img)).set_duration(duration).set_fps(FPS)


def _make_outro_card(duration: float) -> ImageClip:
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    _gradient(d, (0, 60, 10), (5, 20, 5))
    ft  = _load_font(105)
    fs  = _load_font(55)
    t1  = "WORKOUT COMPLETE!"
    t2  = "Subscribe for more workouts"
    _outline(d, (_cx(d,t1,ft), int(H*.28)), t1, ft, (255,255,255), r=5)
    d.text((_cx(d,t2,fs), int(H*.58)), t2, font=fs, fill=(255,215,0))
    return ImageClip(np.array(img)).set_duration(duration).set_fps(FPS)

def _make_rest_card_np() -> np.ndarray:
    """Returns the rest card as a numpy array (no duration — used for countdown overlay)."""
    img  = Image.new("RGB", (W, H), (13, 13, 13))
    d    = ImageDraw.Draw(img)
    # Just draw a subtle background — the countdown will fill the rest
    _gradient(d, (20, 10, 10), (5, 5, 5))
    return np.array(img)


# ── Caption + countdown overlay ───────────────────────────

def _draw_text_centered(draw, y, text, font, fill, outline=(0,0,0), r=3):
    bb  = draw.textbbox((0,0), text, font=font)
    tx  = (W - (bb[2]-bb[0])) // 2
    for dx,dy in [(-r,-r),(r,-r),(-r,r),(r,r)]:
        draw.text((tx+dx, y+dy), text, font=font, fill=outline)
    draw.text((tx, y), text, font=font, fill=fill)


def _burn_exercise_frame(frame: np.ndarray, caption: str,
                         t: float, total_dur: float, count_dur: float = 0) -> np.ndarray:
    """
    count_dur = the EXACT user-specified seconds (e.g. 10).
    total_dur = padded vid_dur (slightly longer, used only for progress bar).
    """
    if count_dur <= 0:
        count_dur = total_dur

    img  = Image.fromarray(frame).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_cap   = _load_font(64)
    font_timer = _load_font(90)
    font_small = _load_font(38)

    # ── Bottom caption bar ────────────────────────────
    bb    = draw.textbbox((0,0), caption, font=font_cap)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad   = 22
    bar_h = th + pad * 2
    bar_y = H - bar_h - 6

    bar = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(bar).rectangle([0, bar_y, W, bar_y+bar_h], fill=(0,0,0,180))
    img  = Image.alpha_composite(img, bar)
    draw = ImageDraw.Draw(img)

    tx = (W - tw) // 2
    ty = bar_y + pad
    for dx,dy in [(-3,-3),(3,-3),(-3,3),(3,3)]:
        draw.text((tx+dx, ty+dy), caption, font=font_cap, fill=(0,0,0,255))
    draw.text((tx, ty), caption, font=font_cap, fill=(255,255,255,255))

    # ── Countdown timer — uses count_dur so it shows the exact user value ──
    secs_left = max(0, int(math.floor(count_dur - t)))
    timer_str = str(secs_left)

    # Colour: green → yellow → red last 5s
    if secs_left > count_dur * 0.5:
        t_color = (80, 255, 80, 255)
    elif secs_left > 5:
        t_color = (255, 220, 0, 255)
    else:
        t_color = (255, 60, 60, 255)

    tb   = draw.textbbox((0,0), timer_str, font=font_timer)
    tw_t = tb[2]-tb[0]
    tx_t = W - tw_t - 40
    ty_t = 30

    # Dark pill behind timer
    pill = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle(
        [tx_t-18, ty_t-10, tx_t+tw_t+18, ty_t+(tb[3]-tb[1])+10],
        radius=16, fill=(0,0,0,160))
    img  = Image.alpha_composite(img, pill)
    draw = ImageDraw.Draw(img)
    for dx,dy in [(-3,-3),(3,-3),(-3,3),(3,3)]:
        draw.text((tx_t+dx, ty_t+dy), timer_str, font=font_timer, fill=(0,0,0,255))
    draw.text((tx_t, ty_t), timer_str, font=font_timer, fill=t_color)

    # "SEC" label below timer
    sec_lbl = "SEC"
    sl_bb   = draw.textbbox((0,0), sec_lbl, font=font_small)
    sx      = tx_t + (tw_t - (sl_bb[2]-sl_bb[0])) // 2
    sy      = ty_t + (tb[3]-tb[1]) + 4
    draw.text((sx, sy), sec_lbl, font=font_small, fill=(200,200,200,255))

    # ── Progress bar (very bottom, 6px tall) ─────────
    progress = min(1.0, t / count_dur) if count_dur > 0 else 0
    prog_bar = Image.new("RGBA", (W, H), (0,0,0,0))
    pb_draw  = ImageDraw.Draw(prog_bar)
    pb_draw.rectangle([0, H-6, W, H], fill=(40,40,40,200))
    pb_draw.rectangle([0, H-6, int(W*progress), H], fill=(80,220,80,255))
    img = Image.alpha_composite(img, prog_bar)

    return np.array(img.convert("RGB"))


def _burn_rest_frame(frame: np.ndarray, t: float, total_dur: float, count_dur: float = 0) -> np.ndarray:
    """
    count_dur = exact user rest seconds (e.g. 15).
    total_dur = padded duration (slightly longer).
    """
    if count_dur <= 0:
        count_dur = total_dur

    img  = Image.fromarray(frame).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_big   = _load_font(200)
    font_label = _load_font(70)
    font_next  = _load_font(48)

    # Countdown uses count_dur so it starts at exactly e.g. 15, not 16 or 17
    secs_left = max(0, int(math.floor(count_dur - t)))
    timer_str = str(secs_left)

    # Colour changes as rest runs out
    if secs_left > count_dur * 0.5:
        color = (255, 220, 0, 255)
    elif secs_left > 3:
        color = (255, 140, 0, 255)
    else:
        color = (255, 50, 50, 255)

    # Large countdown number centered
    bb  = draw.textbbox((0,0), timer_str, font=font_big)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx  = (W - tw) // 2
    ty  = (H - th) // 2 - 30
    for dx,dy in [(-5,-5),(5,-5),(-5,5),(5,5)]:
        draw.text((tx+dx, ty+dy), timer_str, font=font_big, fill=(0,0,0,255))
    draw.text((tx, ty), timer_str, font=font_big, fill=color)

    # "REST" above number
    rest_lbl = "REST"
    rl_bb    = draw.textbbox((0,0), rest_lbl, font=font_label)
    rx       = (W - (rl_bb[2]-rl_bb[0])) // 2
    ry       = ty - (rl_bb[3]-rl_bb[1]) - 20
    draw.text((rx, ry), rest_lbl, font=font_label, fill=(255,255,255,200))

    # "GET READY!" when last 3 seconds
    if secs_left <= 3:
        gr_lbl  = "GET READY!"
        gr_font = _load_font(80)
        gr_bb   = draw.textbbox((0,0), gr_lbl, font=gr_font)
        gx      = (W - (gr_bb[2]-gr_bb[0])) // 2
        gy      = ty + th + 20
        draw.text((gx, gy), gr_lbl, font=gr_font, fill=(255,80,80,255))

    # Progress bar — depleting red bar, based on count_dur
    remain   = min(1.0, (count_dur - t) / count_dur) if count_dur > 0 else 0
    prog_bar = Image.new("RGBA", (W, H), (0,0,0,0))
    pb_draw  = ImageDraw.Draw(prog_bar)
    pb_draw.rectangle([0, H-10, W, H], fill=(60,0,0,200))
    pb_draw.rectangle([0, H-10, int(W*remain), H], fill=(220,60,60,255))
    img = Image.alpha_composite(img, prog_bar)

    return np.array(img.convert("RGB"))


# ── Clip helpers ──────────────────────────────────────────

def _fit_clip(clip):
    tw, th = OUTPUT_SIZE
    if clip.w / clip.h > tw / th:
        clip = clip.resize(height=th)
    else:
        clip = clip.resize(width=tw)
    return clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=tw, height=th)


def _clean_name(filename: str) -> str:
    name  = filename.replace(".mp4", "")
    parts = name.split("_")
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    return " ".join(parts).replace("-", " ").title()


# ── Main ─────────────────────────────────────────────────

def create_video(
    folder: str,
    clips_folder: str,
    enriched_segments: list,
    music_file,
    clip_files: list = None,
    fps: int = FPS,
) -> str:
    os.makedirs(folder, exist_ok=True)

    vid_segments   = []
    audio_segments = []

    for seg in enriched_segments:
        stype      = seg["type"]
        audio_dur  = seg["audio_dur"]
        audio_path = seg.get("audio_path")

        if stype == "exercise":
            clip_dur = float(seg.get("clip_duration") or audio_dur)
            vid_dur  = max(clip_dur, audio_dur + AUDIO_PAD_SECS)
        elif stype == "rest":
            rest_dur = float(seg.get("rest_duration") or audio_dur)
            vid_dur  = max(rest_dur, audio_dur + AUDIO_PAD_SECS)
        else:
            vid_dur = audio_dur + AUDIO_PAD_SECS

        # ── Audio ─────────────────────────────────────
        if audio_path and os.path.exists(audio_path):
            a = AudioFileClip(audio_path)
            a = a.subclip(0, min(a.duration, vid_dur))
            if a.duration < vid_dur - 0.05:
                from moviepy.audio.AudioClip import AudioClip
                sil = AudioClip(lambda t: 0, duration=vid_dur - a.duration)
                sil.fps = 44100
                a = concatenate_audioclips([a, sil])
        else:
            from moviepy.audio.AudioClip import AudioClip
            a = AudioClip(lambda t: 0, duration=vid_dur)
            a.fps = 44100
        audio_segments.append(a)

        # ── Video ─────────────────────────────────────
        if stype == "intro":
            print(f"  [intro   ]  voice={audio_dur:.1f}s  total={vid_dur:.1f}s")
            vid_segments.append(_make_intro_card(vid_dur))

        elif stype == "exercise":
            clip_file = seg.get("file")
            if not clip_file:
                vid_segments.append(_make_rest_card(vid_dur))
                continue

            path = os.path.join(clips_folder, clip_file)
            if not os.path.exists(path):
                print(f"  WARNING: missing {path}")
                vid_segments.append(_make_rest_card(vid_dur))
                continue

            name    = seg.get("exercise") or _clean_name(clip_file)
            caption = name.upper()
            cd      = seg.get("clip_duration", vid_dur)
            print(f"  [exercise]  {name:<20s}  clip={cd}s  voice={audio_dur:.1f}s  total={vid_dur:.1f}s")

            raw = VideoFileClip(path)
            if raw.duration < vid_dur:
                loops = int(vid_dur / raw.duration) + 2
                raw   = concatenate_videoclips([raw] * loops)
            raw = raw.subclip(0, vid_dur)
            raw = _fit_clip(raw)

            # Burn caption + countdown — count_dur = EXACT user input (e.g. 10s)
            # vid_dur may be longer due to voice padding, but timer shows user's value
            labeled = raw.fl(
                lambda gf, t, cap=caption, dur=vid_dur, count=float(cd):
                    _burn_exercise_frame(gf(t), cap, t, dur, count),
                apply_to=["mask"]
            )
            vid_segments.append(labeled)

        elif stype == "rest":
            rd = seg.get("rest_duration", vid_dur)
            print(f"  [rest    ]  rest={rd}s  voice={audio_dur:.1f}s  total={vid_dur:.1f}s")
            rest_np  = _make_rest_card_np()
            rest_img = ImageClip(rest_np).set_duration(vid_dur).set_fps(FPS)
            # count = EXACT user rest seconds; vid_dur may be slightly longer
            rest_cd  = rest_img.fl(
                lambda gf, t, dur=vid_dur, count=float(rd):
                    _burn_rest_frame(gf(t), t, dur, count),
                apply_to=["mask"]
            )
            vid_segments.append(rest_cd)

        elif stype == "outro":
            print(f"  [outro   ]  voice={audio_dur:.1f}s  total={vid_dur:.1f}s")
            vid_segments.append(_make_outro_card(vid_dur))

        else:
            vid_segments.append(_make_rest_card(vid_dur))

    if not vid_segments:
        print("ERROR: no segments.")
        return ""

    print("\n  Concatenating ...")
    final_video = concatenate_videoclips(vid_segments, method="compose")
    final_voice = concatenate_audioclips(audio_segments)

    sync_dur    = min(final_video.duration, final_voice.duration)
    final_video = final_video.subclip(0, sync_dur)
    final_voice = final_voice.subclip(0, sync_dur)
    print(f"  Duration: {sync_dur:.1f}s  ({sync_dur/60:.1f} min)")

    audio_tracks = [final_voice]
    if music_file and os.path.exists(music_file):
        music = AudioFileClip(music_file).volumex(0.13)
        if music.duration < sync_dur:
            loops = int(sync_dur / music.duration) + 2
            music = concatenate_audioclips([music] * loops)
        music = music.subclip(0, sync_dur)
        audio_tracks.append(music)
        print("  Music mixed in")

    final_video = final_video.set_audio(CompositeAudioClip(audio_tracks))

    output_file = os.path.join(folder, f"fatburn_{int(time.time())}.mp4")
    print(f"  Exporting -> {output_file}")
    final_video.write_videofile(
        output_file, fps=fps, codec="libx264",
        audio_codec="aac", threads=4, preset="fast", logger=None,
    )
    print(f"Video saved: {output_file}")
    return output_file