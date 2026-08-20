from pathlib import Path
import json, re
from collections import defaultdict

root = Path(__file__).resolve().parent.parent
chunks_path = Path('C:/Users/krist/Desktop/zotero/learning-corpus/paper_chunks_solutions_issues.jsonl')
expansion_path = root / 'kingwen_train_data' / 'full_shotgun_expansion_all.jsonl'
out_path = root / 'kingwen_train_data' / 'full_shotgun_expansion_corpus_enriched.jsonl'

# Load expansion records first to extract keywords
expansion = []
with expansion_path.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            expansion.append(json.loads(line))

print(f'expansion records: {len(expansion)}')

# Build keyword profile for each expansion record
def profile_from_expansion(rec):
    lp = rec.get('label_payload', {})
    cat = str(lp.get('category', '')).lower()
    action = str(lp.get('action', '')).lower()
    intent = lp.get('intent', {})
    if isinstance(intent, dict):
        dominant = str(intent.get('dominant_intent', '')).lower()
        intent_text = ' '.join(str(v) for v in intent.values() if isinstance(v, str)).lower()
    else:
        dominant = str(intent).lower()
        intent_text = dominant
    tool_map = lp.get('tool_native_map', {})
    tools = ' '.join(str(v).lower() for v in tool_map.values() if isinstance(v, str))
    skills = ' '.join(str(s).lower() for s in lp.get('skill_cards', []))
    training = str(lp.get('training_notes', '')).lower()
    phase = str(lp.get('phase_temporal', '')).lower()
    text = str(lp.get('request_text', '') or lp.get('text', '')).lower()
    return set(re.findall(r'[a-z]{3,}', cat + ' ' + action + ' ' + dominant + ' ' + intent_text + ' ' + tools + ' ' + skills + ' ' + training + ' ' + phase + ' ' + text))

profiles = [profile_from_expansion(r) for r in expansion]

# Build chunk keyword index
chunk_keywords = []
with chunks_path.open('r', encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        txt = rec.get('text', '').lower()
        words = set(re.findall(r'[a-z]{3,}', txt))
        chunk_keywords.append((rec, words))

print(f'chunks indexed: {len(chunk_keywords)}')

# Enrich each expansion record
enriched = 0
for rec, profile in zip(expansion, profiles):
    lp = rec.setdefault('label_payload', {})
    
    scored = []
    for ch, words in chunk_keywords:
        overlap = len(profile & words)
        if overlap:
            scored.append((overlap, ch))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    matches = [ch for _, ch in scored[:20]]
    
    evidence = []
    seen_texts = set()
    for ch in matches:
        txt = ch.get('text', '').strip()
        if txt and txt not in seen_texts:
            evidence.append({
                'category': ch.get('category'),
                'label': ch.get('labels', [None])[0],
                'paper_id': ch.get('paper_id'),
                'file': ch.get('file'),
                'text': txt[:500],
            })
            seen_texts.add(txt)
    
    evidence_summary = []
    for ev in evidence[:8]:
        evidence_summary.append(f"[{ev['label']}] {ev['text'][:180]}")
    
    if evidence_summary:
        lp['corpus_evidence'] = evidence
        lp['training_notes'] = '\n'.join(evidence_summary[:6])
        lp['corpus_evidence_count'] = len(evidence)
        lp['corpus_source'] = 'paper_chunks_solutions_issues.jsonl'
        enriched += 1

with out_path.open('w', encoding='utf-8') as f:
    for rec in expansion:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f'enriched records: {enriched}/{len(expansion)}')
print('wrote', out_path)
print('size MB:', round(out_path.stat().st_size / 1024 / 1024, 2))
