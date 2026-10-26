"""Cross-artifact consistency checks for the Pix2Text adjudication pipeline.

Run: cd C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
     python3 scripts/test_adjudication_consistency.py

Verifies:
  1. record identity and count equality across
     pix2text_candidates.jsonl, adjudication_report.jsonl, adjudication_targets.jsonl
  2. carry-forward status preservation (L3 status == L2 status for explicit records)
  3. newly adjudicated records were UNADJUDICATED in L2
  4. detail counts divide with explicit denominators
  5. Layer-2 summary numbers (unique/equation) are consistent with the layer-2 source
"""
import json
import sys

ROOT = 'C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES'
R = ROOT + '\\DATASETS\\PDF_FIDELITY_RENDERINGS\\1907_04931'

FAILS = []


def load(name):
    p = R + '/' + name
    out = []
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def check(name, cond, detail=''):
    if cond:
        print(f'  PASS: {name}')
    else:
        print(f'  FAIL: {name} {detail}')
        FAILS.append(name)


def main():
    print('Cross-artifact consistency verification for 1907.04931')
    print('=' * 60)

    pdf = load('pix2text_candidates.jsonl')
    l2 = load('adjudication_report.jsonl')
    l3 = load('adjudication_targets.jsonl')
    s2 = json.load(open(R + '/adjudication_summary.json', encoding='utf-8'))
    s3 = json.load(open(R + '/adjudication_targets_summary.json', encoding='utf-8'))

    # 1. record identity and count
    print('\n1. record identity / count')
    check('candidates records == 158', len(pdf) == 158, f'got {len(pdf)}')
    check('L2 records == 158', len(l2) == 158, f'got {len(l2)}')
    check('L3 records == 158', len(l3) == 158, f'got {len(l3)}')
    check('candidate element-ids unique',
          len({r['pix2text_element_id'] for r in pdf}) == len(pdf))
    for name, recs in [('l2', l2), ('l3', l3)]:
        n = len({r['pix2text_element_id'] for r in recs})
        check(f'{name} element-ids unique (no dupes)', n == len(recs), f'{n} unique / {len(recs)}')

    # 2. carry-forward status preservation
    print('\n2. carry-forward status preservation')
    l2map = {r['pix2text_element_id']: r['match_status'] for r in l2}
    l3map = {r['pix2text_element_id']: r['match_status'] for r in l3}
    cf_ok = all(l3map[e] == st for e, st in l2map.items()
                if st in ('VISUALLY_VERIFIED', 'SPATIAL_MATCH', 'TEXT_MATCH')
                and e in l3map)
    check('carry-forward statuses preserved', cf_ok, 'L3 must equal L2 for explicit records')

    # 3. newly adjudicated were UNADJUDICATED in L2
    print('\n3. newly adjudicated came from UNADJUDICATED')
    l3_ad = [eid for eid, st in l3map.items() if st == 'ADJUDICATED']
    newly_from_unadj = all(l2map[eid] == 'UNADJUDICATED' for eid in l3_ad if eid in l2map)
    check('all ADJUDICATED came from UNADJUDICATED', newly_from_unadj)

    # 4. detail counts with explicit denominators
    print('\n4. detail denominators')
    nd = s3['newly_adjudicated_detail_distribution']
    expected_total = sum(nd.values())
    check('newly-adjudicated detail counts sum to newly count',
          expected_total == s3['newly_adjudicated_count'],
          f'{expected_total} vs {s3["newly_adjudicated_count"]}')
    cf = s3['carried_forward_detail_distribution']
    check('carried-forward detail counts sum to carried-forward count',
          sum(cf.values()) == s3['carried_forward_count'],
          f'{sum(cf.values())} vs {s3["carried_forward_count"]}')
    check('status_distribution denominator == total_records',
          s3['status_distribution_denominator'] == s3['total_records'])

    # 5. Layer-2 unique/equation counts
    print('\n5. Layer-2 counts (reference)')
    check('L2 unique_expression_count == 137',
          s2.get('unique_expression_count') == 137, f"got {s2.get('unique_expression_count')}")
    check('L2 equation_occurrence_count == 95',
          s2.get('equation_occurrence_count') == 95, f"got {s2.get('equation_occurrence_count')}")

    print('\n' + ('ALL CHECKS PASSED' if not FAILS else f'{len(FAILS)} CHECK(S) FAILED'))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
