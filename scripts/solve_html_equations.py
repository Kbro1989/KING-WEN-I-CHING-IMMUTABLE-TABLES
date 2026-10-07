"""
Solve Equations from ArXiv HTML Corpus
=======================================
Filters extracted equations to complete ones (with = or structural operators),
parses LaTeX into SymPy-compatible format, attempts to solve each.

Output: JSONL with solve results, success/failure stats, and error analysis.
"""
import json, re, sys
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from latex2sympy2 import latex2sympy

transformations = standard_transformations + (implicit_multiplication_application,)

def is_complete_equation(latex):
    """Check if a LaTeX string is a complete equation (not just a symbol)."""
    if not latex or len(latex) < 3:
        return False
    # Must have = or structural operator
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
    # Find all single letters that are not part of function names
    funcs = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'abs'}
    tokens = re.findall(r'[a-zA-Z]+', expr_str)
    variables = set()
    for token in tokens:
        if token not in funcs and len(token) == 1:
            variables.add(token)
    return list(variables)

def solve_equation(latex):
    """Attempt to solve a LaTeX equation using latex2sympy2."""
    result = {
        'latex': latex,
        'normalized': None,
        'solvable': False,
        'solution': None,
        'error': None,
        'variables': [],
    }
    
    try:
        # Use latex2sympy2 for proper LaTeX parsing
        parsed = latex2sympy(latex)
        result['normalized'] = str(parsed)
        
        # Check if it's an equation (Eq object) or expression
        if isinstance(parsed, sympy.Eq):
            lhs = parsed.lhs
            rhs = parsed.rhs
            variables = list(lhs.free_symbols | rhs.free_symbols)
            result['variables'] = [str(v) for v in variables]
            
            if not variables:
                result['error'] = 'no_variables'
                return result
            
            # Solve for first variable
            var = variables[0]
            solution = sympy.solve(lhs - rhs, var)
            result['solvable'] = True
            result['solution'] = str(solution)
        else:
            # It's an expression, not an equation
            result['error'] = 'not_equation'
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Solve equations from arxiv HTML corpus')
    parser.add_argument('--input', default='DATASETS/extractor_training_data_fresh.jsonl', help='Input JSONL file')
    parser.add_argument('--output', default='DATASETS/equation_solve_results.jsonl', help='Output JSONL file')
    parser.add_argument('--stats', default='DATASETS/equation_solve_stats.json', help='Stats JSON file')
    
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
    
    # Print summary
    print(f"\n{'='*60}")
    print("Equation Solving Summary")
    print(f"{'='*60}")
    print(f"Total complete equations: {stats['total']}")
    print(f"Solvable: {stats['solvable']} ({100*stats['solvable']/stats['total']:.1f}%)")
    print(f"Not solvable: {stats['not_solvable']} ({100*stats['not_solvable']/stats['total']:.1f}%)")
    print(f"\nError breakdown:")
    for error, count in sorted(stats['errors'].items(), key=lambda x: -x[1]):
        print(f"  {error}: {count}")
    
    print(f"\nSample solutions:")
    for result in results[:10]:
        if result['solvable']:
            print(f"  {result['latex'][:60]}")
            print(f"    -> {result['solution'][:60]}")

if __name__ == '__main__':
    main()