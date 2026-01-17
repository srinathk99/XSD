def xml_from_xsd_schema_prompt(xsd_text: str) -> str:
    return f"""
    You are an XML Generator from XSD Schema    
You are given an XML Schema Definition (XSD).

TASK:
- Generate ONE valid sample XML document
- The XML MUST strictly conform to the XSD
- Populate value by refering to its element type and pattern and maxLength
- Use correct element order
- Use correct namespaces if defined
- MAKE SURE ALL TAG HAVE CLOSING TAG 

CRITICAL RULES:
- Output ONLY the XML
- Do NOT add explanations
- Do NOT add comments
- Do NOT wrap in markdown

XSD:
{xsd_text}
"""

def regeneration_on_error_prompt(xsd : str , error : str) -> str :
    return f""" 
The xml you generated 
{xsd}
after validation facing an error 
{error} 

TASKS ;
-ANALYZE ERROR MESSAGE AND DO MINIMAL CHANGES TO THE GIVEN XML 
- DO NOT REMOVE / DELETE GIVEN XML ELEMENTS 
- ONLY MODIFY XML ELEMENTS VALUE OR CHANGE ITS ORDER TO MEET THE SEQUENCE

RULES :
- Output ONLY the XML
- Do NOT add explanations
- Do NOT add comments
- Do NOT wrap in markdown

"""


def build_sample_from_skeleton_and_xsd(skeleton : str , xsd : str) -> str:
    return f"""
The skeleton xml :
{skeleton} 
The xml schema used to get the skeleton xml :
{xsd}. 

TASKS :
- TRACK THROUGH THE SKELETON WITH AN XPATH AND LOOK UP IT WITH XSD SXHEMA 
TO GET THE RULES AND RESTRICTION AND PATTERNS 
AND USE THEM TO FILL THE SKELETON XML 

RULE : 
-- Output ONLY the XML
- Do NOT add explanations
- Do NOT add comments
- Do NOT wrap in markdown

"""

