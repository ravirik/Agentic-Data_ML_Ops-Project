```markdown
# Agentic-Data — Retrieval-Augmented (RAG) MLOps Agent

Updated: 2026-01-23

[![Project Status](https://img.shields.io/badge/status-v1.0%20%E2%80%94%20RAG%20Prototype-blue)](#)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-brightgreen)](https://www.python.org/)
[![Observability](https://img.shields.io/badge/observability-Logfire-lightgrey)](#)

Overview
--------
This repository implements an Agentic Retrieval-Augmented Generation (RAG) system for deterministic, auditable data engineering workflows. The agent combines:

- O1 — Memory: persistent vector-backed knowledge (ChromaDB) + curated recipe JSON (`memory_store.json`).
- O2 — Reasoning: type-safe agent wiring using `pydantic-ai` and a Gemini model; the agent performs semantic retrieval + ReAct-style reasoning.
- O3 — Execution & Observability: verified transformation execution and Logfire traces for auditability.

Key goals:
- Use semantic retrieval to ground actions in verified recipes and reduce LLM hallucination.
- Keep execution deterministic and auditable (trace every tool call).
- Protect API quota and execution with usage limits and safety notes.

What changed (RAG-focused)
--------------------------
- Vector store (ChromaDB) is used as the primary retrieval layer. Recipes from `memory_store.json` are vectorized and stored in `chroma_db`.
- `search_knowledge_store` performs semantic lookup in the Chroma collection (intent-based retrieval).
- The agent prompt and wiring explicitly demand "Semantic RAG" operations (inspect → retrieve relevant recipe vectors → adapt & apply verified transformation).
- Code files reflect the RAG stack: `reasoning.py` configures ChromaDB, vector collection, and uses a GoogleModel (Gemini) while the system prompt instructs the agent to operate under a strict RAG protocol.

Repository layout (high-level)
------------------------------
- reasoning.py — Core: RAG wiring, ChromaDB client, agent tools (inspect_dataset, semantic search wrapper, apply_transformation), and run loop.
- agent_reasoning.py — Example async run demonstrating an agent reasoning cycle.
- verify_agent.py — Connectivity + Logfire verification.
- test_tools.py — Local pre-flight tests for tools.
- memory_store.json — Curated recipes (source of truth) used to produce embeddings.
- chroma_db/ — local persistent Chroma database (created at runtime).
- data/ — Example dataset(s) (e.g., data/retail_store_sales.csv).
- Journal.MD / Architecture.MD — experimental notes and architecture rationale.
- LICENSE, .env (not checked in).

Primary components & flow
-------------------------
1. inspect_dataset() — reads CSV schema and sample rows to produce a compact summary the agent can use to form retrieval queries.
2. semantic retrieval — transform query/prompt into an embedding, search the Chroma collection for nearest recipe vectors, retrieve top-k candidate recipes (including metadata: explanation, code snippet, tags).
3. agent reasoning (RAG loop) — agent performs ReAct steps using retrieved context; it adapts recipe snippets to the dataset and decides whether to call apply_transformation.
4. apply_transformation(python_code) — executes verified Python code against an in-repo pandas DataFrame and writes a cleaned artifact (e.g., data/retail_store_sales_cleaned.csv).
5. Observability — Logfire captures agent "thoughts", tool calls, and outcomes for audit.

Visual flow, icons & graphs
---------------------------
Below are the flowchart, icons legend, and an ASCII architecture visual that reflect the current README visuals and match the repo's RAG orientation.

Icon legend
- 🧠 Agent reasoning (O2)
- 📚 O1 Memory (recipes / vector store)
- 🧪 Execution sandbox (apply + save)
- 🔍 Observability (Logfire traces)
- ⚙️ Infra / orchestration (ChromaDB, embeddings)
- 🔒 Safety & policies

ASCII flowchart (high-level)
```
User / CLI
   │
   ▼
🧠 Agent (pydantic-ai + Gemini)  <-- System Prompt enforces "Semantic RAG" protocol
   │
   ├─> inspect_dataset()  — reads data/retail_store_sales.csv (schema & sample)
   │
   ├─> embed(query) -> ⚙️ ChromaDB / transformation_recipes (semantic retrieval)
   │       └─> returns top-k recipes (metadata + code snippet)
   │
   └─> adapt_recipe() -> decide -> apply_transformation(python_code)
            │
            └─> 🧪 exec() (local scope with df) -> writes data/retail_store_sales_cleaned.csv
   │
   ▼
🔍 Logfire traces + stdout (audit trail)
```

Architecture ASCII (detailed)
```
+----------------------+      +----------------------+      +---------------------+
|     User / CLI       | ---> |     Agent (O2)       | ---> |  Execution (O3)     |
|  (prompt / requests) |      | pydantic-ai + LLM    |      | apply_transformation|
+----------------------+      +----------------------+      +---------------------+
                                     |
                                     |  semantic retrieval (embeddings)
                                     v
                             +----------------------+
                             |     ChromaDB (O1)    |
                             |  transformation_recipes
                             +----------------------+
                                     |
                                     v
                             +----------------------+
                             |   memory_store.json  |
                             |  (curated recipes)   |
                             +----------------------+
```

Graph / metrics placeholders
- Embedding/indexing: recipe_count = N, vector_dim = D (computed at indexing time)
- Retrieval: top_k = 3 (configurable)
- UsageLimits: request_limit = 5, tool_calls_limit = 5

Quickstart — run locally (RAG)
------------------------------
1. Clone:
   ```bash
   git clone https://github.com/ravirik/Agentic-Data_ML_Ops-Project.git
   cd Agentic-Data_ML_Ops-Project
   ```

2. Create venv & install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Add credentials to `.env` (examples):
   ```
   LOGFIRE_ENABLED=true
   GOOGLE_API_KEY=...
   ```

4. Ensure example data exists:
   - Add `data/retail_store_sales.csv` or update `reasoning.py`/`agent_reasoning.py` to point to your dataset.

5. Initialize / index `memory_store.json` into ChromaDB (if not already):
   - The Chroma persistent client is configured at `./chroma_db`.
   - Run your indexing script to embed recipes and upsert into `transformation_recipes`.

6. Verify connectivity:
   ```bash
   python verify_agent.py
   ```

7. Run the example RAG reasoning cycle:
   ```bash
   python agent_reasoning.py
   ```

Security & safety (important)
-----------------------------
- apply_transformation currently executes Python snippets using exec() with a local scope containing `df`. This is unsafe for arbitrary, untrusted code.
- Recommended hardening steps:
  - Validate/whitelist AST nodes (no imports, no OS/network access).
  - Execute transformations in a sandboxed subprocess or container.
  - Sign/verify recipes before executing (tether to a trusted source of truth).
  - Keep `.env` and keys out of source control.

Observability & quotas
----------------------
- Logfire is instrumented to capture agent traces and tool calls.
- UsageLimits are enforced in the agent run loop to avoid runaway LLM usage (e.g., 5 RPM / limited tool calls).
- Journal.MD contains run traces and decisions (including rate limit notes).

Extending the project
---------------------
- Add robust indexing scripts to keep `transformation_recipes` synced with `memory_store.json`.
- Expand unit tests: each recipe should have a small golden-case test that runs locally (no LLM calls).
- Harden execution: AST validation, sandboxing, or policy enforcement before running code.
- Add CI: a GitHub Actions workflow that runs local golden tests and lints (no external LLM calls).
- Add visual diagrams (SVG/PNG) to `/docs/` and reference them from README for richer renderers.

Contributing
------------
1. Open an issue describing the change.
2. Branch from `main` and create a PR.
3. Add tests and documentation for any behavior changes.

License & contact
-----------------
Apache-2.0 — see `LICENSE`

Maintainer: @ravirik

Notes
-----
- This README preview adds the missing visual flow, icons, and architecture ASCII diagrams present in the current README.MD. No repo changes were made. Tell me when you want me to commit this version (and which branch).
```