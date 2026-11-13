# scripts/ — King Wen Script Classification Index

**Version:** 2026-11-10
**Total Python scripts:** 393
**Purpose:** Authoritative classification for agent navigation. Each entry includes canonical entry point, consumers, I/O contracts, and verification command.

---

## Classification Legend

| Status | Meaning |
|--------|---------|
| **ACTIVE** | Current supported scripts; part of the 18-stage pipeline or core Layer 0-5 math |
| **EXPERIMENTAL** | Research and development; not in production pipeline |
| **FROZEN** | Immutable benchmark tooling; pinned versions, no changes |
| **HISTORICAL** | Superseded implementations; preserved for provenance |
| **DEPRECATED** | Retained but not recommended; use ACTIVE alternative |

---

## ACTIVE — Core Pipeline (18-Stage Unified)

| Script | Stage | Canonical Entry Point | Consumers | Verification |
|--------|-------|----------------------|-----------|--------------|
| `full_hexagram_shotgun.py` | 01 | `shotgun_expand(request_text, emotional_input)` | `emotional_engine.capture_pre_slider`, `expand_server.py`, `kingwen_train_data/full_shotgun_expansion_all.jsonl` | `python -c "from full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); print(len(r['expanded']), len(r['resolved']))"` |
| `enrich_kit_models.py` | 02 | `enrich_kits()` | `DATASETS/kingwen_model_sets/kit_*.json`, `update_3d_kits_with_quantum_wavepackets.py` | `python enrich_kit_models.py --verify` |
| `bridge_pog2_ontology.py` | 03 | `bridge_ontology()` | POG2 integration consumers | `python bridge_pog2_ontology.py --dry-run` |
| `shap_e_kingwen_3d_generator.py` | 04 | `generate_shap_e_3d()` | `DATASETS/shap_e_model_cache/`, `generate_avatar_meshes.py` | `python shap_e_kingwen_3d_generator.py --hex 1` |
| `sync_voicebox_npc_profiles.py` | 05 | `sync_profiles()` | `DATASETS/kingwen_64_npc_voice_profiles.json`, Voicebox training | `python sync_voicebox_npc_profiles.py --verify` |
| `test_jkd_chapter_chorus.py` | 06 | `test_chorus()` | JKD audio pellet ingestion | `python test_jkd_chapter_chorus.py --hex 1` |
| `bridge_math_diagram_extractor.py` | 07 | `bridge_diagram_extractor()` | Math diagram extraction pipeline | `python bridge_math_diagram_extractor.py --verify` |
| `bridge_desktop_3d_engines.py` | 08 | `bridge_desktop_engines()` | OpenUSD, Godot, CollisionVis | `python bridge_desktop_3d_engines.py --verify` |
| `sync_all_desktop_viewers.py` | 09 | `sync_viewers()` | Desktop viewer sync manifest | `python sync_all_desktop_viewers.py --verify` |
| `test_cognitive_variation.py` | 10 | `test_cognitive_variation()` | Input modulation tests | `python test_cognitive_variation.py` |
| `bridge_rsmv_shap_e_manifesto.py` | 11 | `bridge_manifesto()` | RSMV cache schema + Shap-E synthesis | `python bridge_rsmv_shap_e_manifesto.py --verify` |
| `bridge_quantumlab_visualization.py` | 12 | `bridge_quantumlab()` | 3D space-time wave packet plots | `python bridge_quantumlab_visualization.py --hex 1` |
| `bridge_collisionvis_upgrade.py` | 13 | `bridge_collisionvis()` | CollisionVis physics + HLSL shader | `python bridge_collisionvis_upgrade.py --verify` |
| `bridge_rayeren_capability_vectors.py` | 14 | `bridge_rayeren()` | RayeRen neural speech + KD vectors | `python bridge_rayeren_capability_vectors.py --verify` |
| `verify_unbound_persona_domains.py` | 15 | `verify_persona_domains()` | 27×27 (729) persona domain matrix | `python verify_unbound_persona_domains.py` |
| `bridge_quantum_64_grid.py` | 16 | `bridge_quantum_grid()` | QuantumLab 64-grid density mapping | `python bridge_quantum_64_grid.py --verify` |
| `verify_math_jacobian_hamiltonian.py` | 17 | `verify_jacobian_hamiltonian()` | SaveString V2.1 & Jacobian/Hamiltonian audit | `python verify_math_jacobian_hamiltonian.py` |
| `verify_output_mismatches.py` | 18 | `verify_mismatches()` | Exhaustive 64-component output audit | `python verify_output_mismatches.py` |
| `shotgun_rollout_runtime.py` | 19 | `run_rollout(hex, emotional_input)` | Chained 8-phase rollout per hexagram | `python shotgun_rollout_runtime.py --hex 1` |
| `rl_shotgun_measurables.py` | 20 | `extract_measurables(hex)` | RL-measurable extraction from rollout | `python rl_shotgun_measurables.py --hex 1` |

---

## ACTIVE — Core Layer 0-5 Math (KINGWEN_AGENT_ONBOARDING.md)

| Script | Layer | Canonical Entry Point | Purpose |
|--------|-------|----------------------|---------|
| `emotional_engine.py` | 0 | `capture_pre_slider()`, `expand_hexagram()`, `sample_resolve()`, `extract_intent()`, `compute_consensus_from_resolved()`, `derive_dynamic_emotional_input()` | Core expansion, consensus, intent extraction |
| `kingwen_ternary_tables_complete.py` | 0 | `HEXAGRAM_BASE`, `PHASE_INFO`, `PHASE_LINE_MAP`, `EMOTIONAL_WEIGHTS`, `VOICEBOX_VOICE_POOL`, `TOTAL_ENCODINGS` | 9-bit encoding, immutable tables (read-only) |
| `decision_matrix.py` | 0 | `compute_decision_matrix()` | Interference computation |
| `temporal_emotional_engine.py` | 0 | `temporal_emotional_engine()` | Phase-aware delta scoring |
| `hexagram_personality.py` | 0 | `build_hexagram_personality_map()` | Archetype vectors |
| `KING_WEN_TABLES.py` | 0 | `verify_registry()` | Python verification entrypoint |
| `expand_server.py` | 1 | `POST /expand` endpoint | Local HTTP expansion server |
| `kingwen_quantum_process.py` | 1 | `run_quantum_process(query, emotional_input)` | Possibility tensor generator |
| `superposition_capture.py` | 1 | `capture_pre_slider()` | Capture pipeline |
| `kingwen_expansion_wrapper.py` | 1 | `expansion_wrapper()` | Multi-domain wrapper |
| `multi_layer_expand.py` | 1 | `multi_layer_expand()` | Layered expansion |
| `kingwen_mobius_sphere.py` | 2 | `mobius_projection()` | Riemann sphere projection for avatar coords |
| `kingwen_state_transition.py` | 2 | `state_transition()` | State transition Jacobian chain rule |
| `bridge_ply_to_godot_mesh.py` | 2 | `convert_ply_to_godot()` | PLY→OBJ converter for Godot |

---

## ACTIVE — Math Extraction Pipeline (Lua-math-tool.md)

| Script | Purpose | Entry Point | Verification |
|--------|---------|-------------|--------------|
| `semantic_math_extractor.py` | Core math extraction from PDFs | `extract(pdf_path)` | `python -m py_compile semantic_math_extractor.py` |
| `mathml_parser.py` | MathML tree parsing | `parse(mathml_string)` | `python -m py_compile mathml_parser.py` |
| `math_recovery_tool.py` | LaTeX → canonical tokens | `recover(latex_string)` | `python test_nested_args.py` |
| `math_contract.py` | Canonical schema (4 status dims) | `ParseStatus`, `StructuralStatus`, `BackendStatus`, `SolutionStatus` | `python -m py_compile math_contract.py` |
| `math_pdf_parser.py` | 6-layer PDF parser | `parse(pdf_path, max_pages, dpi)` | `python -m py_compile math_pdf_parser.py` |
| `visual_math_translator.py` | 2D PDF geometry → canonical | `assemble_structure(regions)` | `python -m py_compile visual_math_translator.py` |
| `chroma_visual_reader.py` | Multi-scale 2D math geometry | `assemble_structure(regions)` | `python -m py_compile chroma_visual_reader.py` |
| `alttext_cross_checker.py` | MathML vs alttext comparison | `compare(alttext, expr_tokens)` | `python -m py_compile alttext_cross_checker.py` |
| `math_context_extractor.py` | Context preservation | `extract_with_context(pdf_path, page_num)` | `python -m py_compile math_context_extractor.py` |
| `display_equation_extractor.py` | Display equation extraction | `extract(html)` | `python -m py_compile display_equation_extractor.py` |
| `math_symbol_classifier.py` | Symbol classification | `classify(ocr_text, shape_features)` | `python -m py_compile math_symbol_classifier.py` |
| `extract_math_clean.py` | Clean math extraction | `extract(pdf_path, page_num)` | `python -m py_compile extract_math_clean.py` |
| `extract_tex_macros.py` | TeX macro extraction | `extract_macros(tex_content)` | `python -m py_compile extract_tex_macros.py` |
| `extract_jspace_math.py` | J-space math extraction | `extract_function(content, func_name)` | `python -m py_compile extract_jspace_math.py` |
| `math_occurrence_accounting.py` | Occurrence accounting | `ledger(paper_id, version, stage)` | `python test_occurrence_accounting.py` |
| `math_notation_mapping.py` | Unicode→SymPy/Wolfram | `to_sympy(unicode_char)` | `python -m py_compile math_notation_mapping.py` |
| `math_structure_extractor.py` | Structure extraction | `extract(pdf_path, page_num)` | `python -m py_compile math_structure_extractor.py` |
| `prose_math_extractor.py` | Prose math extraction | `extract_from_html(html, arxiv_id)` | `python -m py_compile prose_math_extractor.py` |
| `structural_ast_extractor.py` | MathML → ExprNode tree | `extract(mathml_node)` | `python -m py_compile structural_ast_extractor.py` |
| `math_symbol_vision_hooks.py` | Vision symbol hooks | `register(hook_name, fn)` | `python -m py_compile math_symbol_vision_hooks.py` |
| `math_ast_integration.py` | AST + occurrence binding | `bind_occurrence(ast_tree, key)` | `python -m py_compile math_ast_integration.py` |
| `e2e_math_pipeline.py` | End-to-end pipeline | `fetch → extract → parse → solve` | `python e2e_math_pipeline.py --arxiv 2605.00155` |

---

## ACTIVE — VHDL & Hardware Generators

| Script | Purpose | Entry Point | Output |
|--------|---------|-------------|--------|
| `generate_vhdl_roms.py` | KingWen9BitResolver VHDL ROM | `generate_vhdl()` | `KingWen9BitResolver.vhd` |
| `generate_vhdl_testbench.py` | VHDL testbench + expected pkg | `generate_testbench()` | `tb_KingWen9BitResolver.vhd`, `KingWenExpected_pkg.vhd` |
| `verify_vhdl_resolver_parity.py` | 512-address GHDL simulation | `verify_parity()` | Pass/fail |

---

## ACTIVE — Verification & Audit Scripts

| Script | Purpose | Verification |
|--------|---------|--------------|
| `verify_registry.py` | Validates `KING_WEN_TABLES.py` | `python verify_registry.py` |
| `verify_output_mismatches.py` | 64-component output audit | `python verify_output_mismatches.py` |
| `verify_math_jacobian_hamiltonian.py` | SaveString V2.1 + Jacobian/Hamiltonian | `python verify_math_jacobian_hamiltonian.py` |
| `verify_unbound_persona_domains.py` | 27×27 persona domain matrix | `python verify_unbound_persona_domains.py` |
| `verify_vhdl_resolver_parity.py` | VHDL 512-address functional | `python verify_vhdl_resolver_parity.py` |
| `verify_cross_engine_cli_validation.py` | 8-suite cross-engine validation | `python verify_cross_engine_cli_validation.py` |
| `verify_output_mismatches.py` | 64-component output mismatch audit | `python verify_output_mismatches.py` |
| `verify_tensor_memory.py` | Tensor memory verification | `python verify_tensor_memory.py` |
| `verify_9bit_resolver.py` | 9-bit resolver verification | `python verify_9bit_resolver.py` |

---

## EXPERIMENTAL — Research & Development

| Script | Purpose | Status |
|--------|---------|--------|
| `arxiv_html_parser.py` | arXiv HTML → MathML extraction | Active development |
| `arxiv_provenance.py` | arXiv provenance chain | Active development |
| `math_nesting_proof.py` | Nested argument proof | Experimental |
| `math_corruption_test.py` | Corruption detection | Experimental |
| `math_micro_test.py` | Micro tests | Experimental |
| `math_regression_detail.py` | Regression hunting | Experimental |
| `math_regression_hunt.py` | Regression analysis | Experimental |
| `math_failure_taxonomy.py` | Failure classification | Experimental |
| `math_failure_corpus.py` | Failure corpus builder | Experimental |
| `math_unknown_inventory.py` | Unknown command inventory | Experimental |
| `batch_math_pipeline.py` | Batch processing | Experimental |
| `multi_engine_parser.py` | Multi-engine parser stacking | Experimental |
| `solve_all.py` | Comprehensive solver | Experimental |
| `solve_comprehensive.py` | Comprehensive solver | Experimental |
| `solve_dual_path.py` | Dual-path solving | Experimental |
| `solve_html_equations.py` | HTML equation solving | Experimental |
| `solve_latex.py` | LaTeX solving | Experimental |
| `solve_latex_only.py` | LaTeX-only solving | Experimental |
| `solve_pylatexenc.py` | PyLaTeXenc backend | Experimental |
| `solve_provenance.py` | Provenance solving | Experimental |
| `solve_quick.py` | Quick solver | Experimental |
| `solve_sample.py` | Sample solver | Experimental |
| `solve_selective.py` | Selective solving | Experimental |
| `solve_unicode.py` | Unicode solving | Experimental |
| `solve_unicode_10.py` | Unicode solving v10 | Experimental |
| `solve_unicode_only.py` | Unicode-only solving | Experimental |
| `solve_with_definitions.py` | Definition-aware solving | Experimental |

---

## EXPERIMENTAL — Vision & OCR

| Script | Purpose | Status |
|--------|---------|--------|
| `targeted_depth_ocr.py` | High-zoom OCR for tall/wide symbols | Active |
| `targeted_math_detector.py` | Targeted math detection | Active |
| `vision_math_extractor.py` | Vision-based extraction | Active |
| `vision_comparison_pipeline.py` | Vision comparison pipeline | Active |
| `chroma_visual_reader.py` | Chroma visual reader | Active |
| `visual_math_translator.py` | Visual math translation | Active |
| `spatial_syntactic_observer.py` | Spatial syntactic observation | Experimental |
| `bridge_depth_anything_v2.py` | Depth Anything V2 bridge | Active |
| `bridge_depth_anything_v2.py` | Depth Anything V2 bridge (hardened) | Active |
| `render_fullpage_depth.py` | Full-page depth rendering | Active |
| `controlled_depth_run.py` | Controlled depth run | Active |
| `audit_pdf_depth_lineage.py` | PDF depth lineage audit | Experimental |
| `audit_rendered_png_producers.py` | Rendered PNG audit | Experimental |
| `experiments_crop_isolation.py` | Crop isolation experiments | Experimental |
| `experiments_multi_paper_generalization.py` | Multi-paper generalization | Experimental |
| `evaluate_cross_paper_generalization_v1.py` | Cross-paper generalization | Experimental |
| `evaluate_cross_paper_v2_strict.py` | Cross-paper v2 strict | Experimental |
| `evaluate_rahmani_generalization.py` | Rahmani generalization | Active |
| `evaluate_output_reference.py` | Output reference evaluation | Experimental |
| `evaluate_structural_completeness_b2.py` | Structural completeness B2 | Experimental |
| `evaluate_three_fidelity_dimensions.py` | Three fidelity dimensions | Experimental |
| `evaluate_v1_v2_cross_paper_comparison.py` | V1 vs V2 comparison | Experimental |

---

## FROZEN — Immutable Benchmark Tooling

| Script | Purpose | Frozen Artifact |
|--------|---------|-----------------|
| `build_benchmark_manifest.py` | Benchmark manifest builder | `benchmark_manifest.json` |
| `build_benchmark_representativeness.py` | Benchmark representativeness | `benchmark_representativeness_report.json` |
| `run_representative_page_evaluation.py` | Representative page evaluation | `representative_page_evaluation.jsonl` |
| `run_independent_validation_1406.py` | Independent validation 1406 | Frozen |
| `run_independent_validation_2102.py` | Independent validation 2102 | Frozen |
| `run_v2_v3_comparison.py` | V2 vs V3 comparison | Frozen |
| `run_border_evaluation.py` | Border evaluation | Frozen |
| `freeze_baseline.py` | Baseline freeze | Frozen |
| `freeze_cross_paper_case_registry_manifest.py` | Case registry freeze | Frozen |
| `freeze_cross_paper_v1_evaluation_manifest.py` | Cross-paper v1 freeze | Frozen |
| `freeze_producer_integrity_baseline.py` | Producer integrity freeze | Frozen |
| `freeze_rahmani_generalization_manifest.py` | Rahmani freeze | Frozen |
| `audit_candidate_crops.py` | Candidate crop audit | Frozen |
| `audit_contract_verification_paths.py` | Contract verification paths | Frozen |
| `audit_gold_equation_chains_1505.py` | Gold equation chains | Frozen |
| `audit_glyph_catalog.py` | Glyph catalog audit | Frozen |
| `audit_multi_paper_experiment.py` | Multi-paper experiment audit | Frozen |
| `audit_pdf_depth_lineage.py` | PDF depth lineage audit | Frozen |
| `audit_python_files.py` | Python files audit | Frozen |
| `audit_rendered_png_producers.py` | Rendered PNG producers audit | Frozen |
| `audit_repo_math_join.py` | Repo math join audit | Frozen |
| `audit_vilt_structural_completeness.py` | ViLT structural audit | Frozen |
| `correctness_harness.py` | Correctness harness | Frozen |
| `positive_control_comparison.py` | Positive control | Frozen |

---

## HISTORICAL — Superseded Implementations

| Script | Superseded By | Note |
|--------|---------------|------|
| `collapse_full_128.py` | `full_hexagram_shotgun.py` | 128-state model removed |
| `kingwen_training.py` | `build_full_shotgun_jsonl.py` | Old training pipeline |
| `run_all.py` | `run_all_unified_pipeline.py` | Old pipeline runner |
| `run_all_vhdl_testbenches.py` | `verify_vhdl_resolver_parity.py` | Old VHDL runner |
| `run.py` | `run_all_unified_pipeline.py` | Old entry point |
| `run_generators.py` | Individual generator scripts | Old runner |
| `generate_engine.py` | TS generators in src/ | Old TS generator |
| `generate_parser.py` | TS parser generators | Old TS generator |
| `generate_types.py` | TS type generators | Old TS generator |
| `generate_utils.py` | TS utils generators | Old TS generator |
| `generate_readable_perspectives.py` | `build_hexagram_skill_cards.py` | Old skill cards |
| `generate_full_code_solution.py` | Per-hex training data | Old generator |
| `generate_full_shotgun_30gb.py` | `build_full_shotgun_jsonl.py` | Old 30GB generator |
| `build_full_shotgun_jsonl.py` (old) | `build_full_shotgun_jsonl.py` (current) | Replaced |
| `build_training_data.py` | `build_per_hex_training_data.py` | Old training data |
| `kingwen_lexical_gate.py` | `build_full_shotgun_jsonl.py` | Old lexical gate |
| `kingwen_master_unified_registry.py` | `kingwen_train_data/` | Old registry |

---

## DEPRECATED — Retained But Not Recommended

| Script | Replacement | Reason |
|--------|-------------|--------|
| `collapse_full_128.py` | `full_hexagram_shotgun.py::shotgun_expand()` | 128-state model invalid |
| `generate oracle.deprecated` | `src/core/OracleEngine.ts` | Old TS generator |
| `generate emotionalparser+narrativeengine.deprecated` | `src/parser/EmotionalParser.ts`, `NarrativeEngine.ts` | Old TS generator |
| `generate deterministichash+temporalmath.deprecated` | `src/utils/DeterministicHash.ts`, `TemporalMath.ts` | Old TS generator |
| `generate oracleengine.ts.deprecated` | `src/core/OracleEngine.ts` | Old TS generator |
| `save registry.deprecated` | `data/` JSON files | Old save format |
| `test file.deprecated` | `tests/oracle.test.ts` | Old test |
| `verifycation.py.deprecated` | `verify_registry.py` | Typo + old verification |
| `categorize.py` | `classify_chain_roles.py` | Old categorization |
| `categorize2.py` | `classify_chain_roles.py` | Old categorization v2 |
| `debug_jag.py` through `debug_jag7.py` | `audit_*` scripts | Debug scripts |
| `debug_transpose.py` through `debug_transpose4.py` | `audit_*` scripts | Debug scripts |
| `debug_star.py` | `audit_*` scripts | Debug script |
| `debug_tree.py` | `structural_ast_extractor.py` | Debug script |
| `debug_extra_byte.py` | `delimiter_identity.py` | Debug script |
| `debug_faces.py`, `debug_faces_detail.py` | `verify_output_mismatches.py` | Debug scripts |
| `fix_generators.py` | Regenerate from source | One-time fix |
| `fix_md_references.py` | Manual doc updates | One-time fix |
| `patch_diag.py` | `verify_output_mismatches.py` | Patch diagnostic |
| `patch_exc.py` | `verify_output_mismatches.py` | Patch diagnostic |
| `patch_targeted.py` | `verify_output_mismatches.py` | Patch diagnostic |

---

## Test Scripts (tests/ + scripts/test_*)

| Script | Type | Purpose |
|--------|------|---------|
| `test_math_contract.py` | Contract | Canonical schema tests |
| `test_math_contract_adversarial.py` | Contract | Adversarial contract tests |
| `test_mathml_parser_on_corpus.py` | Parser | MathML parser on corpus |
| `test_nested_args.py` | Recovery | Nested argument recovery |
| `test_mbox_dollar_recovery.py` | Recovery | \mbox + $ recovery |
| `test_parse_real.py` | Parser | Real parsing |
| `test_pix2text_harvest.py` | Vision | Pix2Text harvest |
| `test_preservation.py` | Contract | Preservation tests |
| `test_provenance_corruption.py` | Contract | Provenance corruption |
| `test_rationale_corpus.py` | Contract | Rationale corpus |
| `test_relation_identity.py` | Contract | Relation identity |
| `test_semantic_fidelity.py` | Contract | Semantic fidelity |
| `test_solve_direct.py` | Solver | Direct solving |
| `test_structural_conservation.py` | Parser | Structural conservation |
| `test_structural_survival.py` | Parser | Structural survival |
| `test_threshold_policies.py` | Contract | Threshold policies |
| `test_wavepacket_consistency.py` | Quantum | Wave packet consistency |
| `test_integral_ir.py` | Contract | Integral IR |
| `test_canonical_extraction.py` | Extraction | Canonical extraction |
| `test_cognitive_variation.py` | Core | Cognitive variation |
| `test_contextual_expansion_generalized.py` | Core | Contextual expansion |
| `test_geometry_generalization.py` | Vision | Geometry generalization |
| `test_jkd_chapter_chorus.py` | Core | JKD chorus |
| `test_model_lookup.py` | Core | Model lookup |
| `test_munder_fix.py` | Parser | munder fix |
| `test_adjudication_consistency.py` | Vision | Adjudication consistency |
| `test_pix2text_harvest.py` | Vision | Pix2Text harvest |
| `test_attrerr.py` | Debug | AttributeError |
| `test_quick.py` | Debug | Quick test |
| `test_sample.py` | Debug | Sample test |

---

## Verification Commands Quick Reference

```bash
# Core pipeline
python scripts/run_all_unified_pipeline.py

# Core expansion
python -c "from full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); print('expanded',len(r['expanded']),'resolved',len(r['resolved']))"

# Registry verification
python scripts/verify_registry.py

# Math pipeline
python -m py_compile scripts/mathml_parser.py
python -m py_compile scripts/math_recovery_tool.py
python -m py_compile scripts/math_contract.py
python -m py_compile scripts/math_pdf_parser.py

# Tests
python -m pytest tests/ -v
python -m pytest scripts/test_math_contract.py -v
python -m pytest scripts/test_mathml_parser_on_corpus.py -v

# VHDL
python scripts/verify_vhdl_resolver_parity.py

# 18-stage pipeline
python scripts/run_all_unified_pipeline.py

# Expansion server
python scripts/expand_server.py
```

---

## Navigation Tips

1. **Start with ACTIVE Core Pipeline** — 18-stage table in `scripts/README.md`
2. **Layer 0-5 Math** — `KINGWEN_AGENT_ONBOARDING.md` lists exact files per layer
3. **Math Extraction** — `lua-math-tool.md` maps each script to Lua module
4. **Artifact dependencies** — `king-wen-workflow-paths.md` tracks active consumers
5. **Engineering rules** — `AGENTS.md` for invariants and constraints
6. **FROZEN scripts** — Do not modify; they produce frozen baselines
7. **DEPRECATED scripts** — Do not use; replacements listed in table
8. **HISTORICAL scripts** — Reference only; superseded by ACTIVE equivalents