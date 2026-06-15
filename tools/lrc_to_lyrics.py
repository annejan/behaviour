#!/usr/bin/env python3
"""Convert a studio-timed .lrc into lyrics.json on the SID timeline.

The SID (295.5s, GoatTracker) runs at a different tempo than the studio
recording the LRC is timed to. Anchor: first vocal LRC 7.33s <-> SID 12.1s
(verified in VICE); scale the rest by the vocal-span ratio. Clean
parentheticals/gibberish, uppercase, split >24-char lines, dedup consecutive
chorus repeats, blank-line markers at instrumental gaps, cap to <=28 lines.
"""
import re, json, sys

LRC = "/home/annejan/Downloads/Human Behaviour.lrc"
V0_LRC, S0_SID, RATIO = 7.33, 12.1, 1.169
MAXC, MAXLINES = 24, 28

def m2s(t): return S0_SID + (t - V0_LRC) * RATIO

raw=[]
for ln in open(LRC, encoding='utf-8'):
    m=re.match(r'\[(\d+):(\d+\.\d+)\]\s*(.*)', ln)
    if not m: continue
    t=int(m.group(1))*60+float(m.group(2)); txt=m.group(3).strip()
    raw.append((t, txt))

def clean(s):
    s=re.sub(r'\(.*?\)','',s)               # drop parentheticals
    s=s.replace(',', '').strip().upper()
    s=re.sub(r'\s+',' ',s)
    # squeeze the triple-"definitely" mouthful
    s=s.replace('DEFINITELY DEFINITELY DEFINITELY NO LOGIC','DEFINITELY NO LOGIC')
    s=s.replace("THERE'S DEFINITELY NO LOGIC",'DEFINITELY NO LOGIC')
    s=s.replace('BUT OH TO GET INVOLVED IN THE EXCHANGE','TO GET INVOLVED IN')
    s=s.replace('BE READY BE READY','BE READY')
    s=s.replace('YET SO YET SO','YET SO')
    s=s.replace('TERRIBLY TERRIBLY TERRIBLY','TERRIBLY')
    s=s.replace('EVER SO EVER SO','EVER SO')
    return s.strip()

def split24(s):
    if len(s)<=MAXC: return [s]
    cut=s.rfind(' ',0,MAXC+1)
    if cut<=0: return [s[:MAXC]]
    return [s[:cut], s[cut+1:]]

# build (sid_time, text|"") entries
entries=[]
for t,txt in raw:
    st=round(m2s(t),1)
    if txt=='' or txt=='(Gibberish)':
        entries.append((st,""))               # instrumental gap -> clear
        continue
    c=clean(txt)
    if not c:
        entries.append((st,"")); continue
    parts=split24(c)
    entries.append((st,parts[0]))
    if len(parts)>1:
        # second half a bit later
        entries.append((round(st+2.6,1),parts[1]))

# dedup consecutive identical text (collapse chorus repeats), drop dup blanks
ded=[]
for st,txt in entries:
    if ded and ded[-1][1]==txt: continue
    ded.append((st,txt))

# ensure strictly increasing times
fix=[]
for st,txt in ded:
    if fix and st<=fix[-1][0]: st=round(fix[-1][0]+0.3,1)
    fix.append((st,txt))

# prepend intro blank
if fix[0][0]>0.5: fix=[(0.0,"")]+fix

# cap to MAXLINES: drop interior blank markers first, then nearest-merge
while len(fix)>MAXLINES:
    # drop a blank that is adjacent to another entry (least info)
    bi=[i for i,(_,t) in enumerate(fix) if t=="" and 0<i<len(fix)-1]
    if bi: del fix[bi[len(bi)//2]]
    else:
        # drop the shortest text line
        j=min(range(1,len(fix)),key=lambda i:len(fix[i][1]) or 99)
        del fix[j]

out={"comment":"auto from Human Behaviour.lrc, mapped to SID timeline",
     "lines":[[t,txt] for t,txt in fix]}
json.dump(out,open('/home/annejan/Projects/human/lyrics.json','w'),indent=1)
print(f"{len(fix)} lines, max {max(len(t) for _,t in fix)} chars")
for t,txt in fix: print(f"  {t:6.1f}  {txt}")
