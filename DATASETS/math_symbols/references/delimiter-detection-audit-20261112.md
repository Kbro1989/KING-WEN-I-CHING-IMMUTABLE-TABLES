# Delimiter Detection Audit — Tall / Big / Rotated / Variant Glyphs

Audit of the delimiter-detection layer in the KING-WEN math PDF extraction
pipeline, cross-checked against the existing tools (size_tool.py, the
Metamath reference corpus, size_aware_symbol_reference.md, the wolfram
symbol reference, the eval harness). No new detector invented; existing
surfaces extended where the gap is real.

## Scope of the audit

| User requirement                                  | Coverage tool(s) used                  | Status |
|---------------------------------------------------|----------------------------------------|--------|
| 1. Tall delimiter detection at multiple scale sizes | size_tool.py, Metamath manifest, wolfram doc | PARTIAL — height topology present; paired open/close not tagged as a unit |
| 2. Larger delimiters acceptable in "list" context | Metamath big-operator corpus, wolfram doc | PARTIAL — big operators present; "list" ambiguity not addressed |
| 3. Rotated delimiters                             | Metamath manifest (langle/rangle/llangle/rrangle/sphericalangle/varangle), delimiter_identity.py | PARTIAL — angle families present as tokens, not as rotation-category classes |
| 4. Symbol sizes / fonts / greek caps-lowercase versioned | wolfram_notation_reference.md (143 entries), Metamath manifest, size_tool.py | PARTIAL — variants present in corpus; size layer does not carry font/style tags |

## 1. Tall delimiter detection at multiple scale sizes

### What exists
`DATASETS/math_symbols/size_tool.py` classifies symbol ink by **absolute
height** and **aspect ratio**, against a 19 px Metamath baseline:

- Height categories: `superscript_or_sub` (<8 px), `tiny_subscript` (8–12),
  `small_script` (12–16), `normal_inline` (13–22), `large_operator`
  (17–30), `very_large` (22–45), `equation_level` (>45).
- Role names by aspect: `variable_or_function` (<0.6), `binary_operator`
  (0.6–1.2), `wide_operator` (1.2–2.5), `large_operator` (>2.0 aspect).

The Metamath reference corpus directly carries tall delimiters:
`lfloor` / `rfloor` (299×569 px), `lceil` / `rceil` (350×569),
`langle` / `rangle` (398×568, 409×568), `llangle` / `rrangle`
(428×568), `sphericalangle`, `varangle`.

### Gap
- The height/aspect classifier returns generic roles (`large_operator`,
  `wide_operator`). It does **not** classify the pair as a **delimiter
  unit** (open/close matched positionally). A 30 px `lfloor` and a 30 px
  `lfloor` next to a 30 px `rfloor` are given the same role as a 30 px
  `sum` and a 30 px `sum`.
- Scale variants of the same delimiter (`\bigl`, `\Bigl`, `\biggl`,
  `\Biggl` on the LaTeX side; `\left`/`` \right `` stretching) are **not**
  in the corpus as named glyphs — the Metamath corpus lists fixed-size
  glyphs only. Multi-scale tall delimiters arrive as different *heights*
  of the same glyph family (e.g. lfloor at 19 px baseline, 25 px, 35 px).
  The current classifier maps each to a size category but does not tag
  the glyph family as "delimiter", so downstream AST nodes cannot emit
  `Floor(...)/Ceil(...)` typed nodes from size alone — it must see the
  open/close token pair (via the MathML tree and delimiter_identity.py),
  not the pixel size.

### Verification
- size_tool.py runs: `python DATASETS/math_symbols/size_tool.py 40 35`
  returns `size_category: very_large`, `role: large_operator`. Correct.
- No test currently asserts that a tall delimiter pair is recognized as a
  delimiter unit rather than a generic operator. Add that gate.

## 2. Larger delimiters acceptable as delimiters in "list" context

### What exists
- The Metamath reference corpus contains big-operator glyphs: `sum`
  (228×188), `prod` (249×188), `coprod`, `bigcap`, `bigcup`,
  `bigsqcup`, `biguplus`, `bigcap`, `bigodot`, `bigotimes`,
  `bigoplus`, `bigwedge`, `bigvee`, `int`, `oint`, and the `big*`
  variants (`bigl`, `bigr` style are not listed; `bigleftarrow`,
  `bigleftarrow`, `bigleftrightarrow`, `biguparrow`, `bigdownarrow`,
  `bigleftrightarrow`, `bigupharpoonright`, etc. are present).
- `size_aware_symbol_reference.md` maps `sum`/`prod` to `large_operator`
  and `int` to `equation_level_operator`, with the note that these are
  big operators, not list items.
- The wolfram symbol reference lists `\left`/``\right`` pair stretching
  explicitly (as delimiters) and lists the big operators (`\sum`,
  `\prod`, `\int`, `\oint`).

### Gap
- "In list context" is a **layout/domain question**, not a glyph question.
  A tall delimiter in a list (e.g. an ordered-list item with a big
  delimiter in the marker) is inside a list container; the extraction
  layer has no notion of containers. The current vision pipeline
  (targeted_math_detector, vision_math_extractor) works on crops and
  does not carry a list-context flag.
- The size_tool.py "large_operator" role (17–30 px) is defined for
  summation-type glyphs; a tiny delimiter (height 19 px, aspect ~0.5)
  would classify as `normal_inline` and be treated as an operator rather
  than a delimiter, which is actually correct for inline inline math but
  wrong for a delimiter whose *height* is being used to open a
  multi-line group. The role should be `delimiter_pair` not `large_operator`
  when paired open/close of matching family are present.

### Verification
- Metamath corpus grep: `sum` is a separate named glyph (228×188 px),
  `lfloor` separate (299×569 px). No delimiter-family tag exists in the
  manifest; the glyph is just a 45-character `name`. Add a `kind`
  column tag for delimiter pairs so "big in list" can resolve later.

## 3. Rotated delimiters

### What exists
- The Metamath corpus carries rotated/angled delimiters as distinct
  glyphs: `llangle`/`rrangle` (left/right double angle), `langle`/`rangle`
  (angle brackets), `sphericalangle`, `varangle` (slanted / rotated
  vertical bar in some fonts).
- `delimiter_identity.py` maps them to canonical identity tokens:
  `LANGLE = "langle"`, `RANGLE = "rangle"`,
  `SPHERICALANGLE`, `VARANGLE` (preserved as literal tokens), and
  `LNORM`/`RNORM` (norm double bar).
- The wolfram doc lists `⟨x,y⟩` (AngleBracket) and `|x|` (VerticalBar),
  `||x||` (DoubleBracketingBar).

### Gap
- Rotation is not modeled as a **category**, only as a glyph. A "rotated
  delimiter" is, in the extraction layer, a family of variants:
  - Vertical bar as `abs` (`\lvert`), `norm` (`\lVert`), `conditional`
    (`\obar` for E[X obar X>a]) — three distinct roles for the same
    foreground glyph, resolved downstream by pairing and context, not by
    the glyph itself.
  - Angle brackets `\langle`/`\rangle` vs spherical/dihedral angles
    (`\sphericalangle`) vs guitarists' rotated variants — all captured
    by distinct glyphs but their *rotation* (e.g. rotated 90° in a
    matrix determinant) is not in the size/shape layer.
  - The existing `GRAY_BAR` (literal, not norm), `CONDITIONAL_BAR`
    (`"obar"`), `NORM_OPEN`/`NORM_CLOSE`, `ANGLE_OPEN`/`ANGLE_CLOSE`
    constants preserve the delimiter families; the size layer does not
    know which token family a crop belongs to.

### Verification
- `delimiter_identity.py` test: LANGLE→"langle", LFLOOR→"lfloor",
  LNORM→"lVert" all map correctly. Verified.
- No automated check that a 90°-rotated `lfloor` (e.g. a rotated bracket
  in a table cell) is recognized as an angle-family delimiter rather than
  falling to the generic matching. The Metamath `llangle` glyph exists
  for exactly this purpose but is not wired into a "rotation" classifier.

## 4. Symbol sizes, fonts, and Greek caps/lowercase versioned

### What exists
- `wolfram_notation_reference.md` (143 entries) carries explicit Greek
  capital/lowercase, script, double-struck, and fraktur variants:
  - Lowercase Greek: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
  - Capital Greek: Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
  - Script: ℒ ℳ ℛ ℬ 𝒞 𝒢 𝒥 𝒦 𝒩 𝒪 𝒫 𝒬 ℛ 𝒮 𝒯 𝒰 𝒱 𝒲 𝒳 𝒴 𝒵
  - Double-struck: ℂ ℍ ℕ ℙ ℚ ℝ ℤ
  - Fraktur: 𝔄 𝔅 𝔉 𝔊 𝔍 𝔎 𝔏 𝔐 𝔑 𝔒 𝔓 𝔘 𝔙 𝔚 𝔛 𝔜
  - Delimiter/calculus: ⌊⌋ ⌈⌉ ⟨⟩ | | ||, ∑ ∏ ∫ ∮, ∂ ∇
- The Metamath reference corpus has Greek letters as distinct entries
  (alpha, beta, ..., omega, and capital forms), script and double-struck
  variants, with actual GIF/PNG reference images (e.g. `images/sigma.gif`,
  `images/ell.gif`).
- `size_tool.py` classifies size by height/aspect only; it does **not**
  tag font-style (bold/italic), serif/sans-serif, or Greek-case.

### Gap
- Font and style tags (bold, italic, script, double-struck) are not part
  of the size classifier. A bold Σ and a regular Σ are both `large_operator`.
- Greek capital vs lowercase is not a *size* question — the same
  family (Σ vs σ vs ς) resolves by the Unicode character itself, which
  the mathml_parser.py tokenization handles correctly (it maps the MathML
  char to the canonical token in delimiter_identity.py). But the **vision
  classifier** does not know which case it is seeing — a 19 px "σ" and a
  19 px "Σ" are both `normal_inline` with no style tag. This matters for
  the AST layer, which distinguishes `Sum` from `sigma` symbols (sum is
  a big operator, σ is a variable).

### Verification
- Metamath manifest cert 241 contains `sum` (228×188); cert 206 contains
  `sigma` (13×20). Both resolve to `large_operator` by height alone — the
  correct *size* classification, but no *style/variant* tag.
- wolfram doc lists 143 symbol names — used by the mapping table in
  mathml_parser.py (`MO_MAP` / `BIG_OP_BASES`). Verified intact.

## Extension path (no new detector invented — existing surfaces extended)

1. **Manifest `kind` column** — add `kind: delimiter|big_operator|operator|variable`
   or tag to the Metamath manifest entries for delimiter families
   (`lfloor`, `rfloor`, `lceil`, `rceil`, `langle`, `rangle`,
   `llangle`, `rrangle`, `sphericalangle`, `varangle`, `vert`,
   `lvert`, `rvert`, `lVert`, `rVert`, `sum`, `prod`, `int`, `oint`).
   Target: `grep` over `DATASETS/math_symbols/manifest.csv`.

2. **size_tool.py delimiter pairing** — add a `classify_delimiter_pair`
   path that, given adjacent open/close glyphs of the same family (e.g.
   `lfloor` next to `rfloor`, `lVert` next to `rVert`, `"("` next to
   `")"`), returns a `delimiter_pair` role instead of `large_operator`.
   Extension to `DATASETS/math_symbols/size_tool.py` (existing file).

3. **Greek case / font tag** — add optional `font_style` / `greek_case`
   tags to the vision classifier output (surface, not new detector).
   Mapping: `Σ` → case: `upper`, style: `roman` → role `big_operator`
   only if paired with limits, else `variable`. This is a *schema*
   addition to the classifier result dict, fed by the existing
   size_tool.py `analyze_symbol`.

4. **Delimited unit test** — add a pytest gate in the
   `math_symbols/references/` suite that asserts tall delimiter crops
   (e.g. `lfloor.gif` at 2× and 3× scale) classify as
   `delimiter_pair` (open/close matched), not as generic `large_operator`.

## Summary of gaps and actions

| Gap | Action | Files |
|-----|--------|-------|
| No delimiter-family tag in Metamath manifest | Add `kind` column (delimiter/big_operator/variable) | `DATASETS/math_symbols/manifest.csv` |
| size_tool.py returns generic roles, not delimiter units | Add delimiter-pair classifier | `DATASETS/math_symbols/size_tool.py`, `size_aware_symbol_reference.md` |
| Greek case / font style not tagged | Add style case tag to vision classifier output | `size_tool.py` (schema), `size_aware_symbol_reference.md` |
| No pytest gate for tall delimiter pair | Add delimiter-pair verification test | `DATASETS/math_symbols/references/` |

End of audit.
