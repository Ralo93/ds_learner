class Topic:
    def __init__(self, topic_id=None, topic_name=None, keyword=None, explanation=None, embedding=None,
                 category=None, sub_category_1=None, sub_category_2=None, sub_category_3=None, difficulty='basic',
                 importance_level=3, source=None, added_date=None, last_reviewed=None, status='unknown'):
        """
        Initialize a Topic instance.
        """
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.keyword = keyword
        self.explanation = explanation
        self.embedding = embedding  # Serialized embedding, if any
        self.category = category
        self.sub_category_1 = sub_category_1
        self.sub_category_2 = sub_category_2
        self.sub_category_3 = sub_category_3
        self.difficulty = difficulty
        self.importance_level = importance_level
        self.source = source
        self.added_date = added_date
        self.last_reviewed = last_reviewed
        self.status = status

    def to_dict(self):
        """
        Convert the Topic instance to a dictionary.
        """
        return {
            "topic_id": self.topic_id,
            "topic_name": self.topic_name,
            "keyword": self.keyword,
            "explanation": self.explanation,
            "embedding": self.embedding,
            "category": self.category,
            "sub_category_1": self.sub_category_1,
            "sub_category_2": self.sub_category_2,
            "sub_category_3": self.sub_category_3,
            "difficulty": self.difficulty,
            "importance_level": self.importance_level,
            "source": self.source,
            "added_date": self.added_date,
            "last_reviewed": self.last_reviewed,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Topic instance from a dictionary.
        """
        return Topic(
            topic_id=data.get("topic_id"),
            topic_name=data.get("topic_name"),
            keyword=data.get("keyword"),
            explanation=data.get("explanation"),
            embedding=data.get("embedding"),
            category=data.get("category"),
            sub_category_1=data.get("sub_category_1"),
            sub_category_2=data.get("sub_category_2"),
            sub_category_3=data.get("sub_category_3"),
            difficulty=data.get("difficulty", "basic"),
            importance_level=data.get("importance_level", 3),
            source=data.get("source"),
            added_date=data.get("added_date"),
            last_reviewed=data.get("last_reviewed"),
            status=data.get("status", "unknown"),
        )

    def __str__(self):
        """
        String representation of the Topic instance.
        """
        return f"Topic({self.to_dict()})"
