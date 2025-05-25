#!/usr/bin/env python3

import os
import argparse
import yaml

from dotenv import load_dotenv
import pdfplumber

from modules.ollama_titles import OllamaTitles
from modules.openai_titles import OpenAITitles

load_dotenv()

def load_settings(settings_file="settings.yaml"):
    try:
        with open(settings_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading settings file: {e}")
        return None

def initialize_ai(settings, settings_file):
    model = settings.get("model", "ollama")  # Default to "ollama" if not specified
    if model == "ollama":
        print("Using Ollama model.")
        return OllamaTitles(settings_file)
    elif model == "openai":
        print("Using OpenAI model.")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key is missing in environment variables.")
        return OpenAITitles(openai_api_key, settings_file)
    else:
        raise ValueError(f"Unsupported model type: {model}")

def main():
    settings_file = os.getenv("SETTINGS_FILE", "/usr/src/ngx-renamer/settings.yaml")
    settings = load_settings(settings_file)
    if not settings:
        print("Failed to load settings. Exiting.")
        return

    ai = initialize_ai(settings,settings_file)

    parser = argparse.ArgumentParser(description="Get the title of a PDF document")
    parser.add_argument("filename", type=str, help="Path to the PDF file")
    args = parser.parse_args()

    with pdfplumber.open(args.filename) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    new_title = ai.generate_title_from_text(text)

    if new_title:
        print(f"Generated Document Title: {new_title}")
    else:
        print("Failed to generate the document title.")

if __name__ == "__main__":
    main()