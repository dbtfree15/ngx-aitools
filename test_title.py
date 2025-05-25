#!/usr/bin/env python3

import os
import yaml
from dotenv import load_dotenv

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

    ai = initialize_ai(settings, settings_file)

    text = """
John Doe
    123 Main Street
    Helena, MT 59601

    May 16, 2025

    Jane Smith
    456 Elm Street
    Helena, MT 59601

    Dear Ms. Smith,

    I hope this letter finds you well. I am writing to address a concern regarding the property line between our respective properties located at 123 Main Street and 456 Elm Street in Helena, Montana.

    Recently, I noticed that a portion of the fence separating our properties appears to have been moved several feet onto my property. This has raised concerns about the accuracy of the property line as defined in our respective deeds. To ensure clarity and avoid any misunderstandings, I believe it would be beneficial for both of us to review the property boundaries.

    I propose that we hire a licensed surveyor to conduct a professional survey of the property line. This will provide an accurate and impartial determination of the boundary and help resolve any discrepancies. I am willing to share the cost of the survey equally with you.

    Please let me know if this proposal works for you, or if you have any other suggestions for resolving this matter. I believe that addressing this issue promptly and amicably is in the best interest of both parties.

    Thank you for your attention to this matter. I look forward to hearing from you soon.

    Sincerely,
    John Doe               
"""
    new_title = ai.generate_title_from_text(text)
    print(f"Generated Title: {new_title}")


if __name__ == "__main__":
    main()
