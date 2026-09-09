#!/usr/bin/env python3
"""
SPOKE Cell Type Normalizer - Mapper (strict token matching)
===========================================================
Maps free-text cell-type names to preferred Cell Ontology (CL) labels.

Uses token overlap instead of character similarity, so weak letter-based
matches (e.g. astrocyte → plasmacyte) are rejected.

Usage:
    python mapper.py "astrocyte"
    python mapper.py "Tregs"
    python mapper.py "CD8 TEM" --top 3
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_SEED = Path(__file__).resolve().parent.parent / "data" / "seed_dictionary.json"

# Generic words that should not drive a match by themselves
STOP = {"cell", "cells", "positive", "negative", "alpha", "beta", "the", "of", "and", "a", "an"}

# Common abbreviations expanded before matching
ABBREV = {
    "tregs": "regulatory t cell",
    "treg": "regulatory t cell",
    "nk": "natural killer",
    "dcs": "dendritic cell",
    "dc": "dendritic cell",
    "opc": "oligodendrocyte precursor",
    "tem": "effector memory",
    "tcm": "central memory",
    "asc": "antibody secreting",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[+\-_/]", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for k, v in ABBREV.items():
        if t == k or t.startswith(k + " "):
            t = t.replace(k, v, 1)
    return t


def tokens(text: str) -> list[str]:
    return [w for w in normalize_text(text).split() if len(w) > 1 and w not in STOP]


def score_match(query_norm: str, entry_norm: str) -> float:
    """Strict score based on shared meaningful tokens. No pure letter similarity."""
    if not query_norm or not entry_norm:
        return 0.0

    if query_norm == entry_norm:
        return 1.0

    # Whole-phrase containment
    if (
        entry_norm.startswith(query_norm + " ")
        or entry_norm.endswith(" " + query_norm)
        or query_norm.startswith(entry_norm + " ")
        or query_norm.endswith(" " + entry_norm)
    ):
        return 0.95

    q_toks = tokens(query_norm)
    e_toks = tokens(entry_norm)
    if not q_toks or not e_toks:
        return 0.0

    shared = [t for t in q_toks if t in e_toks]
    if not shared:
        return 0.0  # no meaningful word in common → reject

    precision = len(shared) / len(q_toks)
    recall = len(shared) / len(e_toks)

    if precision < 0.6:
        return 0.0

    score = 0.55 + (0.35 * precision) + (0.10 * recall)
    if len(e_toks) <= 3:
        score += 0.05
    return min(score, 0.99)


class CellTypeMapper:
    def __init__(self, seed_path: str | Path | None = None):
        path = Path(seed_path) if seed_path else DEFAULT_SEED
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.version = data.get("version", "unknown")
        self.terms: list[dict[str, Any]] = data["terms"]
        self._entries: list[dict[str, Any]] = []
        for term in self.terms:
            preferred = term["preferred_label"]
            cl_id = term["cl_id"]
            cat = term.get("category", "")
            notes = term.get("notes", "")
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

    def map(self, query: str, top_k: int = 5, min_score: float = 0.70) -> list[dict[str, Any]]:
        q_norm = normalize_text(query)
        if not q_norm:
            return []

        scored: list[tuple[float, dict]] = []
        seen_cl: set[str] = set()

        for entry in self._entries:
            score = score_match(q_norm, entry["norm"])
            if score < min_score:
                continue

            cl_id = entry["cl_id"]
            result = {
                "preferred_label": entry["preferred_label"],
                "cl_id": cl_id,
                "score": round(score, 3),
                "match_type": entry["match_type"],
                "matched_text": entry["text"],
                "category": entry["category"],
                "notes": entry["notes"],
            }

            if cl_id in seen_cl:
                existing = next(s for s in scored if s[1]["cl_id"] == cl_id)
                if score > existing[0]:
                    scored.remove(existing)
                    scored.append((score, result))
            else:
                seen_cl.add(cl_id)
                scored.append((score, result))

        scored.sort(key=lambda x: (-x[0], x[1]["preferred_label"]))
        return [item for _, item in scored[:top_k]]

    def format_results(self, results: list[dict], query: str) -> str:
        if not results:
            return (
                f'No confident match for "{query}".\n'
                "Try a more specific term or check Cell Ontology (OLS)."
            )
        lines = [f'Query: "{query}"', f"Top matches (strict token matching, seed v{self.version}):", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['preferred_label']}  ({r['cl_id']})")
            lines.append(f"   score={r['score']:.2f}  via {r['match_type']}: \"{r['matched_text']}\"")
            if r["notes"]:
                lines.append(f"   note: {r['notes']}")
            lines.append(f"   SPOKE tip: search Cell Type for \"{r['preferred_label']}\"")
            lines.append("")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SPOKE Cell Type Normalizer (strict matching)")
    parser.add_argument("query", help="Free-text cell type name")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    parser.add_argument("--seed", default=None, help="Path to seed_dictionary.json")
    args = parser.parse_args()

    mapper = CellTypeMapper(args.seed)
    results = mapper.map(args.query, top_k=args.top)
    print(mapper.format_results(results, args.query))


if __name__ == "__main__":
    main()
