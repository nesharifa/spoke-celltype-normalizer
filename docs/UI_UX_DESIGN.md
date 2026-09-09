# SPOKE Cell Type Normalizer — UI/UX Design

## Goal
Give researchers a fast, trustworthy way to turn messy free-text cell-type names into the exact Cell Ontology (CL) preferred labels that SPOKE expects, especially for immune cells and neurons.

## Primary user flow
1. User types (or pastes) a free-text name / abbreviation / synonym.
2. Instant (or near-instant) ranked list of CL matches appears.
3. User inspects score, matched synonym, notes, and hierarchy context.
4. One-click actions:
   - Copy preferred label
   - Copy CL ID
   - Open term in OLS (Cell Ontology browser)
   - Open SPOKE Neighborhood Explorer (user then pastes the preferred label into the Cell Type search)
5. (Future) “Search SPOKE with this term” deep-link that pre-fills the Neighborhood Explorer.

## Layout (desktop + mobile)
- **Header**: tool name + “PROTOTYPE” badge + one-sentence purpose.
- **Search card**:
  - Large text input
  - Primary “Normalize” button
  - Example chips (Tregs, microglia, CD8 TEM, OPC, …) for zero-friction discovery
- **Results card**:
  - Ranked result cards
  - Top result visually highlighted (green border)
  - Each card shows: preferred label, CL ID, score, match type + original matched text, category, optional note
  - Action buttons per card
- **Footer**: provenance, link to OLS + SPOKE NE, disclaimer that this is a seed-based prototype.

## Visual language
- Dark theme (matches many scientific tools and reduces eye strain)
- Clear hierarchy: preferred label is the most prominent text
- Score shown numerically; top match emphasized
- Notes in a distinct warning/info color when present (e.g. “prefer microglial cell over macrophage for brain”)
- Minimal chrome; focus on the mapping result

## Interaction principles
- Keyboard-friendly (Enter to search)
- Copy actions give immediate feedback (browser clipboard)
- No forced login / account
- Works offline once the page is loaded (seed embedded in the prototype)
- Graceful empty state with guidance to OLS

## Future enhancements (UI)
- Optional context fields: tissue / anatomy, species, marker string
- Hierarchy browser (parent / children of the chosen CL term)
- “Why this match?” expandable explanation
- Batch mode (paste a list of labels → download mapped table)
- Direct “Open in SPOKE with filters pre-set for CellType + AnatomyCellType + Gene”
- Browser extension that injects suggestions into the live Neighborhood Explorer search box

## Accessibility
- Sufficient contrast
- Focus states on interactive elements
- Semantic HTML
- Screen-reader friendly labels and result structure
