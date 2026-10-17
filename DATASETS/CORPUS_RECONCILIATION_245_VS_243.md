# Corpus Reconciliation — 245 vs 243

**Date:** 2026-10-16
**Status:** RESOLVED

---

## Finding

The discrepancy is a **file count vs unique paper count** difference, not a paper removal.

| Source | Count | Notes |
|--------|-------|-------|
| PDF files on disk | **245** | File count |
| `.text` files on disk | 490 | 2 per paper |
| Unique arxiv IDs in PDFs | **243** | Unique paper count |
| Unique arxiv IDs in `.text` | 243 | Unique paper count |
| Manifest papers | **243** | Canonical denominator |

## Root Cause

**2 papers have duplicate PDF files** (identical byte size, duplicate downloads with different filenames):

| Paper ID | Duplicate files | Size |
|----------|-----------------|------|
| `2106.10934` | `diffusion-generative/2106.10934_GRAND_ Graph Neural Diffusion.pdf`<br>`diffusion-generative/2106.10934_Graph Neural Diffusion.pdf` | 1,690,210 bytes (both) |
| `2605.30323` | `llm-alignment/2605.30323_In-Context Reward Adaptation for Robust Preference Modeling.pdf`<br>`llm-alignment/2605.30323_In-Context-Reward-Adaptation.pdf` | 299,558 bytes (both) |

245 PDF files = 243 unique papers + 2 duplicate files.

## Verified Differences

```
In .text but NOT in manifest: []   (empty)
In manifest but NOT in .text: []   (empty)
In PDFs but NOT in manifest:  []   (empty)
In manifest but NOT in PDFs:  []   (empty)
```

**No paper was removed, deduplicated, or excluded from the manifest.**

## Canonical Denominator

**243 unique papers** is the frozen denominator. It is derived from unique arxiv IDs present in both the PDF corpus and the `.text` corpus, not from the number of files processed.

## Recommendation

The manifest at `DATASETS/CORPUS_MANIFEST_2026-10-16.json` (243 entries) is authoritative. The 245 figure should be understood as a file count and retired as a paper-count claim.
