# King Wen + Supportive Research: Execution Checklist
**Version:** 2026-08-02  
**Status:** Live execution tracker — mark items complete with proof  
**Companion:** `KING-WEN-RESEARCH-GUIDE.md`

**How to use:**
- Each checkbox maps to a guide section (e.g., `[A1]` = Section 2.1, item 1)
- Mark `[x]` only after verification command passes or artifact is written
- "Proof" column must contain exact command output or file path
- Do not mark complete without proof — no fabrications

---

## Section 2.1: State Expansion Engine

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| A1 | `collapse_full_128(50)` returns 64 expanded, 512 resolved | `py_compile emotional_engine.py && python -c "from emotional_engine import collapse_full_128; r=collapse_full_128(50); print('expanded',len(r['expanded']),'resolved',len(r['resolved']))"` | expanded 64 resolved 512 — 2026-08-20 | [x] |
| A2 | Phase_bits 0..7 evenly distributed (64 each) | `python -c "from emotional_engine import collapse_full_128; r=collapse_full_128(50); from collections import Counter; print(Counter(x['phase_bits'] for x in r['resolved']))"` | {0:64, 1:64, 2:64, 3:64, 4:64, 5:64, 6:64, 7:64} — 2026-08-20 | [x] |
| A3 | Porosity normalization: integer 0-4 → 0.0-1.0 | `python -c "from kingwen import normalizePorosity; print(normalizePorosity(0), normalizePorosity(4))"` | | [ ] |
| A4 | `hexagram_full_expansion.json` inject_site fields present | `python -c "import json; d=json.load(open('hexagram_full_expansion.json')); print(all('yao_vocabulary' in x.get('inject_site',{}) for x in d['expanded']))"` | | [ ] |
| A5 | Fallback order works when inject_site empty | `python -c "from kingwen_completion_injection import _build_batch; b=_build_batch(); print('fallback_invoked', any(x.get('inject_site',{}).get('source')=='registry' for x in b))"` | | [ ] |
| A6 | VOICEBOX_VOICE_POOL not trimmed (66 canonical) | `python -c "import json; print(len(json.load(open('src/data/voicebox_profile_payload.json'))['vector_rows']))"` | | [ ] |
| A7 | `_build_batch()` has no winner/dominant collapse | `grep -n "winner\|dominant" kingwen_completion_injection.py` | Should return no matches | [ ] |
| A8 | All 64 hexagram slots in order 1-64, no removal | `python -c "from kingwen_completion_injection import _build_batch; b=_build_batch(); ids=[x['hexagram_id'] for x in b]; print(ids==list(range(1,65)), len(b))"` | | [ ] |

---

## Section 2.2: Worker Consult Rewrite

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| B1 | No `stableHash` 1-hex collapse in `src/index.ts` | `grep -n "stableHash" src/index.ts` | Should return no matches | [ ] |
| B2 | `normalizePorosity()` handles 0-4 integer scale | `grep -n "normalizePorosity" src/index.ts` | Function present, tested | [ ] |
| B3 | Consult returns `all_hexagrams[]` with 64 entries | `curl -s https://kingwen-oracle.kristain33rs.workers.dev/consult -X POST -H "Content-Type: application/json" -d '{"text":"test","emotional_input":50}' \| jq '.all_hexagrams \| length'` | Should return 64 | [ ] |
| B4 | Each resolved entry has `query_tokens`, `phase_temporal`, `resolved_vector` | `python -c "from emotional_engine import collapse_full_128; r=collapse_full_128(50,'test query'); rr=r['resolved']; print(all('query_tokens' in x.get('intent',{}) for x in rr), all('phase_temporal' in x for x in rr), all(x.get('resolved_vector') for x in rr))"` | True True True — all 512 entries pass — 2026-08-20 | [x] |
| B5 | Top result has reasoned output fields | `curl -s ... \| jq '.unified_weave, .sovereign_assertion, .boundary_condition, .dissipator_warning'` | Non-null values | [ ] |
| B6 | `query_tokens`, `resolved_count`, `expanded_count` in payload | `python -c "from emotional_engine import collapse_full_128; r=collapse_full_128(50,'test'); print(r.get('total_resolved'), r.get('total_expanded'))"` | total_resolved=512 total_expanded=64 — 2026-08-20 | [x] |
| B7 | `matchesFilter` reads `hexagram_symbols.category/action` | `grep -n "hexagram_symbols" src/index.ts` | Fallback present | [ ] |
| B8 | `if_is`/`if_is_not` operates on full 64 before filtering | `grep -n "if_is" src/index.ts` | Logic verified in tests | [ ] |
| B9 | `npm run test` passes 4/4 | `cd kingwen-oracle && npm run test` | 4/4 passing | [ ] |
| B10 | Live deploy verified with reasoned output | `curl -s https://kingwen-oracle.kristain33rs.workers.dev/consult -X POST ...` | Returns full 512 states + reasoned output | [ ] | [ ] |

---

## Section 2.3: Reasoning Layer

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| C1 | Signed preference deltas computed: `resolved_vector - expanded_vector` | `grep -n "resolved_vector.*expanded_vector\|delta" src/index.ts` | Delta math present | [ ] |
| C2 | Non-negative effective margin enforced | `grep -n "max(0\|Math.max(0" src/index.ts` | Margin enforcement present | [ ] |
| C3 | `unified_weave` seeded from `trainingNotes` + `inject_site.reason` | Read `buildReasonedOutput()` in `src/index.ts` | Generative prompt pattern, not template concat | [ ] |
| C4 | Context distillation split: `raw_state` + `distilled_answer` | `grep -n "raw_state\|distilled_answer" src/index.ts` | Fields present in payload | [ ] |
| C5 | Phase-aware delta scoring per axis | `grep -n "phase.*delta\|delta.*phase" src/index.ts` | Per-axis delta present | [ ] |
| C6 | Checklist/phase_description keyword overlap for tiebreak | `grep -n "checklist\|phase_description" src/index.ts` | Keyword overlap in ranking | [ ] |
| C7 | Line states diversity tiebreak | `grep -n "line_states.*diversity\|diversity.*line_states" src/index.ts` | Diversity tiebreak present | [ ] |
| C8 | Ranked output changes between different questions | `curl -s ... -d '{"text":"debug inference","emotional_input":50}' \| jq '.all_hexagrams[0].hexagram_id'` vs `curl -s ... -d '{"text":"write essay","emotional_input":50}' \| jq '.all_hexagrams[0].hexagram_id'` | Different top results | [ ] |
| C9 | No template-only patterns in `buildReasonedOutput` | `grep -n "unified_weave.*+\|unified_weave.*concat" src/index.ts` | No string concat of static templates | [ ] |

---

## Section 2.4: Voice / Porosity Mapping

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| D1 | Real voicebox weights loaded from exports | `ls src/data/voicebox_*.json` | Files present | [ ] |
| D2 | Category→voice domain mapping: sovereign→mars, boundary→juno, dissipator→saturn, transformer→jupiter | `grep -n "mars\|juno\|saturn\|jupiter" src/index.ts` | Mapping present | [ ] |
| D3 | Action→speaker hint mapping present | `grep -n "atlas\|viga\|echo\|luna" src/index.ts` | Mapping present | [ ] |
| D4 | `tts_speaker_hint` in consult payload per hexagram | `curl -s ... | jq '.all_hexagrams[0].tts_speaker_hint'` | Non-null | [ ] |
| D5 | `porosity` in every voice artifact | `curl -s ... | jq '.all_hexagrams[0].porosity'` | Float 0.0-1.0 | [ ] |
| D6 | `/tts` routes to Voicebox/Cartesia for weight-driven expression | `grep -n "cartesia\|voicebox" src/index.ts` | Route present | [ ] |
| D7 | Voice adapter zero POG2 dependency | `grep -r "pog2\|POG2" src/openjarvis/speech/` | Zero matches | [ ] |
| D8 | Voice sidecar subscribes `KINGWEN_VOICE_COMPLETE` | `grep -n "KINGWEN_VOICE_COMPLETE" src/openjarvis/cli/_oracle_speak.py` | Present | [ ] |

---

## Section 2.5: Expand Server & Capture Pipeline

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| E1 | `/expand` POST returns 64/512 with `expanded[]`, `resolved[]`, `top_10`, `selected` | `curl -s -X POST http://127.0.0.1:8765/expand -H "Content-Type: application/json" -d '{}' | jq '.expanded_count, .resolved_count, (.top_10 \| length)'` | 64, 512, 10 | [ ] |
| E2 | Bleed formula correct: `porosity_lo + (porosity_hi - porosity_lo) * clamp(emotional_input/100)` | `python -c "from emotional_engine import _clamp; emotional_input=50; bleed=0.144+(0.176-0.144)*_clamp(50/100); print(bleed)"` | 0.160 | [ ] |
| E3 | `/capture` POST appends to JSONL non-blocking | `curl -s -X POST http://127.0.0.1:8765/capture -H "Content-Type: application/json" -d '{"event":"test","session_id":"verify"}' && tail -1 DATASETS/shotgun_captures.jsonl` | JSON line appended | [ ] |
| E4 | Widget fires `captureEvent` on tab switch | Open widget browser console, switch tabs | `captureEvent` logged | [ ] |
| E5 | Baked `hexagrams[]` preserved, live `resolved[]` merged | `grep -n "hexagrams\|resolved" kingwen_512_oracle_widget.html` | Both arrays present | [ ] |
| E6 | expand_server.py process running | `tasklist \| findstr python` or `netstat -ano \| findstr 8765` | LISTENING on 8765 | [ ] |

---

## Section 2.6: Save-String & Batch Protocol

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| F1 | Format: `hex_id:phase:vw:ch:cc:wh:dt:porosity:timestamp:domain` | Read `AvatarSaveString.to_compact()` | 10 colon-separated segments | [ ] |
| F2 | Phase encoding: 8 phases T0..T7 (`past`=0, `present`=1, `future`=2, `transition`=3, `resolution`=4, `dissolution`=5, `crystallization`=6, `void`=7) `[Updated 2026-08-29: expanded from legacy 3-phase a/p/f]` | `python -c "from save_string_v21 import encode_phase; print([encode_phase(i) for i in range(8)])"` | 8 distinct phase codes | [ ] |
| F3 | Batch format: 64 comma-separated, `;` separates payload from metadata | `python -c "from save_string_v21 import BatchSaveString; b=BatchSaveString([...]); print(len(b.entries), ';' in b.to_compact())"` | 64 entries, `;` present | [ ] |
| F4 | Inject-site base64 for `:`/`|` delimiters | `python -c "from save_string_v21 import _encode_inject_extra, _decode_inject_extra; raw={'yao_vocabulary':{'a':'test'}}; enc=_encode_inject_extra(raw); dec=_decode_inject_extra(enc); print(dec==raw)"` | Round-trip true | [ ] |
| F5 | Structural validation, not mega-regex | `python -c "from save_string_v21 import validate_batch; print(validate_batch(b.to_compact()))"` | True for valid batch | [ ] |
| F6 | Backward compat: legacy 10-segment singles parse | `python -c "from save_string_v21 import AvatarSaveString; s=AvatarSaveString.from_compact('1:p:0.5:0.3:0.2:0.1:0.4:0.5:1234567890:sovereign'); print(s.hexagram_id)"` | 1 | [ ] |
| F7 | `INJECT=<base64>` suffix present when inject_site non-empty | `python -c "from save_string_v21 import AvatarSaveString; s=AvatarSaveString(...); print('INJECT=' in s.to_compact())"` | Present when inject_site provided | [ ] |

---

## Section 2.6: Frontend / Widget

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| G1 | 7 tabs present in correct order | Open `kingwen_512_oracle_widget.html` in browser | Tab order: Vector Space → Shotgun Blast → Hexagram Grid → Phase Explorer → State Matrix → Quantum Masking → J-space Jacobian | [ ] |
| G2 | J-space renders 1D Hamiltonian + 2D Jacobian + 3D Riemann sphere | Open J-space tab, inspect panels | Three panels present with correct labels | [ ] |
| G3 | Tab labels match rendered content | Visual inspection + grep for "3D Riemann" | Should say "3D Riemann sphere projection" | [ ] |
| G4 | Shared state: `hexagrams[]` + `resolved[]` + `selectedHexagram` + `selectedPhase` | Browser console: `Object.keys(window.__KINGWEN_STATE__)` | All four keys present | [ ] |
| G5 | Baked `hexagrams[]` preserved, live `resolved[]` merged | Diff initial `hexagrams` vs after `/expand` fetch | `hexagrams` unchanged, `resolved` updated | [ ] |
| G6 | Iframe mount for kingwen mode | `grep -rn "KingwenMainPane\|kingwen" Cinder/App.tsx OpenJarvis/DashboardPage.tsx` | Iframe component present | [ ] |
| G7 | `loadKit()` reads `kit_{hex_id}.json` directly | `grep -n "loadKit\|kit_" ggwaveBridge.ts` | Direct file read, no POG2 import | [ ] |
| G8 | `kitToHexagramNode()` maps kit schema to renderer nodes | `grep -n "kitToHexagramNode" ggwaveBridge.ts` | Mapping function present | [ ] |

---

## Section 2.7: Sovereign Kit Pipeline

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| H1 | `kit_{1..64}.json` built and present | `ls DATASETS/kingwen_model_sets/kit_*.json \| wc -l` | 64 files | [ ] |
| H2 | Schema fields present: baseModel, maleModels_0, femaleModels_0, modelTranslate_0/1/2, rotation_0, rotation_1, big_value, positions[6], extra[14] | `python -c "import json; k=json.load(open('DATASETS/kingwen_model_sets/kit_1.json')); print(list(k.keys()))"` | All fields present | [ ] |
| H3 | Void hexes 15/20/30/40 → South Pole (0,0,-1) | `python -c "import json; [print(h, json.load(open(f'DATASETS/kingwen_model_sets/kit_{h}.json'))['modelTranslate_0']) for h in [15,20,30,40]]"` | `[0,0,-1]` for all four | [ ] |
| H4 | Worker `/v1/kingwen/avatar/{session_id}` serves JS math | `curl -s https://kingwen-oracle.kristain33rs.workers.dev/v1/kingwen/avatar/test \| jq '.nodes \| length'` | 64 nodes | [ ] |
| H5 | KV cache `KINGWEN_AVATAR_CACHE` id `c39fc2ed3ced4b988224861476ca8def` accessible | `wrangler kv key get --binding=KINGWEN_AVATAR_CACHE --namespace-id=c39fc2ed3ced4b988224861476ca8def "test"` | Returns value or null (cache miss OK) | [ ] |
| H6 | Frontend fetches avatar data from Worker directly | `grep -n "kingwen-oracle.kristain33rs.workers.dev" frontend/src/lib/ggwaveBridge.ts` | Direct fetch URL present | [ ] |

---

## Section 3.1: Zotero Corpus Study

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| R1 | Corpus frequency profile built | `python C:/Users/krist/Desktop/zotero/learning-corpus/audit_text_corpus.py` | Output file with word/bigram counts | [ ] |
| R2 | Per-paper routing to hexagrams by (category, action) | `python build_per_hex_training_data.py --dry-run` | Assignment counts per hex | [ ] |
| R3 | All 64 hexagrams have non-empty paper assignments | `python -c "import json; d=json.load(open('output/per_hex_paper_assignments.json')); print(all(len(v)>0 for v in d.values()))"` | True (or explicit list of empty hexes) | [ ] |
| R4 | Bradley-Terry pattern extracted and documented | `grep -n "Bradley-Terry\|bradley_terry" docs/zotero-corpus-findings.md` | Citation + formula present | [ ] |
| R5 | DPO/RLHF conditional equivalence → non-negative margin rule documented | `grep -n "CPO\|non-negative\|effective margin" docs/zotero-corpus-findings.md` | Citation + rule present | [ ] |
| R6 | SELF-ALIGN principles → 64-hex principle mapping drafted | `grep -n "principle\|SELF-ALIGN" docs/zotero-corpus-findings.md` | Mapping table present | [ ] |
| R7 | Model Spec Midtraining → `trainingNotes` as prior documented | `grep -n "Model Spec\|midtraining\|MSM" docs/zotero-corpus-findings.md` | Citation + application present | [ ] |
| R8 | All samples trace back to actual corpus text (no fabrication) | `grep -r "synthetic\|fabricated\|mock" docs/zotero-corpus-findings.md` | Zero matches | [ ] |
| R9 | Findings cross-referenced to guide sections 2.3 and 2.4 | `grep -n "2.3\|2.4\|Reasoning Layer\|Voice Mapping" docs/zotero-corpus-findings.md` | Cross-refs present | [ ] |
| R10 | `kingwen_skill_card_renderer.py` updated with domain tool mappings | `git diff src/openjarvis/tools/kingwen_skill_card_renderer.py` | Non-empty diff with new mappings | [ ] |

---

## Section 3.2: POG2 Reference Audit

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| R11 | Transferable patterns documented: clock authority, state machine boundaries, network bridge contracts | `grep -n "CanonicalClock\|ClockAuthority\|HexagramNetworkBridge" docs/pog2-reference-patterns.md` | All three cited | [ ] |
| R12 | Anti-patterns documented: 1D selection, randomness, folklore labels | `grep -n "anti-pattern\|1D\|folklore\|random" docs/pog2-reference-patterns.md` | Anti-patterns listed | [ ] |
| R13 | Zero POG2 runtime imports in King Wen codebase | `grep -r "pog2\|POG2" src/openjarvis/emotion/ src/openjarvis/cli/` | Zero matches | [ ] |
| R14 | `docs/pog2-reference-patterns.md` written | `ls docs/pog2-reference-patterns.md` | File exists | [ ] |

---

## Section 3.3: Alignment Theory Integration

| ID | Item | Verification Command | Proof | Status |
|---|---|---|---|---|
| R15 | Bradley-Terry mapped to King Wen `relevance_score` | `grep -n "Bradley-Terry\|bradley_terry\|preference_strength" src/index.ts emotional_engine.py` | Mapping present in ranking code | [ ] |
| R16 | Non-negative effective margin enforced in ranking | `grep -n "max(0\|Math.max(0\|effective_margin" src/index.ts` | Enforcement present | [ ] |
| R17 | 16 SELF-ALIGN principles → 64-hex `trainingNotes` mapping | `grep -n "principle\|trainingNotes" kingwen_skill_card_renderer.py` | Mapping present | [ ] |
| R18 | Context distillation split: `raw_state` + `distilled_answer` | `grep -n "raw_state\|distilled_answer" src/index.ts` | Fields present | [ ] |

---

## Verification Gate Summary

| Gate | Command | Expected | Verified |
|---|---|---|---|
| A | `py_compile emotional_engine.py expand_server.py` | Exit 0 | [ ] |
| B | `curl -X POST http://127.0.0.1:8765/expand -d '{}' \| jq '.expanded_count, .resolved_count'` | 64, 512 | [ ] |
| C | `cd kingwen-oracle && npm run test` | 4/4 passing | [ ] |
| D | `cd kingwen-oracle && npm run build` | Exit 0 | [ ] |
| E | `pytest tests/cli/test_chat_cmd.py` | Green | [ ] |
| F | `grep -r "openjarvas" src/` | Zero matches | [ ] |
| G | `grep -r "stableHash" src/index.ts` | Zero matches | [ ] |
| H | `grep -n "unified_weave.*+\|unified_weave.*concat" src/index.ts` | No template concat | [ ] |

---

## Progress Tracking

**Phase completion:**
- [ ] Phase 1: State Expansion (A1-A8)
- [ ] Phase 2: Worker Rewrite (B1-B10)
- [ ] Phase 3: Reasoning Layer (C1-C9)
- [ ] Phase 4: Voice Mapping (D1-D8)
- [ ] Phase 5: Capture Pipeline (E1-E6)
- [ ] Phase 6: Save-String Protocol (F1-F7)
- [ ] Phase 7: Frontend/Widget (G1-G8)
- [ ] Phase 8: Sovereign Kit (H1-H6)
- [ ] Phase 9: Zotero Corpus (R1-R10)
- [ ] Phase 10: POG2 Reference (R11-R14)
- [ ] Phase 11: Alignment Theory (R15-R18)

**Last updated:** 2026-08-02  
**Execution log:** Append dated entries with command output for each completed item.
