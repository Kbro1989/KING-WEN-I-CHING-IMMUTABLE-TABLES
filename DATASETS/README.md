# DATASETS Provenance & Extraction Baseline

## 1. PDF Inventory

### 1.1 Benchmark PDFs (14 papers, 30 files)

| arXiv ID | Title | Author(s) | Pages | Source | License |
|---|---|---|---|---|---|
| 2009.00031 | Generative Pretraining from Pixels | Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever | 9 | arXiv | arXiv perpetual non-exclusive license |
| 2102.03334 | ViLT: Vision-and-Language Transformer Without Convolution or Region Supervision | Wonjae Kim, Bokyung Son, Ildoo Kim | 12 | arXiv | arXiv perpetual non-exclusive license |
| 2605.00155 | Wasserstein Distributionally Robust Regret Optimization for Reinforcement Learning from Human Feedback | Yikai Wang, Shang Liu, Jose Blanchet | 59 | arXiv | arXiv perpetual non-exclusive license |
| 2605.00224 | TUR-DPO: Topology- and Uncertainty-Aware Direct Preference Optimization | Abdulhady Abas Abdullah, Fatemeh Daneshfar, Seyedali Mirjalili, Mourad Oussalah | 18 | arXiv | arXiv perpetual non-exclusive license |
| 2605.06070 | Arena as Offline Reward: Efficient Fine-Grained Preference Optimization for Diffusion Models | Zhikai Li, Yue Zhao, Edward Zhongwei Zhang, Xuewen Liu, Jing Zhang, Qingyi Gu, Zhen Dong | 17 | arXiv | arXiv perpetual non-exclusive license |
| 2605.18130 | Rad-VLSM: A Cross-Modal Framework with Semantics-Assisted Prompting for Medical Segmentation and Diagnosis | Fengyi Zhang, Xujie Zeng, Mohan Liu, Zengyi Wang, Yalong Jiang | 14 | arXiv | arXiv perpetual non-exclusive license |
| 2605.22715 | AnyMo: Geometry-Aware Setup-Agnostic Modeling of Human Motion in the Wild | Baiyu Chen, Zechen Li, Wilson Wongso, Lihuan Li, Xiachong Lin, Hao Xue, Benjamin Tag, Flora Salim | 28 | arXiv | arXiv perpetual non-exclusive license |
| 2605.23244 | Convex Optimization for Alignment and Preference Learning on a Single GPU | Miria Feng, Mert Pilanci | 31 | arXiv | arXiv perpetual non-exclusive license |
| 2605.24807 | CLIP-Guided SAM: Parameter-Efficient Semantic Conditioning for Promptable Segmentation | Shayan Jalilian, Abdul Bais | 18 | arXiv | arXiv perpetual non-exclusive license |
| 2605.24856 | The Concept Allocation Zone: Tracking How Concepts Form Across Transformer Depth | James Henry | 37 | arXiv | arXiv perpetual non-exclusive license |
| 2605.25036 | Language Bias in LVLMs: From In-Depth Analysis to Simple and Effective Mitigation | Yangneng Chen, Jing Li | 24 | arXiv | arXiv perpetual non-exclusive license |
| 2605.25334 | Dual-Pathway Geometry-Aware MLLM for Spatial Intelligence | Yufei Zheng, Xuhan Zhu, Zide Liu, Chunpeng Zhou, Chenfeng Wang, Yongchao Xu, Yunnan Wang, Jiawei Liu, Pengfei Yu, Wei Zhai, Yang Cao, Zheng-Jun Zha | 15 | arXiv | arXiv perpetual non-exclusive license |
| 2605.28615 | Compositional Text-to-Image Generation Via Region-aware Bimodal Direct Preference Optimization | Zhuohan Liu, Wujian Peng, Yitong Chen, Zuxuan Wu | 27 | arXiv | arXiv perpetual non-exclusive license |
| 2605.28896 | Feature Geometry of LoRA Adapters: A Sparse Autoencoder Analysis of Representational Divergence in Fine-Tuned Language Models | Prasanth K K | 18 | arXiv | arXiv perpetual non-exclusive license |

### 1.2 File Locations

PDFs are stored in multiple directories (duplicates across categories):

- `DATASETS/benchmark_pdfs/` — 14 files (canonical benchmark set)
- `DATASETS/diffusion-generative/` — 2 files
- `DATASETS/efficient-inference-quantization/` — 1 file
- `DATASETS/llm-alignment/` — 3 files
- `DATASETS/multimodal-learning/` — 2 files
- `DATASETS/pdf/` — 8 files

All PDFs are sourced from arXiv. No publisher versions are included.

## 2. Source & Licensing

### 2.1 Source

All 14 papers are from **arXiv.org** (https://arxiv.org/). Each PDF was downloaded from the arXiv abstract page. The arXiv ID is encoded in the filename (e.g., `2605.00155.pdf`).

### 2.2 License

All papers are distributed under the **arXiv perpetual non-exclusive license**. This license permits reproduction, distribution, and derivative works with attribution. It does not grant trademark rights or imply endorsement.

For papers later published in journals or conferences, the publisher's copyright may apply to the final version. The arXiv versions included here are the author-submitted preprints.

### 2.3 Verification Status

- **arXiv ID**: Verified from filename and PDF metadata
- **Title**: Verified from PDF metadata (except 2009.00031, verified from arXiv page)
- **Author(s)**: Verified from PDF metadata
- **License**: Assumed arXiv perpetual non-exclusive license (not individually verified for each paper)

## 3. Extraction Baseline

### 3.1 Full-Text Baseline

- **File**: `DATASETS/pdf_text_baseline_full.json` (506 KB)
- **Records**: 245 papers
- **Pages**: 5,296 total
- **Schema**: `{"pdf_path": str, "category": str, "page_count": int, "metadata": dict, "pages": [{"page": int, "char_count": int}]}`
- **Note**: This baseline contains per-page character counts only, not full text content.

### 3.2 Full-Text Index

- **File**: `DATASETS/pdf_text_baseline_index.jsonl` (139 KB)
- **Records**: 488 unique arXiv IDs
- **Total characters**: 24,917,409
- **Source**: PyMuPDF text extraction from `C:\Users\krist\Desktop\zotero\learning-corpus\.text\`
- **Categories**: graph-neural-networks (67), diffusion-generative (64), llm-alignment (48), efficient-inference-quantization (42), multimodal-learning (24), plus 243 additional papers

### 3.3 Extraction Tool

- **Tool**: PyMuPDF (pymupdf) 1.28.2
- **Method**: `page.get_text()` per page
- **Date**: 2026-10-16
- **Input**: 245 PDFs from `C:\Users\krist\Desktop\zotero\learning-corpus\`

### 3.4 Math Extraction Baseline

- **File**: `DATASETS/baseline_2026-10-09/`
- **Contents**: `manifest.json`, `occurrences.jsonl`, `pinned_versions.txt`, `scoreboard_v15.json`, `test_results.json`
- **Papers**: 14 papers, 3,409 equations
- **Parser**: `scripts/math_pdf_parser.py` (6-layer extraction)
- **MathML Parser**: `scripts/mathml_parser.py`
- **Contract**: `scripts/math_contract.py`

## 4. Reproduction

### 4.1 Re-extract Full Text

```bash
cd C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES
.venv/Scripts/python.exe -c "
import pymupdf, json
from pathlib import Path
corpus = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
results = []
for pdf in corpus.rglob('*.pdf'):
    doc = pymupdf.open(pdf)
    pages = [{'page': i+1, 'char_count': len(doc[i].get_text())} for i in range(len(doc))]
    results.append({'pdf_path': str(pdf.relative_to(corpus)), 'category': pdf.parent.name, 'page_count': len(doc), 'metadata': doc.metadata, 'pages': pages})
    doc.close()
Path('DATASETS/pdf_text_baseline_full.json').write_text(json.dumps(results, indent=2, ensure_ascii=False))
"
```

### 4.2 Verify Baseline

```bash
.venv/Scripts/python.exe -c "
import json
data = json.load(open('DATASETS/pdf_text_baseline_full.json'))
print(f'Records: {len(data)}')
print(f'Pages: {sum(r[\"page_count\"] for r in data)}')
print(f'Categories: {set(r[\"category\"] for r in data)}')
"
```

### 4.3 Re-run Math Extraction

```bash
.venv/Scripts/python.exe scripts/math_pdf_parser.py --input DATASETS/benchmark_pdfs/ --output DATASETS/math_recovery/
```

## 5. Known Limitations

- The full-text baseline (`pdf_text_baseline_full.json`) contains only character counts, not actual text. For full text, use the `.text` files in `C:\Users\krist\Desktop\zotero\learning-corpus\.text\`.
- 2009.00031 PDF metadata has empty title/author fields; metadata was verified from the arXiv abstract page.
- License information is assumed from arXiv's standard license and was not individually verified for each paper.
- The 14 benchmark papers are a subset of the 245-paper corpus, selected for math extraction benchmarking.
