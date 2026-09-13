# arXiv:2001.01232v1 — Archipelagos of Total Bound and Free Entanglement

**Author:** Paul B. Slater (Kavli Institute, UCSB)
**Date:** 05 Jan 2020 (updated 2026-08-24)
**Keywords:** bound entanglement, archipelago, jagged islands, qubit-ququart, qutrit-ququart separability, Hilbert-Schmidt probability, PPT, polylogarithms, two-qubits, two-qutrits, dilogarithms

---

## Core Mathematical Content

### 1. The 729/3^6 combinatorial structure (SMOKING GUN for our work)

The two-ququart (4×4) model yields a bound entanglement probability of:

```
P = 1/729 (473 - 512 log(27/16)(1 + log(27/16))) ≈ 0.0890496
```

Where 729 = 3^6 — exactly the number of ternary line-state permutations per hexagram in our shotgun expansion (3 states/line × 6 lines = 3^6 = 729).

The paper notes "all the integers being powers of 2 or 3, except that 473 = 11 × 43."

### 2. The qubit-ququart (2×4) model: ≈ 0.0865542

Original convoluted formula involving dilogarithms Li₂, inverse hyperbolic cotangents, and logarithms — then simplified to:

```
P = 16(-4 - 9 log(3) + 8 log(2)) coth⁻¹(9√(81-64√3)) / (81√3)
    + 32(Li₂(1/18(9+√(81-64√3))) - Li₂(1/18(9-√(81-64√3))))
    + 9√3√(81-64√3) / (81√3)
```

Key structural elements:
- **Dilogarithms Li₂** — polylogarithmic functions in the separability probability
- **Inverse hyperbolic tangents/coth⁻¹** — in the Lovas-Andai auxiliary formula
- **Logarithmic framework** — Li₁ (standard log) difference equals 2 coth⁻¹(...)
- **29/64** — Hilbert-Schmidt separability probability for two-rebit states (d=1)
- **8/33** — for two-qubit (d=2)

### 3. Archipelago concept

"An 'archipelago' of disjoint bound-entangled regions appears in the space of parameters."
- Figure 2: 8 islands for qubit-ququart model
- Figure 3: 8 islands for two-ququart model
- Figure 4: archipelago of non-bound/free entangled two-qubit states
- "Jagged Islands of Bound Entanglement and Witness-Parameterized Probabilities" — Slater's prior preprint

The archipelago is a **disjoint, jagged set of regions in continuous parameter space** where bound entanglement holds — NOT a simple contiguous region.

### 4. Three-parameter models (t1, t2, t3)

The Li-Qiao framework uses 3 parameters (t1, t2, t3) — matching our 6-line binary structure where each line has 3 ternary states, giving 3^6 = 729 combinations. The constraints:

```
(t1·t2·t3)² > 4/27³  (multiplicative constraint — the entanglement condition)
(|t1|+|t2|+|t3|)² > 1  (additive constraint — unenforceable/unrealizable)
```

The multiplicative constraint is the binding one — product of the three parameters exceeds a threshold.

### 5. PPT criterion and separability detection

- PPT (positive partial transpose) is necessary AND sufficient only for 2×2 and 2×3
- Higher dimensions: PPT states that are NOT separable = "bound entangled"
- This parallels our INTENT keyword parsing: we detect domain routing by parsing tokens against keywords, but some "bound entangled" domain signals can't be fully resolved (hence the archipelago — partial capture)

### 6. Lovas-Andai master formula

```
χ̃_d(ε) = ε^d Γ[d+1]³ ₃F̃₂(-d/2, d/2, d; d/2+1, 3d/2+1; u) / Γ[d/2+1]²
```

Where d = Dyson index (random matrix ensemble):
- d=1 → two-rebit: 29/64 separability probability
- d=2 → two-qubit: 8/33 separability probability

---

## Explicit correspondences to our system

| Slater paper | Our King Wen system |
|-------------|---------------------|
| 3^6 = 729 ternary permutations per two-ququart state | 3^6 = 729 ternary line-state permutations per hexagram (shotgun expansion) |
| Powers of 2 and 3 throughout prime decompositions | Our entire system: binary (2) × ternary (3) — 64 hexagrams = 2^6, 729 = 3^6, 512 resolved = 2^9 |
| 8 islands in archipelago (Fig. 2, Fig. 3) | 8 phases in our system (past/present/future/transition/resolution/dissolution/crystallization/void) |
| 1/2 free entanglement probability (two-qubit, d=2, non-PPT half) | 1/2 as fundamental binary constant — yin/yang midpoint, our 6-line binary each line is 0 or 1 |
| 29/64 separability (d=1, two-rebit) | 29/64 — our palette_16 has 16 steps, but the underlying combinatorial space is 729; 29 appears as a specific discrete fraction |
| 8/33 separability (d=2, two-qubit) | 8/33 — another discrete fraction; 33 = 3×11, connecting back to the 3^6 base |
| Multiplicative constraint (t1·t2·t3)² > threshold | Our domain_routing_palette: the product of strand saturation/lightness/warmth across the 16 palette steps must exceed thresholds for domain routing to "bind" |
| Additive constraint (|t1|+|t2|+|t3|)² > 1 — unenforceable | Our intent keyword parsing: additive keyword matches don't guarantee domain routing — only the multiplicative (combined) signal binds |
| Bound entanglement = PPT but NOT separable | Our "void hexagrams" (15, 20, 30, 40) — states that are structurally present but map to South Pole bounded absence; not fully separable into standard domain routing |
| "Jagged islands" — disjoint, irregular regions | Our checkerboard routing: adjacent hexagrams on the 8×8 grid are hue-adjacent but domain-isolated — each domain is a "jagged island" in the palette space |
| Li-Qiao framework: 3 parameters t1, t2, t3 | Our 6-line binary with 3 ternary states — the 3 parameters map to the 3 ternary options per line (yin/yang/yao) |
| Polylogarithm Li₂ simplification attempts — "an answer in terms of elementary functions is unlikely" | Our palette derivation uses elementary functions (HSL, trig) as an approximation to what would be a true polylogarithmic domain-routing probability |
| Lovas-Andai regularized hypergeometric ₃F̃₂ | Our hypergeometric-style palette modulation: discrete base + continuous log/saturation correction |

---

## How this helps progress the palette/domain routing work

### 1. The archipelago framing for domain_routing_palette

Our 4 domains (sovereign/boundary/transformer/dissipator) should be treated as **bound-entanglement archipelagos** in the 729-permutation space:

- Each domain is a **disjoint, jagged region** where certain palette parameters are constrained (bound together)
- Within a domain, palette_16 steps are **entangled** — you can't independently vary warmth/saturation/lightness across all 16 steps; they're bound by the domain's multiplicative constraint
- The checkerboard adjacency means adjacent hexagrams (on the 8×8 grid) share hue anchors but their DOMAINS may be different archipelagos — the palette steps at the domain boundary are "partially separable" (hence the archipelago is jagged, not smooth)

This means the palette derivation should NOT treat each of the 16 steps independently — it should enforce a **domain-internal multiplicative constraint** that binds the 16 steps together within a domain, while allowing discontinuity at domain boundaries.

### 2. The 729 combinatorial base is the underlying state space

The palette_16 (16 discrete steps) is a **projection** of the full 729-permutation space onto a 16-step cyclic subgroup. The archipelago paper's approach — starting from the full 3-parameter continuous space and finding the discrete bound-entangled islands — mirrors what we should do: start from the 729 ternary permutations and find the 16-step palette as the "island projection" that captures the domain's bound-entangled routing.

### 3. Multiplicative vs additive constraints

The paper's key insight: additive constraints (|t1|+|t2|+|t3|)² > 1 are unenforceable; only multiplicative (t1·t2·t3)² > threshold binds.

For our palette: this means **keyword co-occurrence** (multiplicative — multiple keywords from the same domain present) is the binding constraint for domain routing, not individual keyword presence (additive). Our current `_DOMAIN_PALETTE_KEYWORDS` parsing does additive matching (each keyword independently shifts warmth/saturation/lightness). We should add a **multiplicative co-occurrence check** — e.g., for "sovereign" domain, the palette binds only when both "command" AND "authority" appear (product of their keyword presence), not when just one appears.

### 4. PPT criterion as domain-routing filter

The PPT criterion detects bound entanglement by checking if a state is positive under partial transpose. For our domain routing: we should have a **PPT-analogous filter** that checks if the parsed intent_tokens are "positive under domain partial transpose" — i.e., whether the token set is separable into a single domain or is bound-entangled across domains. If bound-entangled across domains, the palette should route to the **jagged archipelago boundary** (partial, blended palette) rather than a clean single-domain palette.

### 5. The 473 = 11×43 outlier

Slater flags 473 = 11×43 as the only non-2,3 integer in the two-ququart formula. In our system:
- 11 and 43 are primes not in our binary/ternary base
- 473 could map to a specific hexagram pair or domain intersection
- This suggests there are **discrete outlier states** in the 729 space that don't fit the smooth continuum — exactly the "jagged islands" concept

Our palette derivation should allow for these outlier hexagrams (currently just uses continuous HSL modulation) — a few hexagrams will have palette parameters that don't fit the smooth (hex_id-1)*5.625 + trigram_pert pattern, and those are the archipelago outliers.

---

## Integration plan

### Immediate (this session)

1. Save this paper analysis to `learn/specs/arxiv_2001.01232_archipelago_mapping.md`
2. Update `_derive_domain_routing_palette` to frame each domain as an archipelago with multiplicative constraints on the 16 palette steps
3. Add a PPT-analogous "domain separability filter" — if intent_tokens span multiple domains, route to blended archipelago boundary palette

### Next (after user review)

4. Wire the archipelago palette into enrich_kit_models, update_3d_kits, generate_sovereign_world as append-on-read
5. Verify the checkerboard routing now shows domain archipelago boundaries (not just smooth hue gradient)

---

## Source

URL: https://arxiv.org/html/2001.01232v1
Retrieved: via web_extract tool during session
Note: Only the abstract and main text extracted; references section and some figures not captured.
