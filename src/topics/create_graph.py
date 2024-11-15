import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
from topic import Topic  # Assuming you have a Topic class


def fetch_topics(db_name):
    """Fetch topics from the database and map to Topic objects."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic_name, category, sub_category_1, sub_category_2, sub_category_3, explanation, difficulty, importance_level
        FROM data_science_topics
    """)
    rows = cursor.fetchall()
    print(rows)
    conn.close()
    
    # Map rows to Topic class or dictionary
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


def create_knowledge_graph_with_attributes(topics):
    """Create a knowledge graph from the list of topics."""
    G = nx.DiGraph()

    # Define color mappings
    difficulty_colors = {
        "basic": "#add8e6",       # Light Blue
        "intermediate": "#6495ed", # Medium Blue
        "advanced": "#0000ff",   # Dark Blue
    }
    importance_colors = {
        1: "#98fb98",  # Light Green
        2: "#90ee90",
        3: "#32cd32",  # Lime Green
        4: "#228b22",  # Forest Green
        5: "#006400",  # Dark Green
    }
    subcategory_colors = {
        "sub_category_1": "#ffcccc",  # Light Red
        "sub_category_2": "#ff9999",  # Medium Red
        "sub_category_3": "#ff6666",  # Dark Red
    }

    # Add nodes and edges for hierarchical structure
    for topic in topics:
        # Add category node (highest in hierarchy)
        if topic.category and not G.has_node(topic.category):
            G.add_node(topic.category, label="Category", color="yellow")  # Red for categories

        # Add sub_category_1 node under the category
        if topic.sub_category_1:
            if not G.has_node(topic.sub_category_1):
                G.add_node(topic.sub_category_1, label="Sub-category 1", color=subcategory_colors["sub_category_1"])
                G.add_edge(topic.category, topic.sub_category_1, relationship="contains")

        # Add sub_category_2 node under sub_category_1
        if topic.sub_category_2:
            if not G.has_node(topic.sub_category_2):
                G.add_node(topic.sub_category_2, label="Sub-category 2", color=subcategory_colors["sub_category_2"])
                G.add_edge(topic.sub_category_1, topic.sub_category_2, relationship="contains")

        # Add sub_category_3 node under sub_category_2
        if topic.sub_category_3:
            if not G.has_node(topic.sub_category_3):
                G.add_node(topic.sub_category_3, label="Sub-category 3", color=subcategory_colors["sub_category_3"])
                G.add_edge(topic.sub_category_2, topic.sub_category_3, relationship="contains")

        # Add topic node under sub_category_3
        if topic.topic_name:
            difficulty_color = difficulty_colors.get(topic.difficulty, "#d3d3d3")  # Default: Gray
            #importance_color = importance_colors.get(topic.importance_level, "#d3d3d3")  # Default: Gray

            G.add_node(
                topic.topic_name,
                label="Topic",
                explanation=topic.explanation,
                color=difficulty_color,
                #importance_color=importance_color,
            )
            G.add_edge(topic.sub_category_3, topic.topic_name, relationship="contains")

    return G


def visualize_knowledge_graph(G):
    """Visualize the knowledge graph."""
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)

    # Node attributes for color
    node_colors = [data.get("color", "#d3d3d3") for _, data in G.nodes(data=True)]

    # Draw the graph
    nx.draw(
        G, pos, with_labels=True,
        node_size=3000,
        node_color=node_colors,
        font_size=10,
        font_weight="bold"
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "relationship"))
    plt.title("Knowledge Graph with Difficulty, Importance, and Subcategory Colors", fontsize=15)
    plt.show()


# Main script
if __name__ == "__main__":
    
    db_name = "topics.db"
    topics = fetch_topics(db_name)

    G = create_knowledge_graph_with_attributes(topics)
    visualize_knowledge_graph(G)
