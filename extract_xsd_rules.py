import xmlschema
from pathlib import Path
import json
from xmlschema.validators import XsdElement, XsdGroup, XsdComplexType

BASE_DIR = Path(__file__).parent
XSD_PATH = BASE_DIR / "resource" / "pacs008.xsd"
RULES_DIR = BASE_DIR / "resource" / "rules"
RULES_DIR.mkdir(exist_ok=True)

OUTPUT_JSON = RULES_DIR / f"{XSD_PATH.stem}_rules.json"

schema = xmlschema.XMLSchema(str(XSD_PATH))

rules = {}
choice_groups = []   # list of [xpath1, xpath2, ...]


def local(name):
    if name and name.startswith("{"):
        return name.split("}", 1)[1]
    return name


def extract_facets(xsd_type):
    facets = {}
    for name, facet in xsd_type.facets.items():
        if hasattr(facet, "value"):
            facets[local(name)] = facet.value
    return facets


def process_particle(particle, current_xpath):
    # -------- ELEMENT --------
    if isinstance(particle, XsdElement):
        elem_name = local(particle.name)
        xpath = f"{current_xpath}/{elem_name}"
        xsd_type = particle.type

        rule = {
            "name": elem_name,
            "xpath": xpath,
            "minOccurs": particle.min_occurs,
            "maxOccurs": particle.max_occurs,
            "nillable": particle.nillable
        }

        if isinstance(xsd_type, XsdComplexType):
            rule["type"] = local(xsd_type.name)
            rule["base"] = "complex"
            rule["facets"] = {}
        else:
            rule["type"] = local(xsd_type.name)
            rule["base"] = local(xsd_type.primitive_type.name)
            rule["facets"] = extract_facets(xsd_type)

        rules[xpath] = rule

        if xsd_type.is_complex() and xsd_type.content is not None:
            process_particle(xsd_type.content, xpath)

    # -------- GROUP --------
    elif isinstance(particle, XsdGroup):
        # Capture CHOICE group
        if particle.model == "choice":
            group = []
            for child in particle:
                if isinstance(child, XsdElement):
                    group.append(f"{current_xpath}/{local(child.name)}")
            if len(group) > 1:
                choice_groups.append(group)

        for child in particle:
            process_particle(child, current_xpath)


root_qname = next(iter(schema.elements))
root = schema.elements[root_qname]

process_particle(root, "")

final_json = {
    "rules": rules,
    "choice_groups": choice_groups
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(final_json, f, indent=2)

print("✔ Rules + Choice groups extracted to:", OUTPUT_JSON)
