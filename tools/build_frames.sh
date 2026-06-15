#!/bin/bash
# Extract 16 frames from the Bjork webm, evenly across ~4..250s, center-crop
# 16:9 -> 4:3, scale 320x200, convert each to koala + preview.
set -eo pipefail
cd "$(dirname "$0")/.."
VID="björk ： human behaviour (HD) [p0mRIhK9seg].webm"
N=16
START=4
END=250
for i in $(seq 0 $((N-1))); do
    T=$(python3 -c "print(f'{$START + $i*($END-$START)/($N-1):.2f}')")
    idx=$(printf "%02d" "$i")
    ffmpeg -y -ss "$T" -i "$VID" -frames:v 1 \
        -vf "crop=ih*4/3:ih,scale=320:200" "frames/f$idx.png" 2>/dev/null
    python3 tools/photo_to_koala.py "frames/f$idx.png" "koala/img$idx.kla" \
        --preview "koala/img$idx.png" --contrast 1.12 --sat 1.2
done
# contact sheet
python3 - <<'EOF'
from PIL import Image
import glob
ps = sorted(glob.glob('koala/img*.png'))
cols, rows = 4, 4
w, h = 320, 200
sheet = Image.new('RGB', (cols*w, rows*h), (20,20,20))
for k, p in enumerate(ps):
    im = Image.open(p)
    sheet.paste(im, ((k%cols)*w, (k//cols)*h))
sheet.save('koala/contact.png')
print('contact sheet -> koala/contact.png', len(ps), 'images')
EOF
