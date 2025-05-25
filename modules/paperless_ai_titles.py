import requests
import yaml

from modules.ollama_titles import OllamaTitles
from modules.openai_titles import OpenAITitles


class PaperlessAITitles:
    def __init__(self, paperless_url, paperless_api_key, settings_file="settings.yaml"):
        self.paperless_url = paperless_url
        self.paperless_api_key = paperless_api_key
        self.settings = self.__load_settings(settings_file)
        self.ai = self.__initialize_ai(settings_file)

    def __load_settings(self, settings_file):
        try:
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading settings file: {e}")
            return None

    def __initialize_ai(self, settings_file):
        model = self.settings.get("model", "ollama")  # Default to "ollama" if not specified
        if model == "ollama":
            print("Using Ollama model.")
            return OllamaTitles(settings_file)
        elif model == "openai":
            print("Using OpenAI model.")
            openai_api_key = self.settings.get("openai_api_key", None)
            if not openai_api_key:
                raise ValueError("OpenAI API key is missing in settings.yaml.")
            return OpenAITitles(openai_api_key, settings_file)
        else:
            raise ValueError(f"Unsupported model type: {model}")

    def __get_document_details(self, document_id):
        headers = {
            "Authorization": f"Token {self.paperless_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{self.paperless_url}/documents/{document_id}/", headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Failed to get document details from paperless-ngx. Status code: {response.status_code}"
            )
            print(response.text)
            return None

    def __update_document_title(self, document_id, new_title):
        payload = {"title": new_title}

        headers = {
            "Authorization": f"Token {self.paperless_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.patch(
            f"{self.paperless_url}/documents/{document_id}/",
            json=payload,
            headers=headers,
        )

        if response.status_code == 200:
            print(
                f"Title of {document_id} successfully updated in paperless-ngx to {new_title}."
            )
        else:
            print(
                f"Failed to update title in paperless-ngx. Status code: {response.status_code}"
            )
            print(response.text)

    def generate_and_update_title(self, document_id):
        document_details = self.__get_document_details(document_id)
        if document_details:
            print(f"Current Document Title: {document_details['title']}")

            content = document_details.get("content", "")

            new_title = self.ai.generate_title_from_text(content)

            if new_title:
                print(f"Generated Document Title: {new_title}")

                self.__update_document_title(document_id, new_title)
            else:
                print("Failed to generate the document title.")
        else:
            print("Failed to retrieve document details.")
