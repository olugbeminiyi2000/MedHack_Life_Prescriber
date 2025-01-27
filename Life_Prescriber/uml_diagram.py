import os
import django
import pydot
from django.apps import apps

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Life_Prescriber.settings")  # Replace with your settings module
django.setup()


def generate_custom_model_diagram():
    # Initialize the graph
    graph = pydot.Dot("Django Models", graph_type="digraph", dpi=300)
    graph.set_graph_defaults(fontname="Open Sans, sans-serif", fontsize="16")

    # Fetch all models dynamically
    models = apps.get_models()

    # Store created nodes to avoid duplication
    nodes = {}

    # Define customizations
    node_style = {
        "shape": "box",
        "style": "filled",
        "fillcolor": "#0d81bc",
        "fontcolor": "white",
        "fontsize": "16",
    }
    edge_style = {
        "color": "#f4f4f4",
        "arrowhead": "vee",
        "arrowtail": "dot",
        "dir": "both",
    }

    # Create nodes for all models
    for model in models:
        model_name = model.__name__
        if model_name not in nodes:
            node = pydot.Node(model_name, **node_style)
            nodes[model_name] = node
            graph.add_node(node)

    # Add edges for relationships
    for model in models:
        model_name = model.__name__

        for field in model._meta.get_fields():
            # Check for ForeignKey, ManyToManyField, and OneToOneField relationships
            if field.is_relation and field.related_model:
                target_model_name = field.related_model.__name__

                # Ensure the target node exists
                if target_model_name not in nodes:
                    target_node = pydot.Node(target_model_name, **node_style)
                    nodes[target_model_name] = target_node
                    graph.add_node(target_node)

                # Add edge to represent the relationship
                edge = pydot.Edge(model_name, target_model_name, **edge_style)
                graph.add_edge(edge)

    # Save the graph
    output_dir = os.getcwd()  # Save in the current directory
    graph.write_png(os.path.join(output_dir, "models_custom.png"))
    graph.write_dot(os.path.join(output_dir, "models_custom.dot"))

    print("Custom diagram generated and saved as models_custom.png")


# Run the function
if __name__ == "__main__":
    generate_custom_model_diagram()
