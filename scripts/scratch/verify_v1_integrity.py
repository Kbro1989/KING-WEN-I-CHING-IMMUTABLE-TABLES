import hashlib, json
from pathlib import Path

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

ROOT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

spec_path = ROOT / 'DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json'
spec_sha = sha256_file(spec_path)
with open(spec_path, encoding='utf-8') as f:
    spec = json.load(f)
print('SPEC SHA-256:', spec_sha)
print('SPEC identifier:', spec.get('spec_identifier'))
print('SPEC created_at:', spec.get('created_at'))
print('SPEC engine baseline sha:', spec.get('immutable_engine_baseline', {}).get('engine_sha256'))

engine_path = ROOT / 'scripts/delimiter_aware_structural_recovery.py'
engine_sha = sha256_file(engine_path)
print()
print('ENGINE SHA-256:', engine_sha)

reg_path = ROOT / 'DATASETS/structural_preservation/cross_paper_case_registry_v1.json'
reg_sha = sha256_file(reg_path)
with open(reg_path, encoding='utf-8') as f:
    reg = json.load(f)
print()
print('REGISTRY SHA-256:', reg_sha)
print('REGISTRY status:', reg.get('status'))

eval_path = ROOT / 'DATASETS/structural_preservation/cross_paper_generalization_evaluation_v1.json'
eval_sha = sha256_file(eval_path)
with open(eval_path, encoding='utf-8') as f:
    report = json.load(f)
print()
print('EVAL REPORT SHA-256:', eval_sha)
print('EVAL cases:', len(report['case_evaluations']))
for c in report['case_evaluations']:
    cid = c['case_id']
    verdict = c['terminal_verdict']
    dims = list(c['five_dimension_results'].keys())
    ncs = [n['control_id'] for n in c['negative_control_results']]
    print('  ' + cid + ': verdict=' + verdict + ' dims=' + str(len(dims)) + ' ncs=' + str(len(ncs)))
print('EVAL inputs engine sha:', report['evaluation_inputs']['delimiter_engine_baseline']['sha256'])
print('EVAL inputs spec sha:', report['evaluation_inputs']['specification']['sha256'])
print('EVAL inputs registry sha:', report['evaluation_inputs']['case_registry']['sha256'])

