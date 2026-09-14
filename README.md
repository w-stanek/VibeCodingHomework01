# toolcalling

Homework for tool calling: an LLM (via [OpenRouter](https://openrouter.ai/)) decides whether to call a local Python function, the function runs, and its result is sent back to the model for the final answer.

## Tools

| Tool | Description |
|------|-------------|
| `solve_quadratic(a, b, c)` | Solves `ax^2 + bx + c = 0`; returns real or complex roots (also handles the linear case `a = 0`). |
| `get_weather(city)` | Current weather for a city from the free [Open-Meteo](https://open-meteo.com/) API (no API key needed). |

## Project structure

- `main.py` – OpenRouter client, tool schemas, the tool-calling loop and an example prompt
- `functions.py` – implementations of the tool functions

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```sh
uv sync
```

Create a `.env` file with your OpenRouter API key:

```
OPENROUTER_API_KEY=your-key-here
```

## Run

```sh
uv run main.py
```

To try the weather tool, swap the example messages at the bottom of `main.py` for the commented-out weather ones.
