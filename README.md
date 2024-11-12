
# Flashcard Application

The Flashcard Application is a Python-based study aid designed to help users create, manage, and review flashcards. The app supports various features, including categorizing flashcards, assigning difficulty levels, and tracking study progress. This app uses an SQLite database (`data.db`) to store flashcard information.

## Features

- **Add Flashcards**: Easily create flashcards by providing a question, answer, category, difficulty level, and status.
- **Edit and Delete Flashcards**: Update or remove flashcards to maintain an up-to-date study list.
- **Organize by Category and Difficulty**: Filter and review flashcards based on categories or difficulty levels.
- **Progress Tracking**: Track your flashcards' review status to focus on areas that need improvement.
- **Advanced Search**: Implement future upgrades like advanced search to enhance study focus.

## Setup

### Prerequisites

- Python 3.x installed
- Required libraries installed (if using a virtual environment)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/flashcard-app.git
   cd flashcard-app
   ```

2. **Install Dependencies**

   (Optionally set up a virtual environment)

   ```bash
   python -m venv venv
   source venv/bin/activate       # On macOS/Linux
   venv\Scripts\activate          # On Windows
   ```

   Then install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**

   Create a `config.json` file in the root directory to hold your API keys or other configurations:

   ```json
   {
       "openai": {
           "api_key": "your_api_key_here"
       }
   }
   ```

4. **Initialize the Database**

   Run the application once to initialize the SQLite database as `data.db`, or use the following command to create tables based on the `Flashcard` schema:

   ```bash
   python src/app.py
   ```

## Usage

1. **Starting the Application**

   Launch the application by running:

   ```bash
   python src/app.py
   ```

2. **Creating Flashcards**

   Add new flashcards by specifying the following details:
   - **Question**: The question on the flashcard.
   - **Answer**: The answer to the question.
   - **Category**: The category under which the flashcard falls.
   - **Difficulty**: The difficulty level (e.g., easy, medium, hard).
   - **Status**: A status indicator (e.g., reviewed, pending).

3. **Tracking Progress**

   The app includes options to mark flashcards as reviewed or pending, helping you keep track of progress as you study.

4. **Advanced Video Search (Planned Feature)**

   We are working on implementing advanced video search capabilities, allowing users to input a query (e.g., "yellow hat") to identify frames in a video containing the specified object.

## Code Structure

```plaintext
flashcard-app/
│
├── config.json               # Configuration file for API keys and settings
├── data.db                   # SQLite database file
├── requirements.txt          # Dependencies list
└── src/
    ├── app.py                # Main application script
    ├── functional/
    │   └── advanced_search.py # Planned module for advanced video search
    ├── models/
    │   └── flashcard.py       # Flashcard model definition
    └── utils/
        └── db_init.py        # Database initialization script
```

## Future Enhancements

- **Advanced Video Search**: Search frames or indexes in a video by object recognition.
- **Flashcard Stats**: Generate insights on the study session, including time spent and accuracy.
- **Customizable Categories**: Add, modify, and delete categories for better flashcard organization.

## Contributing

Feel free to open issues or submit pull requests to improve the application.
