#!/bin/bash
# Activate a clip: point the repo-root working files at clips/<name>/.
# Everything per-clip lives in clips/<name>/ (config + curated json + koala +
# source media). The config-driven tools all read the repo root, so switching
# clips just repoints these symlinks; edits write through to clips/<name>/.
#   tools/use_clip.sh bjork | saturday | freed
set -e
cd "$(dirname "$0")/.."
name="$1"
dir="clips/$name"
[ -d "$dir" ] || { echo "no such clip: $dir" >&2; echo "available:" >&2; ls clips/ >&2; exit 1; }

# clear stale root working symlinks (never touch real files)
for f in clip.json segments.json lyrics.json picks.json koala \
         *.sid *.sng *.lrc *.mid *.mp3 *.webm; do
    [ -L "$f" ] && rm -f "$f"
done

# config + curated assets. Always symlink the json (even if not generated yet)
# so a fresh clip's segment.py / lrc_to_lyrics.py output writes *through* into
# clips/<name>/ instead of stranding a real file at the (gitignored) root.
for f in clip.json segments.json lyrics.json picks.json; do
    ln -sfn "$dir/$f" "$f"
done
mkdir -p "$dir/koala"
ln -sfn "$dir/koala" koala

# source media (sid/sng/lrc/mid/mp3/webm) — symlinked into root by basename
shopt -s nullglob
for f in "$dir"/*.sid "$dir"/*.sng "$dir"/*.lrc "$dir"/*.mid "$dir"/*.mp3 "$dir"/*.webm; do
    ln -sfn "$f" "$(basename "$f")"
done
shopt -u nullglob

echo "active clip: $name  ($(python3 -c "import json;c=json.load(open('clip.json'));print(c['title'],c['name'])"))"
