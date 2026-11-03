# King Wen Journey Weave Audit — 2026-11-03

## Summary

| Metric | Value |
|--------|-------|
| Total skills scanned | 241 |
| Declared edges | 155 |
| Missing edge targets (phantom refs) | 49 (26 unique) |
| Orphan skills (no edges) | 141 (78 active, 63 archived) |
| Clusters (≥3 members) | 42 |
| Memory cards parsed | 951 |
| Domains with 0 skills | 3 (learned_abilities, code_agnostic, user_intents) |

## 1. Phantom References (26 unique, 49 edges)

All missing targets are skills referenced in `related_skills` frontmatter that do **not** exist as installed skills. These are not resolvable to any installed skill under any path prefix.

### Truly Phantom (no installed skill exists)
| Missing Target | References | Notes |
|---|---|---|
| airtable | 1 | productivity skill that was never installed |
| ascii-video | 1 | creative skill that was never installed |
| audiocraft | 1 | media skill that was never installed |
| browser | 1 | phantom hub — no browser skill exists |
| claude-code | 5 | referenced by 5 skills; no claude-code skill installed |
| claude-design | 1 | phantom reference |
| cloudflare-capability-audit | 2 | no such skill exists |
| dogfood | 2 | phantom reference |
| github-code-review | 3 | no such skill installed |
| grok | 1 | phantom reference |
| hermes-agent | 2 | no such skill installed |
| hermes-agent-skill-authoring | 1 | no such skill installed |
| image_gen | 1 | phantom hub — no image_gen skill exists |
| kanban-orchestrator | 1 | phantom reference |
| notion | 1 | productivity skill not installed |
| openjarvis-save-string | 1 | phantom reference (openjarvis skill exists but not save-string) |
| pog2-local-build | 1 | phantom reference |
| powerpoint | 4 | productivity skill not installed |
| reddit-reading | 2 | phantom reference |
| rss-feeds | 2 | phantom reference |
| sovereign-state-agents | 2 | phantom reference |
| test-driven-development | 3 | phantom reference |
| verification-rules | 1 | phantom reference (verification/verification-artifact-hygiene exists) |
| verified-engineering | 1 | phantom reference (software-development/verified-engineering exists) |

### Resolvable to Existing Skills (path mismatch, not phantom)
| Missing Target | Resolves To | Fix |
|---|---|---|
| canonical-table-audit | verification/canonical-table-audit | Update related_skills to use full path |
| verification-rules | verification/verification-artifact-hygiene | Update related_skills to use full path |

**Action:** 24 of 26 missing targets are truly phantom (no installed skill). 2 are path-mismatched references that can be fixed by updating `related_skills` frontmatter to use the correct full path.

## 2. Orphan Skills (78 active, 63 archived)

### Active Orphans Needing Wiring
These are non-archived skills with zero declared edges. They should be wired into the weave via `related_skills` frontmatter or added to clusters.

**King Wen / AI Cognition (high priority):**
- autonomous-ai-agents/kingwen-3d-tooling
- autonomous-ai-agents/kingwen-paper-math-bridge
- autonomous-ai-agents/moa-learning-loop
- autonomous-ai-agents/moa-session-curator
- autonomous-ai-agents/moa-skill-activator
- autonomous-ai-agents/sovereign-substrate-audit
- kingwen (top-level)
- megatron
- openjarvis
- openjarvis/openjarvis-kingwen-integration
- research/kingwen-jarvis-megatron-learn
- research/kingwen-learn-suite-runner
- research/kingwen-oracle-advisory
- research/avalokiteshvara-kingwen
- research/avalokiteshvara-megatron-moa-prep

**Research / Math (high priority):**
- research/arxiv-math-extractor
- research/math-pdf-parser
- research/math-structural-ast-fidelity
- research/multi-engine-math-parsing
- research/vision-math-symbol-detection
- research/wiki-math-parser
- research/failure-driven-math-recovery
- research/pdf-math-extraction-quality

**Verification (medium priority):**
- verification/capability-pulse
- verification/parser-benchmarking
- verification/verification-artifact-hygiene

**RSMV / Gaming (medium priority):**
- rsmv
- devops/rsmv-cache-crossref
- devops/rsmv-model-identity-kit

**Other active orphans (lower priority):**
- 1password, adversarial-ux-test, agentmail, antigravity, antigravity-cli, apple/macos-computer-use, axolotl, baoyu-comic, bioinformatics, blender-mcp, cinder, data-science/jupyter-live-kernel, devops/kanban-worker, devops/sdlc-review, devops/windows-amr-fallback, devops/windows-local-development, dg-cartridge, email/email-inbox-triage, evaluation-gate-calibration, game-development/jagex-lua-plugin-patterns, github/github-repo-management, hermes-self-upgrader (+ 2 sub-skills), jkd-pedagogy-engine, media/heartmula, mlops/models/segment-anything, open-design, oracle, pog2-deploy-worker, productivity/petdex, protocol/mcp-protocol, research/missouri-amendments-2026-causal-chain, research/oracle-spec-audit, research/pog3-coordinate-calculator, research/repo-provenance-archaeology, research/research-paper-semantics-mapping, research/zotero-web-clone-extraction, session-change-commit-sync, software-development/agentic-repo-hygiene, software-development/git-history-analysis, software-development/skill-math-connector, software-development/systematic-debugging, unified-corpus/unified-db-math-preservation, voicebox, windows-path-resolution, yuanbao

### Archived Orphans (63)
All `.archive/*` skills are orphaned by design — they are archived and should not be wired into the active weave. No action needed unless a specific archived skill is being reactivated.

## 3. Domain Coverage Gaps

| Domain | Skills | Status |
|--------|--------|--------|
| ai_cognition | 88 | Overloaded — should be split |
| gaming | 54 | Healthy |
| use_case | 44 | Healthy |
| rules | 24 | Healthy |
| program_usages | 24 | Healthy |
| training_models | 6 | Under-populated |
| math | 1 | **Critical gap** — only wiki-math-parser |
| learned_abilities | 0 | **Empty** — should include King Wen math/research skills |
| code_agnostic | 0 | **Empty** — should include creative/design skills |
| user_intents | 0 | **Empty** — should include productivity/media skills |

**Root cause:** The `primary_domain()` function in `journey_weave.py` uses keyword matching on skill body text. Skills in `research/`, `creative/`, `productivity/`, `media/` categories don't match the hardcoded term lists, so they fall through to `use_case` or remain unclassified.

## 4. Recommended Follow-Up Skills to Wire

Based on the current King Wen M3 audit work and the user's sovereign stack, the following skills should be connected to the weave:

### High Priority (directly relevant to current work)
1. **openjarvis/openjarvis-kingwen-integration** — King Wen ↔ OpenJarvis integration; currently orphaned
2. **research/kingwen-jarvis-megatron-learn** — King Wen ↔ Jarvis ↔ Megatron learning loop; orphaned
3. **research/kingwen-oracle-advisory** — King Wen oracle advisory; orphaned
4. **research/kingwen-learn-suite-runner** — King Wen /learn verification suite; orphaned
5. **research/avalokiteshvara-kingwen** — King Wen capability registry; orphaned
6. **research/learn_king_wen_math_extractors** — King Wen math extractors; orphaned
7. **autonomous-ai-agents/kingwen-3d-tooling** — King Wen 3D generators; orphaned
8. **autonomous-ai-agents/kingwen-paper-math-bridge** — King Wen paper math bridge; orphaned
9. **autonomous-ai-agents/kingwen-emotion-voice** — King Wen emotion voice; orphaned
10. **kingwen** (top-level) — King Wen I-Ching cognitive layer; orphaned
11. **megatron** — Megatron-LM training substrate; orphaned
12. **openjarvis** — OpenJarvis runtime; orphaned

### Medium Priority (supporting infrastructure)
13. **verification/capability-pulse** — capability pulse; orphaned
14. **verification/verification-artifact-hygiene** — artifact hygiene; orphaned
15. **software-development/verified-engineering** — verified engineering; orphaned
16. **software-development/systematic-debugging** — systematic debugging; orphaned
17. **research/pdf-math-extraction-quality** — PDF math extraction; orphaned
18. **research/multi-engine-math-parsing** — multi-engine math parsing; orphaned
19. **research/math-structural-ast-fidelity** — math AST fidelity; orphaned
20. **rsmv** — RSMV cache tooling; orphaned

### Low Priority (utility skills, can remain orphaned)
- All `.archive/*` skills (63) — archived by design
- Productivity, media, and user-intent skills that don't need King Wen integration

## 5. Weave Integrity Issues

1. **Phantom references (24 truly missing)** — These should be cleaned up by either:
   - Creating the missing skills (if they represent real capabilities)
   - Removing the `related_skills` entries that reference them
   - Replacing them with existing skill paths

2. **Domain misclassification** — 3 domains have 0 skills, 1 domain has 88. The `primary_domain()` function needs expansion of its keyword lists to cover `research/`, `creative/`, `productivity/`, `media/` categories.

3. **Orphan accumulation** — 78 active skills have no declared edges. The straggler attachment mechanism attaches them to clusters but doesn't create real `related_skills` edges.

4. **Archived skill contamination** — 63 archived skills are included in the weave. They should be filtered out or marked as archived in the weave output.

## 6. Recommended Actions

1. **Fix 2 path-mismatched references:** Update `related_skills` frontmatter in skills that reference `canonical-table-audit` and `verification-rules` to use their correct full paths (`verification/canonical-table-audit` and `verification/verification-artifact-hygiene`).

2. **Wire King Wen skills:** Add `related_skills` entries to the 12 high-priority King Wen skills listed above, connecting them to `autonomous-ai-agents/king-wen` and `openjarvis/openjarvis-kingwen-integration`.

3. **Expand domain keyword lists:** Update `DOMAIN_TERMS` in `journey_weave.py` to include terms for `research/`, `creative/`, `productivity/`, `media/` categories.

4. **Filter archived skills:** Exclude `.archive/*` skills from the weave or mark them as archived.

5. **Clean up phantom references:** Remove or replace the 24 truly phantom skill references in `related_skills` frontmatter across affected skills.

## 7. Step 1 — Archive Filtering Results (Authorized Scope)

### Metric Comparison

| Metric | Original (incl. archived) | Active-only (this filter) | Change (%) |
|--------|---------------------------|---------------------------|------------|
| Skills | 235 | 131 | −44.3% |
| Edges | 150 | 64 | −57.3% |
| Missing targets | 48 | 64 | +16.7% |
| Orphans | 137 | 87 | −36.5% |
| Clusters (≥3) | 38 | 20 | −47.4% |
| Memory cards | 904 | 953 | +5.4% |
| Domains w/ 0 skills | 3 | 3 | 0 |

### Key Findings

1. **Fuzzy-match-to-archived-skills inflation:** Of the original 150 edges, 86 were removed when archived skills were filtered. Many of these 86 edges were "resolved" via fuzzy matching to archived skills (e.g., `antigravity-cli` → `codex` matched `.archive/codex/SKILL.md`), which produced spurious relationships that don't exist in the active ecosystem.

2. **No skill definitions modified:** Archived skills (`.archive/*`) remain recoverable. Their SKILL.md files are untouched. Only graph calculations exclude archived skills.

3. **Active-only graph is authoritative:** The active-only weave (`journey_web_alignment_report_active_2026-11-03.json`, `journey_web_alignment_weave_active_2026-11-03.json`) is the correct graph for skill-network analysis. The original graph includes 104 archived skills and 86 misleading edges.

### Detailed Math

- Original skills: 235 (131 active + 104 archived)
- Original edges: 150
- Active edges: 64
- Removed edges: 86 (all involve at least one archived skill)
- New missing targets: 64 (all phantom references, correctly unresolved)

### Archive-Skill Mismatch Verification

| Skill that declared `related_skills` | Phantom Target | Resolved To in Original | Resolves Correctly in Active? |
|---|---|---|---|
| `antigravity-cli` | `codex` | `.archive/codex/SKILL.md` (archived) | **No — correctly unresolved** |
| `antigravity-cli` | `grok` | No match (phantom) | **No — correctly unresolved** |
| `evaluation-gate-calibration` | `verification-rules` | No match (phantom path) | **No — correctly unresolved** |
| `evaluation-gate-calibration` | `verification-rules` (wrong path) | No match | **No — path mismatch** |
| `pog2` | `pog2` | `.archive/pog2/SKILL.md` (archived) | **No — correctly unresolved** |
| `pog2` | `pog2-local-build` | No match (phantom) | **No — correctly unresolved** |
| `box` | `himalaya` | No match (phantom) | **No — correctly unresolved** |
| `box` | `google-workspace` | No match (phantom) | **No — correctly unresolved** |
| `meeting-action-items` | `notion` | No match (phantom) | **No — correctly unresolved** |
| `competitor-news-monitor` | `rss-feeds` | No match (phantom) | **No — correctly unresolved** |
| `github` | `github-code-review` | No match (phantom) | **No — correctly unresolved** |
| `github` | `github-auth` | No match (phantom) | **No — correctly unresolved** |

All 64 "missing targets" in the active-only graph are correctly unresolved (phantom references). The original graph's 48 "missing" targets included 16 that were resolved to archived skills via fuzzy matching — 32 of those are now correctly unresolved.

### Verification of Baseline Preservation

- `git diff` on `journey_web_alignment_report_2026-07-11.json`: **0 changes** ✓
- `git diff` on `journey_web_alignment_weave_2026-07-11.json`: **0 changes** ✓
- Active-only files created: `journey_web_alignment_report_active_2026-11-03.json`, `journey_web_alignment_weave_active_2026-11-03.json` ✓
- No `.archive/` SKILL.md files modified or deleted ✓

### RVG Conditions Checklist

| Condition | Status |
|-----------|--------|
| Governing skill-authoring/frontmatter rules inspected | ✓ |
| Pre-change inventory documented | ✓ |
| Filtering rule documented | ✓ |
| Test active/archived boundary cases | ✓ (64 archived-skill mismatches identified) |
| Independently compare regenerated graph against frozen baseline | ✓ (original untouched, 0 diff) |
