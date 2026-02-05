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
The xml :
{xsd}
the error in it :
{error} 

TASKS ;
-GENERATE MISSING ELEMENT AND ADD IT IMTO XML XPATH.
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

def generate_value_from_rules(rule) :
    return f"""
Generate a valid sample value for an XML element with these rules:

Name: {rule['name']}
Type: {rule['type']}
MinOccurs: {rule['minOccurs']}
MaxOccurs: {rule['maxOccurs']}
Nillable: {rule['nillable']}
Facets: {rule['facets']}

Task:
Generate ONE valid value that satisfies the rules.

Output format:
Return ONLY the value.
Do NOT add explanation.
Do NOT add quotes unless required by the datatype.
Do NOT add any text before or after.
"""

def generate_tag_with_value_from_error(err):
    return f"""
Genrate an xml tag along with valid value
{err}
Return only the tag and its value
Do NOT add explanation.
Do NOT add quotes unless required by the datatype.
Do NOT add any text before or after.
"""

def add_tag_into_sample(tag,sample,errs):
    return f"""
    FROM {errs}
    GET TO KNOW WHERE TO INSERT TAG 
    AND
    INSIDE THIS TAG
{tag}
INTO THIS SAMPLE
{sample}
OUTPUT FORMAT :
RETURN THE MODIFIED SAMPLE ONLY.
Do NOT add explanation.
Do NOT add quotes unless required by the datatype.
Do NOT add any text before or after.
    """

def remove_element(xml,errs):
    return f"""
FROM THE {errs} 
REMOVE ONE OCUURENCE ALONG WITH ITS CHILD
FROM THIS XML
{xml}
OUTPUT FORMAT :
RETURN THE MODIFIED SAMPLE ONLY.
Do NOT add explanation.
Do NOT add quotes unless required by the datatype.
Do NOT add any text before or after.
    """
