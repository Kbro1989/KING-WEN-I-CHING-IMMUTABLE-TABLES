import sys, json, urllib.request
sys.path.insert(0, 'scripts')
from rationale_graph import build_rationale_graph

AIDS = ["2006.11239", "2605.28896", "2605.18130", "2605.25334", "2102.03334"]

rows = []
for aid in AIDS:
    try:
        url = f"https://arxiv.org/html/{aid}"
        req = urllib.request.Request(url, headers={"User-Agent": "rationale/1.0"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        g = build_rationale_graph(html, aid)
        s = g["stats"]
        rows.append((aid, s["equations"], s["numbered"],
                     s["prose_rationale_sentences"], s["edges"],
                     s["edges_by_relation"].get("justifies", 0),
                     s["edges_by_relation"].get("goal_of", 0),
                     s["edges_by_relation"].get("shares_symbols", 0),
                     s["solvable"]))
    except Exception as e:
        print(f"{aid}: FAILED {type(e).__name__}: {e}")

print(f"{'paper':12s} {'eq':>4s} {'num':>4s} {'prose':>6s} {'edges':>6s} "
      f"{'just':>5s} {'goal':>5s} {'symdep':>7s} {'solve':>6s}")
print("-" * 70)
for r in rows:
    print(f"{r[0]:12s} {r[1]:4d} {r[2]:4d} {r[3]:6d} {r[4]:6d} "
          f"{r[5]:5d} {r[6]:5d} {r[7]:7d} {r[8]:6d}")
if rows:
    print("-" * 70)
    print(f"{'TOTAL':12s} {sum(r[1] for r in rows):4d} {sum(r[2] for r in rows):4d} "
          f"{sum(r[3] for r in rows):6d} {sum(r[4] for r in rows):6d} "
          f"{sum(r[5] for r in rows):5d} {sum(r[6] for r in rows):5d} "
          f"{sum(r[7] for r in rows):7d} {sum(r[8] for r in rows):6d}")
