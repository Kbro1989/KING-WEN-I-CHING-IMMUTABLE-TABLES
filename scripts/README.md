# scripts/

Active generation, bridge, and verification surface for the King Wen 64 Sovereign Model Engine.

## Unified 18-Stage Self-Contained Pipeline (`run_all_unified_pipeline.py`)

Run all stages with 100% self-contained parity:
```bash
python scripts/run_all_unified_pipeline.py
```

| Stage | Script | Description |
|---|---|---|
| **01** | `full_hexagram_shotgun.py` | 512-state Hamiltonian expansion & CSV datasets |
| **02** | `enrich_kit_models.py` | NPC model kit persona & skill card enrichment |
| **03** | `bridge_pog2_ontology.py` | POG2 ontology, K-color & CNS module integration |
| **04** | `shap_e_kingwen_3d_generator.py` | 729-vertex deterministic parametric PLY generator |
| **05** | `sync_voicebox_npc_profiles.py` | 64-model FastSpeech/WaveNet voice profiles manifest |
| **06** | `test_jkd_chapter_chorus.py` | 64 audio pellet JKD chapter chorus ingestion |
| **07** | `bridge_math_diagram_extractor.py` | Mathematical diagram extraction bridge |
| **08** | `bridge_desktop_3d_engines.py` | OpenUSD, Godot scene, and CollisionVis generator |
| **09** | `sync_all_desktop_viewers.py` | Desktop viewers sync & import manifest |
| **10** | `test_cognitive_variation.py` | Cognitive variation & input modulation test |
| **11** | `bridge_rsmv_shap_e_manifesto.py` | RSMV cache schema & Shap-E synthesis manifesto |
| **12** | `bridge_quantumlab_visualization.py` | 3D space-time wave packet evolution plots |
| **13** | `bridge_collisionvis_upgrade.py` | CollisionVis physics & HLSL shader upgrade |
| **14** | `bridge_rayeren_capability_vectors.py` | RayeRen neural speech & KD capability vectors |
| **15** | `verify_unbound_persona_domains.py` | 27×27 (729) unbound persona domain matrix audit |
| **16** | `bridge_quantum_64_grid.py` | QuantumLab 64-grid transitional density mapping |
| **17** | `verify_math_jacobian_hamiltonian.py` | SaveString V2.1 & Jacobian/Hamiltonian audit |
| **18** | `verify_output_mismatches.py` | Exhaustive 64-component output mismatch audit |
| **19** | `shotgun_rollout_runtime.py` | 8-phase chained phase rollout per hexagram — hamiltonian/porosity/resolved_vector trajectories, chain_breaks, chain_continuous flags |
| **20** | `rl_shotgun_measurables.py` | RL-measurable extraction from rollout: step_reward (hamiltonian/change/entropy/coherence/chain_bonus), discounted_returns, trajectory_variance, terminal_goodness, per_step_cosine_similarity, delta_vector |

## Chained Phase Rollout & RL Measurables

After the 512-state expansion (stage 01) and the Jacobian/Hamiltonian audit (stage 17), stages 19–20 add a temporal + quantified measurement layer on top of the resolved state chain.

### Stage 19 — `shotgun_rollout_runtime.py`

Chained 8-phase rollout per hexagram. Each phase runs `expand_hexagram()` for that phase_bits, then carries the prior phase's resolved/expanded/porosity/hamiltonian/line_balance/yao_vocabulary forward into the next phase via `_carry_forward()`. Breaks in the handoff are flagged, not dropped.

Per-hexagram output fields:
- `phases` — 8 phase records, each with `expanded_vector`, `resolved_vector`, `inject_site`, `line_balance`, `yao_vocabulary`, `quantum_avatar_state`, `hamiltonian_energy`, `porosity`, plus `rollout_context` when carry_chain is on
- `chain_breaks` — list of `(phase_bits, missing_keys)` for any handoff break
- `chain_continuous` — true when no breaks
- `hamiltonian_trajectory` — `[H_t for t in phases]`
- `porosity_trajectory` — `[porosity_t for t in phases]`
- `resolved_vector_trajectory` — `[resolved_t for t in phases]`
- `final_rollout_state` — last phase's carried-forward state

`_hamiltonian_energy` is called with `List[float]` built from `VEC_KEYS` for both vector arguments (mirrors `full_hexagram_shotgun.py` lines 648–653). For hex 1 the hamiltonian is clamped to 0 because `pq_dot ≈ 0.009` and `lagrangian ≈ 5.1` (from 6 yang lines), so the clamped difference is 0; the temporal signal for this hex lives in the resolved_vector movement and entropy/coherence, not in hamiltonian.

CLI:
```bash
python scripts/shotgun_rollout_runtime.py --hex 1 --out scripts/output/rollout_hex1_v2.json
python scripts/shotgun_rollout_runtime.py --text "..." --emotional-input 50 --out scripts/output/rollout_all.json
```

### Stage 20 — `rl_shotgun_measurables.py`

RL-measurable extraction from a rollout. Turns each phase step into a reward tuple and the 8-step sequence into discounted returns + trajectory statistics.

Per-step `step_reward()` components (weights are measurement heuristics, not derived invariants):
- `hamiltonian` — `_hamiltonian_energy` value × 0.1
- `change` — L2 norm of resolved_vector delta vs prior step × 1.0
- `entropy` — Shannon entropy over normalized resolved_vector components × 0.5 (intrinsic-signal proxy: concentrated vectors score low, spread vectors score high)
- `coherence` — resolved_vector coherence axis value × 0.4
- `chain_bonus` — +0.2 when the step carries forward cleanly (no carry_break)

Trajectory-level outputs:
- `discounted_returns` — 8-step discounted returns, gamma=0.95
- `total_return` — G_0
- `trajectory_variance` — std of step totals
- `terminal_goodness` — heuristic: coherence×0.5 + entropy×0.3 + chain_bonus(0.2 if continuous else 0)
- `delta_vector` + `delta_norm` — initial→final resolved_vector delta per axis
- `per_step_cosine_similarity` — 7 cosine similarities between consecutive resolved vectors
- `initial_entropy` / `final_entropy`, `initial_coherence` / `final_coherence`

Batch output `scripts/output/rl_measurables_all64.json` (64 hexagrams, verified):
- mean_total_return = 7.1472
- mean_trajectory_variance = 0.0696
- mean_terminal_goodness = 0.9114
- 64/64 chain_continuous = True
- range: total_return 6.8413 (hex 52) → 7.4319 (hex 51)

CLI:
```bash
python scripts/rl_shotgun_measurables.py --hex 1 --out scripts/output/rl_measurables_hex1.json
python scripts/rl_shotgun_measurables.py --out scripts/output/rl_measurables_all64.json
```

These are measurement artifacts on top of the existing consensus math — they quantify what the 512-state expansion already produces per hexagram across the 8-phase temporal chain, with reward weights labeled as measurement heuristics rather than derived invariants.

## Hardware & VHDL Generators
- `generate_vhdl_roms.py` — Emits `KingWen9BitResolver.vhd` from `HEXAGRAM_BASE`.
- `generate_vhdl_testbench.py` — Emits `tb_KingWen9BitResolver.vhd` and `KingWenExpected_pkg.vhd`.
- `verify_vhdl_resolver_parity.py` — 512-address functional VHDL simulation with 0 failures.

## Full Expansion Artifacts
- `ternary_full_expansion.json` — 27 trigrams, 729 hexagrams, 5,832 resolved states (2.9 MB)
- `hexagram_full_expansion.json` — 64 hexagrams, 512 resolved states, personalities, inversion pairs
