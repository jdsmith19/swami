print("Loading dependencies...\n")

# Graphs
from graphs.predict_graph import predict_graph

# Internal Libraries
import setup # Loads launch states, sets preferences from .env, enables argument parsing

# Run the app
predict_graph.invoke(
    {},
    config={
        "recursion_limit": 500
    }
)