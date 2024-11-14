# app.py
import time
import streamlit as st
import random
#from db_handler import *
from flashcard import *
import plotly.express as px
import pandas as pd
from fill_cards import *
import requests

# Initialize database
#db_handler = DatabaseHandler()
filler = FlashcardGenerator()

# Set Streamlit to wide layout
st.set_page_config(layout="wide")

st.title("Data Science Learning App")

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Practice Flashcards", "Create/Update Flashcards", "Visualize Flashcards", "DB Browser", "Similarity Viz"])

categories = [
    "General", "Linear Algebra for Machine Learning", "Bash & Git", "SQL", "Probability & Statistics", "Data Science Fundamentals", 
    "Machine Learning Fundamentals", "Visualization", "Object Oriented Programming in Python", "Advanced Trees in Machine Learning", "Time Series", "Computer Vision", "Graph Neural Networks", "Backpropagation", 
    "Databases", "Docker", "Deep Learning", "Streamlit", "NLP", "Transformers", 
    "Transfer Learning", "LLM Optimization", "Fine Tuning LLMs", "Debugging Deep Learning", 
    "Vision Transformers", "CV Projects", "Soft Skills"
]


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
    
    summary = filler.db_handler.get_flashcard_summary_with_diff()

    print(summary)
    
    if summary:
        summary_df = pd.DataFrame(summary, columns=['Category', 'Status', 'Difficulty', 'Count'])
        
        # Modern blue color palette
        difficulty_colors = {
            'basic': '#93C5FD',    # Light blue
            'intermediate': '#3B82F6',  # Medium blue
            'advanced': '#1E40AF'     # Dark blue
        }
        
        status_colors = {
            'unknown': '#BFDBFE',      # Very light blue
            'Learning': '#60A5FA',  # Sky blue
            'known': '#2563EB'   # Royal blue
        }
        
        # 1. Difficulty Distribution
        st.subheader("Questions by Difficulty")
        diff_fig = px.bar(
            summary_df.groupby(['Category', 'Difficulty'])['Count'].sum().reset_index(),
            x='Category',
            y='Count',
            color='Difficulty',
            title=" ",
            labels={
                'Count': 'Number of Questions',
                'Category': 'Question Category',
                'Difficulty': 'Difficulty Level'
            },
            text='Count',
            #barmode='stack',
            color_discrete_map=difficulty_colors
        )
        
        diff_fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Questions",
            legend_title="Difficulty Level",
            template="plotly_white",
            title_x=0.5,
            bargap=0.2,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        diff_fig.update_traces(
            textposition='auto',
            texttemplate='%{text}',
            textfont_size=12,
            textfont_color='white'  # Make text white for better contrast
        )
        
        st.plotly_chart(diff_fig, use_container_width=True)
        
        # 2. Status Distribution
        st.subheader("Questions by Status")
        status_fig = px.bar(
            summary_df.groupby(['Category', 'Status'])['Count'].sum().reset_index(),
            x='Category',
            y='Count',
            color='Status',
            title=" ",
            labels={
                'Count': 'Number of Questions',
                'Category': 'Question Category',
                'Status': 'Question Status'
            },
            text='Count',
            #barmode='stack',
            color_discrete_map=status_colors
        )
        
        status_fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Questions",
            legend_title="Question Status",
            template="plotly_white",
            title_x=0.5,
            bargap=0.2,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        status_fig.update_traces(
            textposition='auto',
            texttemplate='%{text}',
            textfont_size=12,
            textfont_color='white'  # Make text white for better contrast
        )
        
        st.plotly_chart(status_fig, use_container_width=True)
        
    # Summary statistics with horizontal bar plots
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="color: #1E40AF; font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">
                Difficulty Distribution
            </div>
        """, unsafe_allow_html=True)
        
        difficulty_breakdown = summary_df.groupby('Difficulty')['Count'].sum()
        total_questions = difficulty_breakdown.sum()
        
        # Create DataFrame for difficulty plot
        diff_stats = pd.DataFrame({
            'Difficulty': difficulty_breakdown.index,
            'Count': difficulty_breakdown.values,
            'Percentage': (difficulty_breakdown.values / total_questions * 100).round(1)
        })
        
        # Sort by count descending
        diff_stats = diff_stats.sort_values('Count', ascending=True)
        
        # Create horizontal bar plot for difficulty
        diff_fig = px.bar(
            diff_stats,
            y='Difficulty',
            x='Percentage',
            orientation='h',
            text=diff_stats.apply(lambda x: f"{int(x['Count'])} ({x['Percentage']}%)", axis=1),
            color='Difficulty',
            color_discrete_map={
                'basic': '#93C5FD',    # Light blue
                'intermediate': '#3B82F6',  # Medium blue
                'advanced': '#1E40AF'     # Dark blue
            }
        )
        
        diff_fig.update_layout(
            showlegend=False,
            xaxis_title="Percentage of Questions",
            yaxis_title="",
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5E7EB',
                range=[0, 100]
            ),
            height=200
        )
        
        diff_fig.update_traces(
            textposition='auto',
            textfont_size=12,
            textfont_color='white'
        )
        
        st.plotly_chart(diff_fig, use_container_width=True)

    with col2:
        st.markdown("""
            <div style="color: #1E40AF; font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">
                Status Distribution
            </div>
        """, unsafe_allow_html=True)
        
        status_breakdown = summary_df.groupby('Status')['Count'].sum()
        
        # Create DataFrame for status plot
        status_stats = pd.DataFrame({
            'Status': status_breakdown.index,
            'Count': status_breakdown.values,
            'Percentage': (status_breakdown.values / total_questions * 100).round(1)
        })
        
        # Sort by count descending
        status_stats = status_stats.sort_values('Count', ascending=True)
        
        # Create horizontal bar plot for status
        status_fig = px.bar(
            status_stats,
            y='Status',
            x='Percentage',
            orientation='h',
            text=status_stats.apply(lambda x: f"{int(x['Count'])} ({x['Percentage']}%)", axis=1),
            color='Status',
            color_discrete_map={
                'unknown': '#BFDBFE',      # Very light blue
                'Learning': '#60A5FA',  # Sky blue
                'known': '#2563EB'   # Royal blue
            }
        )
        
        status_fig.update_layout(
            #barmode='stack',
            showlegend=False,
            xaxis_title="Percentage of Questions",
            yaxis_title="",
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5E7EB',
                range=[0, 100]
            ),
            height=200
        )
        
        status_fig.update_traces(
            textposition='inside',
            textfont_size=12,
            textfont_color='white'
        )
        
        st.plotly_chart(status_fig, use_container_width=True)
        




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