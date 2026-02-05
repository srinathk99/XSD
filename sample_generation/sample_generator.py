from xml_analyzer.extract_detect_validate import load_all_schema_rules,validate_xml_with_rules
from OpenAI.openaiClient import remove_element_call,xml_with_validation_error_regenerate,generate_tag_with_value_from_error_call,add_tag_into_sample_call
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from technique.loader import load_xsd_as_text

# ---------------- CONFIG ----------------
load_dotenv("path.env")

BASE_DIR = Path(os.getenv("BASE_DIR"))
XSD_PATH = BASE_DIR / os.getenv("XSD_PATH")
SKELETON_DIR = BASE_DIR / os.getenv("SKELETON_DIR")
RULES_DIR=BASE_DIR / os.getenv("RULES_DIR")

schema_name="pacs.008.001.13"
sch_skel=schema_name+"_skeleton.xml"
SKELETON_DIR=SKELETON_DIR/sch_skel

# ---------------- FIND SCHEMA RULE  ----------------

SCHEMA_RULES = load_all_schema_rules(RULES_DIR)
rules_file = SCHEMA_RULES[schema_name]
rules_file = SCHEMA_RULES[schema_name]

def get_default_namespace(root):
    if root.tag.startswith("{"):
        return root.tag.split("}")[0][1:]
    return None

def write_pretty(xml_input, out_file):
    # Parse safely
    if isinstance(xml_input, ET.Element):
        root = xml_input
        tree = ET.ElementTree(root)

    elif isinstance(xml_input, str) and xml_input.lstrip().startswith("<"):
        root = ET.fromstring(xml_input)
        tree = ET.ElementTree(root)

    else:
        tree = ET.parse(str(xml_input))
        root = tree.getroot()

        # ✅ Register detected namespace as default
        ns = get_default_namespace(root)
        if ns:
            ET.register_namespace("", ns)

    # ✅ Proper indentation (NO whitespace explosion)
    ET.indent(tree, space="  ", level=0)

    tree.write(
        out_file,
        encoding="utf-8",
        xml_declaration=True
    )
CURRENT_DIR = Path(__file__).parent
OUTPUT_FILE = CURRENT_DIR / "gen.xml"

xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.13">

</Document>
"""

OUTPUT_FILE = BASE_DIR / "sample_generation" / "gen.xml"
OUTPUT_FILE.write_text(xml_content, encoding="utf-8")
inp=str(OUTPUT_FILE)
print(inp)
validation_errors = validate_xml_with_rules(inp, rules_file)
#validation_errors = validate_xml_using_xsd_sxhema(USER_XML, rules_file)
count=0
inp = load_xsd_as_text(OUTPUT_FILE)

while True:
    count += 1
    if not validation_errors:
        print("XML is VALID against schema rules ✔")
        write_pretty(inp,"gen.xml")
        break
    else:
        print("XML is INVALID ❌\n")
        errs=""
        for err in validation_errors:
            print(" -", err)
            if "Missing" in err:
                tag = generate_tag_with_value_from_error_call(err)
                print(" -", tag)
                inp = add_tag_into_sample_call(tag, inp, err)
                print(inp)
            if "Too many occurrences" in err:
                inp=remove_element_call(inp,err)


    validation_errors = validate_xml_with_rules(inp, rules_file)
    if count == 3:
        break



