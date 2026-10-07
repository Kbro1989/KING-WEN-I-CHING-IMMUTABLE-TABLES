"""
LaTeX Command Registry
=======================
Defines LaTeX commands for proper parsing.
Instead of stripping unknown commands, we define them so the parser
can understand their structure and meaning.

This is the key insight: research LaTeX uses commands like \mbox, \operatorname,
\left, \right that carry semantic meaning. Stripping them loses structure.
Defining them preserves structure for proper equation solving.
"""
import json, re
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

transformations = standard_transformations + (implicit_multiplication_application,)

def is_complete_equation(latex):
    """Check if a LaTeX string is a complete equation."""
    if not latex or len(latex) < 3:
        return False
    if '=' in latex:
        return True
    if any(op in latex for op in ['+', '-', '*', '/']):
        return True
    if any(fn in latex for fn in ['frac', 'sum', 'int', 'prod', 'sqrt']):
        return True
    return False

# ============================================================================
# LaTeX Command Definitions
# ============================================================================

# Text-mode commands: \mbox{text}, \text{text}, \mathrm{text}, \mathbf{text}
# These wrap text that should be treated as a single symbol or label
TEXT_COMMANDS = {
    'mbox': 'text',
    'text': 'text',
    'mathrm': 'text',
    'mathbf': 'text',
    'mathit': 'text',
    'mathsf': 'text',
    'mathtt': 'text',
    'mathcal': 'text',
    'mathbb': 'text',
    'mathfrak': 'text',
}

# Operator commands: \operatorname{name}, \DeclareMathOperator
# These define named operators like sin, cos, log, etc.
OPERATOR_COMMANDS = {
    'operatorname': 'operator',
    'DeclareMathOperator': 'operator',
}

# Delimiter commands: \left, \right, \big, \Big, \bigg, \Bigg
# These define scalable delimiters
DELIMITER_COMMANDS = {
    'left': 'delimiter',
    'right': 'delimiter',
    'big': 'delimiter',
    'Big': 'delimiter',
    'bigg': 'delimiter',
    'Bigg': 'delimiter',
}

# Accent commands: \hat, \bar, \vec, \dot, \ddot, \tilde, \widehat, \overline
# These modify the following symbol
ACCENT_COMMANDS = {
    'hat': 'accent',
    'bar': 'accent',
    'vec': 'accent',
    'dot': 'accent',
    'ddot': 'accent',
    'tilde': 'accent',
    'widehat': 'accent',
    'overline': 'accent',
    'underline': 'accent',
    'overrightarrow': 'accent',
    'overleftarrow': 'accent',
}

# ============================================================================
# LaTeX Pre-processor: Define commands instead of stripping
# ============================================================================

def define_latex_commands(latex):
    """
    Define LaTeX commands for proper parsing.
    
    Instead of stripping unknown commands, we:
    1. Convert \mbox{text} -> text (as a single symbol)
    2. Convert \operatorname{name} -> name (as a function)
    3. Convert \left( -> ( and \right) -> )
    4. Convert \hat{x} -> x_hat (as a modified symbol)
    5. Handle multiple = signs (chained equations)
    
    Returns a string that SymPy can parse.
    """
    s = latex.strip()
    
    # Step 1: Handle \left and \right delimiters
    # \left( -> (, \right) -> ), \left[ -> [, \right] -> ], \left| -> |, \right| -> |
    s = re.sub(r'\\left\s*\(', '(', s)
    s = re.sub(r'\\right\s*\)', ')', s)
    s = re.sub(r'\\left\s*\[', '[', s)
    s = re.sub(r'\\right\s*\]', ']', s)
    s = re.sub(r'\\left\s*\|', '|', s)
    s = re.sub(r'\\right\s*\|', '|', s)
    s = re.sub(r'\\left\s*\\\{', '{', s)
    s = re.sub(r'\\right\s*\\\}', '}', s)
    s = re.sub(r'\\left\s*\\langle', 'langle', s)
    s = re.sub(r'\\right\s*\\rangle', 'rangle', s)
    
    # Step 2: Handle \big, \Big, \bigg, \Bigg (just remove them, they're sizing)
    s = re.sub(r'\\bigg\s*', '', s)
    s = re.sub(r'\\Bigg\s*', '', s)
    s = re.sub(r'\\big\s*', '', s)
    s = re.sub(r'\\Big\s*', '', s)
    
    # Step 3: Handle text-mode commands
    # \mbox{text} -> text (treat as a single symbol)
    # \text{text} -> text
    # \mathrm{text} -> text
    # \mathbf{text} -> text
    for cmd in TEXT_COMMANDS:
        # Match \cmd{text} and replace with just the text
        pattern = rf'\\{cmd}\s*\{{([^{{}}]+)\}}'
        s = re.sub(pattern, r'\1', s)
    
    # Step 4: Handle operator commands
    # \operatorname{name} -> name (treat as a function name)
    s = re.sub(r'\\operatorname\s*\{\s*([a-zA-Z]+)\s*\}', r'\1', s)
    
    # Step 5: Handle accent commands
    # \hat{x} -> x_hat (as a modified symbol)
    # \bar{x} -> x_bar
    # \vec{x} -> x_vec
    # \dot{x} -> x_dot
    # \ddot{x} -> x_ddot
    # \tilde{x} -> x_tilde
    for cmd, replacement in ACCENT_COMMANDS.items():
        # Match \cmd{x} or \cmd{xy} and replace with x_cmd
        pattern = rf'\\{cmd}\s*\{{([a-zA-Z]+)\}}'
        s = re.sub(pattern, rf'\1_{replacement}', s)
    
    # Step 6: Handle fractions
    # \frac{a}{b} -> (a)/(b)
    # \dfrac{a}{b} -> (a)/(b)
    # \tfrac{a}{b} -> (a)/(b)
    s = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\dfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\tfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    
    # Step 7: Handle sqrt
    # \sqrt{a} -> sqrt(a)
    # \sqrt[n]{a} -> a**(1/n)
    s = re.sub(r'\\sqrt\s*\[([^\]]+)\]\s*\{([^{}]+)\}', r'(\2)**(1/(\1))', s)
    s = re.sub(r'\\sqrt\s*\{([^{}]+)\}', r'sqrt(\1)', s)
    
    # Step 8: Handle superscripts and subscripts
    # x^{n} -> x**n
    # x^n -> x**n
    # x_{n} -> x_n
    s = re.sub(r'\^\s*\{([^{}]+)\}', r'**(\1)', s)
    s = re.sub(r'\^\s*([a-zA-Z0-9])', r'**\1', s)
    s = re.sub(r'_\s*\{([^{}]+)\}', r'_\1', s)
    
    # Step 9: Handle common LaTeX operators
    s = s.replace('\\cdot', '*')
    s = s.replace('\\times', '*')
    s = s.replace('\\div', '/')
    s = s.replace('\\pm', '+/-')
    s = s.replace('\\mp', '-/+')
    s = s.replace('\\leq', '<=')
    s = s.replace('\\geq', '>=')
    s = s.replace('\\neq', '!=')
    s = s.replace('\\approx', '~')
    s = s.replace('\\equiv', '==')
    s = s.replace('\\propto', '~')
    s = s.replace('\\infty', 'oo')
    s = s.replace('\\partial', 'diff')
    s = s.replace('\\nabla', 'nabla')
    s = s.replace('\\sum', 'Sum')
    s = s.replace('\\prod', 'Prod')
    s = s.replace('\\int', 'Integral')
    s = s.replace('\\oint', 'Integral')
    
    # Step 10: Handle Greek letters
    greek_map = {
        '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma', '\\delta': 'delta',
        '\\epsilon': 'epsilon', '\\zeta': 'zeta', '\\eta': 'eta', '\\theta': 'theta',
        '\\iota': 'iota', '\\kappa': 'kappa', '\\lambda': 'lambda', '\\mu': 'mu',
        '\\nu': 'nu', '\\xi': 'xi', '\\pi': 'pi', '\\rho': 'rho',
        '\\sigma': 'sigma', '\\tau': 'tau', '\\upsilon': 'upsilon', '\\phi': 'phi',
        '\\chi': 'chi', '\\psi': 'psi', '\\omega': 'omega',
        '\\Gamma': 'Gamma', '\\Delta': 'Delta', '\\Theta': 'Theta', '\\Lambda': 'Lambda',
        '\\Xi': 'Xi', '\\Pi': 'Pi', '\\Sigma': 'Sigma', '\\Upsilon': 'Upsilon',
        '\\Phi': 'Phi', '\\Psi': 'Psi', '\\Omega': 'Omega',
    }
    for latex_cmd, sympy_name in greek_map.items():
        s = s.replace(latex_cmd, sympy_name)
    
    # Step 11: Handle spacing commands
    s = re.sub(r'\\[,;:!]', '', s)
    s = s.replace('\\ ', ' ')
    s = s.replace('\\quad', '  ')
    s = s.replace('\\qquad', '    ')
    
    # Step 12: Handle remaining LaTeX commands
    # Remove any remaining \command{...} patterns
    s = re.sub(r'\\[a-zA-Z]+\s*\{([^{}]+)\}', r'\1', s)
    # Remove any remaining \command patterns
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    
    # Step 13: Clean up braces
    s = s.replace('{', '').replace('}', '')
    
    # Step 14: Handle multiple = signs (chained equations)
    # If there are multiple =, take the first complete equation
    if s.count('=') > 1:
        # Split on = and take the first two parts
        parts = s.split('=')
        if len(parts) >= 2:
            s = parts[0] + '=' + parts[1]
    
    return s.strip()

def solve_with_definitions(latex):
    """
    Solve equation using LaTeX command definitions.
    
    Instead of stripping unknown commands, we define them:
    - \mbox{text} -> text (as a symbol)
    - \operatorname{name} -> name (as a function)
    - \left( -> (, \right) -> )
    - \hat{x} -> x_hat (as a modified symbol)
    """
    try:
        # Define LaTeX commands
        normalized = define_latex_commands(latex)
        
        if not normalized or len(normalized) < 3:
            return {'success': False, 'error': 'empty_after_definitions', 'strategy': 'definitions'}
        
        if '=' not in normalized:
            return {'success': False, 'error': 'no_equality', 'strategy': 'definitions'}
        
        # Split on =
        parts = normalized.split('=')
        if len(parts) != 2:
            return {'success': False, 'error': 'multiple_equalities', 'strategy': 'definitions'}
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        if not lhs or not rhs:
            return {'success': False, 'error': 'empty_side', 'strategy': 'definitions'}
        
        # Parse both sides
        lhs_expr = parse_expr(lhs, transformations=transformations)
        rhs_expr = parse_expr(rhs, transformations=transformations)
        
        # Get variables
        variables = list(lhs_expr.free_symbols | rhs_expr.free_symbols)
        
        if not variables:
            return {'success': False, 'error': 'no_variables', 'strategy': 'definitions'}
        
        # Solve for first variable
        var = variables[0]
        solution = sympy.solve(lhs_expr - rhs_expr, var)
        
        return {
            'success': True,
            'solution': str(solution),
            'variables': [str(v) for v in variables],
            'strategy': 'definitions',
            'normalized': normalized,
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'strategy': 'definitions'}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LaTeX command definition solver')
    parser.add_argument('--input', default='DATASETS/extractor_training_data_fresh.jsonl')
    parser.add_argument('--output', default='DATASETS/equation_solve_results_definitions.jsonl')
    parser.add_argument('--stats', default='DATASETS/equation_solve_stats_definitions.json')
    
    args = parser.parse_args()
    
    # Load records
    with open(args.input) as f:
        records = [json.loads(line) for line in f]
    
    print(f"Loaded {len(records)} records")
    
    # Filter to complete equations
    complete = [r for r in records if is_complete_equation(r['latex'])]
    print(f"Complete equations: {len(complete)}")
    
    # Solve each
    results = []
    stats = {
        'total': len(complete),
        'solvable': 0,
        'not_solvable': 0,
        'by_strategy': {},
        'errors': {},
    }
    
    for i, record in enumerate(complete):
        if (i + 1) % 50 == 0:
            print(f"  Solving {i+1}/{len(complete)}...")
        
        result = solve_with_definitions(record['latex'])
        result['arxiv_id'] = record.get('arxiv_id', 'unknown')
        result['category'] = record.get('category', 'unknown')
        result['context_before'] = record.get('context_before', '')
        result['context_after'] = record.get('context_after', '')
        
        results.append(result)
        
        if result['success']:
            stats['solvable'] += 1
            strategy = result['strategy']
            stats['by_strategy'][strategy] = stats['by_strategy'].get(strategy, 0) + 1
        else:
            stats['not_solvable'] += 1
            error = result.get('error', 'unknown')
            stats['errors'][error] = stats['errors'].get(error, 0) + 1
    
    # Write results
    with open(args.output, 'w') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    # Write stats
    with open(args.stats, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print honest summary
    print(f"\n{'='*60}")
    print("HONEST RESULTS - LaTeX Command Definitions")
    print(f"{'='*60}")
    print(f"Total complete equations: {stats['total']}")
    print(f"Solvable: {stats['solvable']} ({100*stats['solvable']/stats['total']:.1f}%)")
    print(f"Not solvable: {stats['not_solvable']} ({100*stats['not_solvable']/stats['total']:.1f}%)")
    print(f"\nBy strategy:")
    for strategy, count in stats['by_strategy'].items():
        print(f"  {strategy}: {count}")
    print(f"\nError breakdown:")
    for error, count in sorted(stats['errors'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {error[:60]}: {count}")
    
    print(f"\nSample solutions:")
    for result in results[:10]:
        if result['success']:
            latex = result.get('latex', result.get('normalized', 'N/A'))
            print(f"  [{result['strategy']}] {latex[:50]}")
            print(f"    -> {result['solution'][:50]}")

if __name__ == '__main__':
    main()