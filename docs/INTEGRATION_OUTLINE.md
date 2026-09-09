# Integration Outline — Feeding the Normalizer into Biorouter & SPOKE API

## 1. Current SPOKE entry points
- **Neighborhood Explorer (GUI)**: https://spoke.rbvi.ucsf.edu/neighborhood.html  
  User selects node type “Cell Type”, types a name, chooses from dropdown.
- **REST API** (used by NE and programmatic clients): search endpoints that accept node type + query term.
- **Biorouter**: https://biorouter.ucsf.edu/ — LLM front-end that grounds natural-language questions in SPOKE paths.

## 2. Where the normalizer fits

### A. Pre-query normalization (recommended first step)
```
User free-text  →  CellTypeMapper.map()  →  preferred_label + CL ID
                 ↓
         SPOKE search (Cell Type node) using preferred_label
```
Benefits: reduces failed searches and inconsistent dropdown choices caused by synonyms/abbreviations.

### B. Biorouter / LLM pipeline
1. User asks a natural-language question involving cell types  
   (“Which neurotransmitter receptors are expressed on Tregs and microglia?”).
2. LLM (or a dedicated entity-extraction step) identifies candidate cell-type mentions.
3. Each mention is passed through the normalizer → canonical CL term + ID.
4. Biorouter / SPOKE query builder uses only the canonical terms when constructing graph paths.
5. Response can optionally show the original mention → normalized mapping for transparency.

This directly addresses the “many filter options + inconsistent annotations” limitation noted in the original presentation.

### C. Programmatic / batch use
- Python package (the prototype `mapper.py` is the start).
- Call from notebooks, pipelines, or a small FastAPI/Flask service.
- Later: expose a simple HTTP endpoint  
  `GET /normalize?q=Tregs&top=5` → JSON list of matches.

## 3. Concrete integration steps (near-term)

| Step | Action | Effort |
|------|--------|--------|
| 1 | Keep seed dictionary + fuzzy mapper as the fast local path | Done (prototype) |
| 2 | Add optional live OLS lookup (fallback when seed confidence < threshold) | Low–medium |
| 3 | Add a “Copy preferred label” + “Open SPOKE NE” button in the web UI | Done in prototype |
| 4 | Create a URL parameter or deep-link convention for Neighborhood Explorer (if SPOKE team supports it) e.g. `?nodeType=CellType&q=regulatory%20T%20cell` | Requires SPOKE-side change or userscript |
| 5 | Wrap mapper as a Biorouter pre-processing hook or tool call | Medium (coordinate with Biorouter maintainers) |
| 6 | Publish a small public API or npm/PyPI package so other SPOKE users can adopt it | Medium |

## 4. Longer-term vision
- Replace / augment the seed with full CL + embeddings (CellOntologyMapper-style) or GCTHarmony-style LLM harmonization.
- Maintain a SPOKE-specific synonym overlay (terms that appear in HPA / Bgee / literature but are under-represented in core CL synonyms).
- Feed normalization logs back to improve the seed and to suggest new CL terms when needed.
- Browser extension that auto-suggests while the user types in Neighborhood Explorer.

## 5. Non-goals (for the first versions)
- Replacing Cell Ontology itself
- Performing expression or pathway analysis (that stays in SPOKE)
- Guaranteeing 100 % accuracy on every rare or disease-specific cell state (human review + OLS remains the safety net)

## 6. Success metrics
- Reduction in “no results” or wrong-node searches for common immune/neuron terms
- User adoption inside the lab / project (measured by repeated use of the normalizer before SPOKE queries)
- Positive feedback that the original neurotransmitter–immune questions become easier to run reproducibly
