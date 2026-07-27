#!/usr/bin/env python3
"""kingwen_master_unified_registry.py
Master Unification Index & Ingestion Registry for King Wen / OpenJarvis System.

Integrates & Indexes All Workspace Modules:
1. Immutable Ternary Tables (kingwen_ternary_tables_complete.py, KING_WEN_TABLES.py, emotional_engine.py)
2. Training & Quantum Superposition Data (kingwen_train_data/, kingwen_quantum_process.py, superposition_capture.py)
3. RSMV Cache & 3D Agency Kit (rsmv_live_cache_tables.json, rsmv_kit_version_manifest.json, rsmv_cache_formats.jsonl)
4. Learning & Collapse Resolution (learn/scripts/, test_collapse_full_128.py, test_collapse_full_1024.py, cognitive_synapse_pre_slider.py)
5. JKD Pedagogy & Gutenberg Ingestion (DATASETS/jkd_ingestion_binary.jsonl, jkd_ingestion_ternary.jsonl)
6. Avalokiteshvara & Schauberger Implosion Layers (scripts/schauberger_parsing_layers.py, scripts/avalokiteshvara_arms_full.json)
7. VHDL Hardware State Machine (hexagram_state_machine.vhd, decision_matrix.py)
8. TypeScript Node Substrate (src/core/OracleEngine.ts, src/types/IntentVector.ts, src/types/kingwen_shotgun_types.ts)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Subsystem Catalog Mapping
SUBSYSTEM_CATALOG = {
    "core_tables": [
        "kingwen_ternary_tables_complete.py",
        "KING_WEN_TABLES.py",
        "emotional_engine.py",
        "hexagram_personality.py",
        "temporal_emotional_engine.py",
        "journey_weave.py",
        "decision_matrix.py"
    ],
    "hardware_vhdl": [
        "hexagram_state_machine.vhd"
    ],
    "training_and_quantum": [
        "kingwen_train_data/kingwen_quantum_process.py",
        "kingwen_train_data/superposition_capture.py",
        "kingwen_train_data/kingwen_expansion_wrapper.py",
        "kingwen_train_data/kingwen_pretrain.jsonl",
        "kingwen_train_data/megatron_multi_domain.jsonl",
        "kingwen_train_data_demo2/learned_sequential_64.json",
        "kingwen_train_data_demo2/megatron_weights.csv"
    ],
    "rsmv_cache_3d": [
        "kingwen_train_data/rsmv_live_cache_tables.json",
        "kingwen_train_data/rsmv_kit_version_manifest.json",
        "kingwen_train_data/rsmv_cache_formats.jsonl"
    ],
    "learn_harnesses": [
        "learn/scripts/test_collapse_full_128.py",
        "learn/scripts/test_collapse_full_1024.py",
        "learn/scripts/cognitive_synapse_pre_slider.py",
        "learn/scripts/binary_injection_harness.py",
        "learn/scripts/hexagram_oracle_consult.py",
        "learn/scripts/export_megatron_weights.py",
        "learn/scripts/kanban_loop.py",
        "learn/scripts/kanban_timer.py",
        "learn/exports/domain_registry.json"
    ],
    "jkd_pedagogy": [
        "DATASETS/jkd-pedagogy-engine-SKILL.md",
        "DATASETS/jkd_full_text.txt",
        "DATASETS/jkd_ingestion_binary.jsonl",
        "DATASETS/jkd_ingestion_ternary.jsonl"
    ],
    "avalokiteshvara_and_schauberger": [
        "scripts/schauberger_parsing_layers.py",
        "scripts/avalokiteshvara_arms_full.json",
        "scripts/build_avalokiteshvara_registry.py",
        "docs/avalokiteshvara-kingwen-arms.json"
    ],
    "viewfinder_and_widgets": [
        "scripts/build_512_widget.py",
        "DATASETS/kingwen_512_oracle_widget.html"
    ],
    "typescript_substrate": [
        "src/core/OracleEngine.ts",
        "src/core/HexagramRuntimeBridge.ts",
        "src/core/pog3_hexagram_runtime_substrate.py",
        "src/parser/EmotionalParser.ts",
        "src/parser/NarrativeEngine.ts",
        "src/types/IntentVector.ts",
        "src/types/StateCapture.ts",
        "src/types/kingwen_shotgun_types.ts"
    ]
}

def audit_file_inclusions() -> Dict[str, Any]:
    """Audits which files exist in the repository and checks their inclusion status."""
    audit_results = {}
    total_found = 0
    total_missing = 0

    for subsystem, file_list in SUBSYSTEM_CATALOG.items():
        subsystem_status = []
        for rel_path in file_list:
            full_path = _REPO_ROOT / rel_path
            exists = full_path.exists()
            if exists:
                total_found += 1
                size_bytes = full_path.stat().st_size
            else:
                total_missing += 1
                size_bytes = 0
            
            subsystem_status.append({
                "path": rel_path,
                "exists": exists,
                "size_bytes": size_bytes
            })
        
        audit_results[subsystem] = {
            "total_files": len(file_list),
            "files": subsystem_status
        }

    return {
        "repo_root": str(_REPO_ROOT),
        "total_subsystems": len(SUBSYSTEM_CATALOG),
        "total_files_audited": total_found + total_missing,
        "files_found": total_found,
        "files_missing": total_missing,
        "subsystem_details": audit_results
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    summary = audit_file_inclusions()
    print(json.dumps(summary, indent=2))
