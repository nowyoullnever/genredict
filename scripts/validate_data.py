from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
from refresh_data import validate as validate_rym
from refresh_discogs_data import validate as validate_discogs
root=Path(__file__).resolve().parents[1];data=root/"public"/"data"
validate_rym(json.loads((data/"rym"/"graph.json").read_text()))
validate_discogs(json.loads((data/"discogs"/"graph.json").read_text()))
for source in ("rym","discogs"):
 graph=json.loads((data/source/"graph.json").read_text());dictionary=json.loads((data/source/"dictionary.json").read_text());assert {n["id"] for n in dictionary}=={n["id"] for n in graph["nodes"]}
curation_path=data/"nyn-curation.json"
if curation_path.exists():
 curation=json.loads(curation_path.read_text());assert isinstance(curation,dict),"nyn-curation.json must be an object"
 for key,entry in curation.items():
  assert isinstance(entry,dict),f"curation entry {key} must be an object";recommendations=entry.get("recommendations",[]);assert isinstance(recommendations,list),f"recommendations for {key} must be a list";assert len(recommendations)<=4,f"curation entry {key} has more than four recommendations"
  for item in recommendations:`n   assert isinstance(item,dict) and item.get("cover"),f"curation recommendation for {key} requires cover"`n   for field in ("artist","album","year"): assert field not in item or isinstance(item[field],(str,int)),f"curation recommendation {field} for {key} is invalid"
  assert isinstance(entry.get("descriptionKo",""),str),f"descriptionKo for {key} must be text"
overlap=json.loads((data/"taxonomy-overlap.json").read_text());assert all(key in overlap for key in ("shared","rymOnly","discogsOnly","possibleAliases"))
print("RYM, Discogs and curation validation passed")