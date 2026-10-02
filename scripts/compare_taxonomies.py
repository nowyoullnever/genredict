#!/usr/bin/env python3
"""Compare source-independent curation keys without automatic semantic merging."""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"public"/"data"
def rough(value):return re.sub(r"[^a-z0-9]+","",unicodedata.normalize("NFKD",value).encode("ascii","ignore").decode().lower())
def main():
 rym=json.loads((DATA/"rym"/"graph.json").read_text())["nodes"];discogs=json.loads((DATA/"discogs"/"graph.json").read_text())["nodes"]
 rmap={};dmap={}
 for n in rym:rmap.setdefault(n["curationKey"],[]).append(n)
 for n in discogs:dmap.setdefault(n["curationKey"],[]).append(n)
 shared=[{"curationKey":key,"rym":rmap[key][0]["id"],"discogs":dmap[key][0]["id"]} for key in sorted(set(rmap)&set(dmap))]
 ronly=sorted(set(rmap)-set(dmap));donly=sorted(set(dmap)-set(rmap));drough={}
 for key in donly:drough.setdefault(rough(key),[]).append(key)
 possible=[]
 for key in ronly:
  for candidate in drough.get(rough(key),[]):possible.append({"rym":key,"discogs":candidate})
 out={"shared":shared,"rymOnly":ronly,"discogsOnly":donly,"possibleAliases":possible}
 (DATA/"taxonomy-overlap.json").write_text(json.dumps(out,ensure_ascii=False,separators=(",",":")))
 print(f"RYM items: {len(rmap)}; Discogs items: {len(dmap)}; Shared curation keys: {len(shared)}; RYM-only: {len(ronly)}; Discogs-only: {len(donly)}; Possible aliases: {len(possible)}")
if __name__=="__main__":main()