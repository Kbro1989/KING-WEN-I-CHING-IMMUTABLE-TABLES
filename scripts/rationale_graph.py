"""
Rationale Graph Extractor
=========================
Theory papers are not problem sets. They are DECISION-RATIONALE GRAPHS:

    if we want <goal>
      -> <math> is expressed
      -> because <reason>
      -> therefore <math B> is needed
      -> and in relation to <math B>, <math C> ...

This module extracts that graph instead of forcing every equation to be solvable.

Nodes:
  equation   : a numbered display equation, with its recovered expression
  goal       : a stated aim ("we want", "in order to", "to achieve")
  reason     : a stated justification ("because", "since", "therefore")

Edges:
  references : equation A cites equation B via "(N)" in its surrounding prose
  motivates  : a goal sentence introduces an equation
  justifies  : a reason sentence explains an equation
  follows    : an equation begins with '=' (continues the previous)

Output is a JSON graph per paper: nodes + edges + per-equation context.

No solving is required. Solving is an OPTIONAL annotation on a node.
"""
import re, json, sys


GOAL_MARKERS = [
    "we want", "we need", "we wish", "in order to", "to achieve", "to obtain",
    "our goal", "we aim", "the objective", "we seek", "to address",
    "we propose", "we introduce", "we define", "we consider",
]
REASON_MARKERS = [
    "because", "since", "therefore", "thus", "hence", "this ensures",
    "it follows", "as a result", "consequently", "which implies",
    "allows us", "enables", "motivates", "due to", "owing to",
]
NEED_MARKERS = [
    "is needed", "are needed", "is required", "are required", "we require",
    "necessary", "must be", "cannot be", "is essential",
]


def _sentences(text):
    """Split prose into sentences, keeping them intact."""
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if len(p.strip()) > 12]


def _classify(sentence):
    """Classify a prose sentence by rationale role."""
    low = sentence.lower()
    roles = []
    if any(m in low for m in GOAL_MARKERS):
        roles.append("goal")
    if any(m in low for m in REASON_MARKERS):
        roles.append("reason")
    if any(m in low for m in NEED_MARKERS):
        roles.append("need")
    return roles


def _refs_in(sentence):
    """Equation numbers referenced by a sentence: '(3)', 'Eq. (3)', 'Eqs. 3, 4'."""
    found = set()
    for m in re.finditer(r"\((\d+)\)", sentence):
        found.add(int(m.group(1)))
    for m in re.finditer(r"\bEq(?:uation|s)?\.?\s*\(?(\d+)\)?", sentence):
        found.add(int(m.group(1)))
    for m in re.finditer(r"\bEqs?\.?\s*(\d+)\s*(?:and|,)\s*(\d+)", sentence):
        found.add(int(m.group(1)))
        found.add(int(m.group(2)))
    return found


def build_rationale_graph(html, arxiv_id=None):
    """
    Build the decision-rationale graph for one paper.

    Returns dict with nodes, edges, and stats.
    """
    from bs4 import BeautifulSoup
    from mathml_parser import MathMLParser
    from display_equation_extractor import parse_display_equations

    soup = BeautifulSoup(html, "html.parser")

    # --- equation nodes (numbered display equations)
    parsed = parse_display_equations(html, MathMLParser)

    # Join continuation rows (a row starting with '=' continues the previous)
    rows = []
    last = None
    for r in parsed:
        e = r.get("expr")
        if not e:
            continue
        if e.lstrip().startswith("=") and last is not None:
            last["expr"] += e
            last["continues"] = True
            continue
        r["continues"] = False
        rows.append(r)
        last = r

    eq_nodes = {}
    for r in rows:
        num = None
        if r.get("eqno"):
            m = re.search(r"(\d+)", r["eqno"])
            if m:
                num = int(m.group(1))
        key = f"eq{num}" if num else f"eqrow{r.get('group_id')}_{r.get('row_index')}"
        eq_nodes[key] = {
            "type": "equation",
            "number": num,
            "expr": r["expr"],
            "group_id": r.get("group_id"),
            "row_index": r.get("row_index"),
            "is_multiline_group": r.get("is_multiline_group", False),
            "continues_previous": r.get("continues", False),
            "section": None,
        }

    # --- section context: which section does each equation live in?
    for m in soup.find_all("math"):
        ann = m.find("annotation")
        if not ann:
            continue
        # walk up to the nearest section heading
        sec = m.find_previous(["h1", "h2", "h3"])
        if sec:
            label = sec.get_text(" ", strip=True)[:80]
            p = MathMLParser()
            e, _ = p.parse(m)
            if e:
                for k, node in eq_nodes.items():
                    if node["expr"] and node["expr"][:40] == e[:40]:
                        node["section"] = label
                        break

    # --- prose nodes: goal / reason / need sentences, with their refs
    prose_nodes = []
    edges = []
    text_blocks = soup.find_all(["p", "div"], class_=lambda c: (
        isinstance(c, str) and ("ltx_p" in c or "ltx_para" in c)))
    if not text_blocks:
        text_blocks = soup.find_all("p")

    for bi, block in enumerate(text_blocks):
        txt = block.get_text(" ", strip=True)
        if len(txt) < 20:
            continue
        for sent in _sentences(txt):
            roles = _classify(sent)
            if not roles:
                continue
            refs = _refs_in(sent)
            node_id = f"prose{bi}_{len(prose_nodes)}"
            prose_nodes.append({
                "type": "prose",
                "id": node_id,
                "roles": roles,
                "text": sent[:400],
                "refs": sorted(refs),
            })
            # edges: this rationale sentence relates to the equations it cites
            for r in sorted(refs):
                edges.append({
                    "from": node_id,
                    "to": f"eq{r}",
                    "relation": "goal_of" if "goal" in roles else
                                ("justifies" if "reason" in roles else "requires"),
                })

    # --- structural edges: continuation
    prev_key = None
    for k, node in eq_nodes.items():
        if node["continues_previous"] and prev_key:
            edges.append({"from": prev_key, "to": k, "relation": "continues"})
        prev_key = k

    # --- dependency edges inferred from symbol reuse
    #   if equation B uses symbols introduced by equation A, B depends on A
    def idents(expr):
        return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or ""))
    keys = list(eq_nodes)
    for i, a in enumerate(keys):
        sa = idents(eq_nodes[a]["expr"])
        for b in keys[i + 1:]:
            sb = idents(eq_nodes[b]["expr"])
            shared = sa & sb
            # ignore very common single letters
            shared = {s for s in shared if len(s) > 1}
            if len(shared) >= 2:
                edges.append({
                    "from": a, "to": b, "relation": "shares_symbols",
                    "symbols": sorted(shared)[:6],
                })

    # --- optional solve annotation (does NOT gate inclusion)
    try:
        from math_recovery_tool import solve_recovered
        for k, node in eq_nodes.items():
            ok, sol, err, v, triv = solve_recovered(node["expr"], original=node["expr"])
            node["solvable"] = ok
            node["solution"] = sol if ok else None
            node["solve_error"] = err
    except Exception as e:
        for node in eq_nodes.values():
            node["solvable"] = None
            node["solve_error"] = f"annotate_failed:{type(e).__name__}"

    # --- section skeleton
    sections = []
    for h in soup.find_all(["h1", "h2", "h3"]):
        t = h.get_text(" ", strip=True)
        if t:
            sections.append({"level": h.name, "title": t[:120]})

    graph = {
        "arxiv_id": arxiv_id,
        "nodes": list(eq_nodes.values()) + prose_nodes,
        "edges": edges,
        "sections": sections,
        "stats": {
            "equations": len(eq_nodes),
            "numbered": sum(1 for n in eq_nodes.values() if n["number"]),
            "prose_rationale_sentences": len(prose_nodes),
            "edges": len(edges),
            "edges_by_relation": {},
            "solvable": sum(1 for n in eq_nodes.values() if n.get("solvable")),
        },
    }
    for e in edges:
        r = e["relation"]
        graph["stats"]["edges_by_relation"][r] = \
            graph["stats"]["edges_by_relation"].get(r, 0) + 1

    return graph


if __name__ == "__main__":
    import urllib.request

    aid = sys.argv[1] if len(sys.argv) > 1 else "2006.11239"
    url = f"https://arxiv.org/html/{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": "rationale/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

    g = build_rationale_graph(html, aid)
    print(f"RATIONALE GRAPH for {aid}")
    print("=" * 70)
    print(f"  equations              : {g['stats']['equations']}")
    print(f"  numbered               : {g['stats']['numbered']}")
    print(f"  prose rationale nodes  : {g['stats']['prose_rationale_sentences']}")
    print(f"  edges                  : {g['stats']['edges']}")
    print(f"  edges by relation      : {g['stats']['edges_by_relation']}")
    print(f"  solvable (annotation)  : {g['stats']['solvable']}")
    print()
    print("  SAMPLE GOAL / REASON NODES:")
    shown = 0
    for n in g["nodes"]:
        if n["type"] == "prose":
            print(f"   [{','.join(n['roles'])}] {n['text'][:110]}")
            print(f"        refs -> {n['refs']}")
            shown += 1
            if shown >= 8:
                break
    print()
    print("  SAMPLE DEPENDENCY EDGES (symbol reuse):")
    shown = 0
    for e in g["edges"]:
        if e["relation"] == "shares_symbols":
            print(f"   {e['from']} -> {e['to']}  via {e['symbols']}")
            shown += 1
            if shown >= 6:
                break
