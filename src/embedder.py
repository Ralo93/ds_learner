import json
import pickle
import os
import openai
from typing import List, Tuple, Optional
from db_handler import *

from langchain_openai import OpenAIEmbeddings

# Load config.json
with open("config.json", "r") as file:
    config = json.load(file)

# Access the API key
openai_api_key = config["openai"]["api_key"]
openai.api_key = openai_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key  # Ensure it's available as an env variable

# Check if the API key was set successfully
print("API Key:", openai.api_key)

embeddings = OpenAIEmbeddings()

# Define Embedder class
class Embedder:
    def __init__(self, model_engine: str = "text-embedding-ada-002", save_path: str = "../data/"):
        self.model_engine = model_engine
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)
        self.embeddings_dict = {}  # Dictionary to store embeddings
        self.embd_path = os.path.join(self.save_path, "embeddings_db.pkl")

    def create_embedding(self, text: str, flashcard_id: int) -> Optional[List[float]]:
        try:
            # Initialize embeddings and create embedding
            embeddings = OpenAIEmbeddings()
            response = embeddings.embed_documents([text])  # Returns a list of embeddings

            # Check if response is valid and contains at least one embedding
            if response and isinstance(response, list) and len(response) > 0:
                embedding = response[0]
                # Store embedding in the dictionary using flashcard_id as key
                self.embeddings_dict[flashcard_id] = embedding
                return embedding
            else:
                print(f"No embedding returned for flashcard ID {flashcard_id}.")
                return None
        except Exception as e:
            print(f"Error creating embedding for flashcard ID {flashcard_id}: {e}")
            return None

    def save_embeddings(self) -> None:
        # Save all embeddings in a single pickle file
        with open(self.embd_path, "wb") as f:
            pickle.dump(self.embeddings_dict, f)
        print(f"All embeddings saved at {self.embd_path}")


def main():

    db = DatabaseHandler()

    # Initialize Embedder
    embedder = Embedder(save_path="./data/")

    # Define the category and optional status filter
    category = "Databases"
    status = "unknown"  # Change to None if you want all statuses

    # Retrieve flashcards by category and status
    flashcards = db.get_flashcards_by_category(category, status)

    # Create embeddings for the answer part of each flashcard
    for flashcard_id, question, answer in flashcards:
        print(f"Processing flashcard ID: {flashcard_id}")
        # Only retrieve the embedding (no need to unpack two values)
        embedding = embedder.create_embedding(answer, flashcard_id)
        if embedding is not None:
            print(f"Embedding created for flashcard ID {flashcard_id}")
        else:
            print(f"Failed to create embedding for flashcard ID {flashcard_id}")

    # Save all embeddings in a single file
    embedder.save_embeddings()


if __name__ == "__main__":
    main()