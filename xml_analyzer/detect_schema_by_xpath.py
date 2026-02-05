from lxml import etree
from pathlib import Path
import json


# ---------------- CONFIG ----------------

BASE_DIR = Path(__file__).parent

USER_XML = BASE_DIR / "input.xml"

# Map: schema_name -> rules.json
RULES_DIR = BASE_DIR / "resource" / "rules"
def load_all_schema_rules(rules_dir):
    schema_map = {}
    for file in rules_dir.glob("*.json"):
        schema_name = file.stem   # pacs.008.001.08 from pacs.008.001.08.json
        schema_map[schema_name] = file
    return schema_map

SCHEMA_RULES = load_all_schema_rules(RULES_DIR)

# ---------------- STEP 1: EXTRACT XPATHS FROM USER XML ----------------

def extract_xpaths(xml_file):
    tree = etree.parse(str(xml_file))
    root = tree.getroot()
    paths = set()

    def walk(elem, current_path):
        tag = etree.QName(elem).localname
        path = f"{current_path}/{tag}"
        paths.add(path)
        for child in elem:
            walk(child, path)

    walk(root, "")
    return paths


# ---------------- STEP 2: LOAD RULE PATHS ----------------

def load_schema_paths(rules_file):
    with open(rules_file, "r", encoding="utf-8") as f:
        rules = json.load(f)
    return set(rules.keys())


# ---------------- STEP 3: COMPARE STRUCTURE ----------------

def compare_paths(sample_paths, schema_paths):
    matched = sample_paths & schema_paths
    score = len(matched) / len(sample_paths) if sample_paths else 0
    return score, matched


# ---------------- STEP 4: DETECT BEST SCHEMA ----------------

def detect_schema(user_xml, schema_rules_map):
    sample_paths = extract_xpaths(user_xml)
    print(sample_paths)

    best_schema = None
    best_score = 0
    best_matches = set()

    print("\n--- Schema Structure Matching ---\n")

    for schema_name, rules_file in schema_rules_map.items():
        if not rules_file.exists():
            print(f"Rules file missing for {schema_name}: {rules_file}")
            continue

        schema_paths = load_schema_paths(rules_file)
        score, matched = compare_paths(sample_paths, schema_paths)

        print(f"{schema_name:20s} -> Match: {round(score * 100, 2):6.2f}%")

        if score > best_score:
            best_score = score
            best_schema = schema_name
            best_matches = matched

    print("\n--- Result ---")
    print("Detected Schema :", best_schema)
    print("Confidence      :", round(best_score * 100, 2), "%")
    print("Matched Paths  :", len(best_matches), "/", len(sample_paths))

    return best_schema, best_score, best_matches


# ---------------- MAIN ----------------

if __name__ == "__main__":

    if not USER_XML.exists():
        raise FileNotFoundError(f"User XML not found: {USER_XML}")

    detect_schema(USER_XML, SCHEMA_RULES)
