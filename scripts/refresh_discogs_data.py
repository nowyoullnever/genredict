#!/usr/bin/env python3
"""Build Discogs Genre -> Style graph from a list dataset plus explicit mapping only."""
from __future__ import annotations
import json,re,unicodedata,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"public"/"data";OUT=DATA/"discogs"
GENRES_URL="https://raw.githubusercontent.com/hastefuI/discogs-dataset-genres-styles/master/dist/genres.json";STYLES_URL="https://raw.githubusercontent.com/hastefuI/discogs-dataset-genres-styles/master/dist/styles.json"
def slug(text):
 s=unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower();return re.sub(r"^-+|-+$","",re.sub(r"[^a-z0-9]+","-",s)) or "item"
def curation_key(text):return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",text).strip().lower())
def external(name,field):return f"https://www.discogs.com/search/?{field}={urllib.parse.quote(name)}&type=all"
def get(url):return json.loads(urllib.request.urlopen(url,timeout=60).read().decode("utf-8"))
def node_id(name,used):
 base=f"discogs:{slug(name)}";candidate=base;i=2
 while candidate in used:candidate=f"{base}--{i}";i+=1
 used.add(candidate);return candidate
def build(genres,styles,mapping,aliases):
 used=set();by_name={};nodes=[]
 for name in genres:
  ident=node_id(name,used);by_name[name]=ident;nodes.append({"id":ident,"source":"discogs","name":name,"slug":slug(name),"type":"genre","parents":[],"children":[],"depth":0,"externalUrl":external(name,"genre"),"curationKey":"","sourcePath":[],"aliases":[],"dateAdded":None,"lastChanged":None})
 for name in styles:
  ident=node_id(name,used);by_name[name]=ident;nodes.append({"id":ident,"source":"discogs","name":name,"slug":slug(name),"type":"style","parents":[],"children":[],"depth":1,"externalUrl":external(name,"style"),"curationKey":"","sourcePath":[],"aliases":[],"dateAdded":None,"lastChanged":None})
 for n in nodes:n["curationKey"]=aliases.get(n["id"],curation_key(n["name"]))
 edges=[];unmapped=[];known=set(genres)
 for genre,items in mapping.items():
  if genre not in known:continue
  for style in items:
   if style not in by_name:continue
   a,b=by_name[genre],by_name[style]
   if a not in next(n for n in nodes if n["id"]==b)["parents"]:
    next(n for n in nodes if n["id"]==b)["parents"].append(a);next(n for n in nodes if n["id"]==a)["children"].append(b);edges.append({"source":a,"target":b,"relation":"parent"})
 mapped={style for items in mapping.values() for style in items}
 for style in styles:
  if style not in mapped:unmapped.append(style)
 for n in nodes:n["parents"].sort();n["children"].sort()
 return {"nodes":sorted(nodes,key=lambda n:n["name"].casefold()),"edges":sorted(edges,key=lambda e:(e["source"],e["target"]))},sorted(unmapped)
def validate(graph):
 ids={n["id"] for n in graph["nodes"]};assert len(ids)>=700,"unexpectedly small Discogs taxonomy";assert sum(n["type"]=="genre" for n in graph["nodes"])>=15
 for n in graph["nodes"]:assert n["id"].startswith("discogs:") and n["source"]=="discogs" and n["curationKey"]
 for e in graph["edges"]:assert e["source"] in ids and e["target"] in ids
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":")))
def main():
 DATA.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);mapping=json.loads((DATA/"discogs-taxonomy.json").read_text());aliases=json.loads((DATA/"curation-aliases.json").read_text()) if (DATA/"curation-aliases.json").exists() else {};genres=get(GENRES_URL);styles=get(STYLES_URL);graph,unmapped=build(genres,styles,mapping,aliases);validate(graph);now=datetime.now(timezone.utc).isoformat();meta={"source":"discogs","sourceRepository":"hastefuI/discogs-dataset-genres-styles","genresUrl":GENRES_URL,"stylesUrl":STYLES_URL,"atlasSynchronized":now,"nodeCount":len(graph["nodes"]),"edgeCount":len(graph["edges"]),"genreCount":len(genres),"styleCount":len(styles),"unmappedStyleCount":len(unmapped)}
 write(OUT/"graph.json",graph);write(OUT/"dictionary.json",graph["nodes"]);write(OUT/"source-meta.json",meta);write(OUT/"unmapped.json",{"generatedAt":now,"styles":unmapped});write(DATA/"discogs-unmapped.json",{"generatedAt":now,"styles":unmapped});print(f"Discogs: {len(genres)} genres / {len(styles)} styles / {len(unmapped)} unmapped")
if __name__=="__main__":main()