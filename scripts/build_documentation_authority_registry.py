#!/usr/bin/env python3
"""
KING-WEN DOCUMENTATION AUTHORITY REGISTRY (V1.0)

Cross-document authority map for the KING-WEN-I-CHING-IMMUTABLE-TABLES repository.

Generated: 2026-11-11
Source: Verified on-disk via find + sha256 hash computation

Registry fields:
  document_id     — stable unique identifier (relative path, sanitized)
  document_type   — md|json|py|jsonl
  status          — FROZEN / CONFIRMED / IN_PROGRESS / PROPOSED / PENDING_REVIEW
  authority_tier  — Architecture | Implementation | Frozen evaluation | Frozen baseline | Exploratory
  path_status     — PATH_CONFIRMED | PATH_UNVERIFIED | PATH_MISSING
  sha256          — SHA-256 of current on-disk content (computed by this script)
  size_bytes      — current file size on disk
  path            — relative path from repository root
  status          — status of the document

DISCREPANCY NOTE (8 vs 9 golden-standard artifacts):
  The cross-document authority map table in the handoff text lists EIGHT golden-standard
  artifacts, but the textual description mentions "three frozen-regression documents, one frozen
  baseline, two Phase-2 documents, and two evaluation-authority documents" = 8 total.
  If a ninth artifact exists, its path is not in the supplied inventory. This registry
  freezes the 8-artifact count. The ninth item, if it exists, is UNKNOWN and must be
  explicitly identified before any expansion of the frozen set.
"""

import hashlib, json
from pathlib import Path

BASE = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")

# Frozen standard artifact 8-list (verified on disk)
FROZEN_STANDARD_8 = [
    ("docs/adjudication-layer-contract.md", "md", "FROZEN", "Frozen evaluation authority"),
    ("docs/CROSS_PAPER_V2_EVALUATION_PROTOCOL.md", "md", "FROZEN", "Frozen evaluation authority"),
    ("docs/golden-standard-audit-matrix.md", "md", "FROZEN", "Frozen evaluation authority"),
    ("docs/frozen-regression-evaluation-mapping-2026-11-03.md", "md", "FROZEN", "Frozen evaluation authority"),
    ("docs/frozen-regression-execution-results-2026-11-03.md", "md", "FROZEN", "Frozen evaluation evidence"),
    ("DATASETS/vision_comparison/baseline_frozen_padding15.jsonl", "jsonl", "FROZEN", "Frozen baseline"),
    ("docs/phase2b_final_report.md", "md", "FROZEN", "Frozen milestone evidence"),
    ("docs/phase2c_gate5_calibration.md", "md", "FROZEN", "Frozen calibration authority"),
]

# Architecture / implementation
ARCH_IMPL = [
    ("docs/mechanical-swan-architecture.md", "md", "CONFIRMED", "Architecture authority"),
    ("docs/mechanical-swan-component-registry.json", "json", "CONFIRMED", "Architecture supporting artifact"),
    ("lua-math-tool.md", "md", "CONFIRMED", "Implementation"),
    ("scripts/math_recovery/recovery_registry.py", "py", "CONFIRMED", "Implementation / supporting evidence"),
]

# QSMC-1 (exploratory research — 9 documents)
QSMC1 = [
    ("docs/qsmc1-m1-gaussian-kernel-correspondence.md", "md", "PROPOSED", "Exploratory research"),
    ("docs/qsmc1-m2-expectation-consensus-correspondence.md", "md", "PROPOSED", "Exploratory research"),
    ("docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md", "md", "IN_PROGRESS", "Exploratory research"),
    ("docs/qsmc1-m3-dimensional-consistency-analysis.md", "md", "IN_PROGRESS", "Exploratory research"),
    ("docs/qsmc1-m4-phase-representations-correspondence.md", "md", "PROPOSED", "Exploratory research"),
    ("docs/qsmc1-m5-angular-momentum-vortex-correspondence.md", "md", "PROPOSED", "Exploratory research"),
    ("docs/qsmc1-m6-interference-coherence-correspondence.md", "md", "PROPOSED", "Exploratory research"),
    ("docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md", "md", "IN_PROGRESS", "Exploratory research"),
    ("docs/qsmc1-quantum-sim-mathematical-correspondence-audit.md", "md", "PROPOSED", "Exploratory research"),
]

def sha256(file_path):
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

def build_registry(entries):
    """Build registry entries with verified hashes."""
    registry = []
    for rel_path, doc_type, status, tier in entries:
        p = BASE / rel_path
        if p.exists():
            raw = p.read_bytes()
            entry = {
                "document_id": rel_path.replace("/", "_").replace("\\", "_"),
                "document_type": doc_type,
                "status": status,
                "authority_tier": tier,
                "path_status": "PATH_CONFIRMED",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
                "path": str(p.relative_to(BASE)),
                "exists": True,
            }
        else:
            entry = {
                "document_id": rel_path.replace("/", "_").replace("\\", "_"),
                "document_type": doc_type,
                "status": status,
                "authority_tier": tier,
                "path_status": "PATH_MISSING",
                "sha256": None,
                "size_bytes": 0,
                "path": str(p.relative_to(BASE)),
                "exists": False,
            }
        registry.append(entry)
    return registry

def main():
    registry = build_registry(FROZEN_STANDARD_8)
    registry += build_registry(ARCH_IMPL)
    registry += build_registry(QSMC1)

    # Write JSON
    out = BASE / "docs" / "documentation_authority_registry.json"
    out.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(registry)} entries)")

    # Verify CSV count for FROZEN_STANDARD_8
    print(f"\nGolden-standard frozen 8-list: {len(FROZEN_STANDARD_8)} artifacts")
    print(f"Architecture/implementation: {len(ARCH_IMPL)} artifacts")
    print(f"QSMC-1 research: {len(QSMC1)} artifacts")
    print(f"Grand total: {len(registry)}")

    # Discrepancy notes
    print(f"""
DISCREPANCY RECORD (frozen):
  Golden-standard artifact count: 8 (not 9).
  Textual description mentions "three frozen-regression, one frozen baseline,
  two Phase-2, two evaluation-authority" = 8. The ninth artifact is NOT in
  the supplied inventory. Current disposition: unknown, no path assigned.

QSMC-1:
  9 documents classified as exploratory research. Must NOT alter frozen
  regression baselines or evaluation protocols.

Registry file written to:
  docs/documentation_authority_registry.json
""")

if __name__ == "__main__":
    main()
