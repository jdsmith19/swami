# TODO AND IDEAS

## Optimize

- Add a validation agent to the Optimize Planner node
  - Validates that the specific combination has not been tried before. Useful for large max_experiments.
- Add a judge agent to the Optimize Planner node
  - Probably only for Phases 3 and 4.
  - Analyzes the reasoning and provides feedback. Ensures that sound statisical thinking is occurring.
- Clean up how the agent returns state
  - Don't return state directly
  - Return: { "foo": "bar" }

## Tavily

- Integrate Tavily for Expert Analysis.
  - Find 3 - 5 sources of NFL Expert Analysis of upcoming games.
  - Consolidate and categorize the information.
    - Key injuries
    - Picks
    - Other considerations? (coaching, travel, offensive / defensive schemes, player matchups, etc.)

## Prediction Markets

- Integrate prediction markets like Kalshi

## Prediction Results

- Improve logging to database
  - Eventually allow agent to learn from its history

## Looping

- Run the prediction agent multiple times and consolidate the results
  - Add a judge to validate the consolidation

## Python Sandbox

- Give the Game Analysis agent a Python sandbox for running data evaluations

## Podcast Analysis

- The transcription is great, the summarization sucks
  - See what works for Expert Analysis and see if it can be adapted for podcasts
  - Consider RAG retrieval (e.g. Chroma?) so the agent can look up player / team associations for gaining context
  - Consider chunking