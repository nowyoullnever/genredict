from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
from refresh_data import validate
root=Path(__file__).resolve().parents[1]
data=root/"public"/"data"
graph=json.loads((data/"graph.json").read_text())
validate(graph)
dictionary=json.loads((data/"dictionary.json").read_text())
assert {n["id"] for n in dictionary}=={n["id"] for n in graph["nodes"]}
curation_path=data/"nyn-curation.json"
if curation_path.exists():
    curation=json.loads(curation_path.read_text())
    assert isinstance(curation,dict),"nyn-curation.json must be an object"
    for key,entry in curation.items():
        assert isinstance(entry,dict),f"curation entry {key} must be an object"
        recommendations=entry.get("recommendations",[])
        assert isinstance(recommendations,list),f"recommendations for {key} must be a list"
        assert len(recommendations)<=4,f"curation entry {key} has more than four recommendations"
        for item in recommendations:
            assert all(item.get(field) for field in ("artist","album","cover")),f"curation recommendation for {key} requires artist, album, cover"
        assert isinstance(entry.get("descriptionKo",""),str),f"descriptionKo for {key} must be text"
print("data and curation validation passed")