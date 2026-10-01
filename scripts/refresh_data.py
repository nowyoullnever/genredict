#!/usr/bin/env python3
"""Fetch, normalize, diff and validate the mb-rym-hierarchy source into static JSON."""
from __future__ import annotations
import hashlib,json,re,sys,unicodedata,urllib.request
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"public"/"data"
SOURCE="https://raw.githubusercontent.com/FlakyBlueJay/mb-rym-hierarchy/main/RateYourMusic%20Hierarchy.txt"
def slug(text):
 s=unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower();return re.sub(r"^-+|-+$","",re.sub(r"[^a-z0-9]+","-",s)) or "item"
def kind(section,tag):
 if section=="Scenes & Movements": return "scene_movement"
 if section=="Descriptors" or tag in {"mood","descriptor"}: return "descriptor"
 if section=="Genres" or tag=="genre": return "genre"
 return "meta"
def parse(raw):
 nodes={};edges=set();stacks=[];used={}
 for line in raw.splitlines():
  if not line.strip():continue
  spaces=len(line)-len(line.lstrip(" "));level=spaces//4;value=line.strip();name,sep,tag=value.partition("::")
  if level==0: section=name;stacks=[None];continue
  typ=kind(section,tag);base=f"{typ}:{slug(name)}";n=base
  if n in nodes and nodes[n]["name"]!=name:
   n=f"{base}-{hashlib.sha1(name.encode()).hexdigest()[:8]}"
  if n not in nodes:nodes[n]={"id":n,"name":name,"slug":slug(name),"type":typ,"parents":[],"children":[],"depth":level-1,"rymUrl":f"https://rateyourmusic.com/genre/{slug(name)}/" if typ=="genre" and re.fullmatch(r"[A-Za-z0-9 .&'/-]+",name) else None,"sourcePath":[],"aliases":[],"dateAdded":None,"lastChanged":None}
  stacks=stacks[:level];parent=stacks[-1] if stacks else None
  if parent and parent!=n:edges.add((parent,n))
  stacks.append(n)
 for a,b in sorted(edges):nodes[a]["children"].append(b);nodes[b]["parents"].append(a)
 return {"nodes":sorted(nodes.values(),key=lambda n:n["name"].casefold()),"edges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(edges)]}
def validate(graph):
 ids={n["id"] for n in graph["nodes"]}; pairs=set()
 assert len(ids)>100,"unexpectedly small taxonomy" 
 for n in graph["nodes"]: assert n["name"].strip() and n["id"].strip()
 for e in graph["edges"]:
  assert e["source"] in ids and e["target"] in ids and (e["source"],e["target"]) not in pairs;pairs.add((e["source"],e["target"]))
def diff(old,new):
 om={n["id"]:n for n in old.get("nodes",[])};nm={n["id"]:n for n in new["nodes"]};oe={(e["source"],e["target"]) for e in old.get("edges",[])};ne={(e["source"],e["target"]) for e in new["edges"]}
 return {"generatedAt":datetime.now(timezone.utc).isoformat(),"addedNodes":sorted(set(nm)-set(om)),"removedNodes":sorted(set(om)-set(nm)),"addedEdges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(ne-oe)],"removedEdges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(oe-ne)],"typeChanges":[{"id":i,"from":om[i]["type"],"to":nm[i]["type"]} for i in set(om)&set(nm) if om[i]["type"]!=nm[i]["type"]]}
def main():
 DATA.mkdir(parents=True,exist_ok=True);raw=urllib.request.urlopen(SOURCE,timeout=60).read().decode("utf-8");graph=parse(raw);validate(graph)
 old=json.loads((DATA/"graph.json").read_text()) if (DATA/"graph.json").exists() else {};changes=diff(old,graph);now=datetime.now(timezone.utc).isoformat();counts=Counter(n["type"] for n in graph["nodes"])
 (DATA/"graph.json").write_text(json.dumps(graph,ensure_ascii=False,separators=(",",":")))
 (DATA/"dictionary.json").write_text(json.dumps(graph["nodes"],ensure_ascii=False,separators=(",",":")))
 (DATA/"changes.json").write_text(json.dumps(changes,ensure_ascii=False,separators=(",",":")))
 meta={"sourceRepository":"FlakyBlueJay/mb-rym-hierarchy","sourceUrl":SOURCE,"sourceHash":hashlib.sha256(raw.encode()).hexdigest(),"sourceLastUpdated":now,"atlasSynchronized":now,"nodeCount":len(graph["nodes"]),"edgeCount":len(graph["edges"]),"countsByType":counts}
 (DATA/"source-meta.json").write_text(json.dumps(meta,ensure_ascii=False,separators=(",",":")))
 print(f"validated {len(graph['nodes'])} nodes / {len(graph['edges'])} edges")
if __name__=="__main__":main()