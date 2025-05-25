from datetime import datetime
import requests
import yaml
import time
import json  # Import json to handle potential parsing issues


class OllamaTitles:
    def __init__(self, settings_file="settings.yaml") -> None:
        self.settings = self.__load_settings(settings_file)

    def __load_settings(self, settings_file):
        try:
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading settings file: {e}")
            return None

    def __ask_ollama(self, content):
        max_retries = 3
        retry_delay = 3
        for attempt in range(max_retries):
            try:
                model = self.settings.get("ollama_model", "llama3.2:3b")
                api_url = self.settings.get("ollama_api_url", "http://localhost:8271")
                response = requests.post(
                    f"{api_url}/api/generate",  # Corrected URL to match Ollama's API
                    json={"model": model, "prompt": content, "stream": False},
                    timeout=200
                )
                response.raise_for_status()
    
                # Handle potential multi-line JSON response
                try:
                    return json.loads(response.text)  # Parse JSON response
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response: {response.text}")
                    return None
            except Exception as e:
                print(f"Attempt {attempt + 1} failed. Error generating title from Ollama: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Max retries exceeded.")
                    return None

    def generate_title_from_text(self, text):
        with_date = self.settings.get("with_date", False)
        setting_prompt = self.settings.get("prompt", None)
        if setting_prompt:
            prompt = setting_prompt.get("main", "")

            if with_date:
                current_date = datetime.today().strftime("%Y-%m-%d")
                with_date_prompt = setting_prompt.get("with_date", "")
                with_date_prompt = with_date_prompt.replace("{current_date}", current_date)
                prompt += with_date_prompt
            else:
                prompt += setting_prompt.get("no_date", "")
            prompt += setting_prompt.get("pre_content", "") + text
            prompt += setting_prompt.get("post_content", "")
            result = self.__ask_ollama(prompt)
            if result and "response" in result:  # Adjusted to match the expected response format
                return result["response"]
            else:
                print("No valid response from Ollama.")
                return None
        else:
            print("Prompt settings not found.")
            return None