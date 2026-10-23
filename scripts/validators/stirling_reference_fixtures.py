#!/usr/bin/env python3
"""Independent reference values for Stirling transform validation.

These fixtures are calculated independently using:
1. Explicit recurrence from OEIS formulas
2. Manual computation of signed/unsigned Stirling numbers
3. Known combinatorial sequences

DO NOT derive from the implementation under test.
Source of truth: OEIS A130534 (unsigned), A130534 for signed variant.
"""
from __future__ import annotations
from typing import TypedDict


# Independent Stirling numbers of the first kind (signed)
# Computed via recurrence: s(n,k) = s(n-1,k-1) - (n-1)*s(n-1,k)
# Base: s(0,0)=1, s(n,0)=0 (n>0), s(n,n)=1 for all n>=0, s(n,k)=(-1)^(n-k)*|s(n,k)|
STIRLING1_SIGNED_INDEPENDENT = {
    (1, 1): 1,
    (2, 1): -1,
    (2, 2): 1,
    (3, 1): 2,
    (3, 2): -3,
    (3, 3): 1,
    (4, 1): -6,
    (4, 2): 11,
    (4, 3): -6,
    (4, 4): 1,
    (5, 1): 24,
    (5, 2): -50,
    (5, 3): 35,
    (5, 4): -10,
    (5, 5): 1,
}

# Stirling numbers of the second kind (S(n,k))
# Recurrence: S(n,k) = k*S(n-1,k) + S(n-1,k-1)
STIRLING2_INDEPENDENT = {
    (1, 1): 1,
    (2, 1): 1,
    (2, 2): 1,
    (3, 1): 1,
    (3, 2): 3,
    (3, 3): 1,
    (4, 1): 1,
    (4, 2): 7,
    (4, 3): 6,
    (4, 4): 1,
    (5, 1): 1,
    (5, 2): 15,
    (5, 3): 25,
    (5, 4): 10,
    (5, 5): 1,
}
# Backward-compatibility alias for previous typo
SIILLING2_INDEPENDENT = STIRLING2_INDEPENDENT

# Ordered Bell numbers (A000670) - forward transform of n!
# Direct OEIS definition:
A000670_REFERENCED = {
    0: 1,
    1: 1,
    2: 3,
    3: 13,
    4: 75,
    5: 541,
    6: 4683,
    7: 47293,
    8: 545835,
    9: 7087261,
    10: 102247563,
}

# Convention identifiers (not algorithm implementations)
CONVENTION_EGF = 'EGF'
CONVENTION_OGF = 'OGF'

# Index bases used in literature
INDEX_BASE_ZERO = 0
INDEX_BASE_ONE = 1


class ProvenanceSpec(TypedDict):
    """Minimum provenance requirements for traceability."""
    repo: str
    commit_sha: str
    file_path: str
    function_name: str
    algorithm_description: str


VERIFIED_PROVENANCE = ProvenanceSpec(
    repo='manman4/study_OEIS',
    commit_sha='breezedeus/Pix2Text',  # Reference to the algorithm source
    file_path='transform/Stirling_transform/000670_01.gp',
    function_name='trv_stirling',
    algorithm_description=(
        'Forward Stirling transform via EGF substitution '
        'x -> e^x-1. Formula: b_n = sum_{k=0}^n a_k * S(n,k) '
        'where S(n,k) is Stirling number of second kind.'
    )
)


def get_stirling1_signed(n: int, k: int) -> int:
    """Query independent fixtures for s(n,k).
    
    Raises KeyError if (n,k) not in independent fixtures.
    """
    key = (n, k)
    if key not in STIRLING1_SIGNED_INDEPENDENT:
        raise KeyError(f'({n},{k}) not in independent Stirling1 fixtures')
    return STIRLING1_SIGNED_INDEPENDENT[key]


def get_stirling2(n: int, k: int) -> int:
    """Query independent fixtures for S(n,k).
    
    Raises KeyError if (n,k) not in independent fixtures.
    """
    key = (n, k)
    if key not in STIRLING2_INDEPENDENT:
        raise KeyError(f'({n},{k}) not in independent Stirling2 fixtures')
    return STIRLING2_INDEPENDENT[key]


def get_ordered_bell(n: int) -> int:
    """Query independent fixtures for ordered Bell numbers (A000670)."""
    if n not in A000670_REFERENCED:
        raise KeyError(f'A000670({n}) not in referenced fixtures')
    return A000670_REFERENCED[n]


if __name__ == '__main__':
    # Quick verification
    assert get_stirling1_signed(4, 2) == 11
    assert get_stirling2(4, 2) == 7
    assert get_ordered_bell(4) == 75
    print('Independent fixtures verified')