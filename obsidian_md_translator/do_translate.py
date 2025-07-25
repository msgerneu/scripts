import os
import re
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Translator configuration
AZURE_TRANSLATOR_KEY = os.getenv('AZURE_TRANSLATOR_KEY')
AZURE_TRANSLATOR_ENDPOINT = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
AZURE_TRANSLATOR_REGION = os.getenv('AZURE_TRANSLATOR_REGION')
API_VERSION = '3.0'

# Regex patterns to preserve Markdown artifacts
LINK_PATTERN = re.compile(r'!\[[^\]]*\]\([^\)]+\)|\[[^\]]*\]\([^\)]+\)')
INLINE_CODE_PATTERN = re.compile(r'\[\[[^\]]+\]\]')
# Patterns to exclude from translation
EXCLUDE_PATTERNS = [re.compile(r'Link:', re.IGNORECASE), re.compile(r'Source:', re.IGNORECASE)]

def translate_text(text, from_lang='en', to_lang='de'):
    url = f"{AZURE_TRANSLATOR_ENDPOINT}/translate?api-version={API_VERSION}&from={from_lang}&to={to_lang}"
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
        'Content-type': 'application/json'
    }

    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()[0]['translations'][0]['text']

def preserve_and_translate(content):
    # Find and preserve Markdown artifacts and excluded patterns
    preserved = LINK_PATTERN.findall(content) + INLINE_CODE_PATTERN.findall(content)
    for pattern in EXCLUDE_PATTERNS:
        preserved += pattern.findall(content)

    placeholders = [f"__PLACEHOLDER_{i}__" for i in range(len(preserved))]

    for original, placeholder in zip(preserved, placeholders):
        content = content.replace(original, placeholder)

    translated = translate_text(content)

    for placeholder, original in zip(placeholders, preserved):
        translated = translated.replace(placeholder, original)

    return translated

def translate_md_files(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith('.md'):
                rel_path = os.path.relpath(root, input_dir)
                target_dir = os.path.join(output_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)

                input_path = os.path.join(root, filename)
                output_path = os.path.join(target_dir, filename)
                print(input_path)

                with open(input_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                translated_content = preserve_and_translate(content)

                with open(output_path, 'w', encoding='utf-8') as outfile:
                    outfile.write(translated_content)

# Example usage
if __name__ == '__main__':
    input_directory = os.getenv('INPUT_DIRECTORY')
    output_directory = os.getenv('OUTPUT_DIRECTORY')
    translate_md_files(input_directory, output_directory)
    print("Done")
