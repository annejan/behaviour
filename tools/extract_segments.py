#!/usr/bin/env python3
"""Pick the most striking video frame per song segment, convert to koala.

For each segment we scan K candidate frames across the segment's video window
and score them by colorfulness (Hasler-Süsstrunk) + detail (Laplacian
variance) + a brightness gate (penalise near-black filler, avoid blow-out).
The winner is the "epic" frame; cuts still land on the song transitions.
"""
import json, os, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy.ndimage import laplace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
VID = "björk ： human behaviour (HD) [p0mRIhK9seg].webm"
K = 12                      # candidate frames per segment
segs = json.load(open('segments.json'))
SONG = segs['song_len']; VIDLEN = segs['video_len']; segs = segs['segments']
os.makedirs('frames', exist_ok=True)

def grab(t, path, w=320, h=200):
    subprocess.run(["ffmpeg","-y","-ss",f"{t:.2f}","-i",VID,"-frames:v","1",
                    "-vf",f"crop=ih*4/3:ih,scale={w}:{h}",path],
                   check=True, stderr=subprocess.DEVNULL)

def score(path):
    im = np.asarray(Image.open(path).convert('RGB'), dtype=np.float64)
    R,G,B = im[...,0],im[...,1],im[...,2]
    rg = R-G; yb = 0.5*(R+G)-B
    colorful = np.sqrt(rg.std()**2+yb.std()**2) + 0.3*np.sqrt(rg.mean()**2+yb.mean()**2)
    lum = 0.299*R+0.587*G+0.114*B
    detail = laplace(lum).var()
    m = lum.mean()/255.0
    # brightness gate: peak ~0.42, hard penalty when very dark or blown out
    bright = max(0.0, 1.0 - abs(m-0.42)/0.42)
    if m < 0.10: bright *= 0.2          # near-black filler
    return colorful*1.0 + np.sqrt(detail)*2.0 + bright*40.0

for s in segs:
    i = s['idx']
    vt0 = max(1.0, s['start']/SONG*VIDLEN)
    vt1 = min(VIDLEN-1, s['end']/SONG*VIDLEN)
    if vt1-vt0 < 1.5: vt1 = min(VIDLEN-1, vt0+1.5)
    cand = np.linspace(vt0, vt1, K)
    best_t, best_s = cand[0], -1e9
    with tempfile.TemporaryDirectory() as td:
        for t in cand:
            p = os.path.join(td, "c.png"); grab(t, p, 160, 100)
            sc = score(p)
            if sc > best_s: best_s, best_t = sc, t
    fp = f"frames/f{i:02d}.png"; grab(best_t, fp)
    subprocess.run(["python3","tools/photo_to_koala.py",fp,f"koala/img{i:02d}.kla",
                    "--preview",f"koala/img{i:02d}.png","--bg","0",
                    "--contrast","1.15","--sat","1.25"], check=True)
    print(f"#{i:2d} seg {s['start']:.0f}-{s['end']:.0f}s -> best frame @{best_t:.1f}s (score {best_s:.0f})")
print("done")
