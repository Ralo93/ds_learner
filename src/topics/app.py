import sqlite3
import streamlit as st
from pyvis.network import Network
import networkx as nx
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from topic import Topic  # Assuming you have a Topic class

st.set_page_config(layout="wide")


def fetch_topics_with_embeddings(db_name):
    """Fetch topics from the database and load their embeddings."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic_name, category, sub_category_1, sub_category_2, sub_category_3, explanation, difficulty, importance_level, embedding, source
        FROM data_science_topics
    """)
    rows = cursor.fetchall()
    conn.close()

    topics = [
        {
            "topic_name": row[0],
            "category": row[1],
            "sub_category_1": row[2],
            "sub_category_2": row[3],
            "sub_category_3": row[4],
            "explanation": row[5],
            "difficulty": row[6],
            "importance_level": row[7],
            "embedding": pickle.loads(row[8]) if row[8] else None,
            "source": row[9]
        }
        for row in rows
    ]
    return topics


def fetch_topics_hierarchical(db_name):
    """Fetch topics from the database and map to Topic objects."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic_name, category, sub_category_1, sub_category_2, sub_category_3, explanation, difficulty, importance_level
        FROM data_science_topics
        WHERE source <> 'PAPER'
    """)
    rows = cursor.fetchall()
    conn.close()

    topics = [
        Topic(
            topic_name=row[0],
            category=row[1],
            sub_category_1=row[2],
            sub_category_2=row[3],
            sub_category_3=row[4],
            explanation=row[5],
            difficulty=row[6],
            importance_level=row[7]
        )
        for row in rows
    ]
    return topics


def create_graph_with_similarity(topics, similarity_threshold):
    """Create a knowledge graph with nodes for each topic and edges based on cosine similarity."""
    G = nx.Graph()

    # Add nodes to the graph
    for topic in topics:
        if topic["topic_name"]:
            G.add_node(
                topic["topic_name"],
                label=topic["topic_name"],
                explanation=topic["explanation"],
                color = (
                    "green" if topic["source"] == "PAPER" else
                    "#add8e6" if topic["difficulty"] == "basic" else
                    "#6495ed" if topic["difficulty"] == "intermediate" else
                    "#0000ff"
                )#color="green" if topic["source"] == "PAPER" else "green",
                )

    # Calculate cosine similarity and add edges
    embeddings = [topic["embedding"] for topic in topics if topic["embedding"] is not None]
    topic_names = [topic["topic_name"] for topic in topics if topic["embedding"] is not None]
    if embeddings:
        similarity_matrix = cosine_similarity(embeddings)
        for i in range(len(topic_names)):
            for j in range(i + 1, len(topic_names)):
                if similarity_matrix[i][j] > similarity_threshold:
                    G.add_edge(topic_names[i], topic_names[j], weight=similarity_matrix[i][j])

    return G


def create_knowledge_graph_with_attributes(topics):
    """Create a knowledge graph from the list of topics using hierarchy."""
    G = nx.DiGraph()

    # Define color mappings
    difficulty_colors = {
        "basic": "#add8e6",       # Light Blue
        "intermediate": "#6495ed", # Medium Blue
        "advanced": "#0000ff",   # Dark Blue
    }
    subcategory_colors = {
        "sub_category_1": "#ffcccc",  # Light Red
        "sub_category_2": "#ff9999",  # Medium Red
        "sub_category_3": "#ff6666",  # Dark Red
    }

    for topic in topics:
        if topic.category and not G.has_node(topic.category):
            G.add_node(topic.category, label=topic.category, color="yellow")
        if topic.sub_category_1:
            if not G.has_node(topic.sub_category_1):
                G.add_node(topic.sub_category_1, label=topic.sub_category_1, color=subcategory_colors["sub_category_1"])
                G.add_edge(topic.category, topic.sub_category_1, relationship="contains")
        if topic.sub_category_2:
            if not G.has_node(topic.sub_category_2):
                G.add_node(topic.sub_category_2, label=topic.sub_category_2, color=subcategory_colors["sub_category_2"])
                G.add_edge(topic.sub_category_1, topic.sub_category_2, relationship="contains")
        if topic.sub_category_3:
            if not G.has_node(topic.sub_category_3):
                G.add_node(topic.sub_category_3, label=topic.sub_category_3, color=subcategory_colors["sub_category_3"])
                G.add_edge(topic.sub_category_2, topic.sub_category_3, relationship="contains")
        if topic.topic_name:
            difficulty_color = difficulty_colors.get(topic.difficulty, "#d3d3d3")
            G.add_node(
                topic.topic_name,
                label=topic.topic_name,
                explanation=topic.explanation,
                color=difficulty_color,
            )
            G.add_edge(topic.sub_category_3, topic.topic_name, relationship="contains")

    return G


def visualize_knowledge_graph(G):
    """Convert the graph to a Pyvis Network for visualization."""
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    for node_id, node_attrs in G.nodes(data=True):
        net.get_node(node_id)["title"] = node_attrs.get("explanation", "No explanation available")
        net.get_node(node_id)["color"] = node_attrs.get("color", "#d3d3d3")
    return net


# Streamlit App
def main():
    st.title("Knowledge Graph Visualization")

    db_name = st.text_input("Enter the database name:", "topics.db")
    similarity_threshold = st.sidebar.slider("Cosine Similarity Threshold", 0.0, 1.0, 0.7, 0.01)
    enable_embedding_graph = st.sidebar.checkbox("Enable Embedding-Based Graph")

    #if st.button("Load Topics"):
    with st.spinner("Loading topics..."):
        try:
            if enable_embedding_graph:
                topics = fetch_topics_with_embeddings(db_name)
                st.success(f"Fetched {len(topics)} topics with embeddings from the database.")
                G = create_graph_with_similarity(topics, similarity_threshold)
            else:
                topics = fetch_topics_hierarchical(db_name)
                st.success(f"Fetched {len(topics)} topics (hierarchical) from the database.")
                G = create_knowledge_graph_with_attributes(topics)

            net = visualize_knowledge_graph(G)
            net.save_graph("knowledge_graph.html")
            st.components.v1.html(open("knowledge_graph.html", "r").read(), height=800)

        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
