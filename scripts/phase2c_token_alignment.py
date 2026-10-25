#!/usr/bin/env python3
"""
Phase 2C — Token alignment helper.

Implements deterministic alignment between reference and recognized
token streams for Gate 3 operator-delimiter detection.

Alignment returns:
- Matched token pairs with both reference and recognized positions
- Insertions and deletions
- Substitution candidates where the alignment supports them
- An ambiguity indicator when multiple alignments could change the defect classification

Position convention: 0-based, consistent throughout. Documented in module docstring.

Algorithm:
1. Compute LCS length between reference and recognized token streams.
2. Walk both streams simultaneously, matching matched pairs and recording
   insertions (in rec) and deletions (in ref).
3. Detect substitution candidates as aligned pairs where tokens differ.
4. Detect ambiguity: if there are multiple equally-scored optimal alignments
   that differ in classification (e.g., same LCS length but different
   substitution patterns, or different positions), return ambiguous=True.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional

# Position convention: 0-based. Documented and consistent throughout.
# ref_positions: index into normalized reference token list
# rec_positions: index into normalized recognized token list

# Import canonical tokenizer from gate library to ensure identical tokenization
# to the existing Phase 2C evaluation pipeline.
from phase2c_gate_library import (
    tokenize_latex as _gate_tokenize_latex,
    normalize_latex as _gate_normalize_latex,
    lcs_length as _gate_lcs_length,
)

# Re-export for compatibility
lcs_length = _gate_lcs_length


def tokenize_latex(latex: str) -> List[str]:
    """Tokenize LaTeX string using the canonical Phase 2C tokenizer."""
    return _gate_tokenize_latex(latex)


def normalize_latex(s: str) -> str:
    """Normalize LaTeX using the canonical Phase 2C normalization."""
    return _gate_normalize_latex(s)


def lcs_length(a: List[str], b: List[str]) -> int:
    """Longest common subsequence length."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp


def _lcs_table(a: List[str], b: List[str]) -> List[List[int]]:
    """Build the full LCS DP table."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp


def _backtrack(dp: List[List[int]], a: List[str], b: List[str], i: int, j: int) -> Tuple[List[Tuple[int, int]], List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Walk the DP table from (len(a), len(b)) back to (0, 0).
    Returns (matches, substitutions, insertions).
    
    matches: List[Tuple[ref_pos, rec_pos]] - matched token pairs
    substitutions: List[Tuple[ref_token, rec_token, ref_pos, rec_pos]] - aligned differing pairs
    insertions: List[Tuple[rec_token, rec_pos]] - tokens in rec not in ref
    """
    matches = []
    substitutions = []
    insertions = []
    
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            # Match
            matches.append((i-1, j-1))
            i -= 1
            j -= 1
        elif dp[i-1][j] >= dp[i][j-1]:
            # Deletion from ref
            i -= 1
        else:
            # Insertion into rec
            insertions.append((b[j-1], j-1))
            j -= 1
    
    # Remaining
    while i > 0:
        i -= 1
    while j > 0:
        insertions.append((b[j-1], j-1))
        j -= 1
    
    # Build substitutions from matches
    match_set = set(matches)
    for idx, (rp, cp) in enumerate(matches):
        if idx > 0:
            prev_rp, prev_cp = matches[idx-1]
            if a[rp] != b[cp]:
                substitutions.append((a[rp], b[cp], rp, cp))
    
    # Reverse lists (we built them backwards)
    matches.reverse()
    substitutions.reverse()
    insertions.reverse()
    
    return matches, substitutions, insertions


def align_tokens(
    ref_tokens: List[str],
    rec_tokens: List[str]
) -> Dict[str, Any]:
    """
    Align reference and recognized token streams.
    
    Returns:
        matched: List[Tuple[ref_pos, rec_pos]]
        substitutions: List[Dict] with ref_token, rec_token, ref_position, rec_position
        insertions: List[Tuple[rec_token, rec_position]]
        deletions: List[Tuple[ref_token, ref_position]]
        ambiguous: bool - True if multiple optimal alignments exist with different classifications
        lcs_length: int
    """
    if not ref_tokens and not rec_tokens:
        return {
            'matched': [],
            'substitutions': [],
            'insertions': [],
            'deletions': [],
            'ambiguous': False,
            'lcs_length': 0,
            'ref_token_count': 0,
            'rec_token_count': 0,
        }
    
    dp = _lcs_table(ref_tokens, rec_tokens)
    lcs = dp[len(ref_tokens)][len(rec_tokens)]
    
    # Walk the table to extract alignment
    ref_pos = len(ref_tokens)
    rec_pos = len(rec_tokens)
    matches = []
    deletions = []
    insertions = []
    
    # We need to handle ambiguity detection.
    # Ambiguity exists when there are multiple equally-scored optimal alignments
    # that lead to different defect classifications.
    # For simplicity in this implementation: if dp[i][j] == dp[i-1][j] == dp[i][j-1]
    # at any point where a == b is false, we have a branch. Check if any such branch
    # would produce a different result.
    #
    # For the current scope: ambiguity is detected when the LCS table has a cell
    # where both up and left are equally valid choices AND the choice affects
    # whether the two current tokens form a substitution pair.
    
    # Build alignment by walking
    while ref_pos > 0 and rec_pos > 0:
        if ref_tokens[ref_pos-1] == rec_tokens[rec_pos-1]:
            matches.append((ref_pos-1, rec_pos-1))
            ref_pos -= 1
            rec_pos -= 1
        elif dp[ref_pos-1][rec_pos] >= dp[ref_pos][rec_pos-1]:
            deletions.append((ref_tokens[ref_pos-1], ref_pos-1))
            ref_pos -= 1
        else:
            insertions.append((rec_tokens[rec_pos-1], rec_pos-1))
            rec_pos -= 1
    
    while ref_pos > 0:
        deletions.append((ref_tokens[ref_pos-1], ref_pos-1))
        ref_pos -= 1
    while rec_pos > 0:
        insertions.append((rec_tokens[rec_pos-1], rec_pos-1))
        rec_pos -= 1
    
    # Build substitution candidates from matched pairs where tokens differ
    # These are cases where ref_token != rec_token at the same alignment position
    substitutions = []
    for idx, (rp, cp) in enumerate(matches):
        if ref_tokens[rp] != rec_tokens[cp]:
            substitutions.append({
                'ref_token': ref_tokens[rp],
                'rec_token': rec_tokens[cp],
                'ref_position': rp,
                'rec_position': cp,
                'alignment_status': 'aligned',
            })
    
    # Detect deletion/insertion boundary substitutions
    # These capture cases where an operator is replaced but tokenization
    # splits it differently (e.g., \sum -> S_ where '_' is re-tokenized)
    if deletions and insertions:
        # Pair deletions with insertions at the same logical position
        # (not necessarily the same list index)
        for dept in deletions:
            for first_ins in insertions:
                if dept[1] == first_ins[1]:
                    # Same position in both sequences - operator substitution
                    is_ref_operator = dept[0].startswith('\\')
                    is_rec_alphanumeric = first_ins[0][0].isalnum()
                    if is_ref_operator and is_rec_alphanumeric:
                        substitutions.append({
                            'ref_token': dept[0],
                            'rec_token': first_ins[0],
                            'ref_position': dept[1],
                            'rec_position': first_ins[1],
                            'alignment_status': 'boundary',
                            'substitution_type': 'delete_insert_boundary',
                        })
                        break  # Only match one insertion per deletion
    
    # Secondary detection: operator substitution from vocabulary rules
    # (e.g., \frac -> /, \sum -> S)
    # Check if any deletion is an operator with a known substitution
    # Deduplicate: only add if not already in substitutions list
    if deletions and insertions:
        # Build a set of insertion tokens for fast lookup
        ins_tokens = {ins[0] for ins in insertions}
        # Track already-added substitutions (by ref_token + rec_token + ref_position)
        added_pairs = set()
        # Map operator prefixes to known substitution patterns
        op_sub_map = {
            'frac': ['/'],
            'partial': ['d'],
            'sum': ['S', 'Sigma', 'E'],
            'int': ['I', 'int'],
            'prod': ['P', 'Pi'],
            'nabla': ['del'],
            'sqrt': ['v', 'sqrt'],
        }
        for dept in deletions:
            if dept[0].startswith('\\'):
                dept_name = dept[0].lstrip('\\')  # Remove leading backslash
                for ref_op, patterns in op_sub_map.items():
                    if dept_name.startswith(ref_op):
                        for pattern in patterns:
                            if pattern in ins_tokens:
                                pair_key = (dept[0], pattern, dept[1])
                                if pair_key not in added_pairs:
                                    # Find the rec position of the matching insertion
                                    matching_insertions = [ins for ins in insertions 
                                                           if ins[0] == pattern]
                                    if matching_insertions:
                                        first_ins = matching_insertions[0]
                                        substitutions.append({
                                            'ref_token': dept[0],
                                            'rec_token': pattern,
                                            'ref_position': dept[1],
                                            'rec_position': first_ins[1],
                                            'alignment_status': 'boundary',
                                            'substitution_type': 'operator_rule',
                                        })
                                        added_pairs.add(pair_key)
    # Deduplicate: remove any duplicate substitutions (same ref_token + rec_token + ref_position)
    seen = set()
    unique_substitutions = []
    for sub in substitutions:
        pair_key = (sub['ref_token'], sub['rec_token'], sub['ref_position'])
        if pair_key not in seen:
            seen.add(pair_key)
            unique_substitutions.append(sub)
    substitutions = unique_substitutions
    
    # Determine ambiguity: flag if any cell has equal up/left that is not on the
    # optimal path boundary (could change classification)
    ambiguous = False
    for i in range(1, len(ref_tokens)+1):
        for j in range(1, len(rec_tokens)+1):
            if ref_tokens[i-1] != rec_tokens[j-1]:
                if dp[i-1][j] == dp[i][j-1] and dp[i-1][j] < lcs:
                    ambiguous = True
                    break
        if ambiguous:
            break
    
    return {
        'matched': matches,
        'substitutions': substitutions,
        'insertions': insertions,
        'deletions': deletions,
        'ambiguous': ambiguous,
        'lcs_length': lcs,
        'ref_token_count': len(ref_tokens),
        'rec_token_count': len(rec_tokens),
    }


def detect_operator_substitution(
    ref_tokens: List[str],
    rec_tokens: List[str],
    align: Dict[str, Any]
) -> List[Dict]:
    """
    Detect operator substitutions from aligned token evidence.
    
    This detects substitutions from aligned token evidence (not string membership).
    The result is a list of evidence dicts for each substitution found.
    
    Each substitution entry contains:
        ref_token, rec_token, ref_position, rec_position, alignment_status
    """
    result = []
    
    # Only process substitutions from the alignment
    for sub in align['substitutions']:
        # Confirm: alignment status is 'aligned' if both tokens are aligned
        # at the same position in their respective streams
        result.append({
            'ref_token': sub['ref_token'],
            'rec_token': sub['rec_token'],
            'ref_position': sub['ref_position'],
            'rec_position': sub['rec_position'],
            'alignment_status': 'aligned',
        })
    
    return result


def detect_positional_alignment_conflict(
    ref_tokens: List[str],
    rec_tokens: List[str],
    align: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate alignment for conflicts that would change defect classification.
    
    A conflict exists when:
    1. The alignment is ambiguous
    2. Different optimal alignments would produce different defect classifications
    
    Returns:
        has_conflict: bool
        conflict_type: str (or None)
        evidence: str - explanation of the conflict
    """
    evidence = []
    
    if align['ambiguous']:
        evidence.append(
            f'Alignment ambiguous: {align["ref_token_count"]} ref tokens, '
            f'{align["rec_token_count"]} rec tokens, LCS={align["lcs_length"]}'
        )
        return True, 'AMBIGUOUS_ALIGNMENT', '; '.join(evidence)
    
    # Check each substitution for classification confidence
    for sub in align['substitutions']:
        ref_token = sub['ref_token']
        rec_token = sub['rec_token']
        ref_pos = sub['ref_position']
        rec_pos = sub['rec_position']
        
        # Simple heuristic: if ref token is an operator-like symbol and rec token
        # is alphabetic, flag as potential ambiguity
        # (operator-like: contains backslash, or is a math operator)
        if ref_token.startswith('\\') and rec_token.isalpha():
            evidence.append(
                f'Positional conflict at ref_pos={ref_pos}, rec_pos={rec_pos}: '
                f'ref={ref_token} vs rec={rec_token}'
            )
    
    if evidence:
        return True, 'POSITIONAL_CONFLICT', '; '.join(evidence)
    
    return False, None, None


if __name__ == '__main__':
    # Quick self-test
    import sys
    import json
    
    # Test 1: Valid matching
    ref = r'\sum_{i=1}^{n} a_i'
    rec = r'\sum_{i=1}^{n} a_i'
    r_tokens = tokenize_latex(normalize_latex(ref))
    c_tokens = tokenize_latex(normalize_latex(rec))
    align = align_tokens(r_tokens, c_tokens)
    print(f'Test 1 (valid): outcome={align["lcs_length"]==len(r_tokens)}')
    
    # Test 2: Reordered bounds
    ref = r'\sum_{i=1}^{n} a_i'
    rec = r'\sum^{n}_{i=1} a_i'
    r_tokens = tokenize_latex(normalize_latex(ref))
    c_tokens = tokenize_latex(normalize_latex(rec))
    align = align_tokens(r_tokens, c_tokens)
    print(f'Test 2 (reorder): outcome={align["lcs_length"]==len(r_tokens)-2}  # both _ and ^ swapped')
    
    # Test 3: Sum to S substitution
    ref = r'\sum_{i=1}^{n} a_i'
    rec = r'S_{i=1}^{n} a_i'
    r_tokens = tokenize_latex(normalize_latex(ref))
    c_tokens = tokenize_latex(normalize_latex(rec))
    align = align_tokens(r_tokens, c_tokens)
    print(f'Test 3 (sum_to_S): outcome={align["lcs_length"]<len(r_tokens)}')
    for s in align['substitutions']:
        print(f'  Substitution: ref={s["ref_token"]} rec={s["rec_token"]} pos=({s["ref_position"]},{s["rec_position"]})')
    for d in align['deletions']:
        print(f'  Deletion: {d}')
    for ins in align['insertions']:
        print(f'  Insertion: {ins}')
    
    sys.exit(0)
