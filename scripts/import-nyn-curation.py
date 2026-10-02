#!/usr/bin/env python3
"""Import plain-text NYN curation without altering user-authored text."""
from __future__ import annotations
import argparse,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
URL=re.compile(r"https?://[^\s]+")
def normal(text:str)->str:return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",text).strip()).casefold()
def load(path:Path):return json.loads(path.read_text(encoding="utf-8"))
def parse(raw:str):
 entries=[];current=None;errors=[]
 for line_no,line in enumerate(raw.splitlines(),1):
  tabs=len(line)-len(line.lstrip("\t"));text=line[tabs:]
  if tabs==0:
   if not text.strip():continue
   current={"name":text,"description":[],"covers":[],"line":line_no};entries.append(current);continue
  if current is None:
   errors.append(f"line {line_no}: 장르명보다 앞선 들여쓰기");continue
  if tabs==1:
   current["description"].append(text);continue
  if not text.strip():continue
  tokens=text.split();urls=URL.findall(text)
  if not urls or len(urls)!=len(tokens) or any(not URL.fullmatch(token) for token in tokens):
   errors.append(f"line {line_no}: cover URL이 아닙니다");continue
  for value in urls:
   parsed=urlparse(value)
   if parsed.scheme not in {"http","https"} or not parsed.netloc:errors.append(f"line {line_no}: 잘못된 URL {value}")
   else:current["covers"].append(value)
 for entry in entries:
  if len(entry["covers"])>4:errors.append(f"line {entry['line']}: {entry['name']}에 cover가 {len(entry['covers'])}개입니다 (최대 4개)")
 return entries,errors
def resolve(name:str,nodes:list[dict]):
 exact=[n for n in nodes if n.get("name")==name]
 candidates=exact or [n for n in nodes if normal(n.get("name",""))==normal(name)]
 if not candidates:
  candidates=[n for n in nodes if normal(n.get("curationKey",""))==normal(name)]
 keys={n.get("curationKey") for n in candidates if n.get("curationKey")}
 return next(iter(keys)) if len(keys)==1 else None
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("input",type=Path);parser.add_argument("--dry-run",action="store_true");parser.add_argument("--data-dir",type=Path,default=ROOT/"public"/"data",help=argparse.SUPPRESS);args=parser.parse_args()
 raw=args.input.read_text(encoding="utf-8");entries,errors=parse(raw);data=args.data_dir;graph=load(data/"rym"/"graph.json");curation_path=data/"nyn-curation.json";curation=load(curation_path) if curation_path.exists() else {};unmatched=[];resolved=[];seen=set()
 for entry in entries:
  key=resolve(entry["name"],graph["nodes"])
  if not key:unmatched.append(entry["name"]);continue
  if key in seen:errors.append(f"line {entry['line']}: 같은 curationKey를 두 번 입력했습니다 ({key})");continue
  seen.add(key);resolved.append((key,entry))
 print(f"{len(entries)} entries parsed")
 if unmatched:
  print("Unmatched:");[print(f"- {name}") for name in unmatched]
 if errors:
  print("Errors:");[print(f"- {error}") for error in errors];return 1
 added=updated=unchanged=0
 for key,entry in resolved:
  incoming={"descriptionKo":"\n".join(entry["description"]),"recommendations":[{"cover":url} for url in entry["covers"]]}
  old=curation.get(key)
  if old is None:added+=1
  elif old==incoming:unchanged+=1
  else:updated+=1
  curation[key]=incoming
 print("UPDATE:");[print(f"- {entry['name']}") for _,entry in resolved]
 print("Recommendations:");[print(f"- {entry['name']}: {len(entry['covers'])}") for _,entry in resolved]
 if args.dry_run:return 0
 curation_path.write_text(json.dumps(curation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("NYN curation import complete.");print(f"Added: {added}");print(f"Updated: {updated}");print(f"Unchanged: {unchanged}");print(f"Unmatched: {len(unmatched)}");print("Errors: 0")
 return 0
if __name__=="__main__":sys.exit(main())