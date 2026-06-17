# bjork — Björk, *Human Behaviour*

The first Alfred clip. A SID cover of Björk's *Human Behaviour* under 23 koala
frames lifted from Michel Gondry's video (the bear, the forest, the giant),
cut on the song's structural transitions, with the lyrics blitted as sprites.

| | |
|---|---|
| song | Björk — Human Behaviour (4:19) |
| images | 23 koala, video-curated |
| lyrics | 38 lines / 27 unique |
| pulse | `faderamp [6,4,14,3,1]` — bright blue→white (suits the night-blue scenes) |
| status | **done** — builds to `out/human_behaviour.d64`, preview `~/Videos/human_behaviour_c64.mp4` |

```sh
tools/use_clip.sh bjork
python3 tools/lyric_assets.py && python3 tools/gen_parts.py && ./build_demo.sh
python3 tools/render_demo.py
```

Sources here: `human_behaviour.sid` / `.sng` / `.lrc` (the `.mp3` + `.webm` are
copyrighted, kept on disk but not committed). The lyrics are hand-curated in
`lyrics.json` (Björk's part-gibberish vocal spelled out), so `clip.json`'s
`lrc` is empty and `lrc_to_lyrics.py` isn't run for this clip.
