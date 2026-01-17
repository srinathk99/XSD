from lxml import etree
import xmlschema
from pathlib import Path
import random
import string
from datetime import datetime


BASE_DIR = Path(__file__).parent
XSD_PATH = BASE_DIR / "resource" / "CstmrCdtTrfTraceFormat.xsd"
SKELETON_XML = BASE_DIR / "CstmrCdtTrfTraceFormat_skeleton.xml"
OUTPUT_XML = BASE_DIR / "filled.xml"

schema = xmlschema.XMLSchema(str(XSD_PATH))

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(str(SKELETON_XML), parser)
root = tree.getroot()

# Namespace-safe handling
if None in root.nsmap:
    NS = {"ns": root.nsmap[None]}
    USE_NS = True
else:
    NS = {}
    USE_NS = False

def generate_value(xsd_type):
    primitive = xsd_type.primitive_type.name
    facets = xsd_type.facets
    enums = facets.get("enumeration")

    # Enumeration
    if enums:
        return str(random.choice(enums).value)

    # String-like
    if primitive in ("string", "token", "normalizedString"):
        min_len = facets["minLength"].value if "minLength" in facets else 5
        max_len = facets["maxLength"].value if "maxLength" in facets else 10
        length = min(max(min_len, 5), max_len)
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # DateTime
    if primitive == "dateTime":
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    # Date
    if primitive == "date":
        return datetime.utcnow().strftime("%Y-%m-%d")

    # Decimal / Float
    if primitive in ("decimal", "float", "double"):
        return "100.00"

    # Integer family
    if primitive in ("integer", "int", "long", "short", "positiveInteger", "nonNegativeInteger"):
        return "1"

    # Boolean (CRITICAL)
    if primitive == "boolean":
        return "true"   # MUST be string

    # Safe default for any other atomic type
    return "1"

def walk_and_fill(elem, current_xpath):
    tag = etree.QName(elem).localname
    xpath = f"{current_xpath}/{tag}"

    # Locate XSD element
    xsd_elem = schema.find(xpath)

    if xsd_elem is not None and xsd_elem.type is not None:
        if not list(elem):  # leaf
            value = generate_value(xsd_elem.type)
            decoded = xsd_elem.type.decode(value)
            xsd_elem.type.validate(decoded)
            elem.text = value

    for child in elem:
        walk_and_fill(child, xpath)


walk_and_fill(root, "")

# Final validation
final_bytes = etree.tostring(root, encoding="utf-8")
schema.validate(final_bytes)

# Save pretty
pretty = etree.tostring(
    root,
    encoding="utf-8",
    xml_declaration=True,
    pretty_print=True
)

with open(OUTPUT_XML, "wb") as f:
    f.write(pretty)

print("Filled XML generated:", OUTPUT_XML)
