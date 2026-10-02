#!/usr/bin/env python3
"""Build the namespaced RYM taxonomy static dataset."""
from __future__ import annotations
import hashlib,json,re,unicodedata,urllib.request
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"public"/"data"; RYM=DATA/"rym"
SOURCE="https://raw.githubusercontent.com/FlakyBlueJay/mb-rym-hierarchy/main/RateYourMusic%20Hierarchy.txt"
def slug(text):
 s=unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower();return re.sub(r"^-+|-+$","",re.sub(r"[^a-z0-9]+","-",s)) or "item"
def curation_key(text): return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",text).strip().lower())
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
  if n in nodes and nodes[n]["name"]!=name:n=f"{base}-{hashlib.sha1(name.encode()).hexdigest()[:8]}"
  if n not in nodes:nodes[n]={"id":n,"name":name,"slug":slug(name),"type":typ,"parents":[],"children":[],"depth":level-1,"rymUrl":f"https://rateyourmusic.com/genre/{slug(name)}/" if typ=="genre" and re.fullmatch(r"[A-Za-z0-9 .&'/-]+",name) else None,"sourcePath":[],"aliases":[],"dateAdded":None,"lastChanged":None}
  stacks=stacks[:level];parent=stacks[-1] if stacks else None
  if parent and parent!=n:edges.add((parent,n))
  stacks.append(n)
 for a,b in sorted(edges):nodes[a]["children"].append(b);nodes[b]["parents"].append(a)
 return {"nodes":sorted(nodes.values(),key=lambda n:n["name"].casefold()),"edges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(edges)]}
def namespace(graph,aliases):
 used=set(); ids={}
 for n in graph["nodes"]:
  base=f"rym:{n['slug']}"; candidate=base
  if candidate in used: candidate=f"{base}--{n['type']}"
  suffix=2
  while candidate in used: candidate=f"{base}--{suffix}";suffix+=1
  used.add(candidate);ids[n["id"]]=candidate
 nodes=[]
 for old in graph["nodes"]:
  n=dict(old);n["id"]=ids[old["id"]];n["source"]="rym";n["parents"]=[ids[x] for x in old["parents"]];n["children"]=[ids[x] for x in old["children"]];n["externalUrl"]=old.get("rymUrl");n["curationKey"]=aliases.get(n["id"],curation_key(n["name"]));n.pop("rymUrl",None);nodes.append(n)
 return {"nodes":nodes,"edges":[{"source":ids[e["source"]],"target":ids[e["target"]],"relation":"parent"} for e in graph["edges"]]}
def validate(graph):
 ids={n["id"] for n in graph["nodes"]};pairs=set();assert len(ids)>2000,"unexpectedly small RYM taxonomy"
 for n in graph["nodes"]:assert n["id"].startswith("rym:") and n["source"]=="rym" and n["curationKey"]
 for e in graph["edges"]:assert e["source"] in ids and e["target"] in ids and (e["source"],e["target"]) not in pairs;pairs.add((e["source"],e["target"]))
def diff(old,new):
 om={n["id"]:n for n in old.get("nodes",[])};nm={n["id"]:n for n in new["nodes"]};oe={(e["source"],e["target"]) for e in old.get("edges",[])};ne={(e["source"],e["target"]) for e in new["edges"]}
 return {"generatedAt":datetime.now(timezone.utc).isoformat(),"addedNodes":sorted(set(nm)-set(om)),"removedNodes":sorted(set(om)-set(nm)),"addedEdges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(ne-oe)],"removedEdges":[{"source":a,"target":b,"relation":"parent"} for a,b in sorted(oe-ne)],"typeChanges":[{"id":i,"from":om[i]["type"],"to":nm[i]["type"]} for i in set(om)&set(nm) if om[i]["type"]!=nm[i]["type"]]}
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":")))
def main():
 DATA.mkdir(parents=True,exist_ok=True);RYM.mkdir(parents=True,exist_ok=True);aliases=json.loads((DATA/"curation-aliases.json").read_text()) if (DATA/"curation-aliases.json").exists() else {};raw=urllib.request.urlopen(SOURCE,timeout=60).read().decode("utf-8");graph=namespace(parse(raw),aliases);validate(graph);old=json.loads((RYM/"graph.json").read_text()) if (RYM/"graph.json").exists() else {};changes=diff(old,graph);now=datetime.now(timezone.utc).isoformat();counts=Counter(n["type"] for n in graph["nodes"]);meta={"source":"rym","sourceRepository":"FlakyBlueJay/mb-rym-hierarchy","sourceUrl":SOURCE,"sourceHash":hashlib.sha256(raw.encode()).hexdigest(),"sourceLastUpdated":now,"atlasSynchronized":now,"nodeCount":len(graph["nodes"]),"edgeCount":len(graph["edges"]),"countsByType":counts}
 for base,val in ((RYM/"graph.json",graph),(RYM/"dictionary.json",graph["nodes"]),(RYM/"changes.json",changes),(RYM/"source-meta.json",meta),(DATA/"graph.json",graph),(DATA/"dictionary.json",graph["nodes"]),(DATA/"changes.json",changes),(DATA/"source-meta.json",meta)):write(base,val)
 print(f"RYM: {len(graph['nodes'])} nodes / {len(graph['edges'])} edges")
if __name__=="__main__":main()