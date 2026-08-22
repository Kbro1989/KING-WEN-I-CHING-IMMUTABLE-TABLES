# Audit Checklist — Pipeline Variable / External-Program Alignment

**Generated:** 2026-08-22 | **Author:** Hermes (Kirby)
**Scope:** King Wen → Shap-E → rsmv worldgen pipeline + new Moparscape integration surface
**Method:** every claim below is backed by an exact file:line or tool output captured this session. No asserted values without a source.

---

## PIPELINE CHAIN (intent → math → layers → outcome)

| # | Layer | Component | Path (verified) | Role |
|---|-------|-----------|-----------------|------|
| 1 | Intent | King Wen hexagram state machine | `KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/kingwen_quantum_process.py` (B1-patched) | Source of truth for 64-hex state |
| 2 | State packet | `kit_{1..64}.json` | `DATASETS/kingwen_model_sets/kit_1.json` (65 files total) | Canonical per-hex avatar packet: `grounded_npc.hexagram_id`, `coder_specialty`, `schauberger.motion_type`, Riemann `modelTranslate_0..2`, `rotation_0/1`, `big_value`, `positions[6]`, `extra[14]` |
| 3 | Generator | `shap_e_kingwen_3d_generator.py` | `scripts/shap_e_kingwen_3d_generator.py:19,50-56` | Reads `kit_{h}.json` → `grounded_npc.hexagram_id` → builds Shap-E prompt → emits 729-vert PLY |
| 4 | Geometry | Shap-E (EXTERNAL) | `C:\Users\krist\Desktop\shap-e` (repo present) | Generates point-cloud PLY. 585 PLYs on disk (`DATASETS/kingwen_3d_meshes/shap_e_hex_*.ply`) |
| 5 | Compliance | `transform_object_rsmv.py` | `scripts/transform_object_rsmv.py:122-155` | Repacks PLY float→rsmv `models` struct (Int16 pos, RGB555 col, faceCount=0) |
| 6 | Target | rsmv wire format (EXTERNAL) | `rsmv/generated/models.d.ts` | `hex_{01..64}_models.json` loaded as `meshes[].vertexCount/positionBuffer/colourBuffer` |
| 7 | Orchestrator | `run_all_unified_pipeline.py` | `scripts/run_all_unified_pipeline.py:22-33,44-61` | 11 sequential subprocess stages; reports "100% parity" if all exit 0 |

---

## EXTERNAL PROGRAMS SHAPING OUTPUT (and their influence)

| Program | Path | Influence on pipeline | Verified |
|---------|------|----------------------|----------|
| **King Wen immutable tables** | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES` | Source-of-truth state packets (kit_*.json). All downstream geometry derives from `hexagram_id`. | ✅ kit_1.json present, 65 files |
| **Shap-E** | `C:\Users\krist\Desktop\shap-e` | PLY mesh generation. Determines vertex count (729), color, shape. | ✅ repo present, 585 PLYs on disk |
| **rsmv** | `C:\Users\krist\Desktop\rsmv` | Target wire format (Int16 pos / RGB555 col / Uint16 index). Defines struct contract. | ✅ `models.d.ts` read; hex_01 loads clean |
| **Moparscape (NEW)** | `C:\Users\krist\Desktop\moparscape` | Cache/NPc data source candidate. **Format-incompatible** with rsmv (see GAP-1). | ✅ trees on disk, JDK21 compiles |
| **JDK 21 (Temurin)** | `C:\Program Files\Eclipse Adoptium\jdk-21.0.10.7-hotspot` | Compiles Moparscape (`javac *.java` → exit 0, 163 classes). | ✅ verified this session |
| **POG2 scratch** | `C:\Users\krist\.gemini\antigravity\scratch\POG2\scratch` | Source of 16 opcode extractors copied to `rsmv/scripts/pog2_scratch/` (Tier A import-remapped, Tier C quarantined). | ✅ 16 scripts copied, Tier A resolves to `../../src/*` |

---

## OUTCOME VERIFICATION (real artifact, not description)

`hex_01_models.json` loaded and asserted (native Python, this session):
```
format=1  vertexCount=729  faceCount=0
pos len=2187 (729×3)  col len=729
pos min/max = -30000 .. 30000   (Int16 range ✓)
col sample=[49120,50144,50144]  highbit(0x8000) set ✓  (RGB555 packed ✓)
indexBuffers=[[]]  (structurally valid point cloud ✓)
```
→ **Output matches rsmv `models.d.ts` contract.** Compliance layer is real, not fabricated.

---

## DISCREPANCIES / GAPS (open items from this audit)

### GAP-1 — Moparscape cache ≠ rsmv reader (format mismatch)
- Moparscape cache: `main_file_cache.dat` + `idx0..4` (RS2 520-sector format, `Class14.java` in Mopar1/Mopar).
- rsmv reader: classic RSC `.jag` archive parser (`rsmv/src/cache/legacycache.ts`, `compression.ts` bz2/xtea). **No 520-sector/idx-dat reader exists in rsmv.**
- Finding from delegation task-1: "rsmv has **no low-level `main_file_cache`/520-sector reader**".
- **Implication:** Moparscape cache cannot be read by rsmv directly. Integration requires either (a) a 520-sector adapter in rsmv, or (b) feeding Moparscape *NPC definitions* (text, `npc.cfg`) not the binary cache.
- **Status:** OPEN — needs decision (adapter vs text-only feed).

### GAP-2 — B6 still OPEN: kit_1.json `extra[]` pollution
- `kit_1.json` `extra[]` = **205 entries** (verified this session).
- Sample entries are NOT King Wen-aligned:
  `{'type':0,'key':'name','intvalue':0,'stringvalue':'The Creative'}` — raw RSMV cache field tuples, not the intended 14 compositional overlay slots.
- The canonical `kit` schema expects `extra[14]` (Riemann overlay composable like headwear-on-headmodel). 205 polluted entries = prior integration scripts overwrote the slot.
- **Status:** OPEN — needs `extra[]` reset to 14 King-Wen-aligned slots.

### GAP-3 — `search_files` path bug on this host
- Every delegation child hit `rg: ... IO error (os error 3)` for `/c/Users/krist/...` MSYS paths.
- Workaround used: `terminal find/grep` with native Windows paths.
- **Status:** ENVIRONMENT — affects tool reliability, not pipeline correctness. Document for future sessions.

### GAP-4 — Orchestrator "100% parity" claim is stage-exit-based only
- `run_all_unified_pipeline.py:55` increments `stage_passed` on `res.returncode == 0` only.
- It does NOT validate output struct correctness (that was done manually this session via the hex_01 load test).
- **Risk:** a stage can exit 0 while emitting malformed data; pipeline reports "100% parity" falsely.
- **Status:** DESIGN NOTE — recommend post-stage struct assertion in the orchestrator.

---

## INTENT → OUTCOME ALIGNMENT SUMMARY

| Intent | Achieved? | Evidence |
|--------|-----------|----------|
| King Wen drives avatar geometry | ✅ | kit_*.json hexagram_id → shap-E prompt → 729-vert PLY |
| Output is rsmv-loadable | ✅ | hex_01_models.json asserts clean against models.d.ts |
| No fabrication in compliance layer | ✅ | transform_object_rsmv.py:24 "No RNG. No placeholder verts." — PLY verts are real |
| Moparscape feeds worldgen | ⚠️ PARTIAL | Text (npc.cfg) usable; binary cache format-incompatible (GAP-1) |
| kit packets clean | ❌ | B6: 205 polluted extra[] (GAP-2) |

---

## TODO (carried from prior session, still open)
- B2, B3, B4, B7, B9, B10, B11 — prior audit gates (§2 of AUDIT_QUANTUM_3D_SHAPE_E) not yet closed.
- GAP-1, GAP-2 above are new blockers for the Moparscape/worldgen integration.

## Verification commands used (reproducible)
```bat
:: compile Moparscape
cd C:\Users\krist\Desktop\moparscape\Mopar1\Mopar
"%JAVA_HOME%\bin\javac" *.java

:: verify rsmv output struct
python3 -c "import json;d=json.load(open(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\kingwen_rsmv_models\hex_01_models.json'));print(d['meshes'][0]['vertexCount'])"

:: count kit pollution
python3 -c "import json;print(len(json.load(open(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\kingwen_model_sets\kit_1.json'))['extra']))"
```
