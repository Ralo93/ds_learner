import openai
import os
from db_handler import DatabaseHandler
import json

# Load config.json
with open("config.json", "r") as file:
    config = json.load(file)

# Access the API key
openai_api_key = config["openai"]["api_key"]

# Set it as an environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

class FlashcardGenerator:
    def __init__(self, db_name=None):
        self.db_handler = DatabaseHandler(db_name)

    def generate_flashcards(self, category, difficulty, num_flashcards=5):
        """
        Generate unique flashcards for a given topic and difficulty using OpenAI.
        
        Args:
            category (str): The topic category for the flashcards
            difficulty (str): The difficulty level (e.g., "easy", "medium", "hard")
            num_flashcards (int): Number of unique flashcards to generate (default: 5)
            
        Returns:
            int: Number of successfully generated unique flashcards
        """
        successful_cards = 0
        generated_questions = {question for _, question in self.db_handler.get_all_questions()}
        max_attempts = num_flashcards * 2  # Allow for some retry attempts
        attempt_count = 0
        
        try:
            while successful_cards < num_flashcards and attempt_count < max_attempts:
                try:
                    # Format the prompt to explicitly request unique content
                    prompt = [
                        {
                            "role": "user",
                            "content": (
                                f"Generate a unique and specific flashcard on the topic '{category}' "
                                f"with a difficulty level of {difficulty}. Ensure the question is distinct "
                                f"from these previously generated questions: {list(generated_questions)}.\n\n"
                                "Format your response as follows:\n"
                                "Question: [Insert your unique, specific machine learning question here]\n"
                                "Answer: [Provide a detailed, precise answer here]"
                            )
                        },
                        {
                            "role": "system",
                            "content": (
                                "You provide excellent short summaries about data science and machine learning topics and convert them into question-answering pairs. You shine in communicating complex topics in different levels of abstraction, from high (basic) to"
                                "very detailed (advanced). Try to add mathematical examples and expressions where applicable to further enhance understanding of the concepts by trying to answer your questions."
                                "Take your time to think if your answer is factually correct, and add sources at the end of your response."
                                "Ensure the question is both unique and detailed. Avoid overly broad questions. If math is involved, you can add examples in the question and add the answer in the answer section."
                                "For example, instead of asking 'What is overfitting?', ask: "
                                "'How does adding dropout layers mitigate overfitting in neural networks, and what is the trade-off?'"
                            )
                        }
                    ]


                    # Make API call with higher temperature for more variety
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=prompt,
                        max_tokens=400,
                        temperature=0.7,  # Higher temperature for more variety
                        presence_penalty=0.5,  # Encourage unique content
                        frequency_penalty=0.5,  # Discourage repetition
                        n=1
                    )

                    # Extract response text
                    response_text = response.choices[0].message.content.strip()

                    # Parse response
                    if "Question:" not in response_text or "Answer:" not in response_text:
                        raise ValueError("Response not in expected format")

                    # Split into question and answer
                    parts = response_text.split("Question:", 1)
                    qa_text = parts[1] if len(parts) > 1 else parts[0]
                    
                    question_answer = qa_text.split("Answer:", 1)
                    if len(question_answer) != 2:
                        raise ValueError("Could not separate question and answer")

                    question = question_answer[0].strip()
                    answer = question_answer[1].strip()

                    # Validate content
                    if not question or not answer:
                        raise ValueError("Empty question or answer")
                    
                    # Check for minimum length and complexity
                    if len(question) < 15 or len(answer) < 20:
                        raise ValueError("Question or answer too short")

                    # Check uniqueness
                    question_key = question.lower()
                    if question_key in generated_questions:
                        raise ValueError("Duplicate question generated")

                    # Add to tracking set and database
                    generated_questions.add(question_key)
                    self.db_handler.add_flashcard(question, answer, category, difficulty)
                    successful_cards += 1
                    
                    print(f"Generated unique flashcard {successful_cards}/{num_flashcards}:")
                    print(f"Q: {question}")
                    print(f"A: {answer}\n")

                except openai.OpenAIError as e:
                    print(f"OpenAI API error: {str(e)}")
                except ValueError as e:
                    print(f"Validation error: {str(e)}")
                except Exception as e:
                    print(f"Unexpected error while generating flashcard: {str(e)}")
                
                attempt_count += 1
                if attempt_count >= max_attempts and successful_cards < num_flashcards:
                    print(f"Warning: Could only generate {successful_cards} unique flashcards "
                        f"after {max_attempts} attempts")

            return successful_cards

        except Exception as e:
            print(f"Critical error in flashcard generation: {str(e)}")
            return successful_cards
        
        finally:
            # If you want to ensure some cleanup happens
            pass

    def generate_flashcard_from_question(self, question, category, difficulty):
        
        """
        Generate a flashcard based on a predefined question and use OpenAI to get an answer.
        
        Args:
            question (str): The predefined question to generate a flashcard for.
            category (str): The topic category for the flashcard.
            difficulty (str): The difficulty level (e.g., "easy", "medium", "hard").
            
        Returns:
            bool: True if the flashcard was successfully generated and stored, False otherwise.
        """
        try:
            # Format the prompt for OpenAI to answer the provided question
            prompt = [
                {
                    "role": "user",
                    "content": (
                        f"Provide a detailed answer for the following question on the topic '{category}' "
                        f"with a intermediate difficulty level.\n\n"
                        f"Question: {question}\n"
                        "Answer: [Provide a detailed answer here]"
                    )
                }
            ]
            prompt = [
                        {
                            "role": "user",
                            "content": (
                                f"Provide a detailed answer for the following question on the topic '{category}' "
                                f"with an intermediate difficulty level. "
                                "Format your response as follows:\n"
                                f"Question: [Insert the provided question here, which is {question}]\n"
                                "Answer: [Provide a detailed, precise answer here]"
                            )
                        },
                        {
                            "role": "system",
                            "content": (
                                "You provide excellent short summaries about data science and machine learning topics and convert them into question-answering pairs. You shine in communicating complex topics in different levels of abstraction, from high (basic) to"
                                "very detailed (advanced). Try to add mathematical examples and expressions where applicable to further enhance understanding of the concepts by trying to answer your questions."
                                "Take your time to think if your answer is factually correct, and add sources at the end of your response."
                            )
                        }
                    ]

            # Make API call
            response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=prompt,
                        max_tokens=500,
                        temperature=0.3
                    )

            # Extract response text
            response_text = response.choices[0].message.content.strip()

            # Validate response format
            if "Answer:" not in response_text:
                raise ValueError("Response not in expected format")

            # Extract answer from response
            answer = response_text.split("Answer:", 1)[1].strip()

            # Check answer validity
            if not answer or len(answer) < 20:
                raise ValueError("Generated answer is too short or empty")

            # Add flashcard to the database
            #self.db_handler.add_flashcard(question, answer, category, difficulty)
            
            print(f"Generated flashcard for predefined question:\nQ: {question}\nA: {answer}\n")
            return answer

        except openai.OpenAIError as e:
            print(f"OpenAI API error: {str(e)}")
        except ValueError as e:
            print(f"Validation error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error while generating flashcard from question: {str(e)}")
        
        return False


    def close(self):
        """Close the database connection."""
        try:
            self.db_handler.close()
        except Exception as e:
            print(f"Error closing database connection: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = FlashcardGenerator()
    
    # Define topic and difficulty
    category = "Databases"
    difficulty = "basic"
    
    # Generate flashcards for the specified topic and difficulty
    generator.generate_flashcards(category, difficulty, num_flashcards=20)
    
    # Close the database connection
    generator.close()
