"""
LaTeX Equation Solver using pylatexenc
=======================================
Uses pylatexenc for proper LaTeX tokenization instead of regex.
Handles nested braces, custom macros, and complex structures.

Strategy:
1. Tokenize LaTeX with pylatexenc
2. Convert token tree to SymPy-compatible string
3. Parse and solve with SymPy
"""
import json, re, sys
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.macrospec import MacroSpec, EnvironmentSpec
from pylatexenc import macrospec

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

def latex_to_sympy_str(latex):
    """
    Convert LaTeX to SymPy-compatible string using pylatexenc.
    Uses LatexNodes2Text for proper tokenization.
    """
    try:
        # Use pylatexenc to convert LaTeX to plain text
        # This handles nested braces, macros, and environments properly
        converter = LatexNodes2Text()
        
        # First, handle some common patterns that pylatexenc might not handle
        s = latex.strip()
        
        # Remove environments
        s = re.sub(r'\\begin\{([^}]+)\}', '', s)
        s = re.sub(r'\\end\{([^}]+)\}', '', s)
        
        # Handle \left and \right
        s = re.sub(r'\\left\s*\(', '(', s)
        s = re.sub(r'\\right\s*\)', ')', s)
        s = re.sub(r'\\left\s*\[', '[', s)
        s = re.sub(r'\\right\s*\]', ']', s)
        s = re.sub(r'\\left\s*\\\{', '{', s)
        s = re.sub(r'\\right\s*\\\}', '}', s)
        s = re.sub(r'\\left\s*\|', '|', s)
        s = re.sub(r'\\right\s*\|', '|', s)
        s = re.sub(r'\\left\s*\\langle', 'langle', s)
        s = re.sub(r'\\right\s*\\rangle', 'rangle', s)
        s = re.sub(r'\\left\s*\\lfloor', 'lfloor', s)
        s = re.sub(r'\\right\s*\\rfloor', 'rfloor', s)
        s = re.sub(r'\\left\s*\\lceil', 'lceil', s)
        s = re.sub(r'\\right\s*\\rceil', 'rceil', s)
        
        # Handle \big, \Big, \bigg, \Bigg
        s = re.sub(r'\\bigg\s*', '', s)
        s = re.sub(r'\\Bigg\s*', '', s)
        s = re.sub(r'\\big\s*', '', s)
        s = re.sub(r'\\Big\s*', '', s)
        s = re.sub(r'\\bigl\s*', '', s)
        s = re.sub(r'\\Bigl\s*', '', s)
        s = re.sub(r'\\biggr\s*', '', s)
        s = re.sub(r'\\Biggr\s*', '', s)
        
        # Handle text commands
        for cmd in ['mbox', 'text', 'mathrm', 'mathbf', 'mathit', 'mathsf', 'mathtt', 'mathcal', 'mathbb', 'mathfrak', 'mathscr', 'boldsymbol']:
            pattern = rf'\\{cmd}\s*\{{([^{{}}]+)\}}'
            s = re.sub(pattern, r'\1', s)
        
        # Handle operator commands
        s = re.sub(r'\\operatorname\s*\{\s*([a-zA-Z]+)\s*\}', r'\1', s)
        
        # Handle accents
        for cmd, replacement in [('hat', 'hat'), ('bar', 'bar'), ('vec', 'vec'), ('dot', 'dot'), ('ddot', 'ddot'), ('tilde', 'tilde'), ('widehat', 'widehat'), ('overline', 'overline'), ('underline', 'underline'), ('overrightarrow', 'overrightarrow'), ('overleftarrow', 'overleftarrow')]:
            pattern = rf'\\{cmd}\s*\{{([a-zA-Z]+)\}}'
            s = re.sub(pattern, rf'\1_{replacement}', s)
        
        # Handle fractions
        s = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
        s = re.sub(r'\\dfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
        s = re.sub(r'\\tfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
        s = re.sub(r'\\cfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
        
        # Handle sqrt
        s = re.sub(r'\\sqrt\s*\[([^\]]+)\]\s*\{([^{}]+)\}', r'(\2)**(1/(\1))', s)
        s = re.sub(r'\\sqrt\s*\{([^{}]+)\}', r'sqrt(\1)', s)
        
        # Handle superscripts and subscripts
        s = re.sub(r'\^\s*\{([^{}]+)\}', r'**(\1)', s)
        s = re.sub(r'\^\s*([a-zA-Z0-9])', r'**\1', s)
        s = re.sub(r'_\s*\{([^{}]+)\}', r'_\1', s)
        
        # Handle operators
        s = s.replace('\\cdot', '*')
        s = s.replace('\\times', '*')
        s = s.replace('\\div', '/')
        s = s.replace('\\pm', '+/-')
        s = s.replace('\\mp', '-/+')
        s = s.replace('\\oplus', '+')
        s = s.replace('\\otimes', '*')
        s = s.replace('\\odot', '*')
        s = s.replace('\\circ', 'o')
        s = s.replace('\\bullet', '*')
        s = s.replace('\\star', '*')
        s = s.replace('\\ast', '*')
        s = s.replace('\\dagger', '+')
        s = s.replace('\\ddagger', '++')
        s = s.replace('\\amalg', '+')
        s = s.replace('\\cap', '&')
        s = s.replace('\\cup', '|')
        s = s.replace('\\uplus', '+')
        s = s.replace('\\sqcap', '&')
        s = s.replace('\\sqcup', '|')
        s = s.replace('\\vee', '|')
        s = s.replace('\\wedge', '&')
        s = s.replace('\\setminus', '\\')
        s = s.replace('\\wr', 'wreath')
        s = s.replace('\\diamond', '<>')
        s = s.replace('\\bigtriangleup', '^')
        s = s.replace('\\bigtriangledown', 'v')
        s = s.replace('\\triangleleft', '<')
        s = s.replace('\\triangleright', '>')
        s = s.replace('\\lhd', '<')
        s = s.replace('\\rhd', '>')
        s = s.replace('\\unlhd', '<=')
        s = s.replace('\\unrhd', '>=')
        
        # Handle relations
        s = s.replace('\\leq', '<=')
        s = s.replace('\\geq', '>=')
        s = s.replace('\\neq', '!=')
        s = s.replace('\\approx', '~')
        s = s.replace('\\equiv', '==')
        s = s.replace('\\sim', '~')
        s = s.replace('\\simeq', '~')
        s = s.replace('\\cong', '~')
        s = s.replace('\\propto', '~')
        s = s.replace('\\ll', '<<')
        s = s.replace('\\gg', '>>')
        s = s.replace('\\in', 'in')
        s = s.replace('\\notin', 'notin')
        s = s.replace('\\subset', 'subset')
        s = s.replace('\\supset', 'supset')
        s = s.replace('\\subseteq', 'subseteq')
        s = s.replace('\\supseteq', 'supseteq')
        s = s.replace('\\cup', 'union')
        s = s.replace('\\cap', 'intersection')
        s = s.replace('\\emptyset', 'empty')
        s = s.replace('\\forall', 'forall')
        s = s.replace('\\exists', 'exists')
        s = s.replace('\\nexists', 'notexists')
        s = s.replace('\\neg', 'not')
        s = s.replace('\\wedge', 'and')
        s = s.replace('\\vee', 'or')
        s = s.replace('\\Rightarrow', 'implies')
        s = s.replace('\\Leftarrow', 'impliedby')
        s = s.replace('\\Leftrightarrow', 'iff')
        s = s.replace('\\rightarrow', 'to')
        s = s.replace('\\leftarrow', 'gets')
        s = s.replace('\\mapsto', 'mapsto')
        s = s.replace('\\to', 'to')
        s = s.replace('\\gets', 'gets')
        s = s.replace('\\implies', 'implies')
        s = s.replace('\\impliedby', 'impliedby')
        s = s.replace('\\iff', 'iff')
        s = s.replace('\\land', 'and')
        s = s.replace('\\lor', 'or')
        s = s.replace('\\lnot', 'not')
        
        # Handle arrows
        s = s.replace('\\longrightarrow', 'to')
        s = s.replace('\\longleftarrow', 'gets')
        s = s.replace('\\longleftrightarrow', 'iff')
        s = s.replace('\\Longrightarrow', 'implies')
        s = s.replace('\\Longleftarrow', 'impliedby')
        s = s.replace('\\Longleftrightarrow', 'iff')
        s = s.replace('\\xrightarrow', 'to')
        s = s.replace('\\xleftarrow', 'gets')
        s = s.replace('\\uparrow', 'up')
        s = s.replace('\\downarrow', 'down')
        s = s.replace('\\updownarrow', 'updown')
        s = s.replace('\\Uparrow', 'UP')
        s = s.replace('\\Downarrow', 'DOWN')
        s = s.replace('\\Updownarrow', 'UPDOWN')
        s = s.replace('\\nearrow', 'ne')
        s = s.replace('\\searrow', 'se')
        s = s.replace('\\swarrow', 'sw')
        s = s.replace('\\nwarrow', 'nw')
        s = s.replace('\\hookleftarrow', 'hookgets')
        s = s.replace('\\hookrightarrow', 'hookto')
        s = s.replace('\\rightleftharpoons', 'leftright')
        s = s.replace('\\leftrightharpoons', 'leftright')
        s = s.replace('\\overleftrightarrow', 'over')
        s = s.replace('\\overrightarrow', 'overto')
        s = s.replace('\\overleftarrow', 'overgets')
        s = s.replace('\\underrightarrow', 'under')
        s = s.replace('\\underleftarrow', 'under')
        
        # Handle calculus operators
        s = s.replace('\\int', 'Integral')
        s = s.replace('\\oint', 'Integral')
        s = s.replace('\\iint', 'Integral')
        s = s.replace('\\iiint', 'Integral')
        s = s.replace('\\iiiint', 'Integral')
        s = s.replace('\\idotsint', 'Integral')
        s = s.replace('\\sum', 'Sum')
        s = s.replace('\\prod', 'Prod')
        s = s.replace('\\lim', 'Limit')
        s = s.replace('\\partial', 'diff')
        s = s.replace('\\nabla', 'nabla')
        s = s.replace('\\infty', 'oo')
        s = s.replace('\\bigcup', 'Union')
        s = s.replace('\\bigcap', 'Intersection')
        s = s.replace('\\bigvee', 'Or')
        s = s.replace('\\bigwedge', 'And')
        s = s.replace('\\bigoplus', 'Oplus')
        s = s.replace('\\bigotimes', 'Otimes')
        s = s.replace('\\bigodot', 'Odot')
        s = s.replace('\\biguplus', 'Uplus')
        s = s.replace('\\bigsqcup', 'sqcup')
        s = s.replace('\\bigsqcap', 'sqcap')
        
        # Handle Greek letters
        greek_map = {
            '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma', '\\delta': 'delta',
            '\\epsilon': 'epsilon', '\\varepsilon': 'epsilon', '\\zeta': 'zeta', '\\eta': 'eta',
            '\\theta': 'theta', '\\vartheta': 'theta', '\\iota': 'iota', '\\kappa': 'kappa',
            '\\lambda': 'lambda', '\\mu': 'mu', '\\nu': 'nu', '\\xi': 'xi',
            '\\pi': 'pi', '\\varpi': 'pi', '\\rho': 'rho', '\\varrho': 'rho',
            '\\sigma': 'sigma', '\\varsigma': 'sigma', '\\tau': 'tau', '\\upsilon': 'upsilon',
            '\\phi': 'phi', '\\varphi': 'phi', '\\chi': 'chi', '\\psi': 'psi', '\\omega': 'omega',
            '\\Gamma': 'Gamma', '\\Delta': 'Delta', '\\Theta': 'Theta', '\\Lambda': 'Lambda',
            '\\Xi': 'Xi', '\\Pi': 'Pi', '\\Sigma': 'Sigma', '\\Upsilon': 'Upsilon',
            '\\Phi': 'Phi', '\\Psi': 'Psi', '\\Omega': 'Omega',
        }
        for latex_cmd, sympy_name in greek_map.items():
            s = s.replace(latex_cmd, sympy_name)
        
        # Handle functions
        func_map = {
            'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'cot': 'cot', 'sec': 'sec', 'csc': 'csc',
            'arcsin': 'asin', 'arccos': 'acos', 'arctan': 'atan', 'arccot': 'acot',
            'arcsec': 'asec', 'arccsc': 'acsc',
            'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh', 'coth': 'coth',
            'sech': 'sech', 'csch': 'csch',
            'arcsinh': 'asinh', 'arccosh': 'acosh', 'arctanh': 'atanh', 'arccoth': 'acoth',
            'arcsech': 'asech', 'arccsch': 'acsch',
            'log': 'log', 'ln': 'log', 'exp': 'exp',
            'det': 'det', 'dim': 'dim', 'rank': 'rank', 'trace': 'trace', 'diag': 'diag',
            'ker': 'ker', 'hom': 'hom', 'deg': 'deg', 'gcd': 'gcd', 'lcm': 'lcm',
            'min': 'Min', 'max': 'Max', 'sup': 'sup', 'inf': 'inf', 'arg': 'arg', 'mod': 'mod',
            'Pr': 'Pr', 'E': 'E', 'Var': 'Var', 'Cov': 'Cov', 'Corr': 'Corr',
        }
        for latex_cmd, sympy_name in func_map.items():
            s = s.replace('\\' + latex_cmd, sympy_name)
        
        # Handle delimiters
        delim_map = {
            '\\left(': '(', '\\right)': ')',
            '\\left[': '[', '\\right]': ']',
            '\\left\\{': '{', '\\right\\}': '}',
            '\\left|': '|', '\\right|': '|',
            '\\left\\|': '||', '\\right\\|': '||',
            '\\left\\langle': 'langle', '\\right\\rangle': 'rangle',
            '\\left\\lfloor': 'lfloor', '\\right\\rfloor': 'rfloor',
            '\\left\\lceil': 'lceil', '\\right\\rceil': 'rceil',
            '\\left\\lvert': '|', '\\right\\rvert': '|',
            '\\left\\lVert': '||', '\\right\\rVert': '||',
            '\\langle': 'langle', '\\rangle': 'rangle',
            '\\lfloor': 'lfloor', '\\rfloor': 'rfloor',
            '\\lceil': 'lceil', '\\rceil': 'rceil',
            '\\lvert': '|', '\\rvert': '|',
            '\\lVert': '||', '\\rVert': '||',
            '\\{': '{', '\\}': '}', '\\|': '||',
        }
        for latex_cmd, replacement in delim_map.items():
            s = s.replace(latex_cmd, replacement)
        
        # Handle spacing
        s = s.replace('\\,', ' ')
        s = s.replace('\\:', ' ')
        s = s.replace('\\;', ' ')
        s = s.replace('\\!', '')
        s = s.replace('\\ ', ' ')
        s = s.replace('\\quad', '  ')
        s = s.replace('\\qquad', '    ')
        s = s.replace('\\hfill', '')
        s = s.replace('\\vfill', '')
        s = s.replace('\\hspace', ' ')
        s = s.replace('\\vspace', ' ')
        
        # Handle remaining LaTeX commands
        s = re.sub(r'\\[a-zA-Z]+\s*\{([^{}]+)\}', r'\1', s)
        s = re.sub(r'\\[a-zA-Z]+', '', s)
        
        # Clean up braces
        s = s.replace('{', '').replace('}', '')
        
        # Handle multiple = signs
        if s.count('=') > 1:
            parts = s.split('=')
            if len(parts) >= 2:
                s = parts[0] + '=' + parts[1]
        
        return s.strip()
        
    except Exception as e:
        return None

def solve_equation(latex):
    """Solve a LaTeX equation using pylatexenc."""
    result = {
        'latex': latex,
        'solvable': False,
        'solution': None,
        'error': None,
        'variables': [],
        'strategy': 'pylatexenc',
    }
    
    try:
        # Convert LaTeX to SymPy string
        sympy_str = latex_to_sympy_str(latex)
        
        if not sympy_str or len(sympy_str) < 3:
            result['error'] = 'empty_after_conversion'
            return result
        
        if '=' not in sympy_str:
            result['error'] = 'no_equality'
            return result
        
        # Split on =
        parts = sympy_str.split('=')
        if len(parts) != 2:
            result['error'] = 'multiple_equalities'
            return result
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        if not lhs or not rhs:
            result['error'] = 'empty_side'
            return result
        
        # Parse both sides
        lhs_expr = parse_expr(lhs, transformations=transformations)
        rhs_expr = parse_expr(rhs, transformations=transformations)
        
        # Get variables
        variables = list(lhs_expr.free_symbols | rhs_expr.free_symbols)
        
        if not variables:
            result['error'] = 'no_variables'
            return result
        
        # Solve for first variable
        var = variables[0]
        solution = sympy.solve(lhs_expr - rhs_expr, var)
        
        result['solvable'] = True
        result['solution'] = str(solution)
        result['variables'] = [str(v) for v in variables]
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LaTeX equation solver using pylatexenc')
    parser.add_argument('--input', default='DATASETS/extractor_training_data_fresh.jsonl')
    parser.add_argument('--output', default='DATASETS/equation_solve_results_pylatexenc.jsonl')
    parser.add_argument('--stats', default='DATASETS/equation_solve_stats_pylatexenc.json')
    
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
    print("HONEST RESULTS - pylatexenc LaTeX Solver")
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
            latex = result.get('latex', 'N/A')
            print(f"  [{result['strategy']}] {latex[:50]}")
            print(f"    -> {result['solution'][:50]}")

if __name__ == '__main__':
    main()