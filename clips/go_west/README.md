# go_west — Pet Shop Boys, *Go West*

1993 anthem, Soviet-kitsch video (marching uniformed men, red flags, the
Statue of Liberty, CGI cityscape). Lots of iconic imagery survives the dither.

| | |
|---|---|
| song | Pet Shop Boys — Go West (4:20 SID cover) |
| images | 20 koala, video-curated (one agent per slot over 8 candidates) |
| lyrics | 121 lines / 60 unique (57 choir) |
| pulse | lead `faderamp [0,6,6,14,14]` = **blue** (democracy); choir `faderamp2 [0,2,2,10,10]` = **red** (communism) |
| status | **done** — builds to `out/go_west.d64`, preview `~/Videos/go_west_c64.mp4` |

```sh
tools/use_clip.sh go_west
python3 tools/lyric_assets.py && python3 tools/gen_parts.py && ./build_demo.sh
python3 tools/render_demo.py
```

Notes:
- **Call-and-response colour.** The `(...)` lines in the LRC are the choir
  ("Together", "Go West", …). `clip.json` `keep_parens: true` keeps the words,
  and `lrc_to_lyrics.py` flags wholly-parenthetical lines as *choir* (a per-line
  style bit). The engine renders choir lines with `faderamp2` (red) and lead
  lines with `faderamp` (blue) — communism vs democracy, matching the video.
- `lrc_offset: -4.5` — the supplied LRC ran ~4.5 s late vs the SID render
  ("come on" at 0:32, first "Together" at 0:34). `ratio` 1.0.
- 60 unique lines / 121 total — needed the resident layout bump (UNIQ to $3aff,
  ORDER $3b00, ONSET $3c00, STYLE $3e00).
- Sources from Jantje (no `sid_build.cmd` recipe was dropped for this one).
