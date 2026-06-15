#!/usr/bin/env python3
"""Extract one video frame per segment (at segment.video_t), convert to koala.
Frame cuts land on song transitions; imagery follows the video proportionally.
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
VID = "björk ： human behaviour (HD) [p0mRIhK9seg].webm"
segs = json.load(open('segments.json'))['segments']
os.makedirs('frames', exist_ok=True)
for s in segs:
    i = s['idx']; t = s['video_t']
    fp = f"frames/f{i:02d}.png"
    subprocess.run(["ffmpeg","-y","-ss",str(t),"-i",VID,"-frames:v","1",
                    "-vf","crop=ih*4/3:ih,scale=320:200",fp],
                   check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["python3","tools/photo_to_koala.py",fp,f"koala/img{i:02d}.kla",
                    "--preview",f"koala/img{i:02d}.png","--bg","0",
                    "--contrast","1.15","--sat","1.25"], check=True)
print(f"extracted+converted {len(segs)} segment frames")
