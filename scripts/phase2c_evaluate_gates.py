#!/usr/bin/env python3
"""
Phase 2C — Evaluation Script using Gate Library

This is the Phase 2C version of the evaluator, using the shared
phase2c_gate_library.py for gate implementations.
Phase 2B's scripts/phase2b_evaluate_gates.py remains FROZEN.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from phase2c_gate_library import (
    evaluate_batch,
    GATE_NAMES,
)

def main():
    if len(sys.argv) < 3:
        print("Usage: python phase2c_evaluate_gates.py <pilot_selection.json> <recognized_outputs.json> [output.json]")
        sys.exit(1)

    pilot_path = Path(sys.argv[1])
    recognized_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("DATASETS/phase2c_disposition_matrix.jsonl")

    pilot = json.loads(pilot_path.read_text(encoding='utf-8'))
    recognized = json.loads(recognized_path.read_text(encoding='utf-8'))

    results = evaluate_batch(pilot['candidates'], recognized)

    with output_path.open('w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f"Evaluated {len(results)} candidates -> {output_path}")

    from collections import Counter
    for gate in GATE_NAMES:
        cnt = Counter(r[gate] for r in results)
        print(f"  {gate}: {dict(cnt)}")
    disp = Counter(r['final_disposition'] for r in results)
    print(f"  Disposition: {dict(disp)}")

if __name__ == '__main__':
    main()