from pathlib import Path

def ensure_dir(path: str):
    """
    Create *path* and all required parents.
    Equivalent to `mkdir -p` on the command line.
    """
    Path(path).mkdir(parents=True, exist_ok=True)

# Output directories needed for project
directories = ["db", "results", "logs", "logs/scrape", "logs/predict", "logs/optimize"]

# Loop through directories and create them if htey don't exist
for directory in directories:
    ensure_dir(directory)