"""
Layer 4: Math Symbol Classification
====================================
Classifies detected math regions by combining:
- OCR text (from Tesseract)
- Shape characteristics (aspect ratio, fill ratio, stroke width)
- Spatial context (position relative to other regions)

Output: Classified symbols with confidence scores and alternative interpretations.
"""
import json, re
import numpy as np

# Math symbol lookup table: maps OCR text + shape characteristics to symbol identities
MATH_SYMBOL_LOOKUP = {
    # Greek letters
    'α': {'name': 'alpha', 'category': 'greek', 'unicode': 'α', 'latex': '\\alpha'},
    'β': {'name': 'beta', 'category': 'greek', 'unicode': 'β', 'latex': '\\beta'},
    'γ': {'name': 'gamma', 'category': 'greek', 'unicode': 'γ', 'latex': '\\gamma'},
    'δ': {'name': 'delta', 'category': 'greek', 'unicode': 'δ', 'latex': '\\delta'},
    'ε': {'name': 'epsilon', 'category': 'greek', 'unicode': 'ε', 'latex': '\\epsilon'},
    'ζ': {'name': 'zeta', 'category': 'greek', 'unicode': 'ζ', 'latex': '\\zeta'},
    'η': {'name': 'eta', 'category': 'greek', 'unicode': 'η', 'latex': '\\eta'},
    'θ': {'name': 'theta', 'category': 'greek', 'unicode': 'θ', 'latex': '\\theta'},
    'ι': {'name': 'iota', 'category': 'greek', 'unicode': 'ι', 'latex': '\\iota'},
    'κ': {'name': 'kappa', 'category': 'greek', 'unicode': 'κ', 'latex': '\\kappa'},
    'λ': {'name': 'lambda', 'category': 'greek', 'unicode': 'λ', 'latex': '\\lambda'},
    'μ': {'name': 'mu', 'category': 'greek', 'unicode': 'μ', 'latex': '\\mu'},
    'ν': {'name': 'nu', 'category': 'greek', 'unicode': 'ν', 'latex': '\\nu'},
    'ξ': {'name': 'xi', 'category': 'greek', 'unicode': 'ξ', 'latex': '\\xi'},
    'π': {'name': 'pi', 'category': 'greek', 'unicode': 'π', 'latex': '\\pi'},
    'ρ': {'name': 'rho', 'category': 'greek', 'unicode': 'ρ', 'latex': '\\rho'},
    'σ': {'name': 'sigma', 'category': 'greek', 'unicode': 'σ', 'latex': '\\sigma'},
    'τ': {'name': 'tau', 'category': 'greek', 'unicode': 'τ', 'latex': '\\tau'},
    'υ': {'name': 'upsilon', 'category': 'greek', 'unicode': 'υ', 'latex': '\\upsilon'},
    'φ': {'name': 'phi', 'category': 'greek', 'unicode': 'φ', 'latex': '\\phi'},
    'χ': {'name': 'chi', 'category': 'greek', 'unicode': 'χ', 'latex': '\\chi'},
    'ψ': {'name': 'psi', 'category': 'greek', 'unicode': 'ψ', 'latex': '\\psi'},
    'ω': {'name': 'omega', 'category': 'greek', 'unicode': 'ω', 'latex': '\\omega'},
    
    # Capital Greek
    'Γ': {'name': 'Gamma', 'category': 'greek_capital', 'unicode': 'Γ', 'latex': '\\Gamma'},
    'Δ': {'name': 'Delta', 'category': 'greek_capital', 'unicode': 'Δ', 'latex': '\\Delta'},
    'Θ': {'name': 'Theta', 'category': 'greek_capital', 'unicode': 'Θ', 'latex': '\\Theta'},
    'Λ': {'name': 'Lambda', 'category': 'greek_capital', 'unicode': 'Λ', 'latex': '\\Lambda'},
    'Ξ': {'name': 'Xi', 'category': 'greek_capital', 'unicode': 'Ξ', 'latex': '\\Xi'},
    'Π': {'name': 'Pi', 'category': 'greek_capital', 'unicode': 'Π', 'latex': '\\Pi'},
    'Σ': {'name': 'Sigma', 'category': 'greek_capital', 'unicode': 'Σ', 'latex': '\\Sigma'},
    'Υ': {'name': 'Upsilon', 'category': 'greek_capital', 'unicode': 'Υ', 'latex': '\\Upsilon'},
    'Φ': {'name': 'Phi', 'category': 'greek_capital', 'unicode': 'Φ', 'latex': '\\Phi'},
    'Ψ': {'name': 'Psi', 'category': 'greek_capital', 'unicode': 'Ψ', 'latex': '\\Psi'},
    'Ω': {'name': 'Omega', 'category': 'greek_capital', 'unicode': 'Ω', 'latex': '\\Omega'},
    
    # Operators
    '+': {'name': 'plus', 'category': 'operator', 'unicode': '+', 'latex': '+'},
    '-': {'name': 'minus', 'category': 'operator', 'unicode': '-', 'latex': '-'},
    '−': {'name': 'minus', 'category': 'operator', 'unicode': '−', 'latex': '-'},
    '×': {'name': 'times', 'category': 'operator', 'unicode': '×', 'latex': '\\times'},
    '·': {'name': 'cdot', 'category': 'operator', 'unicode': '·', 'latex': '\\cdot'},
    '÷': {'name': 'divide', 'category': 'operator', 'unicode': '÷', 'latex': '\\div'},
    '=': {'name': 'equals', 'category': 'operator', 'unicode': '=', 'latex': '='},
    '<': {'name': 'less', 'category': 'operator', 'unicode': '<', 'latex': '<'},
    '>': {'name': 'greater', 'category': 'operator', 'unicode': '>', 'latex': '>'},
    '≤': {'name': 'leq', 'category': 'operator', 'unicode': '≤', 'latex': '\\leq'},
    '≥': {'name': 'geq', 'category': 'operator', 'unicode': '≥', 'latex': '\\geq'},
    '≠': {'name': 'neq', 'category': 'operator', 'unicode': '≠', 'latex': '\\neq'},
    '≈': {'name': 'approx', 'category': 'operator', 'unicode': '≈', 'latex': '\\approx'},
    '≡': {'name': 'equiv', 'category': 'operator', 'unicode': '≡', 'latex': '\\equiv'},
    '∝': {'name': 'propto', 'category': 'operator', 'unicode': '∝', 'latex': '\\propto'},
    '±': {'name': 'pm', 'category': 'operator', 'unicode': '±', 'latex': '\\pm'},
    '∓': {'name': 'mp', 'category': 'operator', 'unicode': '∓', 'latex': '\\mp'},
    
    # Calculus
    '∫': {'name': 'integral', 'category': 'calculus', 'unicode': '∫', 'latex': '\\int'},
    '∮': {'name': 'oint', 'category': 'calculus', 'unicode': '∮', 'latex': '\\oint'},
    '∂': {'name': 'partial', 'category': 'calculus', 'unicode': '∂', 'latex': '\\partial'},
    '∇': {'name': 'nabla', 'category': 'calculus', 'unicode': '∇', 'latex': '\\nabla'},
    '∑': {'name': 'sum', 'category': 'calculus', 'unicode': '∑', 'latex': '\\sum'},
    '∏': {'name': 'prod', 'category': 'calculus', 'unicode': '∏', 'latex': '\\prod'},
    '√': {'name': 'sqrt', 'category': 'calculus', 'unicode': '√', 'latex': '\\sqrt'},
    '∞': {'name': 'infty', 'category': 'calculus', 'unicode': '∞', 'latex': '\\infty'},
    
    # Logic
    '∧': {'name': 'wedge', 'category': 'logic', 'unicode': '∧', 'latex': '\\wedge'},
    '∨': {'name': 'vee', 'category': 'logic', 'unicode': '∨', 'latex': '\\vee'},
    '¬': {'name': 'neg', 'category': 'logic', 'unicode': '¬', 'latex': '\\neg'},
    '∀': {'name': 'forall', 'category': 'logic', 'unicode': '∀', 'latex': '\\forall'},
    '∃': {'name': 'exists', 'category': 'logic', 'unicode': '∃', 'latex': '\\exists'},
    '∈': {'name': 'in', 'category': 'logic', 'unicode': '∈', 'latex': '\\in'},
    '∉': {'name': 'notin', 'category': 'logic', 'unicode': '∉', 'latex': '\\notin'},
    '⊆': {'name': 'subseteq', 'category': 'logic', 'unicode': '⊆', 'latex': '\\subseteq'},
    '⊂': {'name': 'subset', 'category': 'logic', 'unicode': '⊂', 'latex': '\\subset'},
    '∪': {'name': 'cup', 'category': 'logic', 'unicode': '∪', 'latex': '\\cup'},
    '∩': {'name': 'cap', 'category': 'logic', 'unicode': '∩', 'latex': '\\cap'},
    
    # Arrows
    '→': {'name': 'to', 'category': 'arrow', 'unicode': '→', 'latex': '\\to'},
    '←': {'name': 'gets', 'category': 'arrow', 'unicode': '←', 'latex': '\\gets'},
    '↔': {'name': 'leftrightarrow', 'category': 'arrow', 'unicode': '↔', 'latex': '\\leftrightarrow'},
    '⟹': {'name': 'implies', 'category': 'arrow', 'unicode': '⟹', 'latex': '\\implies'},
    '⟸': {'name': 'impliedby', 'category': 'arrow', 'unicode': '⟸', 'latex': '\\impliedby'},
    '↦': {'name': 'mapsto', 'category': 'arrow', 'unicode': '↦', 'latex': '\\mapsto'},
    
    # Brackets
    '(': {'name': 'lparen', 'category': 'bracket', 'unicode': '(', 'latex': '('},
    ')': {'name': 'rparen', 'category': 'bracket', 'unicode': ')', 'latex': ')'},
    '[': {'name': 'lbracket', 'category': 'bracket', 'unicode': '[', 'latex': '['},
    ']': {'name': 'rbracket', 'category': 'bracket', 'unicode': ']', 'latex': ']'},
    '{': {'name': 'lbrace', 'category': 'bracket', 'unicode': '{', 'latex': '\\{'},
    '}': {'name': 'rbrace', 'category': 'bracket', 'unicode': '}', 'latex': '\\}'},
    '⟨': {'name': 'langle', 'category': 'bracket', 'unicode': '⟨', 'latex': '\\langle'},
    '⟩': {'name': 'rangle', 'category': 'bracket', 'unicode': '⟩', 'latex': '\\rangle'},
    '⌊': {'name': 'lfloor', 'category': 'bracket', 'unicode': '⌊', 'latex': '\\lfloor'},
    '⌋': {'name': 'rfloor', 'category': 'bracket', 'unicode': '⌋', 'latex': '\\rfloor'},
    '⌈': {'name': 'lceil', 'category': 'bracket', 'unicode': '⌈', 'latex': '\\lceil'},
    '⌉': {'name': 'rceil', 'category': 'bracket', 'unicode': '⌉', 'latex': '\\rceil'},
    '|': {'name': 'lvert', 'category': 'bracket', 'unicode': '|', 'latex': '|'},
    '‖': {'name': 'lVert', 'category': 'bracket', 'unicode': '‖', 'latex': '\\|'},
    
    # Functions (multi-character)
    'sin': {'name': 'sin', 'category': 'function', 'unicode': 'sin', 'latex': '\\sin'},
    'cos': {'name': 'cos', 'category': 'function', 'unicode': 'cos', 'latex': '\\cos'},
    'tan': {'name': 'tan', 'category': 'function', 'unicode': 'tan', 'latex': '\\tan'},
    'log': {'name': 'log', 'category': 'function', 'unicode': 'log', 'latex': '\\log'},
    'ln': {'name': 'ln', 'category': 'function', 'unicode': 'ln', 'latex': '\\ln'},
    'exp': {'name': 'exp', 'category': 'function', 'unicode': 'exp', 'latex': '\\exp'},
    'det': {'name': 'det', 'category': 'function', 'unicode': 'det', 'latex': '\\det'},
    'dim': {'name': 'dim', 'category': 'function', 'unicode': 'dim', 'latex': '\\dim'},
    'rank': {'name': 'rank', 'category': 'function', 'unicode': 'rank', 'latex': '\\rank'},
    'trace': {'name': 'trace', 'category': 'function', 'unicode': 'trace', 'latex': '\\trace'},
    'diag': {'name': 'diag', 'category': 'function', 'unicode': 'diag', 'latex': '\\diag'},
    
    # Digits
    '0': {'name': 'zero', 'category': 'digit', 'unicode': '0', 'latex': '0'},
    '1': {'name': 'one', 'category': 'digit', 'unicode': '1', 'latex': '1'},
    '2': {'name': 'two', 'category': 'digit', 'unicode': '2', 'latex': '2'},
    '3': {'name': 'three', 'category': 'digit', 'unicode': '3', 'latex': '3'},
    '4': {'name': 'four', 'category': 'digit', 'unicode': '4', 'latex': '4'},
    '5': {'name': 'five', 'category': 'digit', 'unicode': '5', 'latex': '5'},
    '6': {'name': 'six', 'category': 'digit', 'unicode': '6', 'latex': '6'},
    '7': {'name': 'seven', 'category': 'digit', 'unicode': '7', 'latex': '7'},
    '8': {'name': 'eight', 'category': 'digit', 'unicode': '8', 'latex': '8'},
    '9': {'name': 'nine', 'category': 'digit', 'unicode': '9', 'latex': '9'},
    
    # Letters (variables)
    'a': {'name': 'a', 'category': 'variable', 'unicode': 'a', 'latex': 'a'},
    'b': {'name': 'b', 'category': 'variable', 'unicode': 'b', 'latex': 'b'},
    'c': {'name': 'c', 'category': 'variable', 'unicode': 'c', 'latex': 'c'},
    'd': {'name': 'd', 'category': 'variable', 'unicode': 'd', 'latex': 'd'},
    'e': {'name': 'e', 'category': 'variable', 'unicode': 'e', 'latex': 'e'},
    'f': {'name': 'f', 'category': 'variable', 'unicode': 'f', 'latex': 'f'},
    'g': {'name': 'g', 'category': 'variable', 'unicode': 'g', 'latex': 'g'},
    'h': {'name': 'h', 'category': 'variable', 'unicode': 'h', 'latex': 'h'},
    'i': {'name': 'i', 'category': 'variable', 'unicode': 'i', 'latex': 'i'},
    'j': {'name': 'j', 'category': 'variable', 'unicode': 'j', 'latex': 'j'},
    'k': {'name': 'k', 'category': 'variable', 'unicode': 'k', 'latex': 'k'},
    'l': {'name': 'l', 'category': 'variable', 'unicode': 'l', 'latex': 'l'},
    'm': {'name': 'm', 'category': 'variable', 'unicode': 'm', 'latex': 'm'},
    'n': {'name': 'n', 'category': 'variable', 'unicode': 'n', 'latex': 'n'},
    'o': {'name': 'o', 'category': 'variable', 'unicode': 'o', 'latex': 'o'},
    'p': {'name': 'p', 'category': 'variable', 'unicode': 'p', 'latex': 'p'},
    'q': {'name': 'q', 'category': 'variable', 'unicode': 'q', 'latex': 'q'},
    'r': {'name': 'r', 'category': 'variable', 'unicode': 'r', 'latex': 'r'},
    's': {'name': 's', 'category': 'variable', 'unicode': 's', 'latex': 's'},
    't': {'name': 't', 'category': 'variable', 'unicode': 't', 'latex': 't'},
    'u': {'name': 'u', 'category': 'variable', 'unicode': 'u', 'latex': 'u'},
    'v': {'name': 'v', 'category': 'variable', 'unicode': 'v', 'latex': 'v'},
    'w': {'name': 'w', 'category': 'variable', 'unicode': 'w', 'latex': 'w'},
    'x': {'name': 'x', 'category': 'variable', 'unicode': 'x', 'latex': 'x'},
    'y': {'name': 'y', 'category': 'variable', 'unicode': 'y', 'latex': 'y'},
    'z': {'name': 'z', 'category': 'variable', 'unicode': 'z', 'latex': 'z'},
    
    # Capital letters
    'A': {'name': 'A', 'category': 'variable', 'unicode': 'A', 'latex': 'A'},
    'B': {'name': 'B', 'category': 'variable', 'unicode': 'B', 'latex': 'B'},
    'C': {'name': 'C', 'category': 'variable', 'unicode': 'C', 'latex': 'C'},
    'D': {'name': 'D', 'category': 'variable', 'unicode': 'D', 'latex': 'D'},
    'E': {'name': 'E', 'category': 'variable', 'unicode': 'E', 'latex': 'E'},
    'F': {'name': 'F', 'category': 'variable', 'unicode': 'F', 'latex': 'F'},
    'G': {'name': 'G', 'category': 'variable', 'unicode': 'G', 'latex': 'G'},
    'H': {'name': 'H', 'category': 'variable', 'unicode': 'H', 'latex': 'H'},
    'I': {'name': 'I', 'category': 'variable', 'unicode': 'I', 'latex': 'I'},
    'J': {'name': 'J', 'category': 'variable', 'unicode': 'J', 'latex': 'J'},
    'K': {'name': 'K', 'category': 'variable', 'unicode': 'K', 'latex': 'K'},
    'L': {'name': 'L', 'category': 'variable', 'unicode': 'L', 'latex': 'L'},
    'M': {'name': 'M', 'category': 'variable', 'unicode': 'M', 'latex': 'M'},
    'N': {'name': 'N', 'category': 'variable', 'unicode': 'N', 'latex': 'N'},
    'O': {'name': 'O', 'category': 'variable', 'unicode': 'O', 'latex': 'O'},
    'P': {'name': 'P', 'category': 'variable', 'unicode': 'P', 'latex': 'P'},
    'Q': {'name': 'Q', 'category': 'variable', 'unicode': 'Q', 'latex': 'Q'},
    'R': {'name': 'R', 'category': 'variable', 'unicode': 'R', 'latex': 'R'},
    'S': {'name': 'S', 'category': 'variable', 'unicode': 'S', 'latex': 'S'},
    'T': {'name': 'T', 'category': 'variable', 'unicode': 'T', 'latex': 'T'},
    'U': {'name': 'U', 'category': 'variable', 'unicode': 'U', 'latex': 'U'},
    'V': {'name': 'V', 'category': 'variable', 'unicode': 'V', 'latex': 'V'},
    'W': {'name': 'W', 'category': 'variable', 'unicode': 'W', 'latex': 'W'},
    'X': {'name': 'X', 'category': 'variable', 'unicode': 'X', 'latex': 'X'},
    'Y': {'name': 'Y', 'category': 'variable', 'unicode': 'Y', 'latex': 'Y'},
    'ω': {'name': 'omega', 'category': 'greek', 'unicode': 'ω', 'latex': '\\omega'},
    'ο': {'name': 'omicron', 'category': 'greek', 'unicode': 'ο', 'latex': 'o'},
    
    # Capital Greek (from Wolfram reference)
    'Β': {'name': 'Beta', 'category': 'greek_capital', 'unicode': 'Β', 'latex': '\\Beta'},
    'Γ': {'name': 'Gamma', 'category': 'greek_capital', 'unicode': 'Γ', 'latex': '\\Gamma'},
    'Δ': {'name': 'Delta', 'category': 'greek_capital', 'unicode': 'Δ', 'latex': '\\Delta'},
    'Ε': {'name': 'Epsilon', 'category': 'greek_capital', 'unicode': 'Ε', 'latex': '\\Epsilon'},
    'Ζ': {'name': 'Zeta', 'category': 'greek_capital', 'unicode': 'Ζ', 'latex': '\\Zeta'},
    'Η': {'name': 'Eta', 'category': 'greek_capital', 'unicode': 'Η', 'latex': '\\Eta'},
    'Θ': {'name': 'Theta', 'category': 'greek_capital', 'unicode': 'Θ', 'latex': '\\Theta'},
    'Ι': {'name': 'Iota', 'category': 'greek_capital', 'unicode': 'Ι', 'latex': '\\Iota'},
    'Κ': {'name': 'Kappa', 'category': 'greek_capital', 'unicode': 'Κ', 'latex': '\\Kappa'},
    'Λ': {'name': 'Lambda', 'category': 'greek_capital', 'unicode': 'Λ', 'latex': '\\Lambda'},
    'Μ': {'name': 'Mu', 'category': 'greek_capital', 'unicode': 'Μ', 'latex': '\\Mu'},
    'Ν': {'name': 'Nu', 'category': 'greek_capital', 'unicode': 'Ν', 'latex': '\\Nu'},
    'Ξ': {'name': 'Xi', 'category': 'greek_capital', 'unicode': 'Ξ', 'latex': '\\Xi'},
    'Ο': {'name': 'Omicron', 'category': 'greek_capital', 'unicode': 'Ο', 'latex': '\\Omicron'},
    'Π': {'name': 'Pi', 'category': 'greek_capital', 'unicode': 'Π', 'latex': '\\Pi'},
    'Ρ': {'name': 'Rho', 'category': 'greek_capital', 'unicode': 'Ρ', 'latex': '\\Rho'},
    'Σ': {'name': 'Sigma', 'category': 'greek_capital', 'unicode': 'Σ', 'latex': '\\Sigma'},
    'Τ': {'name': 'Tau', 'category': 'greek_capital', 'unicode': 'Τ', 'latex': '\\Tau'},
    'Υ': {'name': 'Upsilon', 'category': 'greek_capital', 'unicode': 'Υ', 'latex': '\\Upsilon'},
    'Φ': {'name': 'Phi', 'category': 'greek_capital', 'unicode': 'Φ', 'latex': '\\Phi'},
    'Χ': {'name': 'Chi', 'category': 'greek_capital', 'unicode': 'Χ', 'latex': '\\Chi'},
    'Ψ': {'name': 'Psi', 'category': 'greek_capital', 'unicode': 'Ψ', 'latex': '\\Psi'},
    'Ω': {'name': 'Omega', 'category': 'greek_capital', 'unicode': 'Ω', 'latex': '\\Omega'},
    
    # Double-struck (blackboard bold)
    'ℂ': {'name': 'C', 'category': 'double_struck', 'unicode': 'ℂ', 'latex': '\\mathbb{C}'},
    'ℍ': {'name': 'H', 'category': 'double_struck', 'unicode': 'ℍ', 'latex': '\\mathbb{H}'},
    'ℕ': {'name': 'N', 'category': 'double_struck', 'unicode': 'ℕ', 'latex': '\\mathbb{N}'},
    'ℙ': {'name': 'P', 'category': 'double_struck', 'unicode': 'ℙ', 'latex': '\\mathbb{P}'},
    'ℚ': {'name': 'Q', 'category': 'double_struck', 'unicode': 'ℚ', 'latex': '\\mathbb{Q}'},
    'ℛ': {'name': 'R', 'category': 'double_struck', 'unicode': 'ℛ', 'latex': '\\mathbb{R}'},
    'ℝ': {'name': 'R', 'category': 'double_struck', 'unicode': 'ℝ', 'latex': '\\mathbb{R}'},
    'ℤ': {'name': 'Z', 'category': 'double_struck', 'unicode': 'ℤ', 'latex': '\\mathbb{Z}'},
    
    # Script letters
    'ℒ': {'name': 'L', 'category': 'script', 'unicode': 'ℒ', 'latex': '\\mathcal{L}'},
    'ℬ': {'name': 'B', 'category': 'script', 'unicode': 'ℬ', 'latex': '\\mathcal{B}'},
    'ℳ': {'name': 'M', 'category': 'script', 'unicode': 'ℳ', 'latex': '\\mathcal{M}'},
    '𝒞': {'name': 'C', 'category': 'script', 'unicode': '𝒞', 'latex': '\\mathcal{C}'},
    '𝒢': {'name': 'G', 'category': 'script', 'unicode': '𝒢', 'latex': '\\mathcal{G}'},
    '𝒥': {'name': 'J', 'category': 'script', 'unicode': '𝒥', 'latex': '\\mathcal{J}'},
    '𝒦': {'name': 'K', 'category': 'script', 'unicode': '𝒦', 'latex': '\\mathcal{K}'},
    '𝒩': {'name': 'N', 'category': 'script', 'unicode': '𝒩', 'latex': '\\mathcal{N}'},
    '𝒪': {'name': 'O', 'category': 'script', 'unicode': '𝒪', 'latex': '\\mathcal{O}'},
    '𝒫': {'name': 'P', 'category': 'script', 'unicode': '𝒫', 'latex': '\\mathcal{P}'},
    '𝒬': {'name': 'Q', 'category': 'script', 'unicode': '𝒬', 'latex': '\\mathcal{Q}'},
    '𝒮': {'name': 'S', 'category': 'script', 'unicode': '𝒮', 'latex': '\\mathcal{S}'},
    '𝒯': {'name': 'T', 'category': 'script', 'unicode': '𝒯', 'latex': '\\mathcal{T}'},
    '𝒰': {'name': 'U', 'category': 'script', 'unicode': '𝒰', 'latex': '\\mathcal{U}'},
    '𝒱': {'name': 'V', 'category': 'script', 'unicode': '𝒱', 'latex': '\\mathcal{V}'},
    '𝒲': {'name': 'W', 'category': 'script', 'unicode': '𝒲', 'latex': '\\mathcal{W}'},
    '𝒳': {'name': 'X', 'category': 'script', 'unicode': '𝒳', 'latex': '\\mathcal{X}'},
    '𝒴': {'name': 'Y', 'category': 'script', 'unicode': '𝒴', 'latex': '\\mathcal{Y}'},
    '𝒵': {'name': 'Z', 'category': 'script', 'unicode': '𝒵', 'latex': '\\mathcal{Z}'},
    
    # Formal letters
    '𝔄': {'name': 'A', 'category': 'formal', 'unicode': '𝔄', 'latex': '\\mathfrak{A}'},
    '𝔅': {'name': 'B', 'category': 'formal', 'unicode': '𝔅', 'latex': '\\mathfrak{B}'},
    '𝔉': {'name': 'F', 'category': 'formal', 'unicode': '𝔉', 'latex': '\\mathfrak{F}'},
    '𝔊': {'name': 'G', 'category': 'formal', 'unicode': '𝔊', 'latex': '\\mathfrak{G}'},
    '𝔍': {'name': 'J', 'category': 'formal', 'unicode': '𝔍', 'latex': '\\mathfrak{J}'},
    '𝔎': {'name': 'K', 'category': 'formal', 'unicode': '𝔎', 'latex': '\\mathfrak{K}'},
    '𝔏': {'name': 'L', 'category': 'formal', 'unicode': '𝔏', 'latex': '\\mathfrak{L}'},
    '𝔐': {'name': 'M', 'category': 'formal', 'unicode': '𝔐', 'latex': '\\mathfrak{M}'},
    '𝔑': {'name': 'N', 'category': 'formal', 'unicode': '𝔑', 'latex': '\\mathfrak{N}'},
    '𝔒': {'name': 'O', 'category': 'formal', 'unicode': '𝔒', 'latex': '\\mathfrak{O}'},
    '𝔓': {'name': 'P', 'category': 'formal', 'unicode': '𝔓', 'latex': '\\mathfrak{P}'},
    '𝔘': {'name': 'U', 'category': 'formal', 'unicode': '𝔘', 'latex': '\\mathfrak{U}'},
    '𝔙': {'name': 'V', 'category': 'formal', 'unicode': '𝔙', 'latex': '\\mathfrak{V}'},
    '𝔚': {'name': 'W', 'category': 'formal', 'unicode': '𝔚', 'latex': '\\mathfrak{W}'},
    '𝔛': {'name': 'X', 'category': 'formal', 'unicode': '𝔛', 'latex': '\\mathfrak{X}'},
    '𝔜': {'name': 'Y', 'category': 'formal', 'unicode': '𝔜', 'latex': '\\mathfrak{Y}'},
    '𝔷': {'name': 'z', 'category': 'formal', 'unicode': '𝔷', 'latex': '\\mathfrak{z}'},
    
    # Additional operators
    '×': {'name': 'times', 'category': 'operator', 'unicode': '×', 'latex': '\\times'},
    '÷': {'name': 'divide', 'category': 'operator', 'unicode': '÷', 'latex': '\\div'},
    '±': {'name': 'pm', 'category': 'operator', 'unicode': '±', 'latex': '\\pm'},
    '∓': {'name': 'mp', 'category': 'operator', 'unicode': '∓', 'latex': '\\mp'},
    '∝': {'name': 'propto', 'category': 'operator', 'unicode': '∝', 'latex': '\\propto'},
    '≈': {'name': 'approx', 'category': 'operator', 'unicode': '≈', 'latex': '\\approx'},
    '≡': {'name': 'equiv', 'category': 'operator', 'unicode': '≡', 'latex': '\\equiv'},
    '∼': {'name': 'sim', 'category': 'operator', 'unicode': '∼', 'latex': '\\sim'},
    '≅': {'name': 'cong', 'category': 'operator', 'unicode': '≅', 'latex': '\\cong'},
    '⊕': {'name': 'oplus', 'category': 'operator', 'unicode': '⊕', 'latex': '\\oplus'},
    '⊗': {'name': 'otimes', 'category': 'operator', 'unicode': '⊗', 'latex': '\\otimes'},
    '⨯': {'name': 'cross', 'category': 'operator', 'unicode': '⨯', 'latex': '\\times'},
    
    # Additional calculus
    '∮': {'name': 'oint', 'category': 'calculus', 'unicode': '∮', 'latex': '\\oint'},
    '∞': {'name': 'infty', 'category': 'calculus', 'unicode': '∞', 'latex': '\\infty'},
    'ℏ': {'name': 'hbar', 'category': 'calculus', 'unicode': 'ℏ', 'latex': '\\hbar'},
    'ℵ': {'name': 'aleph', 'category': 'calculus', 'unicode': 'ℵ', 'latex': '\\aleph'},
    
    # Additional arrows
    '↦': {'name': 'mapsto', 'category': 'arrow', 'unicode': '↦', 'latex': '\\mapsto'},
    '⟷': {'name': 'leftrightarrow', 'category': 'arrow', 'unicode': '⟷', 'latex': '\\leftrightarrow'},
    '⟸': {'name': 'impliedby', 'category': 'arrow', 'unicode': '⟸', 'latex': '\\impliedby'},
    '⟹': {'name': 'implies', 'category': 'arrow', 'unicode': '⟹', 'latex': '\\implies'},
    
    # Other symbols
    '°': {'name': 'degree', 'category': 'other', 'unicode': '°', 'latex': '^{\\circ}'},
    '∴': {'name': 'therefore', 'category': 'other', 'unicode': '∴', 'latex': '\\therefore'},
    '∵': {'name': 'because', 'category': 'other', 'unicode': '∵', 'latex': '\\because'},
    '∶': {'name': 'ratio', 'category': 'other', 'unicode': '∶', 'latex': ':'},
    '∷': {'name': 'proportion', 'category': 'other', 'unicode': '∷', 'latex': '::'},
    '²': {'name': 'squared', 'category': 'other', 'unicode': '²', 'latex': '^2'},
    '·': {'name': 'cdot', 'category': 'operator', 'unicode': '·', 'latex': '\\cdot'},
    'ϵ': {'name': 'epsilon', 'category': 'greek', 'unicode': 'ϵ', 'latex': '\\epsilon'},
    'ℯ': {'name': 'e', 'category': 'other', 'unicode': 'ℯ', 'latex': 'e'},
    'ⅈ': {'name': 'i', 'category': 'other', 'unicode': 'ⅈ', 'latex': 'i'},
    'ⅉ': {'name': 'j', 'category': 'other', 'unicode': 'ⅉ', 'latex': 'j'},
}

# Shape-based classification for symbols that OCR can't recognize
SHAPE_BASED_CLASSIFICATION = {
    'integral': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'sum': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'prod': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'sqrt': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'fraction_bar': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'sqrt_vinculum': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'horizontal_line': {'aspect_range': (5.0, 50.0), 'fill_range': (0.001, 0.03), 'stroke_range': (0.001, 0.03)},
    'vertical_line': {'aspect_range': (0.02, 0.2), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'large_bracket': {'aspect_range': (0.1, 0.5), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
}

def classify_symbol(ocr_text, aspect_ratio, fill_ratio, normalized_stroke, region_type):
    """
    Classify a math symbol using OCR text and shape characteristics.
    Returns a list of possible classifications with confidence scores.
    """
    classifications = []
    
    # 1. Direct lookup from OCR text
    if ocr_text and ocr_text in MATH_SYMBOL_LOOKUP:
        symbol = MATH_SYMBOL_LOOKUP[ocr_text]
        classifications.append({
            'name': symbol['name'],
            'category': symbol['category'],
            'unicode': symbol['unicode'],
            'latex': symbol['latex'],
            'confidence': 0.9,
            'method': 'direct_lookup',
        })
    
    # 2. Shape-based classification for symbols OCR can't recognize
    if not classifications or classifications[0]['confidence'] < 0.5:
        for symbol_name, profile in SHAPE_BASED_CLASSIFICATION.items():
            aspect_min, aspect_max = profile['aspect_range']
            fill_min, fill_max = profile['fill_range']
            stroke_min, stroke_max = profile['stroke_range']
            
            if (aspect_min <= aspect_ratio <= aspect_max and
                fill_min <= fill_ratio <= fill_max and
                stroke_min <= normalized_stroke <= stroke_max):
                classifications.append({
                    'name': symbol_name,
                    'category': 'calculus' if symbol_name in ['integral', 'sum', 'prod', 'sqrt'] else 'structure',
                    'unicode': None,
                    'latex': None,
                    'confidence': 0.5,
                    'method': 'shape_based',
                })
    
    # 3. Region type classification
    if region_type == 'fraction_bar':
        classifications.append({
            'name': 'fraction_bar',
            'category': 'structure',
            'unicode': None,
            'latex': '\\frac',
            'confidence': 0.8,
            'method': 'region_type',
        })
    elif region_type == 'large_bracket':
        classifications.append({
            'name': 'large_bracket',
            'category': 'bracket',
            'unicode': None,
            'latex': '\\left(',
            'confidence': 0.7,
            'method': 'region_type',
        })
    elif region_type == 'vertical_bar':
        classifications.append({
            'name': 'vertical_bar',
            'category': 'bracket',
            'unicode': '|',
            'latex': '|',
            'confidence': 0.6,
            'method': 'region_type',
        })
    elif region_type == 'script':
        classifications.append({
            'name': 'script',
            'category': 'script',
            'unicode': None,
            'latex': None,
            'confidence': 0.4,
            'method': 'region_type',
        })
    
    # 4. If nothing matched, use OCR text as-is with low confidence
    if not classifications and ocr_text:
        classifications.append({
            'name': ocr_text,
            'category': 'unknown',
            'unicode': ocr_text,
            'latex': ocr_text,
            'confidence': 0.3,
            'method': 'ocr_fallback',
        })
    
    # Sort by confidence
    classifications.sort(key=lambda x: x['confidence'], reverse=True)
    
    return classifications

def classify_regions(regions):
    """
    Classify all regions in a page.
    Returns a list of classified symbols with their relationships.
    """
    classified = []
    
    for i, region in enumerate(regions):
        ocr_text = region.get('ocr_text', '')
        aspect_ratio = region.get('aspect_ratio', 1.0)
        fill_ratio = region.get('fill_ratio', 0.5)
        normalized_stroke = region.get('normalized_stroke', 0.1)
        region_type = region.get('region_type', 'symbol')
        
        classifications = classify_symbol(ocr_text, aspect_ratio, fill_ratio, normalized_stroke, region_type)
        
        classified.append({
            'region_index': i,
            'bbox': region['bbox'],
            'centroid': region['centroid'],
            'region_type': region_type,
            'ocr_text': ocr_text,
            'classifications': classifications,
            'best_classification': classifications[0] if classifications else None,
        })
    
    return classified

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Math symbol classification')
    parser.add_argument('input_json', help='Input JSON from vision extraction')
    parser.add_argument('--output', default='DATASETS/classified_symbols.json')
    
    args = parser.parse_args()
    
    with open(args.input_json) as f:
        data = json.load(f)
    
    results = []
    for page_result in data.get('results', []):
        regions = page_result.get('symbols', [])
        classified = classify_regions(regions)
        
        results.append({
            'page': page_result['page'],
            'total_regions': len(regions),
            'classified_symbols': classified,
        })
    
    output = {
        'total_pages': len(results),
        'results': results,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Classified symbols on {len(results)} pages")
    print(f"Results written to {args.output}")
    
    for r in results:
        print(f"\n  Page {r['page']}: {r['total_regions']} regions")
        for sym in r['classified_symbols'][:5]:
            best = sym['best_classification']
            if best:
                print(f"    {best['name']} ({best['category']}, conf={best['confidence']:.2f}, method={best['method']})")

if __name__ == '__main__':
    main()