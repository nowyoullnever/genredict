from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent));from refresh_data import validate
p=Path(__file__).resolve().parents[1]/"public"/"data";g=json.loads((p/"graph.json").read_text());validate(g);d=json.loads((p/"dictionary.json").read_text());assert {n["id"] for n in d}=={n["id"] for n in g["nodes"]};print("data validation passed")