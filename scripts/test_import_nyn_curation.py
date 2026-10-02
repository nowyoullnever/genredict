#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts"/"import-nyn-curation.py"
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding="utf-8")
with tempfile.TemporaryDirectory() as tmp:
 base=Path(tmp);data=base/"data";nodes=[{"name":"'Ote'a","curationKey":"'ote'a"},{"name":"2 Tone","curationKey":"2 tone"},{"name":"2-Step","curationKey":"2-step"},{"name":"Ambient","curationKey":"ambient"}];write(data/"rym"/"graph.json",{"nodes":nodes});write(data/"nyn-curation.json",{"ambient":{"descriptionKo":"preserve","recommendations":[]}})
 source=base/"input.txt";source.write_text("'Ote'a\n\t첫 문단\n\t\n\t둘째 문단\n\t\thttps://example.com/a.jpg\n2 Tone\n\t설명\n\t\thttps://example.com/b.jpg https://example.com/c.jpg\n2-Step\n\t\thttps://example.com/d.jpg\n",encoding="utf-8")
 result=subprocess.run([sys.executable,str(SCRIPT),str(source),"--data-dir",str(data)],text=True,capture_output=True);assert result.returncode==0,result.stdout+result.stderr
 out=json.loads((data/"nyn-curation.json").read_text());assert out["'ote'a"]["descriptionKo"]=="첫 문단\n\n둘째 문단";assert [x["cover"] for x in out["2 tone"]["recommendations"]]==["https://example.com/b.jpg","https://example.com/c.jpg"];assert out["ambient"]["descriptionKo"]=="preserve"
 update=base/"update.txt";update.write_text("2-Step\n\t새 설명\n",encoding="utf-8");assert subprocess.run([sys.executable,str(SCRIPT),str(update),"--data-dir",str(data)],capture_output=True).returncode==0;out=json.loads((data/"nyn-curation.json").read_text());assert out["2-step"]=={"descriptionKo":"새 설명","recommendations":[]}
 invalid=base/"invalid.txt";invalid.write_text("Ambient\n\t\thttps://e/1 https://e/2 https://e/3 https://e/4 https://e/5\n",encoding="utf-8");assert subprocess.run([sys.executable,str(SCRIPT),str(invalid),"--data-dir",str(data)],capture_output=True).returncode==1
 print("nyn curation importer tests passed")