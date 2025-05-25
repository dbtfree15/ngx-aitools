#!/usr/bin/env python3

import os
import argparse
import requests
from dotenv import load_dotenv
from modules.paperless_ai_titles import PaperlessAITitles

def fetch_document_details(paperless_url, paperless_api_key, document_id):
    """
    Fetch document details from the Paperless-ngx API.
    """
    headers = {
        "Authorization": f"Token {paperless_api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(
            f"{paperless_url}/documents/{document_id}/", headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching document details: {e}")
        return None

def main():
    # Load environment variables
    load_dotenv()

    # Get Paperless-ngx configuration from environment variables
    paperless_url = os.getenv("PAPERLESS_NGX_URL")
    paperless_api_key = os.getenv("PAPERLESS_NGX_API_KEY")
    settings_file = os.getenv("SETTINGS_FILE", "settings.yaml")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a proposed title for a document in Paperless-ngx.")
    parser.add_argument("document_id", type=int, help="The ID of the document to process.")
    args = parser.parse_args()

    document_id = args.document_id
    print(f"Document ID: {document_id}")
    print(f"Paperless URL: {paperless_url}")

    # Fetch document details
    document_details = fetch_document_details(paperless_url, paperless_api_key, document_id)
    if not document_details:
        print("Failed to fetch document details. Exiting.")
        return

    # Extract document content
    content = document_details.get("content", "")
    if not content:
        print("No content available for the document. Exiting.")
        return

    print(f"Current Document Title: {document_details.get('title', 'Unknown')}")
    print(f"Document Content: {content[:500]}...")  # Print the first 500 characters of the content

    # Initialize the AI model
    ai = PaperlessAITitles(paperless_url, paperless_api_key, settings_file)

    # Generate a proposed title
    proposed_title = ai.ai.generate_title_from_text(content)
    if proposed_title:
        print(f"Proposed Title: {proposed_title}")
    else:
        print("Failed to generate a proposed title.")

if __name__ == "__main__":
    main()