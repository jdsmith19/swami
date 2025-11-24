print("Loading dependencies...\n")

# Graphs
from graphs.optimize_graph import app

# Internal Libraries
import setup # Loads launch states, sets preferences from .env, enables argument parsing

# Run the app
app.invoke(
    {}, 
    config={
        "recursion_limit": 500
    }
)