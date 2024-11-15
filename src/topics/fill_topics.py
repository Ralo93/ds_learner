import openai
import os
import json
from db_topics_handler import DatabaseTopicHandler

# Load API key from config.json
with open("config.json", "r") as file:
    config = json.load(file)

openai_api_key = config["openai"]["api_key"]
os.environ["OPENAI_API_KEY"] = openai_api_key


class TopicGenerator:
    def __init__(self, db_name=None):
        self.db_handler = DatabaseTopicHandler(db_name)

    def create_topics(self, category, sub_category_1, sub_category_2, sub_category_3, num_topics, difficulty):
        """
        Generate an overview of topics using OpenAI API and populate the database.

        Args:
            category (str): The main domain of the topics (e.g., "Deep Learning").
            sub_category_1 (str): Higher-level subdomain (e.g., "Fundamentals").
            sub_category_2 (str): Mid-level subdomain (e.g., "Mathematics for Deep Learning").
            sub_category_3 (str): Lower-level subdomain (e.g., "Gradient Descent").
            num_topics (int): Number of topics to generate.
            difficulty (str): Difficulty level (e.g., "basic", "intermediate", "advanced").
        """
        try:
            print(f"DEBUG: Starting topic generation for category '{category}', "
                  f"sub_category_1 '{sub_category_1}', sub_category_2 '{sub_category_2}', "
                  f"sub_category_3 '{sub_category_3}', {num_topics} topics, difficulty '{difficulty}'.")

            # Format the prompt
            prompt = [
                {
                    "role": "user",
                    "content": (
                        f"Create an overview of {num_topics} unique topics on a {difficulty} level for the domain "
                        f"of {category}, specifically the sub-domains {sub_category_1}, {sub_category_2}, "
                        f"and {sub_category_3}. Each topic should include a brief explanation and be suitable for flashcards. "
                        "Format your response as a JSON array with the following structure for each topic:\n"
                        "{\n"
                        "  \"topic_name\": \"Name of the topic\",\n"
                        "  \"keyword\": \"Keyword for the topic, typically a lowercase version of the topic name with underscores\",\n"
                        "  \"explanation\": \"Detailed Explanation of the topic\",\n"
                        "  \"category\": \"Main domain, e.g., 'Deep Learning'\",\n"
                        "  \"sub_category_1\": \"Specific sub-domain, e.g., 'Fundamentals' or 'Training'\",\n"
                        "  \"sub_category_2\": \"Specific sub-domain for sub_category_1, e.g., 'Basics of Deep Learning' or 'Mathematics for Deep Learning'\",\n"
                        "  \"sub_category_3\": \"Specific sub-domain for sub_category_2, e.g., 'Perceptrons' or 'Activation Functions', 'Calculus', 'Optimization'\",\n"
                        "  \"difficulty\": \"Difficulty level, e.g., 'basic', 'intermediate', 'advanced'\",\n"
                        "  \"importance_level\": \"Importance of the topic on a scale of 1 (low) to 5 (high)\",\n"
                        "  \"source\": \"Source of the explanation, e.g., 'Textbook', 'Research Paper', or 'Generated'\",\n"
                        "  \"added_date\": \"Date when this topic was added, in YYYY-MM-DD format\",\n"
                        "  \"last_reviewed\": \"Optional field for the date the topic was last reviewed, or null\",\n"
                        "  \"status\": \"Learning status, e.g., 'unknown', 'learning', or 'known'\"\n"
                        "}"
                        "Ensure the output is strictly a valid JSON array."
                    )
                },
            ]

            print("DEBUG: Prompt prepared. Sending request to OpenAI API...")

            # Make the API call
            response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=prompt,
                        max_tokens=2000,
                        temperature=0.7
                    )

            print("DEBUG: Response received from OpenAI API.")

            # Parse response
            response_text = response.choices[0].message.content.strip()
            print(f"DEBUG: Response text: {response_text}")

            try:
                topics = json.loads(response_text)
                print("DEBUG: Parsed JSON response successfully.")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON response: {response_text}")
                raise e

            # Validate topics structure
            if not isinstance(topics, list):
                print(f"ERROR: Response is not a JSON array of topics. Received: {topics}")
                raise ValueError("Response is not a JSON array of topics")

            print(f"DEBUG: Validating and adding {len(topics)} topics to the database.")

            # Populate the database
            for topic in topics:
                topic_name = topic.get("topic_name")
                explanation = topic.get("explanation")
                keyword = topic.get("keyword")
                importance_level = topic.get("importance_level", 3)
                status = topic.get("status", "unknown")
                source = topic.get("source", "Generated")

                if not topic_name or not explanation:
                    print(f"ERROR: Incomplete topic data: {topic}")
                    raise ValueError("Topic data is incomplete")

                print(f"DEBUG: Adding topic '{topic_name}' to the database.")
                self.db_handler.add_topic(
                    topic_name=topic_name,
                    keyword=keyword,
                    explanation=explanation,
                    embedding=None,  # Currently, no embedding is stored
                    category=category,
                    sub_category_1=sub_category_1,
                    sub_category_2=sub_category_2,
                    sub_category_3=sub_category_3,
                    difficulty=difficulty,
                    importance_level=importance_level,
                    source=source,
                    last_reviewed=None,  # Default to NULL
                    status=status
                )

            print(f"INFO: Successfully added {len(topics)} topics to the database.")

        except openai.OpenAIError as e:
            print(f"ERROR: OpenAI API error: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON decoding error: {str(e)}")
        except ValueError as e:
            print(f"ERROR: Validation error: {str(e)}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {str(e)}")

    def close(self):
        """Close the database connection."""
        try:
            self.db_handler.close()
        except Exception as e:
            print(f"Error closing database connection: {str(e)}")

import json

def load_topics_from_json(file_path):
    """Load topics from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    # Load topics from the JSON file
    topics_file = "topics.json"
    topics = load_topics_from_json(topics_file)

    # Initialize generator
    generator = TopicGenerator(db_name="topics.db")

    # Loop through the topics from the JSON file
    for topic in topics:
        category = topic["category"]
        sub_category_1 = topic["sub_category_1"]
        sub_category_2 = topic["sub_category_2"]
        sub_category_3 = topic["sub_category_3"]
        difficulty = topic["difficulty"]
        num_topics = 1  # Generating one topic at a time

        print(f"Adding topic: {category} > {sub_category_1} > {sub_category_2} > {sub_category_3} ({difficulty})")

        # Generate topics and populate the database
        generator.create_topics(category, sub_category_1, sub_category_2, sub_category_3, num_topics, difficulty)

    # Close the database connection
    generator.close()
