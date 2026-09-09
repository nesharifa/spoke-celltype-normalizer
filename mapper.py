#!/usr/bin/env python3
"""
SPOKE Cell Type Normalizer - Prototype Mapper
=============================================
Simple free-text → Cell Ontology (CL) matcher using a seed dictionary
+ fuzzy string matching. Designed as a starting point for a SPOKE add-on.

Usage:
    from mapper import CellTypeMapper
    mapper = CellTypeMapper()
    results = mapper.map("Tregs")
    print(results)

Or run as script:
    python mapper.py "microglia"
    python mapper.py "CD8 TEM" --top 5
"""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# Default location relative to this file
DEFAULT_SEED = Path(__file__).resolve().parent.parent / "data" / "seed_dictionary.json"


def normalize_text(text: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace, expand a few common patterns."""
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[+\-_/]", " ", t)          # CD4+ → CD4 , TEMRA → temra etc.
    t = re.sub(r"[^\w\s]", " ", t)          # remove remaining punctuation
    t = re.sub(r"\s+", " ", t).strip()
    # light expansions
    replacements = {
        "tregs": "regulatory t cell",
        "treg": "regulatory t cell",
        "nk": "natural killer",
        "dcs": "dendritic cell",
        "dc": "dendritic cell",
        "opc": "oligodendrocyte precursor",
        "tem": "effector memory",
        "tcm": "central memory",
    }
    for k, v in replacements.items():
        if t == k or t.startswith(k + " "):
            t = t.replace(k, v, 1)
    return t


def similarity(a: str, b: str) -> float:
    """Simple ratio similarity (0-1)."""
    return SequenceMatcher(None, a, b).ratio()


class CellTypeMapper:
    def __init__(self, seed_path: str | Path | None = None):
        path = Path(seed_path) if seed_path else DEFAULT_SEED
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.version = data.get("version", "unknown")
        self.terms: list[dict[str, Any]] = data["terms"]
        # Build lookup structures
        self._entries: list[dict[str, Any]] = []
        for term in self.terms:
            preferred = term["preferred_label"]
            cl_id = term["cl_id"]
            cat = term.get("category", "")
            notes = term.get("notes", "")
            # preferred label itself
            self._entries.append({
                "text": preferred,
                "norm": normalize_text(preferred),
                "preferred_label": preferred,
                "cl_id": cl_id,
                "category": cat,
                "notes": notes,
                "match_type": "preferred",
            })
            for syn in term.get("synonyms", []):
                self._entries.append({
                    "text": syn,
                    "norm": normalize_text(syn),
                    "preferred_label": preferred,
                    "cl_id": cl_id,
                    "category": cat,
                    "notes": notes,
                    "match_type": "synonym",
                })

    def map(self, query: str, top_k: int = 5, min_score: float = 0.35) -> list[dict[str, Any]]:
        """
        Return top_k matches for the free-text query.
        Each result contains: preferred_label, cl_id, score, match_type, matched_text, category, notes
        """
        q_norm = normalize_text(query)
        if not q_norm:
            return []

        scored: list[tuple[float, dict]] = []
        seen_cl = set()  # keep best per CL ID

        for entry in self._entries:
            # exact / substring bonus
            score = similarity(q_norm, entry["norm"])
            if q_norm == entry["norm"]:
                score = 1.0
            elif q_norm in entry["norm"] or entry["norm"] in q_norm:
                score = max(score, 0.85)

            if score < min_score:
                continue

            cl_id = entry["cl_id"]
            if cl_id in seen_cl:
                # keep higher score
                existing = next(s for s in scored if s[1]["cl_id"] == cl_id)
                if score > existing[0]:
                    scored.remove(existing)
                    scored.append((score, {
                        "preferred_label": entry["preferred_label"],
                        "cl_id": cl_id,
                        "score": round(score, 3),
                        "match_type": entry["match_type"],
                        "matched_text": entry["text"],
                        "category": entry["category"],
                        "notes": entry["notes"],
                    }))
            else:
                seen_cl.add(cl_id)
                scored.append((score, {
                    "preferred_label": entry["preferred_label"],
                    "cl_id": cl_id,
                    "score": round(score, 3),
                    "match_type": entry["match_type"],
                    "matched_text": entry["text"],
                    "category": entry["category"],
                    "notes": entry["notes"],
                }))

        scored.sort(key=lambda x: (-x[0], x[1]["preferred_label"]))
        return [item for _, item in scored[:top_k]]

    def format_results(self, results: list[dict], query: str) -> str:
        if not results:
            return f'No confident match for "{query}". Try a more specific term or check Cell Ontology (OLS).'
        lines = [f'Query: "{query}"', f"Top matches (prototype seed v{self.version}):", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['preferred_label']}  ({r['cl_id']})")
            lines.append(f"   score={r['score']:.2f}  via {r['match_type']}: \"{r['matched_text']}\"")
            if r["notes"]:
                lines.append(f"   note: {r['notes']}")
            lines.append(f"   SPOKE tip: search Cell Type for \"{r['preferred_label']}\"")
            lines.append("")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SPOKE Cell Type Normalizer prototype")
    parser.add_argument("query", help="Free-text cell type name")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    parser.add_argument("--seed", default=None, help="Path to seed_dictionary.json")
    args = parser.parse_args()

    mapper = CellTypeMapper(args.seed)
    results = mapper.map(args.query, top_k=args.top)
    print(mapper.format_results(results, args.query))


if __name__ == "__main__":
    main()
