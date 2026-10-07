"""
Display Equation Extractor
==========================
arxiv HTML structure for display (complete) equations:

  <table class="ltx_equationgroup ltx_eqn_align ltx_eqn_table">
    <tr class="ltx_equation ltx_eqn_row ltx_align_baseline">     <- ONE display equation
      <td class="ltx_eqn_cell ltx_eqn_center_padleft"></td>
      <td class="ltx_eqn_cell"> ...math... </td>                  <- the formula body
      <td class="ltx_eqn_cell ltx_eqn_eqno">(3)</td>              <- equation number
    </tr>
  </table>

Key facts learned from live inspection:
  - <math display="..."> is ALWAYS "inline" in arxiv HTML (useless as a signal)
  - The real signal is the ancestor <tr class="ltx_equation"> / "ltx_eqn_row"
  - Multi-line systems share a parent <table class="ltx_equationgroup">
  - The equation number lives in td.ltx_eqn_eqno

This module extracts ONLY complete display equations, grouped by their
equation group, with equation numbers preserved.
"""
import re


# Cells that are layout/annotation, not formula body
NON_BODY_CELLS = ("ltx_eqn_center_padleft", "ltx_eqn_center_padright",
                  "ltx_eqn_eqno", "ltx_eqn_padleft", "ltx_eqn_padright")


def _classes(el):
    return el.get("class") or []


def _has_class(el, *names):
    cls = _classes(el)
    return any(n in cls for n in names)


def _is_body_cell(td):
    """A td that holds formula content, not padding or the eqno."""
    cls = _classes(td)
    if not cls:
        return True
    if any(any(bad in c for bad in NON_BODY_CELLS) for c in cls):
        return False
    return True


def extract_display_equations(html):
    """
    Extract complete display equations from arxiv HTML.

    Returns list of:
      {
        "group_id": str,            # table class or synthetic id
        "row_index": int,           # position within the group
        "eqno": str | None,         # "(3)" if present
        "nodes": [math_tag, ...],   # the MathML nodes in the body cell
        "is_multiline_group": bool, # part of a multi-row align block
        "container_classes": [...], # for audit
      }
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # --- Path 1: table.ltx_equationgroup -> tr.ltx_equation rows
    groups = soup.find_all("table", class_=lambda c: c and "ltx_equationgroup" in c)
    group_counter = 0
    for table in groups:
        group_counter += 1
        rows = table.find_all("tr", class_=lambda c: c and (
            "ltx_equation" in c or "ltx_eqn_row" in c))
        is_multi = len(rows) > 1
        for ri, tr in enumerate(rows):
            eqno = None
            body_nodes = []

            # eqno: arxiv puts the number in a td.ltx_eqn_eqno containing
            # span.ltx_tag_equation. NOTE: when class_ is a callable,
            # BeautifulSoup passes EACH class name (a str), not the list —
            # so test substrings directly, never iterate the argument.
            eqno = None
            tag_el = tr.find(["span", "td"], class_=lambda c: (
                "ltx_tag_equation" in c or "ltx_eqn_eqno" in c))
            if tag_el:
                eqno = tag_el.get_text(" ", strip=True) or None

            # body cells
            for td in tr.find_all("td"):
                if not _is_body_cell(td):
                    continue
                for m in td.find_all("math"):
                    body_nodes.append(m)

            if not body_nodes:
                continue

            results.append({
                "group_id": f"eqgroup_{group_counter}",
                "row_index": ri,
                "eqno": eqno,
                "nodes": body_nodes,
                "is_multiline_group": is_multi,
                "container_classes": _classes(tr),
            })

    # --- Path 2: standalone tr.ltx_equation not inside an equationgroup
    all_rows = soup.find_all("tr", class_=lambda c: c and (
        "ltx_equation" in c or "ltx_eqn_row" in c))
    seen_rows = set()
    for r in results:
        for n in r["nodes"]:
            seen_rows.add(id(n))

    standalone = 0
    for tr in all_rows:
        in_group = False
        for p in tr.parents:
            if p.name == "table" and _has_class(p, "ltx_equationgroup"):
                in_group = True
                break
        if in_group:
            continue
        body_nodes = []
        eqno = None
        eqno_td = tr.find("td", class_=lambda c: c and any(
            "ltx_eqn_eqno" in x for x in c))
        if eqno_td:
            eqno = eqno_td.get_text(" ", strip=True) or None
        for td in tr.find_all("td"):
            if not _is_body_cell(td):
                continue
            for m in td.find_all("math"):
                body_nodes.append(m)
        if not body_nodes:
            continue
        if all(id(n) in seen_rows for n in body_nodes):
            continue
        standalone += 1
        results.append({
            "group_id": f"standalone_{standalone}",
            "row_index": 0,
            "eqno": eqno,
            "nodes": body_nodes,
            "is_multiline_group": False,
            "container_classes": _classes(tr),
        })

    return results


def parse_display_equations(html, parser_factory):
    """
    Extract + parse complete display equations into solver expressions.

    parser_factory: callable returning a fresh MathMLParser instance.

    Returns list of:
      {
        "expr": solver expression (str) or None,
        "exprs": [per-node expressions] (for multi-node rows),
        "eqno": str|None,
        "group_id": str,
        "row_index": int,
        "is_multiline_group": bool,
        "unsupported": [...],
        "source": "display",
      }
    """
    out = []
    for row in extract_display_equations(html):
        parser = parser_factory()
        exprs = []
        unsupported_all = []
        for node in row["nodes"]:
            e, unsup = parser.parse(node)
            if e:
                exprs.append(e)
            if unsup:
                unsupported_all.extend(unsup)

        # If the row has multiple math nodes, join them (align rows split on &)
        if len(exprs) == 1:
            expr = exprs[0]
        elif len(exprs) > 1:
            # A multi-node row is usually LHS/RHS or a labelled system.
            # Join with '=' only if exactly two and neither already has '='.
            if len(exprs) == 2 and "=" not in exprs[0] and "=" not in exprs[1]:
                expr = f"{exprs[0]}={exprs[1]}"
            else:
                expr = " ".join(exprs)
        else:
            expr = None

        out.append({
            "expr": expr,
            "exprs": exprs,
            "eqno": row["eqno"],
            "group_id": row["group_id"],
            "row_index": row["row_index"],
            "is_multiline_group": row["is_multiline_group"],
            "unsupported": unsupported_all,
            "source": "display",
        })

    return out


if __name__ == "__main__":
    import sys, json, urllib.request

    url = f"https://arxiv.org/html/{sys.argv[1]}" if len(sys.argv) > 1 else \
        "https://arxiv.org/html/2006.11239"

    req = urllib.request.Request(url, headers={"User-Agent": "display-eq/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

    from mathml_parser import MathMLParser

    rows = extract_display_equations(html)
    print(f"Display equation rows: {len(rows)}")
    print()

    parsed = parse_display_equations(html, MathMLParser)
    solved_like = 0
    for p in parsed[:20]:
        flag = "MULTI" if p["is_multiline_group"] else "     "
        eqno = p["eqno"] or ""
        print(f"  {flag} {eqno:8s} {str(p['expr'])[:100]}")
        if p["expr"] and p["expr"].count("=") == 1:
            solved_like += 1
    print()
    print(f"Rows with exactly one '=': {solved_like}/{len(parsed)}")
    multi = sum(1 for p in parsed if p["is_multiline_group"])
    print(f"Rows in multi-line groups: {multi}")
    withnum = sum(1 for p in parsed if p["eqno"])
    print(f"Rows with equation numbers: {withnum}")
