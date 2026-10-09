#!/usr/bin/env python3
"""
ROOM 5 — TYPED INTEGRAL IR

Target:
    Integral(
        body     = Application(phi, z),
        limits   = {lower: alpha, upper: infinity},
        measure  = Differential(z),
    )

The acceptance criteria (from external audit):
  1. Independent fields: integrand, lower, upper, differential separate
  2. Scope preservation: z in dz is the INTEGRATION VARIABLE, not appended
  3. Nested expression safety:  \\int_a^b f(g(z)) dz  preserves nesting
  4. Limit variation: definite, indefinite, lower-only, upper-only
  5. Conservation: every source occurrence represented
  6. Honest fallback: unsupported forms give partial/failure, NEVER a
     fabricated complete integral
  7. Regression: structural, nested-arg, relation-identity, mbox-dollar intact

Key point: `dz` must be attached to a typed Differential node — character
presence in the output string cannot establish that relationship.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# TYPED IR
# ─────────────────────────────────────────────────────────────────────────

class Node:
    def __init__(self, kind, **fields):
        self.kind = kind
        self.fields = fields

    def to_dict(self):
        out = {"kind": self.kind}
        for k, v in self.fields.items():
            if isinstance(v, Node):
                out[k] = v.to_dict()
            elif isinstance(v, list):
                out[k] = [x.to_dict() if isinstance(x, Node) else x for x in v]
            elif isinstance(v, dict):
                out[k] = {kk: (vv.to_dict() if isinstance(vv, Node) else vv)
                          for kk, vv in v.items()}
            else:
                out[k] = v
        return out

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


def Differential(variable):
    return Node("Differential", variable=variable)


def Integral(body, lower, upper, measure):
    return Node("Integral",
                body=body,
                limits={"lower": lower, "upper": upper},
                measure=measure)


# ─────────────────────────────────────────────────────────────────────────
# MathML -> typed Integral
# ─────────────────────────────────────────────────────────────────────────

from mathml_parser import MathMLParser  # noqa: E402


def parse_integral(mml: str):
    """
    Parse MathML containing an integral into the typed IR.

    Returns (node, notes). `notes` records honest fallbacks — a partial
    structure is reported as partial, never as a complete integral.
    """
    notes = []
    soup = BeautifulSoup(mml, "html.parser")
    math = soup.find("math")
    if math is None:
        return None, ["no_math_tag"]

    # locate the integral operator node (msubsup / munderover over ∫)
    integ = None
    bare = False
    for tag in math.find_all(["msubsup", "munderover", "msub", "munder"]):
        kids = [c for c in tag.find_all(recursive=False)]
        if not kids:
            continue
        op = kids[0].get_text(strip=True)
        if op in ("∫", "∮", "∬", "∭"):
            integ = tag
            break

    if integ is None:
        # BARE integral: <mo>∫</mo> with no script wrapper (indefinite).
        for mo in math.find_all("mo"):
            if mo.get_text(strip=True) in ("∫", "∮", "∬", "∭"):
                integ = mo
                bare = True
                break

    if integ is None:
        return None, ["no_integral_operator"]

    if bare:
        # no limits exist at all — this is an indefinite integral, not a defect
        lower = upper = None
        kids = []
        integ_name = "bare"
    else:
        kids = [c for c in integ.find_all(recursive=False)]
        integ_name = integ.name
    p = MathMLParser()

    lower = upper = None
    if integ_name == "bare":
        pass
    elif integ.name in ("msubsup", "munderover"):
        if len(kids) >= 3:
            lower = p._walk(kids[1])
            upper = p._walk(kids[2])
        else:
            notes.append("integral_arity_partial")
    elif integ.name in ("msub", "munder"):
        if len(kids) >= 2:
            lower = p._walk(kids[1])
        else:
            notes.append("integral_arity_partial")

    # everything AFTER the operator node is the integrand + differential
    tail = []
    for sib in integ.next_siblings:
        if getattr(sib, "name", None):
            tail.append(sib)
    if not tail and integ.parent is not None:
        # <mo> may be inside an <mrow>; take siblings within that parent
        for sib in integ.next_siblings:
            if getattr(sib, "name", None):
                tail.append(sib)

    # find the differential: a 'd' token followed by the integration variable
    diff_var = None
    body_parts = []
    i = 0
    while i < len(tail):
        el = tail[i]
        txt = el.get_text(strip=True)
        # a differential is d / 𝑑 immediately followed by a variable
        if txt in ("d", "𝑑", "ⅆ", "ⅅ", "\\mathrm{d}"):
            # the next element is the integration variable
            if i + 1 < len(tail):
                nxt = tail[i + 1]
                ntxt = nxt.get_text(strip=True)
                if ntxt and re.fullmatch(r"[A-Za-z]", ntxt):
                    diff_var = p._walk(nxt)
                    i += 2
                    continue
                notes.append("differential_without_variable")
                i += 1
                continue
            notes.append("differential_at_end")
            i += 1
            continue
        body_parts.append(p._walk(el))
        i += 1

    body = "".join(x for x in body_parts if x)

    if diff_var is None:
        # HONEST FALLBACK — do not fabricate a complete integral
        notes.append("measure_missing")
        measure = None
    else:
        measure = Differential(diff_var)

    node = Integral(body=body, lower=lower, upper=upper, measure=measure)
    return node, notes


# ─────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────

FIXTURES = [
    # (label, mathml, expected_fields, forbidden)
    (
        "definite with differential",
        '<math><msubsup><mo>∫</mo><mi>α</mi><mi>∞</mi></msubsup>'
        '<mi>φ</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>𝑑</mi><mi>z</mi></math>',
        {"lower": "alpha", "upper": "oo", "variable": "z"},
        # dz must NOT be fused into the body
        ["phi(z)dz", "phi(z)d"],
    ),
    (
        "nested application",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>g</mi><mo>(</mo><mi>z</mi><mo>)</mo><mo>)</mo>'
        '<mi>d</mi><mi>z</mi></math>',
        {"lower": "a", "upper": "b", "variable": "z"},
        ["f(g(z))dz"],
    ),
    (
        "indefinite (no limits)",
        '<math><mo>∫</mo><mi>φ</mi><mo>(</mo><mi>z</mi><mo>)</mo>'
        '<mi>d</mi><mi>z</mi></math>',
        {"lower": None, "upper": None, "variable": "z"},
        ["phi(z)dz"],
    ),
    (
        "lower-only",
        '<math><msub><mo>∫</mo><mi>a</mi></msub>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>d</mi><mi>z</mi></math>',
        {"lower": "a", "upper": None, "variable": "z"},
        [],
    ),
    (
        "no differential (must be flagged, not fabricated)",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo></math>',
        {"lower": "a", "upper": "b", "variable": None},
        [],
    ),
]

print("=" * 84)
print("ROOM 5 — TYPED INTEGRAL IR")
print("=" * 84)
print()

passed = failed = 0
for label, mml, expect, forbidden in FIXTURES:
    node, notes = parse_integral(mml)
    d = node.to_dict() if node else {}
    lim = d.get("limits", {}) or {}
    meas = d.get("measure") or {}
    body = d.get("body", "")

    checks = []
    # 1. independent fields
    checks.append(("limits dict present", isinstance(d.get("limits"), dict)))
    # 2. lower / upper
    checks.append((f"lower={expect['lower']}", lim.get("lower") == expect["lower"]))
    checks.append((f"upper={expect['upper']}", lim.get("upper") == expect["upper"]))
    # 3. differential is a TYPED node, not a substring
    if expect["variable"] is None:
        checks.append(("measure absent (honest)", meas == {} or meas is None))
    else:
        checks.append((f"measure is Differential({expect['variable']})",
                       meas.get("kind") == "Differential"
                       and meas.get("variable") == expect["variable"]))
    # 4. forbidden fusions
    for f in forbidden:
        checks.append((f"NOT fused: {f}", f not in str(body)))

    ok = all(c[1] for c in checks)
    if ok:
        passed += 1
    else:
        failed += 1

    mark = "ok  " if ok else "FAIL"
    print(f"  {mark} {label}")
    print(f"       body    : {body!r}")
    print(f"       limits  : {lim}")
    print(f"       measure : {meas}")
    if notes:
        print(f"       notes   : {notes}")
    if not ok:
        for c, r in checks:
            if not r:
                print(f"       !! {c}")
    print()

print("=" * 84)
print(f"RESULT: {passed}/{len(FIXTURES)} integral IR fixtures pass")
print("=" * 84)
sys.exit(1 if failed else 0)
