"""
Streamlit Material Navigator

Clean UI to navigate a hierarchical JSON structure level-by-level.
Users choose a path from top to bottom; each completed path is stored.
On "End", a simple report listing all chosen paths is generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st
import time
import pandas as pd
from material_tool import load_material_tree, search_material_knowledgebase


# ---------- Page config ----------
st.set_page_config(page_title="Material Navigator", layout="wide")


# ---------- Helpers ----------
def get_top_level_names(tree: list[dict]) -> list[str]:
    return [node.get("name", "") for node in (tree or [])]


def get_children_names(parent_name: str) -> list[str]:
    try:
        resp = json.loads(search_material_knowledgebase(parent_name))
        if resp.get("status") == "found":
            return list(resp.get("subcategories", []))
    except Exception:
        pass
    return []


def path_to_str(path: List[str]) -> str:
    return " > ".join(path)


def write_report(paths: List[List[str]]) -> tuple[str, bytes]:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    title = f"Material Navigator Report - {ts}\n"
    lines = [title, "=" * len(title.strip()), ""]
    if not paths:
        lines.append("No selections.")
    else:
        for i, p in enumerate(paths, 1):
            lines.append(f"{i}. {path_to_str(p)}")
    content = "\n".join(lines) + "\n"

    # Save to file alongside this script
    out_path = Path(__file__).parent / f"selection_report_{ts}.txt"
    out_path.write_text(content, encoding="utf-8")
    return str(out_path), content.encode("utf-8")


# ---------- Session State ----------
if "tree" not in st.session_state:
    st.session_state.tree = load_material_tree() or []
if "current_path" not in st.session_state:
    st.session_state.current_path: List[str] = []
if "selections" not in st.session_state:
    st.session_state.selections: List[List[str]] = []
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False
    st.session_state.report_path = None
    st.session_state.report_data = None
if "stage" not in st.session_state:
    # stages: upload -> table -> chat
    st.session_state.stage = "upload"
if "uploaded_pdf_name" not in st.session_state:
    st.session_state.uploaded_pdf_name = None


# ---------- Chat UI ----------
st.markdown(
    """
    <style>
      .app-header {display:flex; align-items:center; justify-content:space-between; padding: 0.5rem 0;}
      .brand {font-size: 1.6rem; font-weight: 600;}
      .subtle {color: #6b7280;}
      .toolbar .stButton>button {border-radius: 999px; padding: 0.4rem 0.9rem;}
      .primary-btn .stButton>button {background:#2563eb; color:#fff; border:1px solid #1d4ed8;}
      .ghost .stButton>button {background:transparent; border:1px solid #e5e7eb;}
      .danger .stButton>button {background:#ef4444; color:#fff; border:1px solid #dc2626;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-header"><div class="brand">Material Navigator</div><div class="subtle">Demo: PDF -> Table -> Chat</div></div>', unsafe_allow_html=True)

# Demo flow before chat
if st.session_state.stage == "upload":
    st.subheader("Schritt 1: PDF hochladen")
    uploaded = st.file_uploader("Bitte eine PDF-Datei auswählen", type=["pdf"], accept_multiple_files=False)
    if uploaded is not None:
        st.session_state.uploaded_pdf_name = uploaded.name
        with st.spinner("Analysiere Dokument ..."):
            time.sleep(2)
        st.success(f"Datei geladen: {st.session_state.uploaded_pdf_name}")
        st.session_state.stage = "table"
        st.rerun()
    st.stop()
elif st.session_state.stage == "table":
    st.subheader("Schritt 2: Extrahierte Tabelle")
    # Show the attached table as requested
    df_attached = pd.DataFrame([
        {"Material": "Asphalt",      "Category": "Belag"},
        {"Material": "Beton",        "Category": "Belag"},
        {"Material": "Platten",      "Category": "Belag"},
        {"Material": "Naturstein",   "Category": "Belag"},
        {"Material": "Beton",        "Category": "Mauer"},
        {"Material": "Mauerstein",   "Category": "Mauer"},
        {"Material": "Holz",         "Category": "Mauer"},
        {"Material": "Betonblocken", "Category": "Treppe"},
        {"Material": "Naturstein",   "Category": "Treppe"},
        {"Material": "Holz",         "Category": "Treppe"},
    ])
    st.dataframe(df_attached, use_container_width=True)
    st.divider()
    if st.button("Weiter zum Chat", type="primary"):
        st.session_state.stage = "chat"
        st.rerun()
    st.stop()
    excel_path = Path(__file__).parent / "Materialmatrix.xlsx"
    df = None
    if excel_path.exists():
        try:
            df = pd.read_excel(excel_path)
        except Exception:
            df = None
    if df is not None and not df.empty:
        st.caption(f"Source: {excel_path.name} (demo, not parsed from {st.session_state.uploaded_pdf_name})")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Could not load example table. Showing a small demo table.")
        st.dataframe(pd.DataFrame([
            {"Material": "Steel", "Density": 7.85, "Hardness": "HRC 60"},
            {"Material": "Aluminum", "Density": 2.70, "Hardness": "HB 30"},
            {"Material": "Copper", "Density": 8.96, "Hardness": "HB 50"},
        ]), use_container_width=True)
    st.divider()
    if st.button("Continue to Chat", type="primary"):
        st.session_state.stage = "chat"
        st.rerun()
    st.stop()

# Top toolbar
toolbar_left, toolbar_mid, toolbar_right = st.columns([1, 1, 2])
with toolbar_left:
    back_disabled = not st.session_state.current_path
    if st.button("Zurück", disabled=back_disabled):
        if st.session_state.current_path:
            st.session_state.current_path.pop()
            st.session_state.chat.append({
                "role": "assistant",
                "content": "Eine Ebene zurück."
            })
        st.rerun()
with toolbar_mid:
    if st.button("Pfad zurücksetzen"):
        st.session_state.current_path = []
        st.session_state.chat.append({
            "role": "assistant",
            "content": "Pfad zurückgesetzt. Bitte oben neu wählen."
        })
        st.rerun()
with toolbar_right:
    c1, c2 = st.columns([2, 3])
    with c2:
        if st.button("Quit & Download Report"):
            save_path, data = write_report(st.session_state.selections)
            st.session_state.report_ready = True
            st.session_state.report_path = save_path
            st.session_state.report_data = data
    if st.session_state.report_ready and st.session_state.report_data is not None:
        st.success(f"Report gespeichert: {st.session_state.report_path}")
        st.download_button(
            label="Report herunterladen",
            data=st.session_state.report_data,
            file_name=Path(st.session_state.report_path).name,
            mime="text/plain",
        )

st.caption("Wähle Optionen Schritt für Schritt. Am Ende eines Pfads wird er gespeichert und oben neu begonnen.")

# Initialize chat once
if "chat" not in st.session_state:
    st.session_state.chat = []
if "chat_initialized" not in st.session_state:
    st.session_state.chat.append({
        "role": "assistant",
        "content": "Hallo! Bitte wähle eine Kategorie, um zu starten."
    })
    st.session_state.chat_initialized = True
if "step_id" not in st.session_state:
    st.session_state.step_id = 0

# Determine current options at this step
if not st.session_state.current_path:
    options = get_top_level_names(st.session_state.tree)
    prompt = "Bitte wähle eine Kategorie:"
else:
    options = get_children_names(st.session_state.current_path[-1])
    prompt = f"Unterkategorien von '{st.session_state.current_path[-1]}':"

# If at leaf, finalize path and reset
if st.session_state.current_path and not options:
    finished_path = st.session_state.current_path.copy()
    st.session_state.selections.append(finished_path)
    st.session_state.chat.append({
        "role": "assistant",
        "content": f"Pfad abgeschlossen: {path_to_str(finished_path)}. Starte erneut oben."
    })
    st.session_state.current_path = []
    options = get_top_level_names(st.session_state.tree)
    prompt = "Bitte wähle eine Kategorie:"

# Sidebar with selections and report
with st.sidebar:
    st.subheader("Ausgewählte Pfade")
    if st.session_state.selections:
        for i, p in enumerate(st.session_state.selections, 1):
            st.write(f"{i}. {path_to_str(p)}")
    else:
        st.caption("Noch keine Pfade.")

    st.divider()
    if st.button("Ende & Report erzeugen", type="primary", use_container_width=True):
        save_path, data = write_report(st.session_state.selections)
        st.success(f"Report gespeichert: {save_path}")
        st.download_button(
            label="Report herunterladen",
            data=data,
            file_name=Path(save_path).name,
            mime="text/plain",
            use_container_width=True,
        )

# Render chat history
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Render assistant message with current options as buttons
with st.chat_message("assistant"):
    st.write(prompt)

    chosen = None
    cols = st.columns(3) if options else [st]
    for idx, opt in enumerate(options):
        col = cols[idx % len(cols)]
        with col:
            if st.button(opt, key=f"opt-{st.session_state.step_id}-{idx}"):
                chosen = opt

    # Handle choice
    if chosen is not None:
        st.session_state.chat.append({"role": "user", "content": chosen})
        st.session_state.current_path.append(chosen)
        st.session_state.step_id += 1
        st.rerun()
