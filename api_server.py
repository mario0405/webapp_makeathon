from __future__ import annotations

import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from material_tool import load_material_tree, search_material_knowledgebase


app = FastAPI(title="Material Navigator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChildrenResponse(BaseModel):
    status: str
    material: str
    subcategories: list[str] | None = None


@app.on_event("startup")
def _startup() -> None:
    load_material_tree()


@app.get("/api/top", response_model=list[str])
def get_top_level() -> list[str]:
    tree = load_material_tree()
    if tree is None:
        raise HTTPException(status_code=500, detail="material_tree.json not loaded")
    return [node.get("name", "") for node in tree]


@app.get("/api/children", response_model=ChildrenResponse)
def get_children(name: str) -> ChildrenResponse:
    try:
        raw = search_material_knowledgebase(name)
        data = json.loads(raw)
        if data.get("status") == "found":
            return ChildrenResponse(
                status="found",
                material=name,
                subcategories=data.get("subcategories", []),
            )
        return ChildrenResponse(status="not_found", material=name, subcategories=[])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class ReportRequest(BaseModel):
    paths: list[list[str]]


@app.post("/api/report")
def make_report(req: ReportRequest) -> dict:
    # Compose a simple text report and return it to client
    lines = ["Material Navigator Report", "==========================", ""]
    if not req.paths:
        lines.append("No selections.")
    else:
        for i, p in enumerate(req.paths, 1):
            lines.append(f"{i}. {' > '.join(p)}")
    content = "\n".join(lines) + "\n"
    return {"content": content}

