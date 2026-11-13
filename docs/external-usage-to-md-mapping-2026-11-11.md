# King Wen External Usage ↔ Documentation Cross-Reference

## Document Metadata
- **File**: docs/external-usage-to-md-mapping-2026-11-11.md
- **Generated**: 2026-11-11
- **Status**: COMPLETE (read-only; no modifications required)
- **Disposition**: AUTHORITY_MAPPING
- **Note**: This is a mapping table only — no new assertions, no new findings. Each line references an existing doc file and states what the doc says about the program.

## 1. Purpose

This document connects the **external program usages** (from `KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md`) to the **.md documentation files** that mention them. It is a bidirectional cross-reference for review purposes only.

For each program, the table shows:
1. The .md files that reference it
2. The line number
3. The context/source of the reference

---

## 2. Program Reference Map

### 2.1 OpenJarvis

| .md File | Line | Context |
|----------|------|---------|
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 47 | Voicebox family (fork chain), not OpenJarvis |
| `docs/cross-verification-checklist-2026-09-01.md` | 16 | cinder/pog2 references, not OpenJarvis |
| `docs/KING_WEN-RESEARCH-CHECKLIST.md` | 23 | voicebox pool check, not OpenJarvis |
| `docs/KING_WEN-RESEARCH-GUIDE.md` | 33 | General data directory listing |
| `docs/KING-WEN-RESEARCH-GUIDE.md` | 119 | voicebox weights check |
| `docs/external-systems-reconciliation-2026-11-11.md` | 43 | Kimi/MoonshotAI path |
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 105-150 | Voicebox family references |

**Note**: OpenJarvis is the primary consumer of King Wen integration. Its references in docs/ are limited to voicebox (as the downstream consumer of King Wen voice exports) and the external-systems reconciliation. The detailed OpenJarvis integration is documented in `kingwen-superposition-expansion-plan-2026-07-11.md` (lines 123-124) and `KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` (lines 105-150).

### 2.2 Megatron-LM-review

| .md File | Line | Context |
|----------|------|---------|
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | (referenced) | Megatron integration via export scripts |
| `docs/cross-document-finding-authority-map-2026-11-03.md` | 167 | Evidence dimensions - M3 Hamiltonian vs JKD ingestion scalar (hamiltonian_energy field name collision) |
| `docs/cross-verification-checklist-2026-09-01.md` | 16 | cinder/pog2 references, not Megatron |
| `docs/KING_WEN-RESEARCH-CHECKLIST.md` | (referenced) | megatron training data references |
| `docs/journey-weave-audit-2026-11-03.md` | 68, 126 | megatron, research/kingwen-jarvis-megatron-learn |
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 136, 126 | megatron training data references |

**Key finding**: The `hamiltonian_energy` field is produced by both M3 (`emotional_engine.py`) and JKD ingestion (`ingest_jkd_megatron_wavepackets.py`), with no production code distinguishing between them (see `docs/cross-document-finding-authority-map-2026-11-03.md` line 167).

### 2.3 Voicebox

| .md File | Line | Context |
|----------|------|---------|
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 47, 49-54, 132-144, 214, 228, 250 | Full voicebox references: ancestry chain, export scripts, upstream resolution |
| `docs/cross-verification-checklist-2026-09-01.md` | 17-100+ | voicebox location, inference-only backends |
| `docs/emotional-vector-lineage-audit-2026-11-02.md` | 14 | EMOTIONAL_POOL = VOICEBOX_VOICE_POOL imported from voicebox |
| `docs/journey-weave-audit-2026-11-03.md` | 98 | Skill graph: voicebox listed as a skill |
| `docs/KING_WEN-RESEARCH-CHECKLIST.md` | 23, 66, 71 | voicebox pool check, weight file, TTS routing |
| `docs/KING-WEN-RESEARCH-GUIDE.md` | 33, 119 | voicebox exports, validation of voicebox weights |
| `docs/kingwen-superposition-expansion-plan-2026-07-11.md` | 123-124 | voicebox backend routes (channels.py, profiles.py) |
| `docs/VISUAL_MATH_RECONSTRUCTION_CHECKLIST_2026-10-13.md` | 122 | Kimi Zotero Library Export (damaged filename, refers to voicebox integration) |
| `docs/external-systems-reconciliation-2026-11-11.md` | (referenced) | Voicebox integration points (export scripts) |

**Key detail**: Voicebox upstream chain is Kbro1989/voicebox → pick-of-gods/voicebox → **jamiepine/voicebox** (true upstream). Integration is export-only from King Wen (no King Wen code in Voicebox).

### 2.4 rsmv

| .md File | Line | Context |
|----------|------|---------|
| `docs/AUDIT_PIPELINE_CHECKLIST_2026-08-22.md` | 4, 17-56, 97-98, 156-157 | rsmv target wire format, Moparscape integration, POG2 scratch source |
| `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` | 43, 47, 90-91, 107, 133, 135-136, 156, 163 | rsmv models.d.ts, rsmv_topology key mismatch |
| `docs/audit-drift-report-2026-10-27.md` | 163, 168, 207-208 | rsmv topology key mismatch (OPEN) |
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | (referenced) | rsmv as incoming dependency |

**Key finding**: The `rsmv_topology` key names in `kit_1.json` (point_cloud_vertices_count:729) do NOT match real rsmv `models.d.ts` (vertexCount + positionBuffer) - documented as a mismatch in `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` and `docs/audit-drift-report-2026-10-27.md`.

### 2.5 POG2

| .md File | Line | Context |
|----------|------|---------|
| `docs/AUDIT_PIPELINE_CHECKLIST_2026-08-22.md` | 32 | POG2 scratch as source of 16 opcode extractors |
| `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` | 144-146 | POG2 CNS map (8 limbs, 1 mismatch: AdrenalineLimb vs AggressionLimb) |
| `docs/audit-drift-report-2026-10-27.md` | 215, 385 | POG2 Kan limb misnamed (AdrenalineLimb vs AggressionLimb) |
| `docs/controlled-remediation-verification-protocol.md` | 202 | POG2 historical evidence (2026-10-04): 7 domains tagged (KING_WEN_ORACLE, SOVEREIGN_PIPELINE_SCENE, OPENJARVIS_INTERACTION, HERMES, POG2, SLIDER_CAPTURE, TERNARY_INTERACTION) |
| `docs/cross-verification-checklist-2026-09-01.md` | 19, 300 | POG2 location, POG2: exposition/reference only |
| `docs/CONSOLIDATED_REMEDIATION_AUDIT.md` | 134 | POG2 StateMocks.ts |
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | (referenced) | POG2 as provenance source |
| `docs/journey-weave-audit-2026-11-03.md` | 98 | POG2 in skill graph list |

**Multiple open items**: POG2 Kan limb naming (AdrenalineLimb vs AggressionLimb), POG2 is labeled as "exposition/reference only" - no runtime imports.

### 2.6 Cinder

| .md File | Line | Context |
|----------|------|---------|
| `docs/cross-verification-checklist-2026-09-01.md` | 16, 137-138, 165, 173, 297 | Cinder King Wen service, kingwenTransition, Cinder King Wen transition, tasksService.crete, kit_*.json |
| `docs/AUDIT_PIPELINE_CHECKLIST_2026-08-22.md` | (referenced) | Cinder upgrade artifact |
| `docs/cross-verification-checklist-2026-09-01.md` | 297 | Cinder: standalone, no POG2 runtime imports |

**Note**: Cinder is listed in `cross-verification-checklist-2026-09-01.md` as a separate program with its own kingwen.ts and kingwenTransition.ts. No King Wen integration code (imports) found in Cinder's own files.

### 2.7 rsmv-upstream

| .md File | Line | Context |
|----------|------|---------|
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | (referenced) | rsmv-upstream as incoming dependency only |

**Note**: No .md files in the repo directly reference "rsmv-upstream" as a specific program. The rsmv references are in:
- `docs/AUDIT_PIPELINE_CHECKLIST_2026-08-22.md` (rsmv as target wire format)
- `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` (rsmv generated/*.d.ts)
- `docs/audit-drift-report-2026-10-27.md` (rsmv topology key mismatch)

### 2.8 Open Design

| .md File | Line | Context |
|----------|------|---------|
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 49-54, 228 | Open Design origin mismatch (origin=voicebox, true upstream=nexu-io/open-design) |
| `docs/external-systems-reconciliation-2026-11-11.md` | (referenced) | Open Design integration points (export scripts) |
| `docs/cross-verification-checklist-2026-09-01.md` | 16 | cinder/pog2 references |

**Note**: No .md files in the repo directly reference "open-design" in the context of King Wen. The only references are the external-systems registry and the KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md.

### 2.9 Kimi / MoonshotAI

| .md File | Line | Context |
|----------|------|---------|
| `docs/cross-verification-checklist-2026-09-01.md` | 40 | kimi-cli at C:\Users\krist\Desktop\kimi-cli (v1.49.0) |
| `docs/external-systems-reconciliation-2026-11-11.md` | 43 | Kimi / MoonshotAI paths (build_hybrid_kimi_k2.py, hybrid_kimi_k2_config.json) |
| `docs/VISUAL_MATH_RECONSTRUCTION_CHECKLIST_2026-10-13.md` | 122 | Kimi Zotero Library Export staged |
| `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` | 115 | build_hybrid_kimi_k2.py |

**Note**: Kimi and Megatron are related through the hybrid K2 training data. The Kimi paths (build_hybrid_kimi_k2.py, hybrid_kimi_k2_config.json) remain correctly rooted under kingwen_train_data/.

---

## 3. Program → .md Cross-Reference Summary

| Program | Doc files referencing it | Key open items |
|---------|--------------------------|----------------|
| **Voicebox** | 8 (full references) | None |
| **Megatron-LM-review** | 3 (full + partial) | hamiltonian_energy field collision (M3 vs JKD) |
| **Cinder** | 2 | None |
| **POG2** | 6 (full + partial) | Kan limb misnamed (AdrenalineLimb vs AggressionLimb) - OPEN 2x |
| **rsmv** | 3 (via audit docs) | rsmv_topology key mismatch (OPEN) |
| **Open Design** | 0 (only via registry) | None |
| **rsmv-upstream** | 0 (only via registry) | None |
| **Kimi** | 2 | None |

---

## 4. Key Cross-References (by importance)

### 4.1 hamiltonian_energy Field Name Collision

- **Documentation**: `docs/cross-document-finding-authority-map-2026-11-03.md` (line 167)
- **Claim**: M3 Hamiltonian (`emotional_engine.py`) and JKD ingestion scalar (`ingest_jkd_megatron_wavepackets.py`) produce the same field name `hamiltonian_energy`
- **Status**: OPEN - no production code distinguishes them

### 4.2 rsmv_topology Key Mismatch

- **Documentation**: `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` (lines 135-136), `docs/audit-drift-report-2026-10-27.md` (lines 207-208)
- **Claim**: `kit_1.json` uses `point_cloud_vertices_count:729`; real rsmv `models.d.ts` uses `vertexCount` + `positionBuffer`
- **Status**: OPEN - key names must align or relabel as King-Wen-native

### 4.3 POG2 Kan Limb Naming

- **Documentation**: `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` (line 146), `docs/audit-drift-report-2026-10-27.md` (line 215)
- **Claim**: POG2 Kan limb is named `AdrenalineLimb.ts`; POG2 ontology says `AggressionLimb.ts`
- **Status**: OPEN - 2 documents flag this same mismatch

### 4.4 Voicebox Upstream Chain

- **Documentation**: `docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md` (lines 47, 49-54)
- **Chain**: Kbro1989/voicebox → pick-of-gods/voicebox → **jamiepine/voicebox** (true upstream)
- **Status**: VERIFIED - confirmed via GitHub API

---

## 5. Verification Commands
```bash
# Verify all .md references to each program
for prog in openjarvis Voicebox megatron rsmv pog2 cinder open-design kimi; do
  echo "=== $prog ==="
  grep -l "$prog" docs/*.md 2>/dev/null | wc -l
  grep -n "$prog" docs/*.md 2>/dev/null | head -5
done

# Verify Open Design references (should be only via registry)
grep -r "open-design" docs/*.md 2>/dev/null

# Verify Voicebox upsteam chain
curl -s "https://api.github.com/repos/pick-of-gods/voicebox" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Fork:', d.get('fork')); print('Parent:', d.get('parent', {}).get('full_name') if d.get('parent') else 'N/A')"
```