# database_handler.py

import os
import sqlite3
from typing import List, Optional, Tuple

class DatabaseHandler:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = os.path.join(os.path.dirname(__file__), "flashcards.db")

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table() 

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                category TEXT,
                difficulty TEXT DEFAULT 'basic',  
                status TEXT CHECK(status IN ('unknown', 'known')) DEFAULT 'unknown'
            )
        """)
        self.conn.commit()


    def add_flashcard(self, question: str, answer: str, category: str, difficulty: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO flashcards (question, answer, category, difficulty, status)
            VALUES (?, ?, ?, ?, 'unknown')
        """, (question, answer, category, difficulty))
        self.conn.commit()

    def get_flashcards_by_category(self, category: str, status: str = "unknown") -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, question, answer FROM flashcards
            WHERE category = ? AND status = ?
        """, (category, status))
        return cursor.fetchall()

    def update_flashcard_status(self, flashcard_id: int, status: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE flashcards SET status = ? WHERE id = ?
        """, (status, flashcard_id))
        self.conn.commit()

    def get_flashcard_summary(self):
        self.cursor.execute("SELECT category, status, COUNT(*) FROM flashcards GROUP BY category, status")
        return self.cursor.fetchall()
    
    def get_flashcard_summary_with_diff(self):
        self.cursor.execute("""
            SELECT category, status, difficulty, COUNT(*) as count 
            FROM flashcards 
            GROUP BY category, status, difficulty
            ORDER BY category, difficulty
        """)
        return self.cursor.fetchall()
    
    def get_flashcards_by_category(self, category: str, status: Optional[str] = None) -> List[Tuple]:
        """
        Retrieve flashcards by category, optionally filtered by status.
        
        Args:
            category (str): The category to filter flashcards by.
            status (Optional[str]): Optional status filter ("unknown" or "known").
        
        Returns:
            List[Tuple]: List of tuples containing flashcard information.
        """
        cursor = self.conn.cursor()
        if status:
            cursor.execute("""
                SELECT id, question, answer FROM flashcards
                WHERE category = ? AND status = ?
            """, (category, status))
        else:
            cursor.execute("""
                SELECT id, question, answer FROM flashcards
                WHERE category = ?
            """, (category,))
        return cursor.fetchall()


    def get_all_flashcards(self):
        try:
            self.cursor.execute('''
                SELECT id, question, answer, category, difficulty, status
                FROM flashcards 
                ORDER BY category, difficulty
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving flashcards: {e}")
            return []
        
    def get_all_questions(self):
        try:
            self.cursor.execute('''
                SELECT id, question
                FROM flashcards 
                ORDER BY category, question
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving flashcards: {e}")
            return []

    def update_flashcard(self, flashcard_id, question, answer, category, difficulty):
        try:
            self.cursor.execute('''
                UPDATE flashcards 
                SET question = ?, answer = ?, category = ?, difficulty = ? 
                WHERE id = ?
            ''', (question, answer, category, difficulty, flashcard_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating flashcard: {e}")
            return False
        
    def get_flashcards_by_filters(self, category, status, difficulty):
        query = "SELECT * FROM flashcards WHERE category = ? AND status = ?"
        params = [category, status]
        
        if difficulty != "All":
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
        
        # In db_handler.py or equivalent file
    def update_flashcard_status(self, flashcard_id, status="unknown"):
        query = "UPDATE flashcards SET status = ? WHERE id = ?"
        self.cursor.execute(query, (status, flashcard_id))
        self.conn.commit()

    def delete_flashcard(self, flashcard_id):
        try:
            self.cursor.execute('DELETE FROM flashcards WHERE id = ?', (flashcard_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting flashcard: {e}")
            return False

    def close(self):
        self.conn.close()


#db_handler = DatabaseHandler()