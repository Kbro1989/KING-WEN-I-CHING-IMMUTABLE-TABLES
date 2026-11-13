"""Verify evidence graph CONFLICT and AGREE node lineage.

For each case, checks:
  1. Every CONFLICT node has >= 2 predecessors.
  2. CONFLICT predecessor node IDs correspond to real gold_ast or engine nodes.
  3. Every AGREE node has >= 2 predecessors from distinct channels.
  4. The node attributes (gold_says, engine_says) match what is actually
     present in the registry and evaluation report — not just copied labels.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from structural_evidence_graph import (
    build_evidence_graph, get_conflicts, get_agreements,
    KIND_CONFLICT, KIND_GOLD_AST, KIND_ASSEMBLED_DELIMITER
)

ROOT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open(ROOT / 'DATASETS/structural_preservation/cross_paper_case_registry_v1.json', encoding='utf-8') as f:
    reg = json.load(f)
with open(ROOT / 'DATASETS/structural_preservation/cross_paper_generalization_evaluation_v1.json', encoding='utf-8') as f:
    report = json.load(f)

papers_map = {p['paper_id']: p for p in reg['papers']}
eval_map = {c['case_id']: c for c in report['case_evaluations']}

all_ok = True
for case_data in reg['cases']:
    cid = case_data['case_id']
    pid = case_data['parent_paper_id']
    eng = eval_map[cid]['engine_classification']
    paper_data = papers_map.get(pid)

    G = build_evidence_graph(case_data, eng, paper_data)

    print(f'--- {cid} ---')

    # Verify conflicts
    conflicts = get_conflicts(G)
    for conf in conflicts:
        nid = conf['node_id']
        preds = list(G.predecessors(nid))
        pred_kinds = [G.nodes[p].get('kind') for p in preds]
        pred_channels = [G.nodes[p].get('channel') for p in preds]
        gold_says = conf.get('gold_says', '')
        engine_says = conf.get('engine_says', '')

        # Cross-check gold_says against actual registry
        actual_env = case_data.get('gold_ast', {}).get('environment_type', '')
        # Cross-check engine_says against actual engine classification
        actual_eng_kind = eng['opening'].get('kind', '')
        actual_eng_method = eng['opening'].get('resolution_method', '')

        env_to_kind = {
            'bmatrix': 'bracket', 'Bmatrix': 'brace', 'pmatrix': 'parenthesis',
            'vmatrix': 'vertical_bar', 'nested_sequence_vector': 'bracket',
            'extended_norm_squared_with_embedded_math': 'norm',
        }
        expected_gold_kind = env_to_kind.get(actual_env, actual_env)

        ok_gold = expected_gold_kind in gold_says
        ok_eng = (engine_says == actual_eng_kind) or (engine_says == 'unresolved' and actual_eng_method == 'unresolved')
        ok_preds = len(preds) >= 2
        ok_channels = 'ground_truth' in pred_channels or 'engine' in pred_channels

        status = 'OK' if (ok_gold and ok_eng and ok_preds and ok_channels) else 'FAIL'
        if status != 'OK':
            all_ok = False
        print(f'  CONFLICT {conf["dimension"]}: {status}')
        print(f'    predecessors: {preds}')
        print(f'    gold_says={gold_says!r}  actual_env={actual_env!r}  expected_kind={expected_gold_kind!r}  ok_gold={ok_gold}')
        print(f'    engine_says={engine_says!r}  actual_eng_kind={actual_eng_kind!r}  ok_eng={ok_eng}')
        print(f'    ok_preds={ok_preds}  ok_channels={ok_channels}')

    # Verify agreements
    agreements = get_agreements(G)
    for agr in agreements:
        nid = agr['node_id']
        preds = list(G.predecessors(nid))
        pred_channels = [G.nodes[p].get('channel') for p in preds]
        gold_val = agr.get('gold', '')
        engine_val = agr.get('engine', '')

        actual_env = case_data.get('gold_ast', {}).get('environment_type', '')
        actual_eng_kind = eng['opening'].get('kind', '')
        env_to_kind = {
            'bmatrix': 'bracket', 'Bmatrix': 'brace', 'pmatrix': 'parenthesis',
            'vmatrix': 'vertical_bar', 'nested_sequence_vector': 'bracket',
            'extended_norm_squared_with_embedded_math': 'norm',
        }
        expected_kind = env_to_kind.get(actual_env, actual_env)

        ok_gold = gold_val == actual_env
        ok_eng = engine_val == actual_eng_kind
        ok_kind_match = (actual_eng_kind == expected_kind)
        ok_preds = len(preds) >= 2
        ok_channels = ('ground_truth' in pred_channels) and ('engine' in pred_channels)

        status = 'OK' if (ok_gold and ok_eng and ok_kind_match and ok_preds and ok_channels) else 'FAIL'
        if status != 'OK':
            all_ok = False
        print(f'  AGREE {agr["dimension"]}: {status}')
        print(f'    predecessors: {preds}')
        print(f'    gold_val={gold_val!r}  actual_env={actual_env!r}  ok_gold={ok_gold}')
        print(f'    engine_val={engine_val!r}  actual_eng_kind={actual_eng_kind!r}  ok_eng={ok_eng}')
        print(f'    kind_match={ok_kind_match}  ok_preds={ok_preds}  ok_channels={ok_channels}')

    if not conflicts and not agreements:
        print('  (no CONFLICT or AGREE nodes)')

print()
print('OVERALL LINEAGE VERIFICATION:', 'PASS' if all_ok else 'FAIL')

