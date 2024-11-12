class Flashcard:
    def __init__(self, question, answer, category, difficulty="basic", status="unknown"):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty  # New attribute for difficulty level
        self.status = status

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "difficulty": self.difficulty,  # Include difficulty in the dictionary
            "status": self.status,
        }
