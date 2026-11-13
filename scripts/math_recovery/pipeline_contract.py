#!/usr/bin/env python3
"""Math Recovery Puzzle Box — Pipeline Contract (V2.1.1-A)

Four independent status dimensions. Each must be tracked separately;
never conflate parse success with mathematical correctness.

    ParseStatus   — can the text be tokenized into a tree at all?
    StructuralStatus — does the tree preserve delimiter identity,
                       nesting, and bounding structure?
    BackendStatus  — can SymPy/Wolfram/Lean/PARI/Sage consume the IR?
    SolutionStatus — did the solver accept and return a coherent result?

Usage:
    from math_recovery.pipeline_contract import (
        detect_status, classify_recovery, verify_occurrence_conservation
    )

    record = {"paper_id": "1212.0957", "page": 8, "parser": "tree_path",
              "parse": 28, "structural": 28, "backend": 12, "solve": 9}
    classify_recovery(record)

"""
