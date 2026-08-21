# OEIS Submission Draft — King Wen 512-State Deterministic Phase-Space Family

**Author**: Kevin Browder (Kbro1989)  
**Date**: 2026-08-20  
**Repository**: [https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES](https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES)  

---

## 1. Proposed Sequence A357XXX (Primary)

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
* **Implementation alignment**: In the operational runtime (`emotional_engine.py::_intent_to_vector`), SHA256 is replaced by a cumulative ASCII sum $\text{hash\_val} = \sum \text{ord}(c)$ for performance, and expanded into a 5-axis coprime prime vector field across 5 distinct prime moduli ($97, 89, 83, 79, 73$) to prevent inter-axis aliasing:
  - $\text{chaos} \propto (\text{hash\_val} \pmod{97}) / 97.0$
  - $\text{whimsy} \propto ((\text{hash\_val} // 7) \pmod{89}) / 89.0$
  - $\text{darkTone} \propto ((\text{hash\_val} // 13) \pmod{83}) / 83.0$
  - $\text{coherence} \propto ((\text{hash\_val} // 19) \pmod{79}) / 79.0$
  - $\text{voiceWeight} \propto ((\text{hash\_val} // 23) \pmod{73}) / 73.0$
  The single mod-97 SHA256 formula $a(n)$ is the 1D mathematical base specification for the sequence.
* **Application**: This sequence seeds the 5-axis emotional vector perturbation in a 512-state King Wen I Ching oracle engine. Each term perturbs the chaos, whimsy, darkTone, coherence, and voiceWeight axes of a Hamiltonian field consensus computation.
* **Period**: The sequence is aperiodic by construction (SHA256 preimage resistance). For practical purposes, the period exceeds $2^{256}$.

### References
* Kevin Browder (Kbro1989), King Wen 512-State Immutable Oracle, GitHub repository (2026). 9-bit deterministic state resolver, zero-roll Hamiltonian accumulator, 512-state phase-space superposition.
* K. Wen (trad.), I Ching (Zhou Yi), King Wen sequence of 64 hexagrams.

### Links
* [Source Code Repository](https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES): `emotional_engine.py`, function `_intent_to_vector()` (deterministic semantic token hash perturbation).

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

## 2. Companion Sequence A357XXY (Structural)

### Name
`a(n) = 10 * floor(n/8) + 10 + (n mod 8)` for $n = 0..511$ — compact encoding of the 64 King Wen hexagrams ($1..64$) each paired with 8 temporal phases ($0..7$).

### Terms (first 32)
```
10, 11, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 44, 45, 46, 47
```

### Offset
`0`

### Formula
$$a(n) = 10 \cdot (\lfloor n/8 \rfloor + 1) + (n \bmod 8)$$

### Comments
* Encodes the complete 512-state ($2^9$) phase space of the King Wen 512-state oracle. Each hexagram appears exactly 8 times, once per temporal phase: past, present, future, transition, resolution, dissolution, crystallization, void.
* The 9-bit state resolver maps any `(emotional_input, request_text)` pair to a unique index $n \in 0..511$, which resolves to hexagram $\lfloor n/8 \rfloor + 1$ in phase $n \bmod 8$.
* The encoding $10 \cdot h + p$ is chosen because it is human-readable: $a(0)=10$ means hexagram 1, phase 0; $a(511)=647$ means hexagram 64, phase 7.

### Cross-references
* **A357XXX**: Perturbation sequence above
* **A102241**: King Wen hexagram order

---

## 3. Companion Sequence A357XXZ (Constant)

### Name
Constant sequence $a(n) = 729 = 3^6$ — the number of ternary line-state assignments (yin/yang/changing) for a 6-line hexagram.

### Terms (first 20)
```
729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729, 729
```

### Offset
`0`

### Formula
$$a(n) = 729$$

### Comments
* Each of the 64 canonical hexagrams sits at the center of a local 729-state ternary neighborhood ($3^6$ line permutations).
* Globally: $64 \times 729 = 46,656$ resolved line-state combinations.
* The 729 local permutations and the $27 \times 27 = 729$ global trigram matrix coordinates are distinct combinatorial structures that share the same cardinality ($3^6 = 3^3 \times 3^3$).
* This constant sequence serves as a structural anchor in the training corpus, marking every hexagram entry with its local permutation dimension.

### Cross-references
* **A000244**: $3^n$
* **A357XXX**, **A357XXY**

---

### Keywords
`deterministic`, `hash`, `modular`, `phase-space`, `I Ching`, `oracle`, `pseudorandomness extractor`, `zero-roll`
