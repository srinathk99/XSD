from dotenv import load_dotenv
import os

load_dotenv("resource/apikey.env")

KEY=os.getenv("OPENAI_API_KEY")
print("API KEY =",KEY )

from openai import OpenAI

client = OpenAI(api_key=KEY)

from technique.loader import load_xsd_as_text
from prompts.schema_prompt import xml_from_xsd_schema_prompt,regeneration_on_error_prompt,build_sample_from_skeleton_and_xsd

def generate_xml_from_xsd(xsd_path: str) -> str:
    xsd_text = load_xsd_as_text(xsd_path)
    prompt = xml_from_xsd_schema_prompt(xsd_text)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text

def xml_with_validation_error_regenerate(xml :str , error : str) -> str :

    prompt = regeneration_on_error_prompt(xml , error )
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text

def generate_sample_from_skeleton(skeleton_psth,xsd_path):
    xsd_text = load_xsd_as_text(xsd_path)
    skeleton_text = load_xsd_as_text(skeleton_psth)
    prompt = build_sample_from_skeleton_and_xsd(skeleton_text,xsd_text)

    print("generate_sample_from_skeleton")

    response = client.responses.create(
        model="gpt-5.2",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text
