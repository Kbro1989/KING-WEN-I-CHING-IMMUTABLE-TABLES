# Math-to-PDF Association Contract v1

## 1. Purpose and scope

This contract defines the association sidecar layer between the existing
extraction machinery and the semantic MathML/AST pipeline. It does **not**
modify, replace, or expand `ExprNode`; it does not add a new extraction
engine; and it does not watermark existing frozen artifacts.

Existing modules preserved:
- `arxiv_html_parser.py` (HTML → MathML tree)
- `mathml_parser.py` (MathML → solver expression)
- `math_contract.py` (`ExprNode`, `SourceOccurrence`, `RecoveryRecord`)
- `structural_ast_extractor.py` (MathML → typed `ExprNode` tree)
- `math_ast_integration.py` (occurrence binding on AST root)
- `targeted_math_detector.py` (PDF per-character observations with bbox)
- `v2_delimiter_aware_structural_recovery.py` and `delimiter_aware_structural_recovery.py`
  (delimiter recovery gates D1–D6 — frozen baseline, no changes)

New scope this contract governs:
- Stage A — source-occurrence ↔ PDF expression-region alignment
- Stage B — AST node ↔ glyph observation association
- Relationship geometry (role-level bboxes, not just a merged union)
- Independently adjudicated validation (contract tests vs association tests)

---

## 2. Sidecar schema

All sidecar records are emitted as a versioned JSON document. Each record
is an independent object with its own stable ID and no cross-record
references by implicit position.

### 2.1 Top-level document skeleton

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-11-12T00:00:00Z",
  "source_occurrence_table": {
    "paper_id": "2605.00155",
    "paper_version": "v1",
    "extraction_revision": "mathml-20261112"
  },
  "source_alignments": [ /* Stage A records */ ],
  "ast_nodes": [ /* Stage B nodes */ ],
  "glyph_observations": [ /* per-character observations */ ],
  "node_associations": [ /* Stage B bindings */ ],
  "relationship_geometry": [ /* role-level geometry */ ]
}
```

### 2.2 `source_alignment` record

```json
{
  "id": "src_align:2605.00155:v1:math[42]:pdf_region_3",
  "source_occurrence_id": "paper:2605.00155:v1:math[42]",
  "pdf_sha256": "sha256:9f2c...",
  "page_index": 3,
  "expression_region": {
    "rect_pdf_pt": [100.0, 200.0, 350.0, 240.0],
    "block_index": 0,
    "line_index": 4,
    "span_index": 0
  },
  "alignment_method": "page_region_overlap",
  "confidence": 0.88,
  "note": "unverified_region"
}
```

### 2.3 `ast_node` record

```json
{
  "id": "paper:2605.00155:v1:math[42]:root/0",
  "parent_id": "paper:2605.00155:v1:math[42]:root",
  "tree_path": "root/0",
  "source_expr_id": "paper:2605.00155:v1:math[42]",
  "kind": "msup",
  "value": null,
  "attributes": {
    "base_node_id": "paper:2605.00155:v1:math[42]:root/0",
    "exponent_node_id": "paper:2605.00155:v1:math[42]:root/1"
  },
  "glyph_ids": [ "glyph:2605.00155:v1:math[42]:1" ],
  "association_status": "established"
}
```

### 2.4 `glyph_observation` record

```json
{
  "id": "glyph:2605.00155:v1:math[42]:1",
  "page_index": 3,
  "observation_type": "page_i_block_j_line_k_span_m_char",
  "char": "x",
  "bbox_pdf_pt": [100.0, 200.0, 110.0, 208.0],
  "width_pt": 10.0,
  "height_pt": 8.0,
  "font": "Times-Roman",
  "font_size_pt": 12.0
}
```

### 2.5 `node_association` record

```json
{
  "node_id": "paper:2605.00155:v1:math[42]:root/0",
  "matched_glyph_ids": ["glyph:2605.00155:v1:math[42]:1"],
  "association_method": "expression_region_overlap",
  "confidence": 0.87,
  "status": "established"
}
```

### 2.6 `relationship_geometry` record

```json
{
  "relationship_id": "rel:paper:2605.00155:v1:math[42]:root/0",
  "expression_type": "msup",
  "relationships": [
    {
      "child_role": "base",
      "child_node_id": "paper:2605.00155:v1:math[42]:root/0",
      "child_glyph_ids": ["glyph:2605.00155:v1:math[42]:1"],
      "child_bbox_pdf_pt": [100.0, 200.0, 110.0, 208.0]
    },
    {
      "child_role": "exponent",
      "child_node_id": "paper:2605.00155:v1:math[42]:root/1",
      "child_glyph_ids": ["glyph:2605.00155:v1:math[42]:2"],
      "child_bbox_pdf_pt": [102.0, 195.0, 104.0, 203.0]
    }
  ],
  "combined_bbox_pdf_pt": [100.0, 195.0, 110.0, 208.0]
}
```

---

## 3. Deterministic node identity

Node IDs are computed from the source occurrence and the tree path; they do
not modify the frozen `ExprNode`.

```
node_id = source_expr_id + ":" + tree_path
```

where `source_expr_id = paper_id:version:source_locator` and `tree_path` is
the pre-order path from the root (e.g. `root/0`, `root/1`, `root/0/child`).

The tree path is interpreted against a versioned AST serialization. If the
AST shape changes, the association record must be regenerated; it is not
guaranteed to survive AST revision changes.

### 3.1 Role attachment (no `ExprNode` mutation)

Child roles are attached in `attributes` on the parent `ExprNode`, as
already done in `math_ast_integration.py` through `source_expr_id`. This
contract extends that by adding a `base_node_id`/`exponent_node_id` (for
`msup`), `numerator_node_id`/`denominator_node_id` (for `mfrac`), and the
corresponding three roles for `munderover`. These are attributes on the
**parent** node — not new fields on `ExprNode`.

### 3.1 Sidecar writer location and non-mutation

The sidecar writer (`build_association_sidecar`) lives in the production
module `scripts/math_pdf_association.py`, not in the test file. The test
suite imports it and exercises it. The writer:

- accepts a list of records with a `record_type` discriminator;
- never mutates the input records (it reads `record_type` via `.get()`);
- returns a fresh sidecar dict on every call;
- is deterministic: identical input records produce identical output.

### 3.2 Versioning extension

The node_id scheme from Section 3 remains:

```
node_id = source_expr_id + ":" + tree_path
```

The node_id itself stays stable for backward compatibility. To detect
AST/schema or extraction changes, the sidecar carries versioned metadata
at top level:

| Field | Meaning |
| --- | --- |
| `ast_schema_version` | AST schema version under which the node_id was computed. A schema change produces a new association record. |
| `extractor_version` | Extraction pipeline version (e.g. `mathml-20261112`). |
| `source_occurrence_table.source_occurrence_hash` | Optional SHA-256 of the source occurrence. When present, links the whole sidecar to a specific source version. |

A sidecar built under a different AST schema or extractor version is
**not** interoperable with one built under the old versions, even if the
`node_id` strings collide. Always check `ast_schema_version` and
`extractor_version` before merging association records.

### 3.3 Canonical serialization for idempotence

Sidecar documents are serialized to JSON with stable key ordering
`sort_keys=True`, compact `separators=(",", ":")`, and no whitespace.
Repeated builds with identical inputs produce byte-equivalent canonical
JSON. This is the operational definition of sidecar idempotence:

```
s1 = sidecar_to_canonical_json(sidecar1)
s2 = sidecar_to_canonical_json(sidecar2)
s1 == s2   # True  (not merely structurally equal, byte-identical)
```

The function `sidecar_to_canonical_json` is provided in
`scripts/math_pdf_association.py` and is used by the idempotence test
(`test_contract_09`).

### 3.4 Version compatibility enforcement (production API)

The version metadata is recorded, but recording alone does not enforce
compatibility. The production module `scripts/math_pdf_association.py`
exports three functions for enforcing version checks at the boundary
where association records are loaded:

| Function | Behavior |
| --- | --- |
| `is_version_compatible(sidecar, ast_schema_version, extractor_version)` | Returns `True` iff the sidecar's `ast_schema_version`, `extractor_version`, and `schema_version` match the current contract. |
| `validate_sidecar_compatibility(sidecar, ...)` | Raises `VersionMismatchError` if the sidecar is not compatible. Call at load time in any consuming module. |
| `quarantine_incompatible_sidecar(sidecar, ...)` | Returns a fresh, quarantined copy (`quarantined: True`, association records cleared) for stale records that must be rejected or flagged. |

Calling these at the load boundary prevents stale association records
from being silently accepted. Example:

```
from math_pdf_association import validate_sidecar_compatibility

def load_association(path):
    sidecar = load_json(path)
    validate_sidecar_compatibility(sidecar)  # raises if stale
    return sidecar
```

Then, the version-compatibility enforcement test
(`test_contract_11_version_compatibility_enforcement`) verifies that a
sidecar built under `ast-v0` / `mathml-20260101` fails
`is_version_compatible` and raises `VersionMismatchError` on
`validate_sidecar_compatibility`, while a sidecar built under the
current contract (`ast-v1` / `mathml-20261112`) passes.

Stage A establishes which PDF expression region corresponds to a given
source occurrence. It must **precede** Stage B.

Stage A input:
- `SourceOccurrence` (paper_id, paper_version, source_locator,
  occurrence_index, source_hash)
- `targeted_math_detector.py` per-char observations (font, size,
  bbox_pdf_pt, page_index, block_index, line_index, span_index, char_index)

Stage A output: one `source_alignment` record per matched occurrence.

Stage A alignment evidence levels:
- `page_region_overlap` — the MathML expression's coordinate bounds
  (computed from the associated glyph observations) intersect the PDF
  expression region within a tolerance.
- `page_region_fallback` — no bounding box available; the association is
  marked `unverified_region` with evidence `page_region_overlap` set to
  `null`.

### 4.1 Ambiguity rules

If a single source occurrence maps to more than one PDF expression region,
or multiple source occurrences map to the same region, the association is
marked `ambiguous` with the competing IDs listed. No forced decision.

If a source occurrence has no geometry evidence, it is marked `unresolved`
and its `pdf_sha256`, `page_index`, and `expression_region` are
`null`. `unresolved` is a valid status — it is not an error.

---

## 5. Stage B — semantic-to-glyph association contract

Stage B associates each AST node with its glyph observations.

### 5.1 Association method

Association methods (in order of reliability):
1. `expression_region_overlap` — bounding-box intersection with tolerance
   (default 1.0 pt, configurable per call)
2. `expression_region_exact` — exact containment (no tolerance) — reserved
   for equality checks
3. `node_id_replay` — the capture layer recorded source-ordered glyph IDs
   that are replayed from the AST in document order (usage permitted only
   when coordinates are absent from the source)
4. `glyph_geometry_match` — the glyph character matches the node value
   and the bbox matches the expression region exactly
5. `expression_region_leak` — no explicit correspondence; recorded as
   `unverified_regression` with confidence 0.0 and the method listed for
   manual adjudication

`expression_region_overlap` is the preferred method; `node_id_replay` and
`expression_region_leak` are treated as fallbacks and produce weaker
associations.

### 5.2 Association statuses

- `established` — association from a high-reliability method with
  confidence >= 0.80
- `ambiguous` — method was reliable but the region is ambiguous or
  confidence < 0.80
- `unresolved` — no geometry evidence or the mapping is impossible
- `unverified_regression` — fallback method used; least reliable;
  requires manual adjudication

---

## 6. Relationship geometry contract

A relationship must retain its component geometry, not merely a merged
bounding box.

For `msup`:
```json
{
  "child_role": "base",
  "child_node_id": "...",
  "child_glyph_ids": [...],
  "child_bbox_pdf_pt": [100.0, 200.0, 110.0, 208.0]
}
```
```json
{
  "child_role": "exponent",
  "child_node_id": "...",
  "child_glyph_ids": ["..."],
  "child_bbox_pdf_pt": [102.0, 195.0, 104.0, 203.0]
}
```
The `combined_bbox_pdf_pt` is the union of the child bboxes — it is the
final output, not proof of the association by itself.

---

## 7. Acceptance criteria

Testing is split into two categories.

### 7.1 Contract tests

Manually constructed associations verify that the schema, role mapping,
bbox calculations, and provenance work correctly. These do not establish
association accuracy.

Contract test inputs must include:
- `<msup><ci>x</ci><cn>2</cn></msup>`
- `<mfrac><mi>a</mi><mi>b</mi></mfrac>`
- `<munderover><mo>∑</mo><mi>i</mi><mi>n</mi></munderover>`
- a tall delimiter (e.g. `\left\{ ... \right\}`)
- a malformed or unexpected MathML fragment

Expected contract test outputs:
- all record types present in the sidecar
- `node_id = source_expr_id + ":" + tree_path`
- `relationship_id` computed per relationship, with recursive child roles
- per-child `child_bbox_pdf_pt` preserved (not collapsed to the combined
  bbox)
- no `ExprNode` mutation in sidecar build (verify by hash comparison of
  the input `ExprNode` before and after)

### 7.2 Association tests

The bridge must independently discover the correspondence from its
permitted inputs and be evaluated against separately adjudicated gold, not
manually supplied AST-to-glyph IDs.

Metrics:
- node association precision and recall
- glyph coverage
- role assignment accuracy
- ambiguous association rate
- unmatched AST node rate
- unmatched glyph rate
- relationship bbox IoU and edge residual against gold

---

## 8. Provenance and reproducibility

- Every record carries its extraction revision (set by
  `source_occurrence_table.extraction_revision`).
- Every record carries an explicit association method and confidence.
- The sidecar is regenerated, never patched in place, when any source
  changes.
- Receipt verification is: the sidecar JSON is produced by a script, and
  the sidecar is machine-readable and directly consumable by a downstream
  consumer (no glue necessary).

No sidecar record is trusted until it passes the schema validation above
and the association status is one of `established`, `ambiguous`,
`unresolved`, or `unverified_regression`.
