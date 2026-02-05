import ollama
from prompts.schema_prompt import generate_value_from_rules

def ask_ollama_to_generate_values(rules):

    prompt = generate_value_from_rules(rules)

    response = ollama.generate(model="llama3", prompt=prompt)

    return response["response"].strip()

