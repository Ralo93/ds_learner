import streamlit as st
import networkx as nx
import pickle
from pyvis.network import Network
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Set Streamlit to wide layout
st.set_page_config(layout="wide")

st.title("Data Science Learning App Visualizer")

HEIGHT = 400

# Directory for embeddings files
EMBEDDINGS_DIR = "data/"

# Function to load all embeddings from .pkl files in a directory
def load_all_embeddings(directory):
    embeddings_dict = {}
    file_groups = {}
    group_id = 1
    for file in os.listdir(directory):
        if file.endswith(".pkl"):
            with open(os.path.join(directory, file), "rb") as f:
                embeddings = pickle.load(f)
                embeddings_dict.update(embeddings)
                # Assign a unique group for nodes in this file
                for node_id in embeddings.keys():
                    file_groups[node_id] = group_id
            group_id += 1
    return embeddings_dict, file_groups

# Function to create a NetworkX graph from embeddings with similarity-based edges
def create_graph(embeddings_dict, file_groups, similarity_threshold):
    G = nx.Graph()

    # Add nodes to the graph with file-based colors
    for node_id, embedding in embeddings_dict.items():
        G.add_node(node_id, title=str(node_id), group=file_groups[node_id])

    # Calculate cosine similarity and add edges based on the threshold
    ids = list(embeddings_dict.keys())
    embeddings = np.array(list(embeddings_dict.values()))
    similarities = cosine_similarity(embeddings)

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):  # Avoid duplicate edges and self-loops
            if similarities[i, j] >= similarity_threshold:
                G.add_edge(ids[i], ids[j], weight=similarities[i, j])

    return G

# Function to visualize the graph using Pyvis with PageRank-based node sizes
def visualize_graph(G, min_size=15, max_size=50):
    # Compute PageRank
    pagerank_scores = nx.pagerank(G)

    # Normalize PageRank scores to a fixed range
    min_rank = min(pagerank_scores.values())
    max_rank = max(pagerank_scores.values())



    def normalize(rank):
        """Normalize rank score to a size within [min_size, max_size]."""
        return min_size + (rank - min_rank) / (max_rank - min_rank) * (max_size - min_size)

    # Set up Pyvis Network
    net = Network(height="400px", width="100%", bgcolor="white", font_color="black")
    net.show_buttons(filter_=['physics'])  # Enable physics for interactive experience

    # Add nodes with sizes based on normalized PageRank scores
    for node, rank in pagerank_scores.items():
        size = normalize(rank)  # Apply normalization
        net.add_node(node, title=str(node), size=size, group=G.nodes[node]["group"])

    # Add edges
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, weight=data["weight"])

    # Save the generated HTML file to display in Streamlit
    path = "graph.html"
    net.save_graph(path)
    return path

# Streamlit app
st.title("Embedding Visualization with Cosine Similarity Threshold and PageRank")
st.write("Visualize embeddings as nodes from multiple `.pkl` files with distinct colors per file. Node sizes represent importance based on PageRank.")

# Add a slider to set the similarity threshold in the sidebar
similarity_threshold = st.sidebar.slider("Cosine Similarity Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

# Load and visualize embeddings
if os.path.exists(EMBEDDINGS_DIR):
    embeddings, file_groups = load_all_embeddings(EMBEDDINGS_DIR)
    st.write("Embeddings loaded successfully.")

    # Create graph based on the similarity threshold
    graph = create_graph(embeddings, file_groups, similarity_threshold)
    graph_path = visualize_graph(graph, min_size=15, max_size=50)
    
    # Display graph in Streamlit
    st.components.v1.html(open(graph_path, 'r').read(), height=1000, scrolling=True)
else:
    st.error("Embeddings directory not found. Please ensure `.pkl` files are located in the specified directory.")
