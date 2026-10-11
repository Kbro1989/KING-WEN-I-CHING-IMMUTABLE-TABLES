"""
Checkerboard Math Extraction & Resolution System
=================================================
Extracts all math from arXiv HTML, builds position-level constraint table,
creates 3rd-dimension descriptors per box, resolves unknown slots,
cross-references with Wolfram notation, and measures match rates.

Usage:
    python scripts/math_checkerboard.py --html <path> --output <dir>
"""

import sys
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

# ============================================================================
# LAYER 1: HTML EXTRACTION
# ============================================================================

def extract_math_with_context(html_path):
    """Extract all math tags with full context from arXiv HTML."""
    with open(html_path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    math_tags = soup.find_all('math')
    
    results = []
    for i, tag in enumerate(math_tags):
        annotation = tag.find('annotation')
        latex = annotation.text.strip() if annotation else ""
        alttext = tag.get('alttext', '')
        display = tag.get('display', 'inline')
        intent = tag.get('intent', '')
        tag_id = tag.get('id', f'math_{i}')
        
        # Get surrounding context
        parent = tag.find_parent(['p', 'div'])
        context = ""
        if parent:
            context = parent.get_text(strip=True)[:500]
        
        # Get MathML structure
        mathml = str(tag)
        
        results.append({
            'index': i,
            'id': tag_id,
            'latex': latex,
            'alttext': alttext,
            'display': display,
            'intent': intent,
            'context': context,
            'mathml': mathml,
        })
    
    return results


# ============================================================================
# LAYER 2: POSITION-LEVEL CONSTRAINT TABLE
# ============================================================================

def build_constraint_table(math_entries):
    """Build position-level constraint table for each math entry."""
    table = []
    
    for entry in math_entries:
        latex = entry['latex']
        if not latex:
            continue
        
        # Parse LaTeX into tokens
        tokens = tokenize_latex(latex)
        
        # Build position constraints
        positions = []
        for pos_idx, token in enumerate(tokens):
            pos = {
                'pos_id': f"{entry['id']}_p{pos_idx}",
                'token': token,
                'pos_type': classify_token(token),
                'source_value': token,
                'descriptors': get_descriptors(token),
                'requirements': get_requirements(token),
                'polarity': 'positive',  # Will be updated after resolution
                'fidelity': 1.0,
                'candidate': token,
                'score': 0.0,
            }
            positions.append(pos)
        
        table.append({
            'entry_id': entry['id'],
            'latex': latex,
            'context': entry['context'],
            'positions': positions,
            'total_boxes': len(positions),
            'positive_boxes': 0,
            'negative_boxes': 0,
            'fidelity': 0.0,
            'status': 'unresolved',
        })
    
    return table


def tokenize_latex(latex):
    """Tokenize LaTeX into commands, brackets, scripts, numbers, variables."""
    latex = latex.strip()
    tokens = []
    i = 0
    while i < len(latex):
        ch = latex[i]
        if ch == "\\":
            j = i + 1
            if j < len(latex) and latex[j].isalpha():
                while j < len(latex) and latex[j].isalpha():
                    j += 1
                tokens.append(latex[i:j])
                i = j
                continue
            tokens.append(latex[i:j])
            i = j
        elif ch in "(){}[]|":
            tokens.append(ch)
            i += 1
        elif ch in "+-*/=<>":
            tokens.append(ch)
            i += 1
        elif ch in "^_":
            tokens.append(ch)
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < len(latex) and (latex[j].isdigit() or latex[j] == "."):
                j += 1
            tokens.append(latex[i:j])
            i = j
        elif ch.isalpha():
            j = i
            while j < len(latex) and latex[j].isalpha():
                j += 1
            tokens.append(latex[i:j])
            i = j
        elif ch == " ":
            i += 1
        else:
            tokens.append(ch)
            i += 1
    return tokens


def classify_token(token):
    """Classify a token into position type."""
    if token in ('\\frac', '\\dfrac', '\\tfrac', '\\cfrac'):
        return 'fraction'
    elif token in ('\\sum', '\\prod', '\\int', '\\oint', '\\iint', '\\iiint'):
        return 'big_operator'
    elif token in ('\\sqrt', '\\root'):
        return 'root'
    elif token in ('\\lim', '\\max', '\\min', '\\sup', '\\inf'):
        return 'limit_operator'
    elif token in ('\\sin', '\\cos', '\\tan', '\\cot', '\\sec', '\\csc',
                   '\\arcsin', '\\arccos', '\\arctan', '\\arccot',
                   '\\sinh', '\\cosh', '\\tanh', '\\coth', '\\sech', '\\csch',
                   '\\log', '\\ln', '\\exp'):
        return 'function'
    elif token in ('\\ell', '\\ellp'):
        return 'ell_variant'
    elif token in ('\\alpha', '\\beta', '\\gamma', '\\delta', '\\epsilon',
                   '\\zeta', '\\eta', '\\theta', '\\iota', '\\kappa', '\\lambda',
                   '\\mu', '\\nu', '\\xi', '\\pi', '\\rho', '\\sigma', '\\tau',
                   '\\upsilon', '\\phi', '\\chi', '\\psi', '\\omega',
                   '\\Gamma', '\\Delta', '\\Theta', '\\Lambda', '\\Xi', '\\Pi',
                   '\\Sigma', '\\Upsilon', '\\Phi', '\\Psi', '\\Omega'):
        return 'greek'
    elif token in ('\\mathbb', '\\mathcal', '\\mathfrak', '\\mathbf', '\\mathit'):
        return 'font_variant'
    elif token in ('\\leq', '\\geq', '\\neq', '\\approx', '\\sim', '\\simeq',
                   '\\cong', '\\propto', '\\equiv', '\\ll', '\\gg',
                   '\\subset', '\\supset', '\\subseteq', '\\supseteq',
                   '\\in', '\\notin', '\\ni', '\\mid',
                   '\\Rightarrow', '\\Leftarrow', '\\Leftrightarrow',
                   '\\rightarrow', '\\leftarrow', '\\mapsto', '\\to', '\\gets',
                   '\\implies', '\\iff', '\\wedge', '\\vee', '\\neg',
                   '\\forall', '\\exists', '\\cap', '\\cup', '\\setminus',
                   '\\emptyset', '\\infty', '\\partial', '\\nabla'):
        return 'relation'
    elif token in ('+', '-', '*', '/', '^', '_', '='):
        return 'operator'
    elif token in ('(', ')', '[', ']', '{', '}', '|', '\\|'):
        return 'bracket'
    elif token[0].isdigit() or (len(token) > 1 and token[0] == '.' and token[1].isdigit()):
        return 'number'
    elif token[0].isalpha():
        return 'variable'
    else:
        return 'unknown'


def get_descriptors(token):
    """Get descriptors for a token."""
    descriptors = []
    
    # Check for ell variant (Greek script 'l' used as metric)
    if token in ('\\ell', '\\\\ell'):
        descriptors.append('script_letter')
        descriptors.append('math_letter')
        descriptors.append('variable')
        descriptors.append('canonically_ellipsoid')
        return descriptors
    if token in ('\\ellp', '\\\\ellp'):
        descriptors.append('script_letter')
        descriptors.append('math_letter')
        descriptors.append('variable')
        descriptors.append('canonically_ellipsoid')
        descriptors.append('promptwise_norm_lp')
        return descriptors

    # Check for Greek
    greek_map = {
        '\\alpha': 'greek', '\\beta': 'greek', '\\gamma': 'greek',
        '\\delta': 'greek', '\\epsilon': 'greek', '\\zeta': 'greek',
        '\\eta': 'greek', '\\theta': 'greek', '\\iota': 'greek',
        '\\kappa': 'greek', '\\lambda': 'greek', '\\mu': 'greek',
        '\\nu': 'greek', '\\xi': 'greek', '\\pi': 'greek',
        '\\rho': 'greek', '\\sigma': 'greek', '\\tau': 'greek',
        '\\upsilon': 'greek', '\\phi': 'greek', '\\chi': 'greek',
        '\\psi': 'greek', '\\omega': 'greek',
    }
    if token in greek_map:
        descriptors.append('greek_letter')
    
    # Check for relation
    if token in ('\\leq', '\\geq', '\\neq', '\\approx', '\\sim', '\\simeq',
                 '\\cong', '\\propto', '\\equiv', '\\ll', '\\gg'):
        descriptors.append('relation')
        descriptors.append('non_equality')
    
    # Check for arrow
    if token in ('\\Rightarrow', '\\Leftarrow', '\\Leftrightarrow',
                 '\\rightarrow', '\\leftarrow', '\\mapsto', '\\to', '\\gets',
                 '\\implies', '\\iff'):
        descriptors.append('arrow')
        descriptors.append('non_equality')
    
    # Check for set
    if token in ('\\subset', '\\supset', '\\subseteq', '\\supseteq',
                 '\\in', '\\notin', '\\ni', '\\mid'):
        descriptors.append('set_relation')
        descriptors.append('non_equality')
    
    # Check for logic
    if token in ('\\wedge', '\\vee', '\\neg', '\\forall', '\\exists'):
        descriptors.append('logic')
        descriptors.append('non_equality')
    
    # Check for big operator
    if token in ('\\sum', '\\prod', '\\int', '\\oint', '\\iint', '\\iiint'):
        descriptors.append('big_operator')
        descriptors.append('has_limits')
    
    # Check for function
    if token in ('\\sin', '\\cos', '\\tan', '\\log', '\\exp', '\\sqrt'):
        descriptors.append('function')
        descriptors.append('has_argument')
    
    # Check for font variant
    if token in ('\\mathbb', '\\mathcal', '\\mathfrak', '\\mathbf', '\\mathit'):
        descriptors.append('font_variant')
        descriptors.append('has_argument')
    
    # Check for bracket
    if token in ('(', ')', '[', ']', '{', '}', '|', '\\\\|'):
        descriptors.append('bracket')
        if token in ('(', '[', '{', '|', '\\\|'):
            descriptors.append('opening')
        else:
            descriptors.append('closing')
    
    # Check for operator
    if token in ('+', '-', '*', '/', '^', '_', '='):
        descriptors.append('operator')
        if token == '=':
            descriptors.append('equality')
        elif token in ('^', '_'):
            descriptors.append('script')
        else:
            descriptors.append('arithmetic')
    
    # Check for number
    if token[0].isdigit() or (len(token) > 1 and token[0] == '.' and token[1].isdigit()):
        descriptors.append('number')
        descriptors.append('numeric')
    
    # Check for variable
    if token[0].isalpha() and token not in greek_map:
        descriptors.append('variable')
        descriptors.append('symbolic')
    
    return descriptors


def get_requirements(token):
    """Get requirements for a token to be positive."""
    requirements = []
    
    pos_type = classify_token(token)
    
    if pos_type == 'relation':
        requirements.append('must_preserve_relation_identity')
        requirements.append('must_not_collapse_to_equality')
        requirements.append('must_match_source_relation_type')
    elif pos_type == 'greek':
        requirements.append('must_preserve_greek_letter')
        requirements.append('must_match_source_glyph')
    elif pos_type == 'big_operator':
        requirements.append('must_preserve_operator')
        requirements.append('must_have_limits')
        requirements.append('must_have_index_variable')
    elif pos_type == 'function':
        requirements.append('must_preserve_function_name')
        requirements.append('must_have_argument')
    elif pos_type == 'bracket':
        requirements.append('must_balance')
        requirements.append('must_match_opening_closing')
    elif pos_type == 'number':
        requirements.append('must_be_well_formed_numeric')
        requirements.append('must_not_fabricate_value')
    elif pos_type == 'variable':
        requirements.append('must_be_valid_identifier')
        requirements.append('must_not_fabricate_symbol')
    elif pos_type == 'operator':
        requirements.append('must_be_valid_operator')
        if token == '=':
            requirements.append('must_have_exactly_one_equality')
    elif pos_type == 'font_variant':
        requirements.append('must_preserve_variant')
        requirements.append('must_have_argument')
    elif pos_type == 'unknown':
        requirements.append('must_resolve_from_context')
        requirements.append('must_match_known_usage')
    
    return requirements


# ============================================================================
# LAYER 3: RESOLUTION ENGINE
# ============================================================================

def resolve_unknown_slot(token, context, wolfram_map):
    """Resolve an unknown slot using context and Wolfram notation."""
    candidates = []
    
    # Check if it's a known relation
    if token in wolfram_map.get('relations', {}):
        candidates.append({
            'value': wolfram_map['relations'][token],
            'confidence': 0.9,
            'source': 'wolfram_relation',
        })
    
    # Check if it's a known operator
    if token in wolfram_map.get('operators', {}):
        candidates.append({
            'value': wolfram_map['operators'][token],
            'confidence': 0.8,
            'source': 'wolfram_operator',
        })
    
    # Check if it's a known Greek letter
    if token in wolfram_map.get('greek', {}):
        candidates.append({
            'value': wolfram_map['greek'][token],
            'confidence': 0.9,
            'source': 'wolfram_greek',
        })
    
    # Check context for clues
    if context:
        # Look for "Let X be" patterns
        let_match = re.search(r'Let\s+(\w+)\s+be', context)
        if let_match:
            candidates.append({
                'value': let_match.group(1),
                'confidence': 0.7,
                'source': 'context_let',
            })
        
        # Look for "where X is" patterns
        where_match = re.search(r'where\s+(\w+)\s+is', context)
        if where_match:
            candidates.append({
                'value': where_match.group(1),
                'confidence': 0.6,
                'source': 'context_where',
            })
    
    # Sort by confidence
    candidates.sort(key=lambda x: -x['confidence'])
    
    return candidates


def load_wolfram_map():
    """Load Wolfram notation map from reference."""
    return {
        'relations': {
            '≤': 'LessEqual', '≥': 'GreaterEqual', '≠': 'Unequal',
            '<': 'Less', '>': 'Greater', '=': 'Equal',
            '≈': 'ApproximateEqual', '≡': 'Congruent',
            '∼': 'TildeTilde', '∝': 'Proportional',
            '⊆': 'Subset', '⊂': 'SubsetEqual',
            '∈': 'Element', '∉': 'NotElement',
            '∧': 'And', '∨': 'Or', '¬': 'Not',
            '∀': 'ForAll', '∃': 'Exists',
            '→': 'Rule', '⟹': 'ImpliedRightArrow',
            '⟸': 'LeftArrow', '⟷': 'DoubleArrow',
            '↦': 'RuleDelayed',
        },
        'operators': {
            '+': 'Plus', '-': 'Minus', '*': 'Times', '/': 'Divide',
            '^': 'Power', '_': 'Subscript', '!': 'Factorial',
            '×': 'Times', '÷': 'Divide', '±': 'PlusMinus',
            '∩': 'Intersection', '∪': 'Union',
            '∑': 'Sum', '∏': 'Product', '∫': 'Integral',
            '∮': 'ContourIntegral', '∂': 'PartialD',
            '∇': 'Del', '√': 'Sqrt', '∞': 'Infinity',
        },
        'greek': {
            'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
            'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
            'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
            'ν': 'nu', 'ξ': 'xi', 'π': 'pi', 'ρ': 'rho',
            'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon', 'φ': 'phi',
            'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
            'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta',
            'Ε': 'Epsilon', 'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta',
            'Ι': 'Iota', 'Κ': 'Kappa', 'Λ': 'Lambda', 'Μ': 'Mu',
            'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron', 'Π': 'Pi',
            'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
            'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega',
        },
        'brackets': {
            '(': '(', ')': ')', '[': '[', ']': ']',
            '{': '{', '}': '}', '|': '|', '\\|': 'DoubleBracketingBar',
            '⌊': 'Floor', '⌋': 'Floor', '⌈': 'Ceiling', '⌉': 'Ceiling',
            '⟨': 'AngleBracket', '⟩': 'AngleBracket',
        },
        'functions': {
            'sin': 'Sin', 'cos': 'Cos', 'tan': 'Tan',
            'cot': 'Cot', 'sec': 'Sec', 'csc': 'Csc',
            'arcsin': 'ArcSin', 'arccos': 'ArcCos', 'arctan': 'ArcTan',
            'sinh': 'Sinh', 'cosh': 'Cosh', 'tanh': 'Tanh',
            'log': 'Log', 'ln': 'Log', 'exp': 'Exp',
            'max': 'Max', 'min': 'Min', 'sup': 'Sup', 'inf': 'Inf',
            'lim': 'Limit', 'argmax': 'ArgMax', 'argmin': 'ArgMin',
        },
    }


# ============================================================================
# LAYER 4: SOLVER
# ============================================================================

def solve_equation(latex, wolfram_map):
    """Attempt to solve a LaTeX equation."""
    # Check for equality
    if '=' not in latex:
        return {
            'solvable': False,
            'reason': 'no_equality',
            'solution': None,
        }
    
    # Check for non-equality relations
    non_eq_relations = ['\\leq', '\\geq', '\\neq', '\\approx', '\\sim',
                        '\\simeq', '\\cong', '\\propto', '\\equiv',
                        '\\subset', '\\supset', '\\subseteq', '\\supseteq',
                        '\\in', '\\notin', '\\ni', '\\mid',
                        '\\Rightarrow', '\\Leftarrow', '\\Leftrightarrow',
                        '\\rightarrow', '\\leftarrow', '\\mapsto', '\\to',
                        '\\gets', '\\implies', '\\iff', '\\wedge', '\\vee',
                        '\\neg', '\\forall', '\\exists']
    
    for rel in non_eq_relations:
        if rel in latex:
            return {
                'solvable': False,
                'reason': f'non_equality_relation:{rel}',
                'solution': None,
            }
    
    # Try to parse and solve
    try:
        # Simple linear equations: ax + b = c
        # This is a placeholder for actual SymPy solving
        return {
            'solvable': True,
            'reason': 'linear_equation',
            'solution': 'parsed',
        }
    except Exception as e:
        return {
            'solvable': False,
            'reason': f'parse_error:{str(e)}',
            'solution': None,
        }


# ============================================================================
# LAYER 5: MATCH RATE MEASUREMENT
# ============================================================================

def measure_match_rates(constraint_table):
    """Measure how many formulas match between extraction and resolution."""
    total = len(constraint_table)
    resolved = 0
    positive = 0
    negative = 0
    
    for entry in constraint_table:
        if entry['status'] == 'resolved':
            resolved += 1
        if entry['fidelity'] >= 0.8:
            positive += 1
        elif entry['fidelity'] < 0.3:
            negative += 1
    
    return {
        'total_entries': total,
        'resolved': resolved,
        'positive': positive,
        'negative': negative,
        'unresolved': total - resolved,
        'resolution_rate': resolved / total if total > 0 else 0,
        'positive_rate': positive / total if total > 0 else 0,
        'negative_rate': negative / total if total > 0 else 0,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Checkerboard Math Extraction')
    parser.add_argument('--html', required=True, help='Path to arXiv HTML file')
    parser.add_argument('--output', default='DATASETS/checkerboard_output', help='Output directory')
    args = parser.parse_args()
    
    print(f"Loading HTML: {args.html}")
    math_entries = extract_math_with_context(args.html)
    print(f"Extracted {len(math_entries)} math entries")
    
    print("Building constraint table...")
    constraint_table = build_constraint_table(math_entries)
    
    print("Loading Wolfram notation map...")
    wolfram_map = load_wolfram_map()
    
    print("Resolving unknown slots...")
    for entry in constraint_table:
        for pos in entry['positions']:
            if pos['pos_type'] == 'unknown':
                candidates = resolve_unknown_slot(
                    pos['token'], entry['context'], wolfram_map
                )
                if candidates:
                    pos['candidate'] = candidates[0]['value']
                    pos['polarity'] = 'positive'
                    pos['fidelity'] = candidates[0]['confidence']
                else:
                    pos['polarity'] = 'negative'
                    pos['fidelity'] = 0.0
        
        # Update entry stats
        entry['positive_boxes'] = sum(1 for p in entry['positions'] if p['polarity'] == 'positive')
        entry['negative_boxes'] = sum(1 for p in entry['positions'] if p['polarity'] == 'negative')
        entry['fidelity'] = entry['positive_boxes'] / entry['total_boxes'] if entry['total_boxes'] > 0 else 0
        entry['status'] = 'resolved' if entry['fidelity'] >= 0.8 else 'partial' if entry['fidelity'] >= 0.3 else 'unresolved'
    
    print("Measuring match rates...")
    match_rates = measure_match_rates(constraint_table)
    
    # Save output
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'constraint_table.json', 'w') as f:
        json.dump(constraint_table, f, indent=2)
    
    with open(output_dir / 'match_rates.json', 'w') as f:
        json.dump(match_rates, f, indent=2)
    
    print(f"\nResults:")
    print(f"  Total entries: {match_rates['total_entries']}")
    print(f"  Resolved: {match_rates['resolved']} ({match_rates['resolution_rate']:.1%})")
    print(f"  Positive: {match_rates['positive']} ({match_rates['positive_rate']:.1%})")
    print(f"  Negative: {match_rates['negative']} ({match_rates['negative_rate']:.1%})")
    print(f"\nOutput saved to: {output_dir}")


if __name__ == '__main__':
    main()
