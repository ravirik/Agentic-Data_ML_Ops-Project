# Agentic Data — MLOps Project 🚀

[![Project Status](https://img.shields.io/badge/status-v1.0%20%E2%80%94%20Heuristic%20Baseline-blue)](#)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-brightgreen)](https://www.python.org/)
[![Observability](https://img.shields.io/badge/observability-Logfire-lightgrey)](#)

A focused Agentic MLOps prototype demonstrating a grounded ReAct-style agent for deterministic data cleaning and remediation. The system couples a type-safe agent framework (pydantic-ai) with a JSON-based knowledge store to avoid hallucinations, an execution layer that applies verified Python transformations, and observability through Logfire.

✨ Built for auditability, deterministic fixes, and rapid prototyping of agentic data engineering flows.

---

Table of contents
- Overview
- Quick architecture (visual)
- Key components
- Repository layout
- Quickstart (run locally)
- Memory (knowledge) store & recipe format
- Example flow (step-by-step)
- Observability & safety
- Testing & debugging
- Extending the project
- Contributing
- License & contact

---

## Overview

This project demonstrates an agentic approach to data engineering:

- O1 — Memory: JSON knowledge store (memory_store.json) of verified transformation recipes.
- O2 — Reasoning: pydantic-ai Agent wired to a Gemini model performing inspect → search → act.
- O3 — Execution & Observability: Decorated tools that apply transformations and Logfire traces for audit.

Goal: deterministic, auditable fixes for common "dirty data" problems (nulls, types, precision, date formats), not free-form generation.

---

## Quick architecture (visual) 🏗️

ASCII flow (simple):
