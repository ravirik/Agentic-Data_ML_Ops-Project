# Agentic Data — MLOps Project 🚀

[![Project Status](https://img.shields.io/badge/status-v1.0%20%E2%80%94%20Heuristic%20Baseline-blue)](#)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-brightgreen)](https://www.python.org/)
[![Observability](https://img.shields.io/badge/observability-Logfire-lightgrey)](#)

A focused Agentic MLOps prototype demonstrating a grounded ReAct-style agent for deterministic data cleaning and remediation. The system couples a type-safe agent framework (pydantic-ai) with a JSON-based knowledge store to avoid hallucinations, an execution layer that applies verified Python transformations, and observability through Logfire.

✨ Built for auditability, deterministic fixes, and rapid prototyping of agentic data engineering flows.

---

Table of contents
- [Overview](#overview)
- [Quick architecture (visual)](#quick-architecture-visual)
- [Key components](#key-components)
- [Repository layout](#repository-layout)
- [Quickstart (run locally)](#quickstart--run-locally)
- [Memory (knowledge) store & recipe format](#memory-knowledge-store--recipe-format)
- [Example flow (step-by-step)](#example-flow-step-by-step)
- [Observability & safety](#observability--safety)
- [Testing & debugging](#testing--debugging)
- [Extending the project](#extending-the-project)
- [Contributing](#contributing)
- [License & contact](#license--contact)

---

<a name="overview"></a>
## Overview

This project demonstrates an agentic approach to data engineering:

- O1 — Memory: JSON knowledge store (memory_store.json) of verified transformation recipes.
- O2 — Reasoning: pydantic-ai Agent wired to a Gemini model performing inspect → search → act.
- O3 — Execution & Observability: Decorated tools that apply transformations and Logfire traces for audit.

Goal: deterministic, auditable fixes for common "dirty data" problems (nulls, types, precision, date formats), not free-form generation.

<a name="quick-architecture-visual"></a>
## Quick architecture (visual) 🏗️

ASCII flow (simple):

```
User / CLI
   │
   ▼
Agent (pydantic-ai)  <-- System Prompt enforces strict ReAct + search protocol
   │
   ├─> inspect_dataset()  — reads data/retail_store_sales.csv (schema & sample)
   │
   ├─> search_knowledge_store(search_term)  — queries memory_store.json
   │
   └─> apply_transformation(column_name, python_code) — executes code, saves cleaned CSV
   │
   ▼
Artifacts: data/retail_store_sales_cleaned.csv  + Logfire traces
```

Icon legend:
- 🧠 Agent reasoning
- 📚 O1 Memory (recipes)
- 🧪 Execution sandbox (apply + save)
- 🔍 Observability (Logfire traces)

<a name="key-components"></a>
## Key components 🔎

- `reasoning.py` — Core tools & agent wiring (`inspect_dataset`, `search_knowledge_store`, `apply_transformation`).
- `agent_reasoning.py` — Example async flow that runs a reasoning cycle and prints agent outputs.
- `verify_agent.py` — Quick connectivity + Logfire verification script.
- `test_tools.py` — Pre-flight tests exercising the tools without running the full agent.
- `memory_store.json` — Curated JSON knowledge store (recipes).
- `data/retail_store_sales.csv` — Example dataset referenced by the scripts (add locally).
- `Journal.MD` / `Architecture.MD.txt` — Design notes, experiments, and architecture rationale.

<a name="repository-layout"></a>
## Repository layout (high-level) 📁
- reasoning.py  
- agent_reasoning.py  
- verify_agent.py  
- test_tools.py  
- memory_store.json  
- data/  
  - retail_store_sales.csv (example input)  
- Journal.MD  
- Architecture.MD.txt  
- LICENSE  
- .env (not checked in; create locally)

<a name="quickstart--run-locally"></a>
## Quickstart — run locally ⚙️

Prereqs:
- Python 3.12
- git
- API keys / environment variables for your model provider if using external LLMs
- Recommended: virtual env (venv/conda)

1) Clone and create a venv
```bash
git clone https://github.com/ravirik/Agentic-Data_ML_Ops-Project.git
cd Agentic-Data_ML_Ops-Project
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
# If requirements.txt is missing:
# pip install pydantic-ai logfire pandas python-dotenv
```

3) Create a `.env` at repo root
```
LOGFIRE_ENABLED=true
# Add provider-specific keys as needed, e.g.:
# GOOGLE_API_KEY=your_api_key_here
```

4) Verify connectivity & instrumentation
```bash
python verify_agent.py
```
Expect a printed agent response or an error that will help you debug API or env issues.

5) Run the reasoning cycle (example)
```bash
python agent_reasoning.py
```
What happens:
- The agent inspects `data/retail_store_sales.csv`
- Searches `memory_store.json` for matching recipes
- Attempts to apply a verified transformation using `apply_transformation`
- Outputs reasoning traces to stdout and sends spans to Logfire (if enabled)

6) Run pre-flight tool tests
```bash
python test_tools.py
```

<a name="memory-knowledge-store--recipe-format"></a>
## Memory (knowledge) store & recipe format 📚

The deterministic knowledge base is `memory_store.json`. It contains an array of recipe objects the agent searches via substring matching.

Example structure:
```json
{
  "recipes": [
    {
      "issue": "Precision loss in Total Spent column",
      "keyword": "float64",
      "explanation": "Round monetary values to 2 decimals to avoid precision drift in SQL aggregates.",
      "solution": "df['Total Spent'] = df['Total Spent'].round(2)"
    },
    {
      "issue": "Null values in Quantity column",
      "keyword": "null",
      "explanation": "Fill missing quantities with 0 for downstream numeric ops.",
      "solution": "df['Quantity'] = df['Quantity'].fillna(0).astype(int)"
    }
  ]
}
```

Best practices:
- Keep `solution` snippets small and well-tested.
- Use technical `keyword` values (data types, error phrases, column names).
- Add `explanation` and `issue` for human-readable traceability.

<a name="example-flow-step-by-step"></a>
## Example flow (step-by-step) 🔁

1. Agent calls `inspect_dataset()` → returns columns, types, sample rows, missing counts.  
2. Agent extracts technical keywords (e.g., `float64`, `null`, column name).  
3. Agent calls `search_knowledge_store(keyword)` → receives matched recipes (substring match).  
4. Agent selects a recipe and calls `apply_transformation(column, solution)`.  
5. `apply_transformation` executes Python code in a constrained local scope and writes `data/retail_store_sales_cleaned.csv`.  
6. Logfire records the agent's "thoughts" and tool calls for audit.

Edge behavior:
- If execution fails, the agent may attempt a single patch (prompt-specified behavior).
- UsageLimits in the agent prompt prevent runaway API usage (max tool calls).

<a name="observability--safety"></a>
## Observability & safety 🔒📈

- Logfire is instrumented in `reasoning.py`. Toggle with `LOGFIRE_ENABLED` in `.env`.  
- Tools are decoupled from the agent — agent suggests code strings; `apply_transformation` executes them in a local scope and reports errors.  
- UsageLimits and prompt-level constraints limit tool calls and retries.  
- Production hardening recommendations: sandbox execution, AST validation, whitelisting, or running transformations under a job agent.

<a name="testing--debugging"></a>
## Testing & debugging 🧪

- Read `Journal.MD` and `Architecture.MD.txt` for experimental traces and rationale.  
- Common issues:
  - Missing `data/retail_store_sales.csv` → add or change filepath in `reasoning.py`/`agent_reasoning.py`
  - Rate limits (HTTP 429) → lower request frequency or upgrade provider quota
  - `memory_store.json` typos → ensure valid JSON (missing commas can break the search)
- Reproducibility: record git commit hash and `.env` values used when running experiments.

<a name="extending-the-project"></a>
## Extending the project ✨

Ideas:
- Add more recipes and test cases to `memory_store.json`.  
- Harden `apply_transformation` with AST parsing / sandbox execution.  
- Add a small CI workflow (GitHub Actions) that runs a tiny golden-end-to-end test.  
- Integrate experiment logging (run manifests with commit hash + env snapshot).  
- Add an inference server for safely serving cleaned data or transformations.

<a name="contributing"></a>
## Contributing 🤝

Contributions are welcome!

1. Open an issue describing the change.  
2. Branch from `main`: `git checkout -b feature/your-change`  
3. Add tests and documentation for behavior changes.  
4. Open a pull request linking to relevant Journal entries where appropriate.

Suggested labels: enhancement, bug, docs, tests, infra.

<a name="license--contact"></a>
## License & contact 📬

This project is available under the Apache-2.0 license — see `LICENSE`.

Maintainer: ravirik

If you'd like, I can:
- Add a GitHub Actions workflow for a tiny "golden run" test,  
- Build a secure sandbox wrapper for recipe execution,  
- Prepare a sample `memory_store.json` with verified recipes and a small test dataset.

Thank you — happy agentic engineering! 🧭