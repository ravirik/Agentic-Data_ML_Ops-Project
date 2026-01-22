# System Architecture: Agentic MLOps Framework

## 1. High-Level Design

The system uses a **Decoupled Agentic Pattern**. The logic (LLM) is separated from the execution (Tools) to ensure that the 
AI cannot perform unauthorized actions on the data.

## 2. Technology Stack

- **Orchestrator:** Pydantic AI (Type-safe agent framework)
- **Reasoning Engine:** Gemini 1.5 Flash (Google Generative AI)
- **Observability:** Pydantic Logfire (OpenTelemetry compliant)
- **Environment:** Python 3.12 (venv)

## 3. Data Flow

1. **User Request** -> Input via Terminal/UI.
2. **Orchestrator** -> Analyzes request and checks available tools.
3. **Reasoning Loop** -> LLM decides if a tool call is required.
4. **Tool Execution** -> Python functions interact with the File System.
5. **Observability** -> Logfire captures the entire trace for audit.

--------------------------

Ingestion Layer: Added Pandas-based metadata extractor for raw CSV files.
Agent Core (O2): Implemented the Iterative Cognitive Loop (Reason -> Act -> Observe -> Reflect) using Gemini 1.5 Flash.
Execution Layer: Integrated Pydantic AI Tools for safe schema inspection.

------------------

Reasoning Engine :- The Updated Logic Flow:

Input: User provides "Dirty" CSV.

Perception: inspect_dataset identifies schema fragility (e.g., float64 precision).

Memory Retrieval: Agent queries memory_store.json for the verified fix.

Refinement: Agent compares internal LLM logic with the retrieved JSON recipe.

Output: A deterministic recommendation for the Execution Layer.


-----------------------

The Architectural Specification 

Component	           Technical Definition	                Role in Pipeline
Agent Class	           pydantic_ai.Agent	        Orchestrates the ReAct (Reason-Act-Observe) loop.
Model Engine	       gemini-flash-latest	        The "Reasoning Kernel" providing the cognitive logic.
O1 (Memory)	           memory_store.json	        The retrieval-augmented knowledge base for deterministic fixes.
O2 (Reasoning)	       search_knowledge_store	    The bridging tool that prevents model hallucinations.
O3 (Observability)	   Logfire	                    The telemetry layer capturing the "Thought Chain."


Model Provider Layer: Transitioned from raw string IDs to GoogleModel via the pydantic_ai.models.google module to handle the 2026 v1beta API pathing.

Knowledge Retrieval (O1): Implementation of a Keyword-to-Recipe Mapper. The retrieval logic now uses Case-Insensitive Substring Matching to 
bridge the gap between LLM reasoning and JSON keys.

Reasoning Loop (O2): Explicit ReAct (Reason-Act-Observe) pattern. The agent is strictly prompted to Search before Suggesting, ensuring 
it acts as a "Grounded Engineer" rather than a "Generative Assistant."

Safety Constraints: Integration of UsageLimits (request_limit=5). This acts as the "Architectural Circuit Breaker" to prevent infinite loops and 
API quota exhaustion.

----------------------------------------------------------------

Section 4.6: Semantic vs. Syntactic Retrieval)

Section 4.6: The Keyword Bottleneck Observations from Trace bffbff07512c4d439f2d86daf0551671 indicate that LLMs prioritize 
Semantic Intent (e.g., "round to two decimal places") over the specific Syntactic Keywords (e.g., "float64") stored in O1. 
To mitigate this, the search_knowledge_store tool was refined to perform substring matching across multiple metadata fields, 
though the primary challenge remains aligning LLM vocabulary with established data engineering schemas.

Section 4.7: Search Protocol Optimization To bridge the semantic gap between LLM reasoning and syntactic JSON retrieval, 
a Strict Search Protocol was implemented in the agent's core instructions. This ensures that tool arguments are derived from the inspect_dataset 
metadata rather than generative descriptions.

The Final Architecture: "The O1-O2-O3 Integration

Stage                Logic Component                                 Empirical Proof (from Trace)
Input                 O1(Memory),                       "FOUND THE FOLLOWING RECIPES: Precision fix"
Process               O2 (Reasoning)                    Mapping the round(2) solution to the Total Spent column.
Action                O3 (Execution)                    "SUCCESS: Transformation applied... File saved."


-------------------------------------------

# Project Architecture: Agentic RAG for ML Lifecycle

## Overview
This system implements an Agentic Retrieval-Augmented Generation (RAG) framework to automate data engineering tasks. It follows a modular O1-O2-O3 design pattern.

### Layer 1: O1 - Knowledge Retrieval (Memory)
* **Vector Store**: Uses **ChromaDB** as a persistent vector database stored locally.
* **Semantic Search**: Implements intent-based retrieval to handle case-insensitivity and synonyms (e.g., mapping "FIX DECIMALS" to "Precision Fix").
* **Source of Truth**: A curated `memory_store.json` containing verified data engineering recipes.

### Layer 2: O2 - Reasoning Engine (Brain)
* **LLM**: `gemini-1.5-flash-latest`.
* **Framework**: **Pydantic AI** for strict type-safe agent definitions.
* **ReAct Loop**: A Reasoning + Acting cycle that performs multi-step discovery (Inspect -> Search -> Apply).

### Layer 3: O3 - Observability & Safety (Execution)
* **Guardrails**: **UsageLimits** enforce a 5-request ceiling per cycle to prevent infinite loops and manage API costs.
* **Observability**: Integrated with **Pydantic Logfire** for real-time trace monitoring.
* **Executioner**: A local-scope `exec()` environment that applies generated Python code directly to the CSV dataset.

