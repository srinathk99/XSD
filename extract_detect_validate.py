from lxml import etree
from pathlib import Path
import json
import re

# ---------------- CONFIG ----------------

BASE_DIR = Path(__file__).parent
USER_XML = BASE_DIR / "input.xml"
RULES_DIR = BASE_DIR / "resource" / "rules"


# ---------------- STEP 1: EXTRACT XPATHS WITH COUNTS ----------------

def extract_paths_with_counts(xml_file):
    tree = etree.parse(str(xml_file))
    root = tree.getroot()
    paths = {}

    def walk(elem, current_path):
        tag = etree.QName(elem).localname
        path = f"{current_path}/{tag}"
        paths[path] = paths.get(path, 0) + 1
        for child in elem:
            walk(child, path)

    walk(root, "")
    return paths, tree


# ---------------- STEP 2: LOAD ALL RULE FILES ----------------

def load_all_schema_rules(rules_dir):
    schema_map = {}
    for file in rules_dir.glob("*_rules.json"):
        schema_name = file.stem.replace("_rules", "")
        schema_map[schema_name] = file
    return schema_map


# ---------------- STEP 3: DETECT BEST MATCHING SCHEMA ----------------

def detect_schema(user_xml, schema_rules_map):
    sample_paths, _ = extract_paths_with_counts(user_xml)

    best_schema = None
    best_score = 0

    for schema_name, rules_file in schema_rules_map.items():
        with open(rules_file, "r") as f:
            data = json.load(f)
            rules = data["rules"] if "rules" in data else data

        schema_paths = set(rules.keys())
        matched = set(sample_paths.keys()) & schema_paths
        score = len(matched) / len(sample_paths) if sample_paths else 0

        print(f"{schema_name:20s} -> Match: {round(score * 100, 2):6.2f}%")

        if score > best_score:
            best_score = score
            best_schema = schema_name

    print("\nDetected Schema :", best_schema)
    print("Confidence      :", round(best_score * 100, 2), "%")
    return best_schema


# ---------------- STEP 4: HELPERS ----------------

def to_ns_safe_xpath(clean_xpath):
    parts = clean_xpath.strip("/").split("/")
    return "/" + "/".join([f"*[local-name()='{p}']" for p in parts])


def validate_value(value, facets):
    if "minLength" in facets and len(value) < facets["minLength"]:
        return False, f"Length < minLength {facets['minLength']}"
    if "maxLength" in facets and len(value) > facets["maxLength"]:
        return False, f"Length > maxLength {facets['maxLength']}"
    if "pattern" in facets and facets["pattern"]:
        if not re.fullmatch(facets["pattern"], value):
            return False, "Pattern mismatch"
    return True, None


# ---------------- STEP 5: VALIDATION WITH CHOICE ----------------

def validate_xml_with_rules(xml_file, rules_file):
    path_counts, tree = extract_paths_with_counts(xml_file)
    root = tree.getroot()

    with open(rules_file, "r") as f:
        data = json.load(f)

    rules = data["rules"]
    choice_groups = data.get("choice_groups", [])

    errors = []

    def resolved_by_choice(xpath):
        for group in choice_groups:
            if xpath in group:
                for sibling in group:
                    if path_counts.get(sibling, 0) > 0:
                        return True
        return False

    for xpath, rule in rules.items():
        count = path_counts.get(xpath, 0)

        # ---------- Skip subtree if optional parent missing ----------
        parts = xpath.strip("/").split("/")
        skip = False

        for i in range(1, len(parts)):
            parent_path = "/" + "/".join(parts[:i])
            if parent_path in rules:
                parent_rule = rules[parent_path]
                parent_count = path_counts.get(parent_path, 0)

                if parent_rule["minOccurs"] == 0 and parent_count == 0:
                    skip = True
                    break

        if skip:
            continue

        # ---------- Cardinality ----------
        if count < rule["minOccurs"]:
            if resolved_by_choice(xpath):
                continue
            errors.append(f"Missing required element: {xpath}")

        if rule["maxOccurs"] is not None and count > rule["maxOccurs"]:
            errors.append(f"Too many occurrences of: {xpath}")

        # ---------- Value Validation ----------
        if rule["base"] != "complex" and count > 0:
            ns_safe_xpath = to_ns_safe_xpath(xpath)
            nodes = root.xpath(ns_safe_xpath)

            for node in nodes:
                value = (node.text or "").strip()
                ok, msg = validate_value(value, rule["facets"])
                if not ok:
                    errors.append(f"{xpath} = '{value}' → {msg}")

    return errors


# ---------------- MAIN ----------------

if __name__ == "__main__":

    if not USER_XML.exists():
        raise FileNotFoundError(f"User XML not found: {USER_XML}")

    SCHEMA_RULES = load_all_schema_rules(RULES_DIR)

    print("\n--- Detecting Schema ---\n")
    schema_name = detect_schema(USER_XML, SCHEMA_RULES)

    rules_file = SCHEMA_RULES[schema_name]

    print("\n--- Validating XML Against Detected Schema ---\n")
    validation_errors = validate_xml_with_rules(USER_XML, rules_file)

    if not validation_errors:
        print("XML is VALID against schema rules ✔")
    else:
        print("XML is INVALID ❌\n")
        for err in validation_errors:
            print(" -", err)
