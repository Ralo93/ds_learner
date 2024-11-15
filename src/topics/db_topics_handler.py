# database_handler.py

import json
import os
import sqlite3
from typing import List, Optional, Tuple

class DatabaseTopicHandler:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = os.path.join(os.path.dirname(__file__), "topics.db")

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table() 

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_science_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT NOT NULL,
                keyword TEXT NOT NULL, 
                explanation TEXT NOT NULL, 
                embedding BLOB,  -- To store the serialized embedding of the explanation
                category TEXT,  -- e.g., 'Machine Learning', 'Statistics', 'Deep Learning', etc.
                sub_category_1 TEXT,  -- e.g., 'Fundamentals', 'Architectures', 'Training'
                sub_category_2 TEXT,  -- e.g., 'Basics', 'Mathematics', 'FeedForwardNN'
                sub_category_3 TEXT,  -- e.g., 'Probability', 'Information Flow', 'Backpropagation'
                difficulty TEXT CHECK(difficulty IN ('basic', 'intermediate', 'advanced')) DEFAULT 'basic',  
                importance_level INTEGER CHECK(importance_level BETWEEN 1 AND 5) DEFAULT 3, -- 1 (Low) to 5 (High)
                source TEXT, -- e.g., textbook, research paper, tutorial, etc.
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Track when the topic was added
                last_reviewed TIMESTAMP, -- Track when it was last reviewed
                status TEXT CHECK(status IN ('unknown', 'known', 'learning')) DEFAULT 'unknown'
            )
        """)
        self.conn.commit()

    def get_distinct_categories(self) -> List[str]:
        """
        Retrieve a list of distinct categories from the data_science_topics table.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category FROM data_science_topics
            WHERE category IS NOT NULL
        """)
        categories = cursor.fetchall()
        # Extract the category names from the result tuples
        return [category[0] for category in categories]

    def get_items_by_category(self, category: str) -> List[Tuple[int, str]]:
        """
        Retrieve the id and explanation columns for all items in a given category.
        
        Args:
            category (str): The category to filter items by.
        
        Returns:
            List[Tuple[int, str]]: A list of tuples containing item id and explanation.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, explanation FROM data_science_topics
            WHERE category = ?
        """, (category,))
        return cursor.fetchall()

    def add_topic(self, topic_name, keyword, explanation, embedding, category, sub_category_1, sub_category_2, sub_category_3, difficulty='basic', importance_level=3, source=None, status='unknown', last_reviewed=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO data_science_topics (
                topic_name, keyword, explanation, embedding, category, sub_category_1, sub_category_2, sub_category_3,
                difficulty, importance_level, source, status, last_reviewed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic_name, keyword, explanation, embedding, category, sub_category_1, sub_category_2, sub_category_3,
            difficulty, importance_level, source, status, last_reviewed))
        self.conn.commit()

    def get_topics_by_attribute(self, attribute: str, value: str) -> List[Tuple[int, str]]:
        """
        Retrieve a list of tuples containing id and explanation columns for topics filtered by a specific attribute.

        Args:
            attribute (str): The column name to filter by.
            value (str): The value to match for the given attribute.

        Returns:
            List[Tuple[int, str]]: A list of tuples, where each tuple contains the id and explanation.
        """
        cursor = self.conn.cursor()
        query = f"SELECT id, explanation FROM data_science_topics WHERE {attribute} = ?"
        cursor.execute(query, (value,))
        return cursor.fetchall()

    def get_all_from_category(self, category):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM data_science_topics WHERE category = ?
        """, (category,))
        return cursor.fetchall()

    def update_topic(self, topic_id, attribute, new_value):
        cursor = self.conn.cursor()
        query = f"UPDATE data_science_topics SET {attribute} = ? WHERE id = ?"
        cursor.execute(query, (new_value, topic_id))
        self.conn.commit()

    def delete_topic(self, topic_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM data_science_topics WHERE id = ?
        """, (topic_id,))
        self.conn.commit()

 
    def close(self):
        self.conn.close()

    def populate_database_from_json(self, json_file: str, category=None, sub_category_1=None, sub_category_2=None, sub_category_3=None, importance_level=5, source='PAPER', status='unknown'):
        """
        Reads a JSON file containing keywords and explanations and populates the database.

        Args:
            json_file (str): Path to the JSON file.
            db_handler (DatabaseTopicHandler): An instance of DatabaseTopicHandler to interact with the database.
            category (str, optional): Category to assign to all entries. Defaults to None.
            sub_category_1 (str, optional): Sub-category 1 to assign to all entries. Defaults to None.
            sub_category_2 (str, optional): Sub-category 2 to assign to all entries. Defaults to None.
            sub_category_3 (str, optional): Sub-category 3 to assign to all entries. Defaults to None.
            importance_level (int, optional): Importance level to assign to all entries. Defaults to 3.
            source (str, optional): Source to assign to all entries. Defaults to None.
            status (str, optional): Status to assign to all entries. Defaults to 'unknown'.
        """
        # Load the JSON data
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        for entry in data:
            keyword = entry.get("Keyword")
            explanation = entry.get("Explanation")

            # Add entry to the database
            db_handler.add_topic(
                topic_name=keyword,
                keyword=keyword,
                explanation=explanation,
                embedding=None,  # No embedding provided in the JSON
                category=category,
                sub_category_1=sub_category_1,
                sub_category_2=sub_category_2,
                sub_category_3=sub_category_3,
                difficulty='advanced',  # Set to 'advanced' as per the requirement
                importance_level=importance_level,
                source=source,
                status=status
         )
if __name__ == "__main__":
    
    db_handler = DatabaseTopicHandler()

        # Path to the JSON file
    json_file_path = r"C:\Users\rapha\repositories\learning_cards\data\keywords\output.json"


    db_handler.populate_database_from_json(json_file=json_file_path)