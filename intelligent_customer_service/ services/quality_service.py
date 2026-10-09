import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def check_quality(text: str):
    with open(DATA_DIR / "quality_rules.json", "r", encoding="utf-8") as f:
        rules = json.load(f)
    
    warnings = []
    for category in rules.get("categories", []):
        for child in category.get("children", []):
            for rule in child.get("rules", []):
                if rule["keyword"] in text:
                    warnings.append(f"触犯规则: {rule['keyword']}，建议: {rule['action']}")
    return warnings
