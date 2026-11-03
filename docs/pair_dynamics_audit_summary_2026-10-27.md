# Pair-Dynamics Audit — Verification Script Passed

**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES  
**Verification basis:** Canonical binary encodings from `king_wen_64_verified.json` (64 hexagrams)  
**Verification script:** `scripts/pair_verification.py` (executable, regression-tested)  
**Audit date:** October 27, 2026

---

## 1. VERIFIED RESULTS (EXECUTABLE CHECKS PASSED)

| Metric                                | Verified result |
| ------------------------------------- | --------------- |
| Binary reversal pairs                 | 28              |
| Hexagrams participating in reversal   | 56              |
| Bitwise complement pairs              | 32              |
| Hexagrams participating in complement | 64              |
| Same-partner dual pairs               | 4               |
| Hexagrams without reversal partners   | 8 (1, 2, 27, 28, 29, 30, 61, 62) |
| Hexagrams without complement partners | 0               |

**Verification status:** ✓ PASS — executable script `scripts/pair_verification.py` generates pairs from canonical encodings and compares against `docs/pair_dynamics_verification.json`. Failures would be reported as assertion errors.

---

## 2. CORRECTIONS APPLIED

### Data-Coverage Defect Resolved

The earlier complement count (30) was based on an **incomplete CSV** (`kingwen_hexagram_pairs.csv`). The CSV omitted two valid complement pairs. Recomputing from the canonical binary encodings:

- **53 ↔ 54** (binary 001100 → 110011) — complement pair
- **63 ↔ 64** (binary 101010 → 010101) — complement pair

These two pairs bring the canonical complement count from 30 → 32.

### Same-Partner Dual Pairs (4)

| Pair | Nature |
|------|--------|
| (11, 12) | Reversal + complement, same partner |
| (17, 18) | Reversal + complement, same partner |
| (53, 54) | Reversal + complement, same partner (was missing from CSV) |
| (63, 64) | Reversal + complement, same partner (was missing from CSV) |

---

## 3. BIT ORDER CONVENTION

The canonical six-bit encoding is read **bottom-to-top** (`binary` field in `king_wen_64_verified.json`):

- Line 0 = bottom (young yin)
- Line 5 = top (old yang)

### Transformations (from canonical encodings)

- **Inversion (reversal):** reverse the six bits — line_0↔line_5, line_1↔line_4, line_2↔line_3
- **Complement (bit-flip):** flip every bit — 0→1, 1→0 at each position

Example: Hex 1 (111111) complements to Hex 2 (000000). Hex 3 (010001) reverses to Hex 4 (100010).

---

## 4. AUDIT VERDICT

**Pair-dynamics audit conclusion:** The pair relationship structure is source-derived from canonical binary encodings. All 64 hexagrams are accounted for. The corrected counts (28 inversion pairs, 32 complement pairs, 0 without complement) are internally consistent and reproducible from the source data via the executable verification script.

**Status:** ✓ Verification-script passed. Artifacts verified. Layer 0 provisionally complete.

---

## 5. B4 GATE 2 — REMAINING

The pair audit establishes binary structural relationships but does **not** determine the approved quantum parameter mapping. The six unresolved B4 specification questions remain open:

1. **Authoritative input mapping:** canonical identity and line order → upper/lower trigram IDs
2. **Closed-form compliance:** whether SHA-256 is permitted per contract
3. **Prime multipliers:** role, modulus, and mathematical effect
4. **Coherence:** how it changes generated angles and missing-value handling
5. **Sensitivity and identity preservation:** traceable identity vs. unique numerical outputs
6. **Downstream behavior:** which circuit and Hamiltonian properties must remain invariant

---

## 6. ARTIFACTS

- **Verification script:** `scripts/pair_verification.py` — executable, regenerates pairs from canonical binary encodings, compares against JSON, fails on mismatch
- **Artifact:** `docs/pair_dynamics_verification.json` — verified counts, bit order metadata, pair tables
- **Report:** `docs/pair_dynamics_audit_corrected.md` — corrected counts and CSV incompleteness note
- **B4 spec:** `docs/B4-PARAM-SPEC-KW-B4-PARAM-001.md` — draft (unapproved)

---

**Audit date:** October 27, 2026  
**Analyst:** Kbro1989 / Kristain33rs  
**Verification method:** Executable comparison of generated pairs against canonical binary encodings and stored JSON artifact  
**Status:** ✓ Verification-script passed. Layer 0 provisionally complete. B4 Gate 2 pending.
