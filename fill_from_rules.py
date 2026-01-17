from lxml import etree
from pathlib import Path
import json
import random
import string
from datetime import datetime
import re


BASE_DIR = Path(__file__).parent
RULES_JSON = BASE_DIR / "CstmrCdtTrfTraceFormat_rules.json"
SKELETON_XML = BASE_DIR / "CstmrCdtTrfTraceFormat_skeleton.xml"
OUTPUT_XML = BASE_DIR / "cct_filled.xml"


# ---------- LOAD RULES ----------
with open(RULES_JSON, "r", encoding="utf-8") as f:
    RULES = json.load(f)


# ---------- VALUE GENERATOR BASED ON RULES ----------

def generate_value(rule):
    base = rule.get("base")
    facets = rule.get("facets", {})

    # Enumeration
    if "enumeration" in facets:
        return str(random.choice(facets["enumeration"]))

    # String
    if base in ("string", "token", "normalizedString"):
        min_len = facets.get("minLength", 5)
        max_len = facets.get("maxLength", 10)
        length = min(max(min_len, 5), max_len)
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # Pattern
    if "pattern" in facets:
        # Simple fallback for regex: generate alphanumerics
        return "ABC123"

    # DateTime
    if base == "dateTime":
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    # Date
    if base == "date":
        return datetime.utcnow().strftime("%Y-%m-%d")

    # Decimal
    if base in ("decimal", "float", "double"):
        return "100.00"

    # Integer
    if base in ("integer", "int", "long", "short", "positiveInteger", "nonNegativeInteger"):
        return "1"

    # Boolean
    if base == "boolean":
        return "true"

    # Safe default
    return "1"


# ---------- LOAD SKELETON ----------
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(str(SKELETON_XML), parser)
root = tree.getroot()


def walk(elem, current_xpath):
    tag = etree.QName(elem).localname
    xpath = f"{current_xpath}/{tag}"

    if xpath in RULES:
        rule = RULES[xpath]
        if not list(elem):   # leaf only
            value = generate_value(rule)
            elem.text = value

    for child in elem:
        walk(child, xpath)


# ---------- RUN ----------
walk(root, "")

# ---------- SAVE PRETTY ----------
pretty = etree.tostring(
    root,
    encoding="utf-8",
    xml_declaration=True,
    pretty_print=True
)

with open(OUTPUT_XML, "wb") as f:
    f.write(pretty)

print("✔ Filled XML generated from rules:", OUTPUT_XML)
