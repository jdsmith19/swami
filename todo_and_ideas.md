# TODO AND IDEAS

## General Outputs

- Add more detail for logging and the database
  - Add team_id to predictions
  - Add agent_id to predictions
  - Add was_best_result to results
  - Add day / date to games
  - Order the results

## Token Counts

- Use a reducer for total_tokens
  - Apply to all agents

## Final Report

- Create the final report generation agent

## More Stability

- Either add empty confidence to results that don't have confidence OR create the tables if they don't exist on setup

## Optimize

- Add a validation agent to the Optimize Planner node
  - Validates that the specific combination has not been tried before. Useful for large max_experiments.
- Add a judge agent to the Optimize Planner node
  - Probably only for Phases 3 and 4.
  - Analyzes the reasoning and provides feedback. Ensures that sound statisical thinking is occurring.
- Clean up how the agent returns state
  - Don't return state directly
  - Return: { "foo": "bar" }
- Send back to judge after resetting messages because of multiple validation failures
  - Set judged = state["judged"] at start
  - Set judged = False if resetting messages
  - return { "judged": judged }
- Be smarter about context window
  - Dynamically set state["trimmed_results"] based on token count

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

## Web UI

- Create Web UI for agents
  - Kick off agent run
  - Show progress
  - See historical results