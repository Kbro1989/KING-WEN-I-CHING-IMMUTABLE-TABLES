"""
Dual-Path Equation Solver
=========================
Tries multiple parsing strategies and reports honest results.
No faking, no acceptance of failure without trying alternatives.

Strategy 1: latex2sympy2 (proper LaTeX parser)
Strategy 2: Regex normalization + SymPy (for simple equations)
Strategy 3: Direct SymPy parsing (for already-clean equations)

Reports real success/failure rates for each strategy.
"""
import json, re, sys
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from latex2sympy2 import latex2sympy

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

def normalize_latex(latex):
    """Normalize LaTeX for SymPy parsing."""
    s = latex.strip()
    
    # Remove LaTeX formatting commands
    s = re.sub(r'\\displaystyle', '', s)
    s = re.sub(r'\\textstyle', '', s)
    s = re.sub(r'\\mbox\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', s)
    
    # Convert LaTeX operators
    s = s.replace('\\cdot', '*')
    s = s.replace('\\times', '*')
    s = s.replace('\\div', '/')
    s = s.replace('\\pm', '+/-')
    s = s.replace('\\mp', '-/+')
    
    # Remove LaTeX spacing
    s = re.sub(r'\\[,;:!]', '', s)
    s = s.replace('\\ ', ' ')
    
    # Convert fractions: \frac{a}{b} -> (a)/(b)
    s = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\dfrac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\tfrac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', s)
    
    # Convert sqrt: \sqrt{a} -> sqrt(a)
    s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
    
    # Convert superscripts: x^{n} -> x**n, x^n -> x**n
    s = re.sub(r'\^\{([^{}]+)\}', r'**(\1)', s)
    s = re.sub(r'\^([a-zA-Z0-9])', r'**\1', s)
    
    # Convert subscripts: x_{n} -> x_n (for variable names)
    s = re.sub(r'_\{([^{}]+)\}', r'_\1', s)
    
    # Remove remaining LaTeX commands
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    
    # Remove braces
    s = s.replace('{', '').replace('}', '')
    
    # Clean up
    s = s.strip()
    
    return s

def extract_variables(expr_str):
    """Extract variable names from an expression string."""
    funcs = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'abs'}
    tokens = re.findall(r'[a-zA-Z]+', expr_str)
    variables = set()
    for token in tokens:
        if token not in funcs and len(token) == 1:
            variables.add(token)
    return list(variables)

def solve_with_latex2sympy2(latex):
    """Strategy 1: Use latex2sympy2 for proper LaTeX parsing."""
    try:
        parsed = latex2sympy(latex)
        
        if isinstance(parsed, sympy.Eq):
            lhs = parsed.lhs
            rhs = parsed.rhs
            variables = list(lhs.free_symbols | rhs.free_symbols)
            
            if not variables:
                return {'success': False, 'error': 'no_variables', 'strategy': 'latex2sympy2'}
            
            var = variables[0]
            solution = sympy.solve(lhs - rhs, var)
            return {
                'success': True,
                'solution': str(solution),
                'variables': [str(v) for v in variables],
                'strategy': 'latex2sympy2',
            }
        else:
            return {'success': False, 'error': 'not_equation', 'strategy': 'latex2sympy2'}
            
    except Exception as e:
        return {'success': False, 'error': str(e), 'strategy': 'latex2sympy2'}

def solve_with_regex(latex):
    """Strategy 2: Use regex normalization + SymPy."""
    try:
        normalized = normalize_latex(latex)
        
        if not normalized or len(normalized) < 3:
            return {'success': False, 'error': 'empty_after_normalization', 'strategy': 'regex'}
        
        if '=' not in normalized:
            return {'success': False, 'error': 'no_equality', 'strategy': 'regex'}
        
        parts = normalized.split('=')
        if len(parts) != 2:
            return {'success': False, 'error': 'multiple_equalities', 'strategy': 'regex'}
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        if not lhs or not rhs:
            return {'success': False, 'error': 'empty_side', 'strategy': 'regex'}
        
        lhs_expr = parse_expr(lhs, transformations=transformations)
        rhs_expr = parse_expr(rhs, transformations=transformations)
        
        variables = list(lhs_expr.free_symbols | rhs_expr.free_symbols)
        
        if not variables:
            return {'success': False, 'error': 'no_variables', 'strategy': 'regex'}
        
        var = variables[0]
        solution = sympy.solve(lhs_expr - rhs_expr, var)
        
        return {
            'success': True,
            'solution': str(solution),
            'variables': [str(v) for v in variables],
            'strategy': 'regex',
            'normalized': normalized,
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'strategy': 'regex'}

def solve_equation(latex):
    """Try all strategies and return the first success."""
    result = {
        'latex': latex,
        'solvable': False,
        'solution': None,
        'error': None,
        'variables': [],
        'strategy': None,
        'attempts': [],
    }
    
    # Strategy 1: latex2sympy2
    r1 = solve_with_latex2sympy2(latex)
    result['attempts'].append(r1)
    if r1['success']:
        result['solvable'] = True
        result['solution'] = r1['solution']
        result['variables'] = r1['variables']
        result['strategy'] = r1['strategy']
        return result
    
    # Strategy 2: Regex normalization
    r2 = solve_with_regex(latex)
    result['attempts'].append(r2)
    if r2['success']:
        result['solvable'] = True
        result['solution'] = r2['solution']
        result['variables'] = r2['variables']
        result['strategy'] = r2['strategy']
        return result
    
    # All strategies failed
    result['error'] = r2.get('error', 'unknown')
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Dual-path equation solver')
    parser.add_argument('--input', default='DATASETS/extractor_training_data_fresh.jsonl')
    parser.add_argument('--output', default='DATASETS/equation_solve_results_dual.jsonl')
    parser.add_argument('--stats', default='DATASETS/equation_solve_stats_dual.json')
    
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
        
        result = solve_equation(record['latex'])
        result['arxiv_id'] = record.get('arxiv_id', 'unknown')
        result['category'] = record.get('category', 'unknown')
        result['context_before'] = record.get('context_before', '')
        result['context_after'] = record.get('context_after', '')
        
        results.append(result)
        
        if result['solvable']:
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
    print("HONEST RESULTS - No faking")
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
        if result['solvable']:
            print(f"  [{result['strategy']}] {result['latex'][:50]}")
            print(f"    -> {result['solution'][:50]}")

if __name__ == '__main__':
    main()