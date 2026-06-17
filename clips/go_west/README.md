# go_west — Pet Shop Boys, *Go West*

1993 anthem, Soviet-kitsch video (marching uniformed men, red flags, the
Statue of Liberty, CGI cityscape). Lots of iconic imagery survives the dither.

| | |
|---|---|
| song | Pet Shop Boys — Go West (4:20 SID cover) |
| images | 20 koala, video-curated (one agent per slot over 8 candidates) |
| lyrics | 80 lines / 48 unique |
| pulse | `faderamp [0,2,10,7,1]` — black→red→yellow→white (suits the red-flag theme) |
| status | **done** — builds to `out/go_west.d64`, preview `~/Videos/go_west_c64.mp4` |

```sh
tools/use_clip.sh go_west
python3 tools/lyric_assets.py && python3 tools/gen_parts.py && ./build_demo.sh
python3 tools/render_demo.py
```

Notes:
- 48 unique lyric lines (1152B) — fits the UNIQ window ($3300–$37ff, ~53 max).
- SID cover 4:20 (`song_len` 260) under a 4:51 video (`video_len` 291.3); the
  koala timeline maps song→video by ratio. `ratio` 1.0 — the LRC is the official
  lyric affine-mapped onto the SID render's vocal.
- Sources from Jantje (no `sid_build.cmd` recipe was dropped for this one).
