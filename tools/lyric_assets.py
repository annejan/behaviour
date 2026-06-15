#!/usr/bin/env python3
"""Precompute lyric sprite shapes using the authentic C64 char ROM (crisp 8x8).
8px hires font => 3 chars per 24px sprite, 8 sprites = 24-char white row.
Engine is a pure memcpy (192 bytes/line, 24/sprite -> block+21).

Outputs out/lyric_spr.bin (N*192), out/lyric_onset.bin (N*2 LE frames),
        out/lyric_preview.png. Prints NLINES for the engine .const.
"""
import json, os
import numpy as np
from PIL import Image

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs('out',exist_ok=True)
CHARGEN="/home/annejan/.local/share/vice/C64/chargen-901225-01.bin"
ROM=open(CHARGEN,'rb').read()

# char -> C64 screen code (uppercase charset, glyph index = screen code)
def sc(ch):
    if ch==' ': return 32
    if 'A'<=ch<='Z': return ord(ch)-64           # A=1..Z=26
    if '0'<=ch<='9': return ord(ch)-48+48         # 0=48..9=57
    return {',':44,"'":39,'.':46,'!':33,'?':63,'-':45,'(':40,')':41}.get(ch,32)

def glyph(ch):
    s=sc(ch); return ROM[s*8:s*8+8]

def line_shapes(text):
    text=text.upper()[:24]
    codes=[c for c in text]+[' ']*(24-len(text))
    out=bytearray()
    for s in range(8):                 # 8 sprites
        for r in range(8):             # 8 rows
            for c in range(3):         # 3 chars per sprite
                out.append(glyph(codes[s*3+c])[r])
    return out                          # 192 bytes

def main():
    d=json.load(open('lyrics.json'))['lines']
    spr=bytearray(); onset=bytearray()
    for t,txt in d:
        spr+=line_shapes(txt)
        fr=int(round(t*50)); onset+=bytes([fr&0xff,(fr>>8)&0xff])
    open('out/lyric_spr.bin','wb').write(spr)
    open('out/lyric_onset.bin','wb').write(onset)
    open('src/lyric_n.asm','w').write(f".const LYRIC_NLINES = {len(d)}\n")
    print(f"NLINES={len(d)} spr={len(spr)}B onset={len(onset)}B (C64 chargen 8px)")

    # preview: unpack a few lines' shapes (rows 0-7) back to pixels
    def unpack(sh):
        im=np.zeros((8,192),np.uint8)
        for s in range(8):
            for r in range(8):
                for c in range(3):
                    v=sh[s*24+r*3+c]
                    for bit in range(8):
                        if v&(1<<(7-bit)): im[r,s*24+c*8+bit]=255
        return im
    samples=[(i,l[1]) for i,l in enumerate(d) if l[1]][:8]
    canvas=Image.new('RGB',(192*2,len(samples)*(8+3)*2),(0,0,40))
    for i,(li,txt) in enumerate(samples):
        im=unpack(spr[li*192:li*192+192])
        rgb=np.zeros((8,192,3),np.uint8); rgb[im>0]=(255,255,255)
        canvas.paste(Image.fromarray(rgb).resize((192*2,16),Image.NEAREST),(0,i*22))
    canvas.save('out/lyric_preview.png'); print("preview -> out/lyric_preview.png")

if __name__=='__main__': main()
