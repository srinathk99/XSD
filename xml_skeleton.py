import xmlschema
import xml.etree.ElementTree as ET
from lxml import etree
from pathlib import Path
from xmlschema.validators import XsdElement, XsdGroup


# ---------------- CONFIG ----------------

BASE_DIR = Path(__file__).parent
XSD_PATH = BASE_DIR / "resource" / "pacs008.xsd"
OUTPUT_XML = BASE_DIR / "pacs008_skeleton.xml"


# ---------------- CORE LOGIC ----------------

def process_type(xsd_type, parent_elem):
    if not xsd_type.is_complex():
        return

    content = xsd_type.content
    if content is None:
        return

    process_particle(content, parent_elem)


def process_particle(particle, parent_elem):

    # -------- REAL ELEMENT --------
    if isinstance(particle, XsdElement):
        elem = ET.SubElement(parent_elem, particle.name)
        process_type(particle.type, elem)

    # -------- GROUP (sequence / choice / all) --------
    elif isinstance(particle, XsdGroup):
        model = particle.model

        if model in ("sequence", "all"):
            for child in particle:
                occurs = child.min_occurs if child.min_occurs > 0 else 1
                for _ in range(occurs):
                    process_particle(child, parent_elem)

        elif model == "choice":
            # Skeleton strategy: first option
            for child in particle:
                process_particle(child, parent_elem)
                break


# ---------------- PRETTY WRITE ----------------

def write_pretty(xml_root, output_path):
    """
    Pretty-print safely without namespace corruption
    """
    rough_bytes = ET.tostring(xml_root, encoding="utf-8")
    parser = etree.XMLParser(remove_blank_text=True)
    lxml_elem = etree.fromstring(rough_bytes, parser)

    pretty_bytes = etree.tostring(
        lxml_elem,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True
    )

    with open(output_path, "wb") as f:
        f.write(pretty_bytes)


# ---------------- MAIN ----------------

def generate_skeleton():
    if not XSD_PATH.exists():
        raise FileNotFoundError(f"XSD not found: {XSD_PATH}")

    schema = xmlschema.XMLSchema(str(XSD_PATH))

    # Root XSD element (Document)
    root_qname = next(iter(schema.elements))
    root_xsd = schema.elements[root_qname]

    # Register namespace ONCE
    ns = root_xsd.target_namespace
    ET.register_namespace("", ns)

    # Create XML root WITHOUT manual {ns}
    xml_root = ET.Element(root_xsd.name)

    # Build skeleton
    process_type(root_xsd.type, xml_root)

    # Pretty write
    write_pretty(xml_root, OUTPUT_XML)

    print(f"✅ Skeleton XML generated at: {OUTPUT_XML}")


if __name__ == "__main__":
    generate_skeleton()
