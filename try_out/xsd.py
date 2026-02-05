import xmlschema
def validate_xml_using_xsd_sxhema(path,xmls) -> str :
    schema = xmlschema.XMLSchema(path)
    bools=schema.is_valid(xmls)
    if bools :
        return "success"

    try:
        schema.validate(xmls)
    except Exception as e:
       return str(e)


