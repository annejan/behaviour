#!/usr/bin/env python3
"""Build lyrics.json on the SID timeline from the user's full interpreted
lyric set (gibberish parts spelled out), timestamped to the LRC.

Anchor: first vocal LRC 7.33s <-> SID 12.1s; scale by vocal-span ratio ~1.169.
Clean/abbreviate to <=24 chars, split where needed, dedup consecutive repeats,
blank markers at instrumental gaps. No hard line cap (engine uses a 2nd sprite
region at $c000), but kept under ~44.
"""
import json

V0_LRC, S0_SID, RATIO = 7.33, 12.1, 1.169
MAXC = 24
def m2s(t): return round(S0_SID + (t - V0_LRC) * RATIO, 1)

# (LRC time, line) — user's interpreted lyrics incl. gibberish readings.
LINES = [
 (7.33,  "If you ever get close to a human"),
 (13.13, "And human behaviour"),
 (18.02, "Be ready to get confused"),
 (21.98, "And me and my hereafter"),
 (27.02, "There's definitely no logic"),
 (30.72, "To human behaviour"),
 (35.23, "But yet so irresistible"),
 (39.49, "And me and my fear cannot"),
 (45.58, "And there is no map, uncertain"),
 (55.03, ""),
 (61.35, "They're terribly moody"),
 (65.54, "Of human behaviour"),
 (70.31, "Then all of a sudden turn happy"),
 (74.26, "And they and my hereafter"),
 (79.00, "But oh to get involved in the exchange"),
 (83.28, "Of human emotions"),
 (87.77, "Is ever so satisfying"),
 (91.99, "And they and my hero"),
 (98.04, "And there is no map, uncertain"),
 (107.81,""),
 (124.43,"Human behaviour, human behaviour"),
 (142.45,"And there is no map"),
 (146.86,"And a compass wouldn't help at all"),
 (151.92,"Uncertain"),
 (160.43,"Human behaviour"),
 (175.29,"There's definitely no logic"),
 (179.94,"Human, human, human"),
 (192.0, ""),
 (227.70,"There's definitely no logic"),
 (232.63,"Human, human, human, human"),
 (248.5, ""),
]

ABBR = {
 "THERE'S DEFINITELY NO LOGIC":"DEFINITELY NO LOGIC",
 "AND ME AND MY HEREAFTER":"ME AND MY HEREAFTER",
 "AND ME AND MY FEAR CANNOT":"ME AND MY FEAR CANNOT",
 "AND THEY AND MY HEREAFTER":"THEY AND MY HEREAFTER",
 "AND THEY AND MY HERO":"THEY AND MY HERO",
 "BUT OH TO GET INVOLVED IN THE EXCHANGE":"TO GET INVOLVED IN THE",
 "HUMAN BEHAVIOUR HUMAN BEHAVIOUR":"HUMAN BEHAVIOUR",
}
def clean(s):
    s=s.replace(',','').upper().strip()
    s=' '.join(s.split())
    return ABBR.get(s,s)
def split24(s):
    if len(s)<=MAXC: return [s]
    cut=s.rfind(' ',0,MAXC+1)
    return [s[:cut],s[cut+1:]] if cut>0 else [s[:MAXC]]

ent=[]
for t,txt in LINES:
    st=m2s(t)
    if not txt: ent.append((st,"")); continue
    parts=split24(clean(txt))
    ent.append((st,parts[0]))
    if len(parts)>1: ent.append((round(st+2.6,1),parts[1]))

ded=[]
for st,txt in ent:
    if ded and ded[-1][1]==txt: continue
    ded.append((st,txt))
fix=[]
for st,txt in ded:
    if fix and st<=fix[-1][0]: st=round(fix[-1][0]+0.3,1)
    fix.append((st,txt))
if fix[0][0]>0.5: fix=[(0.0,"")]+fix

json.dump({"comment":"full interpreted lyrics, LRC->SID timeline",
           "lines":[[t,x] for t,x in fix]},
          open('/home/annejan/Projects/human/lyrics.json','w'),indent=1)
print(f"{len(fix)} lines, max {max(len(x) for _,x in fix)} chars")
for t,x in fix: print(f"  {t:6.1f}  {x}")
