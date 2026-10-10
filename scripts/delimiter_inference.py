"""
Delimiter Inference Layer
==========================

Pairs delimiter tokens into typed AST nodes and infers delimiter TYPE from
structural context when the token itself is ambiguous.

Input:  a recovered string containing identity tokens
        (langle, rangle, lVert, rVert, lfloor, rfloor, lceil, rceil, |)
Output: a list of typed delimiter nodes with resolved types

This module does NOT solve equations. It preserves structure so the AST layer
can represent Floor(x), Ceil(x), Norm(x), AngleBracket(...), Abs(x), and
Conditional(value, condition) as distinct node types.

Usage:
    from delimiter_inference import DelimiterInferer, infer_delimiters
    nodes = infer_delimiters("lVert x rVert + lfloor y rfloor")
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ============================================================================
# Typed delimiter nodes
# ============================================================================

@dataclass
class DelimiterNode:
    """A paired delimiter with its content and resolved type."""
    open_token: str
    close_token: str
    content: str
    delim_type: str  # 'angle', 'norm', 'floor', 'ceil', 'abs', 'conditional'
    start_pos: int
    end_pos: int
    confidence: float = 1.0  # 1.0 = certain, <1.0 = inferred
    notes: List[str] = field(default_factory=list)


@dataclass
class UnmatchedDelimiter:
    """A delimiter token that could not be paired."""
    token: str
    pos: int
    reason: str


# ============================================================================
# Token definitions
# ============================================================================

OPEN_TOKENS = {
    "langle": "angle",
    "lVert": "norm",
    "lfloor": "floor",
    "lceil": "ceil",
    "|": "bar",  # ambiguous: abs or conditional
}

CLOSE_TOKENS = {
    "rangle": "angle",
    "rVert": "norm",
    "rfloor": "floor",
    "rceil": "ceil",
    "|": "bar",
}

# All delimiter tokens (for scanning)
ALL_DELIM_TOKENS = set(OPEN_TOKENS.keys()) | set(CLOSE_TOKENS.keys())


# ============================================================================
# Pairing algorithm
# ============================================================================

def _find_tokens(s: str) -> List[Tuple[str, int]]:
    """Find all delimiter tokens in string, in order.
    Returns list of (token, position) tuples.
    """
    tokens = []
    i = 0
    while i < len(s):
        # Try multi-char tokens first (longest match)
        matched = False
        for tok in ("lVert", "rVert", "lfloor", "rfloor", "lceil", "rceil", "langle", "rangle"):
            if s[i:i+len(tok)] == tok:
                tokens.append((tok, i))
                i += len(tok)
                matched = True
                break
        if not matched:
            if s[i] == "|":
                tokens.append(("|", i))
            i += 1
    return tokens


def _pair_tokens(s: str, tokens: List[Tuple[str, int]]) -> Tuple[List[DelimiterNode], List[UnmatchedDelimiter]]:
    """Pair open/close tokens using a stack.
    Returns (paired_nodes, unmatched).

    Special case: '|' is both OPEN and CLOSE. When the stack top is also '|',
    the current '|' closes it. Otherwise it opens a new pair.
    """
    paired = []
    unmatched = []
    stack = []  # stack of (token, pos, expected_close_type)

    for tok, pos in tokens:
        if tok == "|":
            # Ambiguous: check if stack top is also '|'
            if stack and stack[-1][0] == "|":
                # Close the open '|'
                open_tok, open_pos, _ = stack.pop()
                content = s[open_pos + 1:pos]
                paired.append(DelimiterNode(
                    open_token="|",
                    close_token="|",
                    content=content,
                    delim_type="bar",
                    start_pos=open_pos,
                    end_pos=pos + 1,
                ))
            else:
                # Open a new '|'
                stack.append(("|", pos, "bar"))
        elif tok in OPEN_TOKENS:
            expected = OPEN_TOKENS[tok]
            stack.append((tok, pos, expected))
        elif tok in CLOSE_TOKENS:
            actual = CLOSE_TOKENS[tok]
            # Find matching open in stack (most recent unmatched open of same type)
            found = False
            for idx in range(len(stack) - 1, -1, -1):
                open_tok, open_pos, expected_type = stack[idx]
                if expected_type == actual:
                    # Found match
                    content = s[open_pos + len(open_tok):pos]
                    paired.append(DelimiterNode(
                        open_token=open_tok,
                        close_token=tok,
                        content=content,
                        delim_type=actual,
                        start_pos=open_pos,
                        end_pos=pos + len(tok),
                    ))
                    stack.pop(idx)
                    found = True
                    break
            if not found:
                unmatched.append(UnmatchedDelimiter(
                    token=tok, pos=pos,
                    reason=f"no matching open for {tok}"
                ))

    # Remaining stack items are unmatched opens
    for open_tok, open_pos, expected_type in stack:
        unmatched.append(UnmatchedDelimiter(
            token=open_tok, pos=open_pos,
            reason=f"no matching close for {open_tok}"
        ))

    return paired, unmatched


# ============================================================================
# Type inference for ambiguous bars
# ============================================================================

def _infer_bar_type(node: DelimiterNode, context_before: str, context_after: str) -> str:
    """Infer whether |...| is Abs or Conditional.

    Heuristics:
    - If content contains a relation token (>, <, =, in, etc.) → Conditional
    - If content is a simple expression → Abs
    - If preceded by E[ or P( or similar expectation/probability → Conditional
    - If content has a comma or semicolon → Conditional (set builder)
    """
    content = node.content.strip()

    # Conditional indicators in content
    conditional_patterns = [
        r'>', r'<', r'=', r'\bin\b', r'\bforall\b', r'\bexists\b',
        r',', r';', r':', r'\bobar\b',
    ]
    for pat in conditional_patterns:
        if re.search(pat, content):
            return "conditional"

    # Context-based: expectation/probability before
    if re.search(r'E\s*\[|P\s*\(|Pr\s*\(', context_before):
        return "conditional"

    # Default: absolute value
    return "abs"


# ============================================================================
# Structural similarity inference
# ============================================================================

def _infer_from_similar_equations(
    target_node: DelimiterNode,
    all_equations: List[str],
    target_eq_idx: int,
) -> Tuple[str, float, List[str]]:
    """Look at structurally similar equations to infer delimiter type.

    If the same content appears in other equations with a KNOWN delimiter type,
    use that as evidence.

    Returns (inferred_type, confidence, notes).
    """
    target_content = target_node.content.strip()
    if not target_content:
        return target_node.delim_type, 0.5, ["empty content, cannot infer"]

    # Find equations with similar content
    similar_types = []
    notes = []

    for i, eq in enumerate(all_equations):
        if i == target_eq_idx:
            continue
        # Check if this equation contains the same content
        if target_content in eq:
            # Find what delimiter wraps it in that equation
            # Look for the content surrounded by delimiters
            for match in re.finditer(
                r'(lVert|lVert|lfloor|lfloor|lceil|lceil|langle|langle|\|)' + re.escape(target_content) + r'(rVert|rVert|rfloor|rfloor|rceil|rceil|rangle|rangle|\|)',
                eq
            ):
                open_tok = match.group(1)
                if open_tok in OPEN_TOKENS:
                    similar_types.append(OPEN_TOKENS[open_tok])
                    notes.append(f"found in eq {i} with {open_tok}")

    if similar_types:
        # Majority vote
        from collections import Counter
        counts = Counter(similar_types)
        best_type, best_count = counts.most_common(1)[0]
        confidence = best_count / len(similar_types)
        return best_type, confidence, notes

    return target_node.delim_type, 0.5, ["no similar equations found"]


# ============================================================================
# Main inferer
# ============================================================================

class DelimiterInferer:
    """Infer delimiter types from recovered strings."""

    def __init__(self, equations: List[str] = None):
        self.equations = equations or []
        self._type_cache = {}  # content -> (type, confidence)

    def infer(self, s: str, eq_idx: int = -1) -> List[DelimiterNode]:
        """Infer all delimiters in a string.
        Returns list of DelimiterNode with resolved types.
        """
        tokens = _find_tokens(s)
        paired, unmatched = _pair_tokens(s, tokens)

        # Sort by position
        paired.sort(key=lambda n: n.start_pos)

        # Handle unmatched '|' as conditional separators
        # E[X | X > 0] has a single '|' that is a conditional, not abs
        for unmatched_item in unmatched:
            if unmatched_item.token == "|":
                context_before = s[:unmatched_item.pos]
                context_after = s[unmatched_item.pos:]
                # If the context suggests expectation/probability, it's conditional
                if re.search(r'E\s*\[|P\s*\(|Pr\s*\(', context_before):
                    paired.append(DelimiterNode(
                        open_token="|",
                        close_token="|",
                        content=s[unmatched_item.pos + 1:].strip().rstrip("]").strip(),
                        delim_type="conditional",
                        start_pos=unmatched_item.pos,
                        end_pos=unmatched_item.pos + 1,
                        confidence=0.8,
                        notes=["inferred conditional from single bar in expectation context"],
                    ))

        # Resolve ambiguous types
        for node in paired:
            if node.delim_type == "bar":
                # Get context
                context_before = s[:node.start_pos]
                context_after = s[node.end_pos:]
                node.delim_type = _infer_bar_type(node, context_before, context_after)
                node.notes.append(f"bar resolved to {node.delim_type} from context")

        # Handle unmatched lVert/rVert pairs (MathML single-glyph norm): if the
        # token is unmatched and we have the opening half, report as norm with
        # reduced confidence since we inferred the close from alternation.
        for unmatched_item in unmatched:
            if unmatched_item.token in ("lVert", "rVert"):
                # Only report if we have a balance hint; otherwise skip
                if unmatched_item.token == "lVert":
                    paired.append(DelimiterNode(
                        open_token="lVert",
                        close_token="rVert",
                        content=unmatched_item.pos and s[unmatched_item.pos:],
                        delim_type="norm",
                        start_pos=unmatched_item.pos,
                        end_pos=unmatched_item.pos + len("lVert"),
                        confidence=0.7,
                        notes=["MathML single-glyph norm: inferred close via alternation"],
                    ))

        # Resolve ambiguous types
        for node in paired:
            if node.delim_type == "bar":
                # Get context
                context_before = s[:node.start_pos]
                context_after = s[node.end_pos:]
                node.delim_type = _infer_bar_type(node, context_before, context_after)
                node.notes.append(f"bar resolved to {node.delim_type} from context")

            # Try structural similarity inference for low-confidence cases
            if node.confidence < 1.0 and self.equations:
                inferred, conf, notes = _infer_from_similar_equations(
                    node, self.equations, eq_idx
                )
                if conf > node.confidence:
                    node.delim_type = inferred
                    node.confidence = conf
                    node.notes.extend(notes)

        return paired

    def to_ast_nodes(self, s: str, eq_idx: int = -1) -> List[dict]:
        """Convert to AST-ready dict format."""
        nodes = self.infer(s, eq_idx)
        result = []
        for node in nodes:
            result.append({
                "type": node.delim_type,
                "content": node.content,
                "start": node.start_pos,
                "end": node.end_pos,
                "confidence": node.confidence,
                "notes": node.notes,
            })
        return result


def infer_delimiters(s: str, equations: List[str] = None, eq_idx: int = -1) -> List[DelimiterNode]:
    """Convenience function: infer delimiters in a string."""
    inferer = DelimiterInferer(equations)
    return inferer.infer(s, eq_idx)


# ============================================================================
# Self-test
# ============================================================================

if __name__ == "__main__":
    # Test cases
    test_cases = [
        # (input, expected_type)
        ("lVert x rVert", "norm"),
        ("lfloor x rfloor", "floor"),
        ("lceil x rceil", "ceil"),
        ("langle x rangle", "angle"),
        ("|x|", "abs"),
        ("|x > 0|", "conditional"),
        ("E[X | X > 0]", "conditional"),
        ("lVert x rVert + lfloor y rfloor", "norm"),  # first one
    ]

    print("=== Delimiter Inference Self-Test ===")
    all_pass = True
    for s, expected in test_cases:
        nodes = infer_delimiters(s)
        if not nodes:
            print(f"  FAIL: {s!r} -> no nodes")
            all_pass = False
            continue
        # For multi-delimiter cases, check the first one
        actual = nodes[0].delim_type
        status = "PASS" if actual == expected else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  {status}: {s!r} -> {actual} (expected {expected})")
        for n in nodes:
            print(f"         {n.open_token}...{n.close_token} = {n.delim_type} "
                  f"(conf={n.confidence:.2f}, notes={n.notes})")

    print(f"\n{'ALL PASS' if all_pass else 'SOME FAILED'}")
