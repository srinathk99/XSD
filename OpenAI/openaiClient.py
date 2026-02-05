from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR/"apikey.env")

KEY=os.getenv("OPENAI_API_KEY")
#print("API KEY =",KEY )

from openai import OpenAI

client = OpenAI(api_key=KEY)

from technique.loader import load_xsd_as_text
from prompts.schema_prompt import (xml_from_xsd_schema_prompt,regeneration_on_error_prompt,
                                   build_sample_from_skeleton_and_xsd,generate_value_from_rules,
                                   generate_tag_with_value_from_error,add_tag_into_sample,
                                   remove_element)

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
        model="gpt-5.2",
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

def ask_ai_for_values(rules) :
    prompt = generate_value_from_rules(rules)
    response = client.responses.create(
        model="gpt-5.2",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text

def generate_tag_with_value_from_error_call(error) :
    prompt = generate_tag_with_value_from_error(error)
    response = client.responses.create(
        model="gpt-5.2",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text


def add_tag_into_sample_call(tag,sample,errs):
    prompt = add_tag_into_sample(tag,sample,errs)
    response = client.responses.create(
        model="gpt-5.2",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text

def remove_element_call(xml,errs):
    prompt = remove_element(xml,errs)
    response = client.responses.create(
        model="gpt-5.2",
        input=prompt,
        temperature=0.2  # low = deterministic + schema-safe
    )

    return response.output_text
