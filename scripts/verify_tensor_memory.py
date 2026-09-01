"""
Verify King Wen Tensor Memory implementation.
Run: python scripts/verify_tensor_memory.py from repo root.
"""
from __future__ import annotations

import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from core.tensor_memory import (
    KingWenTensorMemory,
    hex_phase_to_coordinate,
    coordinate_to_slot,
    inversion_mirror,
    gaussian_write,
    conv_lstm_update,
    trilinear_read,
    D, H, W, C,
)

def main():
    mem = KingWenTensorMemory()
    content = np.zeros(C, dtype=np.float32)
    content[0] = 0.7
    content[1] = 0.5
    content[2] = 0.3
    content[3] = 0.9
    content[4] = 0.6
    content[16] = 1.0
    content[18] = 0.5

    for hid in range(1, 65):
        for pid in range(8):
            mem.write_hex_phase(hid, pid, 0.5, content)

    occ = mem.occupancy()
    assert len(occ) == 512, f"Expected 512 occupied slots, got {len(occ)}"
    print(f"OK: occupancy={len(occ)}")

    for hid in range(1, 11):
        for pid in range(8):
            vec = mem.read_hex_phase(hid, pid, 0.5)
            assert vec.shape == (C,), f"Wrong read shape: {vec.shape}"
    print("OK: read_hex_phase shape")

    mem2 = KingWenTensorMemory()
    for hid in range(1, 65):
        for pid in range(8):
            mem2.write_hex_phase(hid, pid, 0.5, content)
    h1 = mem.state_hash()
    h2 = mem2.state_hash()
    assert h1 == h2, f"Determinism failed: {h1} != {h2}"
    print(f"OK: deterministic_replay hash={h1}")

    # Inversion pair mirror: preserves bounds, differs from original
    mu_a = hex_phase_to_coordinate(1, 0, 0.5)
    mu_a_mirror = inversion_mirror(mu_a)
    for i in range(3):
        assert -1.0 - 1e-6 <= mu_a_mirror[i] <= 1.0 + 1e-6, f"Mirror out of bounds axis {i}: {mu_a_mirror[i]}"
        assert abs(mu_a_mirror[i] - mu_a[i]) > 1e-6, f"Mirror identical on axis {i}"
    slot_orig = coordinate_to_slot(mu_a)
    slot_mirror = coordinate_to_slot(mu_a_mirror)
    assert 0 <= slot_mirror <= 511, f"Mirror slot out of range: {slot_mirror}"
    print(f"OK: inversion_mirror mu_a={mu_a} mirror={mu_a_mirror} slot={slot_orig} mirror_slot={slot_mirror}")

    vec_direct = mem.read_hex_phase(1, 0, 0.5, use_inversion=False)
    vec_mirror = mem.read_hex_phase(1, 0, 0.5, use_inversion=True)
    assert not np.allclose(vec_direct, vec_mirror), "Mirror read should differ from direct"
    print("OK: inversion_mirror read differs from direct")

    mem3 = KingWenTensorMemory()
    assert mem3.gamma == -2.0
    gate_val = 1.0 / (1.0 + math.exp(-mem3.gamma))
    assert gate_val < 0.2, f"Gamma gate should suppress memory, got {gate_val}"
    print(f"OK: no-harm gate sigmoid(-2.0)={gate_val:.4f}")

    mem4 = KingWenTensorMemory()
    h_before = mem4.state_hash()
    mem4.write_hex_phase(1, 0, 0.5, content)
    h_after = mem4.state_hash()
    assert h_before != h_after, "State hash should change after write"
    print(f"OK: state_hash_changes {h_before} -> {h_after}")

    mem5 = KingWenTensorMemory()
    mem5.write_hex_phase(1, 0, 0.5, content)
    mem5.write_hex_phase(2, 1, 0.7, content)
    out_path = os.path.join(os.getcwd(), "DATASETS", "tensor_memory_test.json")
    mem5.save(out_path)
    mem6 = KingWenTensorMemory.load(out_path)
    assert mem5.state_hash() == mem6.state_hash(), "Save/load hash mismatch"
    print(f"OK: save_load_roundtrip hash={mem5.state_hash()}")

    print("\nALL TENSOR MEMORY VERIFICATIONS PASSED")

if __name__ == "__main__":
    main()
