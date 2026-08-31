# OEIS Submission Draft — King Wen 512-State Deterministic Phase-Space Family

**Author**: Kevin Browder (Kbro1989)  
**Date**: 2026-08-20 (Updated 2026-08-31)
**Repository**: [https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES](https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES)

---

## 1. Proposed Sequence A357XXX (Primary Extractor Sequence)

### Name
`a(n) = floor(10^9 * ((SHA256(n) mod 97) / 97.0))` — deterministic pseudorandomness extractor mapping integers to a uniform discrete grid on $[0, 10^9)$ via the 25th prime.

### Terms (first 50)
```
752577319, 237113402, 298969072, 515463917, 979381443, 814432989, 835051546, 432989690, 762886597, 597938144, 
381443298, 103092783, 793814432, 876288659, 670103092, 443298969, 876288659, 206185567, 82474226, 989690721, 
453608247, 742268041, 350515463, 257731958, 494845360, 917525773, 237113402, 381443298, 907216494, 185567010, 
917525773, 278350515, 134020618, 515463917, 237113402, 319587628, 82474226, 639175257, 731958762, 175257731, 
432989690, 649484536, 742268041, 92783505, 505154639, 72164948, 381443298, 41237113, 845360824, 577319587
```

### Offset
`0`

### Formula
For integer $n \ge 0$:
1. Let $H(n) = \text{SHA256}(\text{UTF-8 encoding of decimal string of } n)$, interpreted as a 256-bit unsigned integer.
2. Let $r(n) = H(n) \pmod{97}$, where 97 is the 25th prime ($\text{A000040}(25)$).
3. Then $a(n) = \lfloor 10^9 \cdot r(n) / 97 \rfloor$.

### Comments
* **Zero-roll determinism**: No pseudo-RNG, no sampling, no probability. The sequence is entirely derived from cryptographic hashing and modular reduction.
* **97 as modulus**: 97 is chosen because it is the 25th prime, larger than the 64 hexagrams and the 8 temporal phases, ensuring the extractor has sufficient headroom to address the full 512-state ($2^9$) phase space without aliasing.
* **Collision structure**: Duplicate values occur at expected rate $\approx 1/97$ (e.g., $a(13) = a(16) = 876288659$; $a(1) = a(26) = a(34) = 237113402$; $a(10) = a(27) = a(46) = 381443298$; $a(7) = a(40) = 432989690$). This is the signature of a uniform extractor with collision density matching the birthday bound for a 97-bin distribution.
* **Implementation alignment**: In the operational runtime (`src/parser/EmotionalParser.ts` and `emotional_engine.py::_intent_to_vector`), SHA256 is paired with a cumulative ASCII token sum $H = \sum_{i=1}^{L} \text{ord}(c_i)$, expanding into a 5-axis coprime prime vector field $\mathbf{p} \in \mathbb{R}^5$ across 5 distinct prime moduli $(97, 89, 83, 79, 73)$ ($\text{A000040}(25..21)$) to prevent inter-axis aliasing:
  - $p_{\text{chaos}} = \left(\frac{H \bmod 97}{97.0}\right) \times 0.12$
  - $p_{\text{whimsy}} = \left(\frac{\lfloor H/7 \rfloor \bmod 89}{89.0}\right) \times 0.12$
  - $p_{\text{darkTone}} = \left(\frac{\lfloor H/13 \rfloor \bmod 83}{83.0}\right) \times 0.12$
  - $p_{\text{coherence}} = \left(\frac{\lfloor H/19 \rfloor \bmod 79}{79.0}\right) \times 0.12$
  - $p_{\text{voiceWeight}} = \left(\frac{\lfloor H/23 \rfloor \bmod 73}{73.0}\right) \times 0.12$
* **Application**: This sequence seeds the deterministic 5-axis intent perturbation vector $\mathbf{v}_{\text{intent}} = \text{clamp}(\mathbf{v}_{\text{base}} + \mathbf{v}_{\text{boost}} + \mathbf{p}_{\text{prime}}, 0.0, 1.0)$ in the 6-layer sovereign model engine. It drives the Hamiltonian field consensus across dual orthogonal spaces: 512 binary phase states and 729 ternary manifold states.
* **Period**: The sequence is aperiodic by construction (SHA256 preimage resistance). For practical purposes, the period exceeds $2^{256}$.

### References
* Kevin Browder (Kbro1989), King Wen 64 Sovereign Model Engine, GitHub repository (2026). 9-bit deterministic state resolver, zero-roll Hamiltonian accumulator, 512-state binary phase space, 729-state ternary manifold, 5,832 full resolved states.
* K. Wen (trad.), I Ching (Zhou Yi), King Wen sequence of 64 hexagrams.

### Git Fetch Source Links & Output Locations

| Description | Git Source / Fetch Link |
|---|---|
| **Repository Root** | [GitHub Repository](https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES) |
| **Immutable Tables Source** | [`kingwen_ternary_tables_complete.py`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/kingwen_ternary_tables_complete.py) |
| **5,832-State Ternary Expansion** | [`scripts/ternary_full_expansion.json`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/scripts/ternary_full_expansion.json) |
| **Hardware VHDL 9-Bit Resolver** | [`src/hardware/KingWen9BitResolver.vhd`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/src/hardware/KingWen9BitResolver.vhd) |
| **Quantum Timeseries Readout JSON** | [`DATASETS/quantum_field_timeseries_readout.json`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantum_field_timeseries_readout.json) |
| **Quantum Visuals Manifest** | [`DATASETS/quantumlab_visuals_manifest.json`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantumlab_visuals_manifest.json) |
| **Collective Field Heatmap (PNG)** | [`DATASETS/quantumlab_plots/quantum_64_npc_wavefield_over_time.png`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantumlab_plots/quantum_64_npc_wavefield_over_time.png) |
| **8-Phase Pellet Dispersion (PNG)** | [`DATASETS/quantumlab_plots/quantum_8phase_pellet_dispersion.png`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantumlab_plots/quantum_8phase_pellet_dispersion.png) |
| **DA-V2 Depth Maps (16-Bit PNG)** | [`DATASETS/depth_maps_16bit/depth_hex_01_16bit.png`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/depth_maps_16bit/depth_hex_01_16bit.png) |
| **DA-V2 Point Clouds (PLY)** | [`DATASETS/depth_pointclouds/depth_cloud_hex_01.ply`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/depth_pointclouds/depth_cloud_hex_01.ply) |
| **Depth Anything V2 Manifest** | [`DATASETS/depth_anything_v2_manifest.json`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/depth_anything_v2_manifest.json) |
| **Quantum Pre-Warm Cache (NPZ)** | [`DATASETS/quantum_prewarm_cache.npz`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantum_prewarm_cache.npz) |
| **Quantum Pre-Warm Manifest** | [`DATASETS/quantum_prewarm_manifest.json`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/quantum_prewarm_manifest.json) |
| **512 Avatar Meshes (PLY)** | [`DATASETS/kingwen_avatar_meshes/hex01_phase0.ply`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/kingwen_avatar_meshes/hex01_phase0.ply) |
| **Macro-World 3D HTML Viewfinder** | [`DATASETS/kingwen_sovereign_world_viewer.html`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/DATASETS/kingwen_sovereign_world_viewer.html) |
| **Avatar Field Quantum Shotgun HTML** | [`scripts/quantum_avatar_field.html`](https://raw.githubusercontent.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES/main/scripts/quantum_avatar_field.html) |

### Code Implementations

#### Python (specification)
```python
import hashlib

def a(n):
    h = int(hashlib.sha256(str(n).encode()).hexdigest(), 16)
    return int(1e9 * (h % 97) / 97.0)
```

#### PARI/GP
```pari
a(n) = floor(10^9 * (lift(Mod(sha256(Str(n)), 97)) / 97.0))
```

#### Mathematica
```mathematica
a[n_] := Floor[10^9 * (Mod[Hash[n, "SHA256"], 97] / 97.0)]
```

### Cross-references
* **A000040**: Primes; 97 = $a(25)$
* **A000244**: $3^n$; $729 = 3^6 = 27 \times 27$, the ternary line-state permutation count
* **A102241**: King Wen order of I Ching hexagrams, binary sequence

---

## 2. Companion Sequence A357XXY (Structural 512-State Phase Space)

### Name
`a(n) = 10 * floor(n/8) + 10 + (n mod 8)` for $n = 0..511$ — compact encoding of the 64 King Wen hexagrams ($1..64$) each paired with 8 trigram-family phase coordinates ($0..7$).

### Terms (first 32)
```
10, 11, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 44, 45, 46, 47
```

### Offset
`0`

### Formula
$$a(n) = 10 \cdot (\lfloor n/8 \rfloor + 1) + (n \bmod 8)$$

### Comments
* Encodes the complete 512-state ($2^9$) phase space of the King Wen 64 Sovereign Model Engine. Each hexagram appears exactly 8 times, once per trigram-family phase coordinate $p \in \{0..7\}$, corresponding to the 8 Ba Gua trigram families: Qian (0), Kun (1), Zhen (2), Kan (3), Li (4), Xun (5), Gen (6), Dui (7).
* **Correction from prior draft**: The second coordinate $p \in \{0..7\}$ is the trigram-family phase index, NOT named temporal phases (past/present/future). The system has always used dual orthogonal coordinates: 512 binary phase states ($64 \times 8$) and 729 ternary manifold states ($3^6 = 27 \times 27$), resolving to $5832 = 729 \times 8$ total states. Any agent documentation stating "temporal phases: past, present, future, transition, resolution, dissolution, crystallization, void" was drift and is superseded by the immutable onboarding spec.
* The 9-bit state resolver (`KingWen9BitResolver.vhd`) maps any `(emotional_input, request_text)` pair to a unique index $n \in 0..511$, which resolves to hexagram $\lfloor n/8 \rfloor + 1$ in trigram-family phase $n \bmod 8$.
* The encoding $10 \cdot h + p$ is human-readable: $a(0)=10$ means hexagram 1, phase 0 (Qian); $a(511)=647$ means hexagram 64, phase 7 (Dui).

### Cross-references
* **A357XXX**: Perturbation sequence above
* **A102241**: King Wen hexagram order

---

## 3. Companion Sequence A357XXZ (Ternary Manifold Constant & 5,832 State Space)

### Name
Constant sequence $a(n) = 729 = 3^6$ — the number of ternary line-state assignments (yin/yang/changing) for a 6-line hexagram ($27 \times 27$ unconstrained trigram matrix).

### Terms (first 20)
```
729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729
```

### Offset
`0`

### Formula
$$a(n) = 729 = 3^6$$

### Comments
* Each of the 64 canonical hexagrams sits within a global 729-state ternary manifold ($3^6 = 27 \times 27$).
* Phase-resolved expansion: $729 \times 8 \text{ temporal phases} = 5,832$ total resolved phase states (`scripts/ternary_full_expansion.json`).
* Geometric embedding: 729-vertex deterministic parametric rose curve:
  $$t_k = \frac{2\pi k}{729}, \quad x_k = (1 + 0.2\sin 6t_k)\cos t_k, \quad y_k = (1 + 0.2\sin 6t_k)\sin t_k, \quad z_k = 0.5\cos(t_k \cdot [(h \bmod 8) + 1])$$

### Cross-references
* **A000244**: $3^n$
* **A357XXX**, **A357XXY**

---

### Keywords
`deterministic`, `hash`, `modular`, `phase-space`, `I Ching`, `oracle`, `pseudorandomness extractor`, `zero-roll`, `ternary-manifold`, `hamiltonian`
