import json
from pathlib import Path
from collections import defaultdict

p = Path("references/comparative_study/raw_code/omnidocbench/visual_matcher.py")
lines = p.read_text(encoding="utf-8").splitlines()

# Lines 44 to 89 contain the dictionary entries
entries = []
for idx in range(44, 89):
    line = lines[idx].strip()
    if not line or line.startswith("#"):
        continue
    # Format: "key": "val",
    parts = line.split(":", 1)
    if len(parts) == 2:
        k = parts[0].strip().strip('"')
        v = parts[1].strip().rstrip(',').strip().strip('"')
        entries.append((k, v))

print(f"Total entries parsed: {len(entries)}")

by_target = defaultdict(list)
for k, v in entries:
    by_target[v].append(k)

categories = {
    ".": ("multiplication_vs_punctuation", "Conflates scalar product, inner product, and continuation dots with sentence period"),
    "\\|": ("norm_vs_parallel_relation", "Conflates opening norm, closing norm, double vertical bar, and parallel relation"),
    "|": ("absolute_value_vs_pipe", "Conflates opening abs, closing abs, conditional probability, and set-builder divider"),
    "/": ("fraction_vs_quotient", "Conflates division slash with backslash and algebraic quotient structures"),
    "[": ("bracket_macro_flattening", "Flattens directional LaTeX bracket macro to ASCII"),
    "]": ("bracket_macro_flattening", "Flattens directional LaTeX bracket macro to ASCII"),
    "\\{": ("brace_macro_flattening", "Flattens directional LaTeX brace macro to escaped punctuation"),
    "\\}": ("brace_macro_flattening", "Flattens directional LaTeX brace macro to escaped punctuation"),
    "\\langle": ("angle_bracket_syntax", "Normalizes syntactic angle bracket to bra-ket delimiter"),
    "\\rangle": ("angle_bracket_syntax", "Normalizes syntactic angle bracket to bra-ket delimiter"),
    "<": ("relation_vs_delimiter", "Conflates text comparison relation with angle bracket"),
    ">": ("relation_vs_delimiter", "Conflates text comparison relation with angle bracket"),
    "_": ("underscore_vs_equals", "Conflates text underscore with macron/equal macro"),
    "\\to": ("arrow_relation_macro", "Normalizes rightarrow macro alias"),
    "T": ("transpose_vs_letter", "Conflates matrix transpose operator \\top with Roman capital letter T"),
    "'": ("prime_vs_quote", "Normalizes prime operator to ASCII quote"),
    "*": ("ast_vs_asterisk", "Conflates \\ast operator with asterisk punctuation"),
    "\\le": ("inequality_alias", "Normalizes leq to le"),
    "\\ge": ("inequality_alias", "Normalizes geq to ge"),
    "\\ne": ("inequality_alias", "Normalizes neq to ne"),
    ":": ("colon_vs_ratio", "Conflates math colon punctuation with mapping/ratio separator"),
    "\\ddot": ("accent_diacritic_variant", "Normalizes capitalized Ddot macro"),
    "\\bar": ("accent_diacritic_variant", "Normalizes capitalized Bar macro"),
    "\\vec": ("accent_diacritic_variant", "Normalizes capitalized Vec macro"),
    "\\tilde": ("accent_diacritic_variant", "Normalizes capitalized Tilde macro"),
    "\\dagger": ("dag_vs_dagger", "Normalizes dag macro alias"),
    "\\ddagger": ("ddag_vs_ddagger", "Normalizes ddag macro alias"),
    "n": ("backslash_corrupt_mapping", "Maps textbackslash to letter 'n'"),
    "\\lnot": ("logic_negation_alias", "Normalizes neg to lnot"),
    "\\not=": ("inequality_expansion", "Rewrites neq to not="),
}

catalog = {
    "catalog_identifier": "OMNIDOCBENCH-CDM-TOKEN-COLLISION-CATALOG-V1",
    "source_file": "src/metrics/cdm/modules/visual_matcher.py",
    "source_repo": "opendatalab/OmniDocBench@0604d98",
    "function": "norm_same_token",
    "total_rules_in_special_map": len(entries),
    "total_unique_target_buckets": len(by_target),
    "collision_groups_multi_token": {k: v for k, v in by_target.items() if len(v) > 1},
    "full_rule_mapping": [
        {
            "target_normalized_token": dst,
            "source_tokens": srcs,
            "multi_source_collision": len(srcs) > 1,
            "category": categories.get(dst, ("macro_alias", "Macro alias"))[0],
            "semantic_impact": categories.get(dst, ("macro_alias", "Macro alias"))[1],
        }
        for dst, srcs in sorted(by_target.items())
    ],
    "structural_delimiters_stripped_by_regex": [
        "\\left", "\\right", "\\big", "\\Big", "\\wide", "\\var", "\\string"
    ]
}

out_path = Path("references/comparative_study/cdm_token_collision_catalog.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Generated catalog at {out_path}: {len(entries)} rules across {len(by_target)} target buckets.")
print("Multi-token collisions:", list(catalog["collision_groups_multi_token"].keys()))
