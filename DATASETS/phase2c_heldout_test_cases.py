# Held-out Gate 3 evaluation — Phase 2C
# These mutations and controls were NOT used during development.
# Evaluator commit: fe2843963e66c9131ebd442ce05b8e84b90f4374
# Fixture hashes recorded in DATASETS/phase2c_heldout_fixture_hashes.json

held_out_mutations = [
    # Unseen expressions for known substitution types
    (r"\sum_{k=1}^{m} x_k", r"S_{k=1}^{m} x_k", "summation->S"),
    (r"\int_{a}^{b} g(x) dx", r"I_{a}^{b} g(x) dx", "integral->I"),
    (r"\partial y / \partial x", r"d y / d x", "partial_derivative->d"),
    (r"\frac{x+1}{y-1}", r"(x+1) / (y-1)", "fraction->/"),
    # New substitution types (unseen during development)
    (r"\prod_{i=1}^{n} x_i", r"P_{i=1}^{n} x_i", "product->P"),
    (r"\sqrt{x^2 + y^2}", r"v{x^2 + y^2}", "radical->v"),
    # Multi-operator substitutions
    (r"\sum_{i=1}^{n} \frac{a_i}{b_i}", r"S_{i=1}^{n} a_i / b_i", "summation->S + fraction->/"),
    (r"\int_{0}^{1} \partial f / \partial x dx", r"I_{0}^{1} d f / d x dx", "integral->I + partial_derivative->d"),
]

held_out_controls = [
    # Valid expressions that naturally contain d, S, I, /
    (r"d x / d t", r"d x / d t", "valid_d"),
    (r"S_{i=1}^{n} a_i", r"S_{i=1}^{n} a_i", "valid_S"),
    (r"I_{0}^{1} f(x) dx", r"I_{0}^{1} f(x) dx", "valid_I"),
    (r"a / b", r"a / b", "valid_slash"),
    # Valid expressions with operators that should NOT trigger substitution
    (r"\sum_{i=1}^{n} a_i", r"\sum_{i=1}^{n} a_i", "valid_summation"),
    (r"\int_{0}^{1} f(x) dx", r"\int_{0}^{1} f(x) dx", "valid_integral"),
    (r"\frac{a}{b}", r"\frac{a}{b}", "valid_fraction"),
    (r"\partial x / \partial t", r"\partial x / \partial t", "valid_partial"),
    # Expressions with operators in different but valid contexts
    (r"\sum_{i=1}^{n} \int_{0}^{1} f(x) dx", r"\sum_{i=1}^{n} \int_{0}^{1} f(x) dx", "valid_multi_op"),
    (r"\frac{\partial f}{\partial x}", r"\frac{\partial f}{\partial x}", "valid_nested"),
]

held_out_ambiguous = [
    # Cases where alignment might be ambiguous
    (r"\sum_{i=1}^{n} a_i", r"\sum_{i=1}^{n} a_i + S", "ambiguous_insertion"),
    (r"\frac{a}{b} + \frac{c}{d}", r"a / b + c / d", "ambiguous_multi_fraction"),
]
