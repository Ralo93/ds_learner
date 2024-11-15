import json
import pickle
import os
from typing import List, Optional
import openai

from db_topics_handler import DatabaseTopicHandler
from langchain_openai import OpenAIEmbeddings

# Load config.json
with open("../config.json", "r") as file:
    config = json.load(file)

# Access the API key
openai_api_key = config["openai"]["api_key"]
openai.api_key = openai_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key

print("API Key loaded successfully.")


class Embedder:
    def __init__(self, model_engine: str = "text-embedding-ada-002"):
        self.model_engine = model_engine

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Creates embedding for a given text using OpenAI Embeddings."""
        try:
            embeddings = OpenAIEmbeddings()
            response = embeddings.embed_documents([text])
            if response and isinstance(response, list) and len(response) > 0:
                return response[0]
            else:
                print(f"Failed to generate embedding for text: {text}")
                return None
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None


def main():
    # Initialize database handler and embedder
    db = DatabaseTopicHandler()
    embedder = Embedder()

    # Retrieve distinct categories from the database
    categories = db.get_distinct_categories()

    for category in categories:
        print(f"Processing category: {category}")

        # Retrieve items with explanations in the category
        items = db.get_items_by_category(category)

        for item_id, explanation in items:
            print(f"Processing item ID: {item_id}")
            embedding = embedder.create_embedding(explanation)
            if embedding:
                # Save embedding directly into the database
                db.update_topic(item_id, "embedding", pickle.dumps(embedding))
                print(f"Embedding saved for item ID {item_id}")
            else:
                print(f"Failed to create embedding for item ID {item_id}")


def main_by_paper():
    # Initialize database handler and embedder
    db = DatabaseTopicHandler()
    embedder = Embedder()

    # Retrieve items with explanations in the category and "source" == "PAPER"
    items = db.get_topics_by_attribute("source", "PAPER")
    #print(items)

    for item_id, explanation in items:
        print(f"Processing item ID: {item_id}")
        
        # Generate embedding for the explanation
        embedding = embedder.create_embedding(explanation)
        if embedding:
            # Save embedding directly into the database
            db.update_topic(item_id, "embedding", pickle.dumps(embedding))
            print(f"Embedding saved for item ID {item_id}")
        else:
            print(f"Failed to create embedding for item ID {item_id}")

    # Close the database connection
    db.close()

if __name__ == "__main__":

    main_by_paper()
