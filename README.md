# human — Björk "Human Behaviour" C64 demo

A single-sided C64 demo (Spindle 3.1 / pefchain): a SID cover of Björk's
*Human Behaviour* plays while 16 koala images — frames lifted from the music
video and dithered to the C64 palette — are streamed off disk and cut on the
song's structural transitions.

**Status (v0.1.0):** music + images working. One disk, one playthrough,
50 Hz locked, load-on-the-go (double-buffered across two VIC banks). Lyric
sprites planned next.

## Layout

| path | what |
|------|------|
| `human_behaviour.sid` | the tune (PSID, init $1000 / play $1003, 4:55) |
| `tools/photo_to_koala.py` | photo → multicolor koala (.kla), FS dither, black bg |
| `tools/segment.py` | Foote-style novelty → song section boundaries → `segments.json` |
| `tools/extract_segments.py` | one video frame per section → koala |
| `tools/gen_parts.py` | generates the 16 Spindle parts + `build_demo.sh` + `script_demo` |
| `build_demo.sh` | assembles parts (KickAss) + links the d64 (pefchain) |
| `koala/imgNN.kla` | the 16 images |
| `out/human.d64` | the demo (build artifact) |

## Build

Needs KickAssembler + Spindle 3.1 binaries (reused from `../x2026`), Python 3
with Pillow/NumPy/SciPy, ffmpeg, and the source `.webm` (not redistributed).

```sh
python3 tools/segment.py /tmp/hb.wav 255.05 295.5 --n 16 --out segments.json
python3 tools/extract_segments.py     # frames → koala
python3 tools/gen_parts.py            # → src/pNN*.asm, script_demo, build_demo.sh
./build_demo.sh                       # → out/human.d64
```

## How it works

- **Music** rides resident via Spindle's `--music` (PSID header stripped,
  loaded at $1000); part 0 installs the play routine with the `M` tag so
  pefchain calls it every frame — including during load gaps, so the SID
  never drops.
- **Images** are multicolor bitmaps. Even parts use VIC bank 1
  ($4000 screen / $6000 bitmap), odd parts bank 2 ($8000 / $a000). pefchain
  preloads the next image into the *other* bank while the current one shows,
  then a part's `setup` flips the bank (via `$dd02`, since Spindle owns
  `$dd00`) and copies its colour RAM to `$d800`.
- **Timing**: each part counts down its section length (a 16-bit frame
  timer) and raises an advance flag; the pefchain script waits on it, so
  cuts land on the detected song transitions.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
