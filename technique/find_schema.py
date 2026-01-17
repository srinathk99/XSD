import os
import xmlschema
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XSD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "resource"))

def get_root_tag(xml_source):
    root = ET.parse(xml_source).getroot()
    return root.tag

def get_root_children(xml_source):
    root = ET.parse(xml_source).getroot()
    return {child.tag for child in root}

def extract_schema_root(xsd_path):
    schema = xmlschema.XMLSchema(xsd_path)
    return schema.root_elements[0].name

def strip_ns(tag: str) -> str:
    """Remove namespace from XML tag"""
    if tag is None:
        return ""
    return tag.split("}", 1)[-1] if "}" in tag else tag

def get_xml_root(xml_source):
    tree = ET.parse(xml_source)
    return tree.getroot()

def detect_matching_schema(xml_source):
    if not os.path.isdir(XSD_DIR):
        raise FileNotFoundError(f"XSD directory not found: {XSD_DIR}")

    matches = []
    errors_by_schema = {}

    for file in os.listdir(XSD_DIR):
        if not file.endswith(".xsd"):
            continue

        xsd_path = os.path.join(XSD_DIR, file)

        try:
            schema = xmlschema.XMLSchema(xsd_path)
            error = next(schema.iter_errors(xml_source), None)

            if error is None:
                matches.append(file)
            else:
                errors_by_schema[file] = str(error)

        except xmlschema.XMLSchemaException as e:
            errors_by_schema[file] = str(e)

    return matches, errors_by_schema

def detect_best_matching_schema(xml_source, threshold=70):

    if not os.path.isdir(XSD_DIR):
        raise FileNotFoundError(f"XSD directory not found: {XSD_DIR}")

    root = get_xml_root(xml_source)
    xml_root_local = strip_ns(root.tag)
    xml_children = {strip_ns(child.tag) for child in root}

    results = []

    for file in os.listdir(XSD_DIR):
        if not file.endswith(".xsd"):
            continue

        xsd_path = os.path.join(XSD_DIR, file)

        print(f"\n🔍 Validating against schema: {file}")

        try:
            schema = xmlschema.XMLSchema(xsd_path)

            # ---- ROOT MATCH (40%) ----
            schema_root = schema.root_elements[0].qualified_name
            schema_root_local = strip_ns(schema_root)
            root_score = 40 if schema_root_local == xml_root_local else 0

            # ---- STRUCTURE MATCH (30%) ----
            expected_children = {
                strip_ns(e.name)
                for e in schema.root_elements[0].type.content
                if hasattr(e, "name")
            }

            overlap = len(xml_children & expected_children)
            structure_score = min(30, overlap * 5)

            # ---- VALIDATION ERRORS ----
            errors = list(schema.iter_errors(xml_source))

            if not errors:
                print("  ✅ No validation errors")
            else:
                print(f"  ❌ {len(errors)} validation errors:")
                for idx, err in enumerate(errors, 1):
                    print(f"    {idx}. Path   : {err.path}")
                    print(f"       Reason : {err.reason}")

            val_score = validation_score(errors) * 0.3
            final_score = int(root_score + structure_score + val_score)

            results.append({
                "schema": file,
                "score": final_score,
                "errors": len(errors)
            })

        except Exception as e:
            print(f"  ❌ Schema processing failed: {e}")
            results.append({
                "schema": file,
                "score": 0,
                "errors": float("inf")
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    best = results[0]

    if best["score"] >= threshold:
        return best, results

    return None, results

# --------------------------------------------------
def validation_score(errors):
    score = 100
    for e in errors:
        reason = str(e.reason).lower()
        if "missing" in reason:
            score -= 15
        elif "unexpected" in reason:
            score -= 8
        elif "sequence" in reason or "order" in reason:
            score -= 5
        elif "pattern" in reason or "datatype" in reason:
            score -= 3
        else:
            score -= 2
    return max(score, 0)