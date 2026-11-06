import json

with open("DATASETS/arxiv_html_corpus/2102.03334.json", encoding="utf-8") as f:
    d = json.load(f)

print("Title:", d.get("title"))
eqs = d.get("equations", [])
print(f"Total equations: {len(eqs)}")

# Look for equations mentioning 't_class' or 'v_class' or 'MSA' or 'tanh'
for i, eq in enumerate(eqs):
    ltx = eq.get("latex", "")
    if any(k in ltx for k in ["class", "MSA", "MLP", "tanh", "LN"]):
        print(f"eq index {i}: id={eq.get('id')} type={eq.get('type')}")
        print(f"  latex: {repr(ltx[:100])}")

