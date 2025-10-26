# 🏗️ AI Material Validation Agent

This is a project for the FHNW MAKEathon 2025 "Urban Planning & Sustainable Material" challenge.

## The Problem
Urban planners use PDF plans with material legends (e.g., `Situation Lindenstrasse.pdf`). However, these materials are often spelled inconsistently, use synonyms, or are abbreviated (e.g., "Pflästerung" on the plan vs. "Pflasterbeläge" in the official database). This "mismatch" makes manual validation and sustainability analysis slow and error-prone.

## Our Solution
We built an AI-driven system that bridges this "gap." Our solution consists of four parts:

1.  **A Knowledge Base (KB):** We parsed the official `Materialmatrix.xlsx` into a structured `material_tree.json` and a "translation" map (`aliases.json`) that links real-world terms to the official terms.
2.  **An AI Agent:** A `gemini-2.5-pro` agent (in `agent.py`) that understands user prompts and uses a custom **Tool** to intelligently query the KB.
3.  **A Visual Dashboard:** A `streamlit` web app (`dashboard.py`) that provides a user-friendly interface for searching the KB and visually exploring the complete material hierarchy.
4.  **A Material Chatbot:** An interactive chatbot (`chatbot.py`) that guides users through the material hierarchy in a tree-like navigation system with 3 options per level.

## Project Status
**DONE:**
* [x] Parse the official `Materialmatrix` into a clean JSON Knowledge Base.
* [x] Build a "smart" search tool that can handle synonyms (`aliases.json`).
* [x] Build an interactive Streamlit dashboard for visual search.
* [x] Build a conversational AI agent (`agent.py`) that can answer questions about the materials.
* [x] Build an interactive material chatbot (`chatbot.py`) for tree-like navigation.

**IN PROGRESS:**
* [ ] **PDF Extraction:** Using multimodal AI (`extract.py`) to automatically read material legends from scanned PDF plans.
* [ ] **Knowledge Graph:** Converting our JSON KB into an RDF graph (`material_graph.ttl`) to load into metaphactory.
* [ ] **Sustainability Data:** Integrating CO2 / environmental data into the KB to allow the agent to perform sustainability analysis.

## How to Run

1.  **Set up the environment:**
    ```bash
    conda create -n makeathon python=3.11
    conda activate makeathon
    pip install -r requirements.txt
    ```
2.  **Authenticate with Google Cloud**
    (Add your auth instructions here...)

3.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```
4.  **Run the Agent:**
    ```bash
    python agent.py
    ```
5.  **Run the Material Chatbot:**
    ```bash
    streamlit run chatbot.py
    ```