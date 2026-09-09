# SPOKE Cell Type Normalizer

**Live demo:**  
`https://nesharifa.github.io/spoke-celltype-normalizer/`

A lightweight add-on for the [SPOKE](https://spoke.ucsf.edu/) knowledge graph.  
It maps free-text cell-type names, abbreviations, and synonyms to consistent **Cell Ontology (CL)** preferred labels — especially useful for immune cells and neurons.

This reduces the “inconsistent annotations” problem when searching SPOKE Neighborhood Explorer.

---

## Features

- Instant free-text → CL term mapping (seed dictionary + fuzzy matching)
- Focused on immune cells (Tregs, CD8 TEM, microglia, …) and neurons/glia
- One-click copy of preferred label or CL ID
- Links to Cell Ontology (OLS) and SPOKE Neighborhood Explorer
- Pure front-end — works offline once loaded
- Optional Python mapper for local / batch use

---

## Quick start (website)

1. Open the live GitHub Pages URL (see top of this README after you deploy).
2. Type a cell type (or click an example chip).
3. Copy the preferred label and paste it into [SPOKE Neighborhood Explorer](https://spoke.rbvi.ucsf.edu/neighborhood.html) as a **Cell Type** search.

---

## Repository structure

```
spoke-celltype-normalizer/
├── index.html              ← Web UI (GitHub Pages serves this)
├── data/
│   └── seed_dictionary.json
├── src/
│   └── mapper.py           ← Python version of the mapper
├── docs/
│   ├── UI_UX_DESIGN.md
│   └── INTEGRATION_OUTLINE.md
├── LICENSE
└── README.md
```

---

## Local use

### Web UI
Just open `index.html` in any modern browser.

### Python mapper
```bash
python3 src/mapper.py "Tregs"
python3 src/mapper.py "microglia"
python3 src/mapper.py "CD8 TEM" --top 3
```

---

## How to deploy on GitHub Pages (step-by-step)

### 1. Create the repository
- Go to [github.com/new](https://github.com/new)
- **Repository name:** `spoke-celltype-normalizer` (recommended)
- Description (optional): `Cell type name normalizer for SPOKE – map free-text to Cell Ontology terms`
- Set to **Public**
- **Do not** check “Add a README” (we already have one)
- Click **Create repository**

### 2. Upload the files
**Option A – Web interface (easiest)**
1. On the new empty repo page click **uploading an existing file**
2. Drag **all** the contents of this folder (the files and the `data`, `src`, `docs` folders) into the upload area
3. Commit message: `Initial commit – SPOKE Cell Type Normalizer`
4. Click **Commit changes**

**Option B – Git command line**
```bash
git clone https://github.com/YOUR_USERNAME/spoke-celltype-normalizer.git
cd spoke-celltype-normalizer
# copy all files from the prepared folder into this directory
git add .
git commit -m "Initial commit – SPOKE Cell Type Normalizer"
git push origin main
```

### 3. Enable GitHub Pages
1. In your repo go to **Settings** → **Pages** (left sidebar)
2. Under **Source** choose:
   - Branch: `main`
   - Folder: `/ (root)`
3. Click **Save**
4. Wait 30–60 seconds. GitHub will show the live URL:  
   `https://YOUR_USERNAME.github.io/spoke-celltype-normalizer/`

### 4. (Optional) Make the demo link nice
Edit this README and replace `YOUR_USERNAME` with your actual GitHub username so the live demo link at the top works for everyone.

---

## Suggested repository title & description

| Field              | Suggested value |
|--------------------|-----------------|
| **Repository name** | `spoke-celltype-normalizer` |
| **Description**     | Cell type name normalizer for SPOKE – map free-text / abbreviations to consistent Cell Ontology (CL) terms (immune + neuron focused) |
| **Topics** (optional) | `spoke`, `cell-ontology`, `bioinformatics`, `knowledge-graph`, `single-cell`, `immunology`, `neuroscience` |

---

## Disclaimer
This is a prototype. Always verify critical terms against the official [Cell Ontology on OLS](https://www.ebi.ac.uk/ols4/ontologies/cl) and the live SPOKE graph. The seed list is intentionally focused on immune and neuronal cell types and can be expanded.

---

## License
MIT License – see [LICENSE](LICENSE)

---

Created for exploring immune cell – neuron interactions with SPOKE (2026).
