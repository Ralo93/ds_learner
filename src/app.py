# app.py
import time
import streamlit as st
import random
#from db_handler import *
from flashcard import *
import plotly.express as px
import pandas as pd
from fill_cards import *

# Initialize database
#db_handler = DatabaseHandler()
filler = FlashcardGenerator()

# Set Streamlit to wide layout
st.set_page_config(layout="wide")

st.title("Data Science Learning App")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Practice Flashcards", "Create/Update Flashcards", "Visualize Flashcards", "DB Browser"])

categories = [
    "General", "Linear Algebra for Machine Learning", "Bash & Git", "SQL", "Probability & Statistics", "Data Science Fundamentals", 
    "Machine Learning Fundamentals", "Visualization", "Object Oriented Programming in Python", "Advanced Trees in Machine Learning", "Time Series", "Computer Vision", "Graph Neural Networks", "Backpropagation", 
    "Databases", "Docker", "Deep Learning", "Streamlit", "NLP", "Transformers", 
    "Transfer Learning", "LLM Optimization", "Fine Tuning LLMs", "Debugging Deep Learning", 
    "Vision Transformers", "CV Projects", "Soft Skills"
]

#HOW TO KEEP UP TO DATE



with tab2:
    st.header("Create/Update Flashcards")
    
    # Create two columns for mode selection
    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        mode = st.radio("Choose mode:", ["Create New", "Update Existing"])

    if mode == "Create New":
        # Create new flashcard form
        question = st.text_input("Question")
        category = st.selectbox("Category", categories)
        difficulty = st.selectbox("Difficulty", ["basic", "intermediate", "advanced"])
        
        # Initialize answer in session state if not exists
        if "current_answer" not in st.session_state:
            st.session_state.current_answer = ""
        
        # Button to generate answer
        if st.button("Auto Answer", use_container_width=True):
            if question and category:
                try:
                    answer = filler.generate_flashcard_from_question(question, category, difficulty)
                    if answer:
                        st.session_state.current_answer = answer
                        st.success("Answer generated successfully!")
                    else:
                        st.error("Failed to generate an answer. Please try again.")
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
            else:
                st.warning("Please fill in all required fields.")

        # Always show the answer text area, populated with session state if available
        answer = st.text_area(
            "Answer", 
            value=st.session_state.current_answer,
            height=200,
            key="answer_input"
        )
        
        # Add flashcard button
        if st.button("Add Flashcard", use_container_width=True):
            if question and answer and category:
                try:
                    filler.db_handler.add_flashcard(question, answer, category, difficulty)
                    st.success("Flashcard added successfully!")
                    # Clear the form
                    st.session_state.current_answer = ""
                    # Rerun to reset the form
                    time.sleep(0.5)  # Small delay to show success message
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding flashcard to database: {str(e)}")
            else:
                st.error("Please fill in all fields.")

    else:  # Update mode
        # Select category first
        selected_category = st.selectbox("Select Category", categories)

        # Filter flashcards by the selected category
        flashcards_in_category = filler.db_handler.get_flashcards_by_category(selected_category)

        if flashcards_in_category:
            # Create a selection box with filtered questions as options
            flashcard_options = {f"{card[1]} (ID: {card[0]})": card for card in flashcards_in_category}
            selected_flashcard = st.selectbox(
                "Select flashcard to update",
                options=list(flashcard_options.keys()),
                index=0
            )

            # Get the selected flashcard details
            current_flashcard = flashcard_options[selected_flashcard]
            flashcard_id = current_flashcard[0]

            # Pre-fill form with existing data
            updated_question = st.text_input("Question", value=current_flashcard[1])
            updated_answer = st.text_area("Answer", value=current_flashcard[2], height=200)
            #print(current_flashcard)
            updated_difficulty = st.selectbox(
                "Difficulty",
                ["basic", "intermediate", "advanced"],
                index=["basic", "intermediate", "advanced"].index(current_flashcard[2]) 
                if current_flashcard[2] in ["basic", "intermediate", "advanced"] else 0  # Default to "basic"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Flashcard", use_container_width=True):
                    if updated_question and updated_answer:
                        # Update flashcard in the database
                        filler.db_handler.update_flashcard(
                            flashcard_id,
                            updated_question,
                            updated_answer,
                            selected_category,
                            updated_difficulty
                        )
                        st.success("Flashcard updated successfully!")
                    else:
                        st.error("Please fill in all fields.")
            
            with col2:
                if st.button("Delete Flashcard", use_container_width=True):
                    # Confirm deletion
                    if st.button("Confirm Deletion", key="confirm_delete"):
                        filler.db_handler.delete_flashcard(flashcard_id)
                        st.success("Flashcard deleted successfully!")
                        st.rerun()
        else:
            st.warning(f"No flashcards available in the '{selected_category}' category.")


with tab1:
    # Flashcard Practice Section
    st.header("Practice Flashcards")
    
    # Initialize session state for flashcard management
    if 'current_flashcard' not in st.session_state:
        st.session_state.current_flashcard = None
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False

    # Initialize previous filter states in session_state
    if 'prev_category' not in st.session_state:
        st.session_state.prev_category = None
    if 'prev_status' not in st.session_state:
        st.session_state.prev_status = None
    if 'prev_difficulty' not in st.session_state:
        st.session_state.prev_difficulty = None
    
    # Category, status, and difficulty selection
    category_to_practice = st.selectbox("Choose Category to Practice", categories)
    status = st.radio("Show flashcards marked as:", ["unknown", "known"], index=0)
    difficulty = st.selectbox("Choose Difficulty Level", ["All", "basic", "intermediate", "advanced"])

    def get_random_flashcard():
        """Get a random flashcard from the database based on current criteria"""
        # Retrieve flashcards based on the selected filters
        flashcards = filler.db_handler.get_flashcards_by_filters(category_to_practice, status, difficulty)
        if flashcards:
            return random.choice(flashcards)
        return None

    # Check if any filter has changed
    if (category_to_practice != st.session_state.prev_category or 
        status != st.session_state.prev_status or 
        difficulty != st.session_state.prev_difficulty):
        
        # Update session state with a new random flashcard
        st.session_state.current_flashcard = get_random_flashcard()
        st.session_state.show_answer = False  # Reset answer display

        # Update previous filter states
        st.session_state.prev_category = category_to_practice
        st.session_state.prev_status = status
        st.session_state.prev_difficulty = difficulty

    def handle_response(knew_it):
        """Handle user response and load next flashcard"""
        if st.session_state.current_flashcard:
            flashcard_id = st.session_state.current_flashcard[0]
            new_status = "known" if knew_it else "unknown"
            filler.db_handler.update_flashcard_status(flashcard_id, new_status)
            
            # Reset state and get new flashcard
            st.session_state.show_answer = False
            st.session_state.current_flashcard = get_random_flashcard()
            st.rerun()  # Refresh to reflect the updated status

    # Display flashcard if it exists
    if st.session_state.current_flashcard:
        flashcard = st.session_state.current_flashcard
        question = flashcard[1]
        answer = flashcard[2]
        
        # Create a card-like container
        card = st.container()
        with card:
            st.markdown("### Current Flashcard")
            # Show question or answer based on the state of `show_answer`
            if not st.session_state.show_answer:
                if st.button(f"Question: {question}", use_container_width=True):
                    st.session_state.show_answer = True  # Toggle to show answer
                    st.rerun()
            else:
                if st.button(f"Answer: {answer}", use_container_width=True):
                    st.session_state.show_answer = False  # Toggle back to question
                    st.rerun()

            # Show response buttons only when answer is revealed
            if st.session_state.show_answer:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("I knew it! 👍", use_container_width=True):
                        handle_response(True)
                with col2:
                    if st.button("I didn't know it 👎", use_container_width=True):
                        handle_response(False)
    else:
        st.write("No flashcards available in this category with the selected status and difficulty level.")




with tab3:
    st.header("Flashcard Summary")
    summary = filler.db_handler.get_flashcard_summary()
    
    if summary:
        # Convert summary data to DataFrame for plotting
        summary_df = pd.DataFrame(summary, columns=['Category', 'Status', 'Count'])
        
        # Create a bar plot using Plotly Express
        fig = px.bar(
            summary_df, 
            x='Category', 
            y='Count', 
            color='Status', 
            barmode='group',
            title="Flashcard Status by Category",
            labels={'Count': 'Number of Flashcards', 'Category': 'Flashcard Category'},
            text='Count'
        )
        
        # Customize layout for modern look
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Flashcards",
            legend_title="Flashcard Status",
            template="plotly_white",
            title_x=0.7
        )
        
        # Display the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No flashcards available for visualization.")


with tab4:
    st.header("Browse Flashcards")

    # Filter options
    filter_category = st.selectbox("Filter by Category", options=["All"] + categories)
    filter_difficulty = st.selectbox("Filter by Difficulty", options=["All", "basic", "intermediate", "advanced"])
    filter_status = st.radio("Filter by Status", options=["All", "unknown", "known"])

    # Get all flashcards from the database and apply filters
    flashcards = filler.db_handler.get_all_flashcards()
    #print(flashcards)
    flashcards = [
    {
        "id": card[0],
        "question": card[1],
        "answer": card[2],
        "category": card[3],
        "difficulty": card[4],
        "status": card[5],
    }
    for card in filler.db_handler.get_all_flashcards()
]
    
    # Apply category filter
    if filter_category != "All":
        flashcards = [card for card in flashcards if card['category'] == filter_category]

    # Apply difficulty filter
    if filter_difficulty != "All":
        flashcards = [card for card in flashcards if card['difficulty'] == filter_difficulty]

    # Apply status filter
    if filter_status != "All":
        flashcards = [card for card in flashcards if card['status'] == filter_status]

    if flashcards:
        flashcards_df = pd.DataFrame(flashcards, columns=['id', 'question', 'answer', 'category', 'difficulty', 'status'])
        st.dataframe(flashcards_df, use_container_width=True)

        if filter_status == "known":
            # Add "Unbeknownst" button for each row
            for card in flashcards:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**Flashcard ID {card['id']} - Question:** {card['question']}")
                with col2:
                    if st.button("Unbeknownst", key=f"unknown_{card['id']}"):
                        filler.db_handler.update_flashcard_status(card['id'], status="unknown")
                        st.success(f"Status updated to 'unknown' for flashcard ID {card['id']}")
                        st.rerun()
    else:
        st.write("No flashcards match the selected filters.")





                 
# Close the database connection when done
filler.db_handler.close()