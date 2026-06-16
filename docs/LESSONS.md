# Lessons — hard-won gotchas building this demo

Non-obvious things that cost real time. Read before touching the engine,
the Spindle wiring, or the capture flow.

## Spindle / VIC

- **VIC bank: write `$dd02`, never `$dd00`.** Spindle's IRQ loader owns
  `$dd00` (IEC serial) and rewrites it constantly, so any bank bits you set
  there get clobbered → VIC reads the wrong bank (garbage). Select the bank
  via the DDR `$dd02`: `3d`=bank1 ($4000), `3e`=bank2 ($8000). (handbook 1.3)
- **`call_play` placeholder must be exactly 3 bytes.** `bit $0000` gets
  assembled by KickAss as the 2-byte zero-page `BIT`; pefchain patches the
  callmusic slot with a 3-byte `jsr PLAY`, so a 2-byte placeholder makes the
  patch clobber the next opcode → `$02 JAM` (CPU halt) at the first
  transition. Emit `.byte $2c,$00,$00` to lock it at 3 bytes.
- **No `'Z'` zero-page tag on the parts.** Every part legitimately reuses the
  same zp; declaring `'Z'` makes pefchain think consecutive parts conflict →
  it inserts blank fillers → a filler lands on the music page `$10` → fatal.
  Leave zp undeclared (loader only reserves `$f4-$f8`).
- **Alternate BOTH code page and VIC bank between consecutive parts**
  (even=$0800/bank1, odd=$0900/bank2). If consecutive parts share any page,
  pefchain can't double-buffer → blank fillers. One filler at the `--loop`
  point is normal and unavoidable.
- **`--music` keeps multiple files resident** until the next music loads
  (never, here). Used to keep SID + lyric engine + sprite data alive across
  all parts. `'I'` tags are belt-and-braces only.

## Koala converter

- A `.kla` is **10003 bytes**; the background byte is the **last** byte
  (offset 10002), NOT `$2711`/10001 (that's the last colour byte). Reading
  the wrong offset bakes a colour value into `$d021`.
- mkpef colour-data offset is **`$232a`** (9002 dec), not `$2342`.
- Dark video frames blow out to bright **cyan** if you pick the most-frequent
  colour as background (no dark-teal in the C64 palette). Force **black bg**.
- `INIT` the SID only on **part 0** (else every image transition restarts the
  tune).

## Lyric sprite engine

- 8 hires sprites = a **24-char** row (3 chars/sprite, 8px C64 charset). 4px
  squashed fonts are unreadable. Lines must be **<=24 chars**.
- Sprite shapes precomputed on host (`lyric_spr.bin`) → the 6502 engine is a
  pure memcpy. Shapes blitted to **both** VIC banks on a line change, plus
  re-blitted in each part's setup (the freshly-flipped bank has stale bytes).
- >28 lines overflow `$2a00`'s budget → 2nd region at **`$c000`** (engine
  picks by threshold; `lyric_assets.py` writes the count to `src/lyric_n.asm`).
- Timing from the `.lrc` is **studio-timed**, not SID-timed. Anchor first
  vocal (LRC 7.33s ↔ SID 12.1s) and scale by the vocal-span ratio (~1.169).

## VICE capture (the painful one)

- **x11grab can't read VICE's GL surface on Xvfb** (output is black). Offscreen
  capture via Xvfb is a dead end with this GTK/GL build.
- On the real display VICE **throttles rendering to ~1fps when its window is
  unfocused/occluded** → x11grab gets a near-static stream. **Focus + raise
  the window** (`wmctrl -i -a <id>` + `-b remove,below`) → it renders 50fps
  and x11grab works. Confirm with a 4s test (≈200 frames).
- Capture region = window `x,y+27` (skip menubar), `720x544` (skip status bar).
  Re-fetch geometry every run — the window moves.
- **Audio: capture the monitor of the sink VICE actually outputs to.** It
  follows the *default* sink, which changes when the user switches output
  device (e.g. to Bluetooth → `bluez_output.*.monitor`). Find it via
  `pactl list sink-inputs` (VICE's `Sink:` id) → that sink's `.monitor`.
  A wrong/empty monitor gives a silent track (`-91 dB`). Any other audio
  playing to that sink **bleeds into the recording** — silence everything else.
- If audio came out silent, you can re-mux the clean rendered SID wav
  (`sidplayfp -w`) with `-itsoffset <demo-start-s> -stream_loop -1` instead of
  recapturing (alignment = the boot+load lead, ~13s).
- **To capture the boot/load/run:** start `ffmpeg` first, then fire
  `vice_autostart` ~1.5s later. For a clean power-on boot screen, hard-reset
  via MCP (`vice_machine_reset` mode `hard`) — it survived here, though the
  skill warns it can crash the mcp build (relaunch if so).
- **Launching VICE headless is flaky.** `run_in_background` is sandboxed
  without X (instant exit); pass `DISPLAY=:0 XAUTHORITY=...` and just retry —
  it's intermittent.

## Offline render fallback

`render_demo.py` composites the koala frames + a faithful replica of the
lyric-sprite animation + the SID wav into a clean 50fps MP4 in ~26s — no
capture flakiness. Pixel-faithful minus the authentic VICE border/scanlines.
