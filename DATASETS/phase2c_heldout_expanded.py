# Expanded held-out Gate 3 evaluation — Phase 2C
# Diverse expressions beyond development fixtures
# Evaluator commit: fe2843963e66c9131ebd442ce05b8e84b90f4374
# Labels independently defined before evaluation

# Nested operators
held_out_mutations_expanded = [
    # Nested summation inside fraction
    (r"\frac{\sum_{i=1}^{n} a_i}{b}", r"\frac{S_{i=1}^{n} a_i}{b}", "nested_summation_in_fraction"),
    # Integral with nested partial derivative
    (r"\int_{0}^{1} \frac{\partial f}{\partial x} dx", r"\int_{0}^{1} \frac{d f}{d x} dx", "nested_integral_partial"),
    # Product inside radical
    (r"\sqrt{\prod_{i=1}^{n} x_i}", r"\sqrt{P_{i=1}^{n} x_i}", "nested_product_in_radical"),
    # Double summation with fraction
    (r"\sum_{i=1}^{n} \sum_{j=1}^{m} \frac{a_{ij}}{b_{ij}}", r"S_{i=1}^{n} S_{j=1}^{m} a_{ij} / b_{ij}", "double_summation_fraction"),
    # Integral of fraction
    (r"\int_{0}^{1} \frac{f(x)}{g(x)} dx", r"\int_{0}^{1} f(x) / g(x) dx", "integral_of_fraction"),
    # Partial derivative in matrix context
    (r"\frac{\partial^2 f}{\partial x^2}", r"\frac{d^2 f}{d x^2}", "second_partial_derivative"),
    # Summation with radical
    (r"\sum_{i=1}^{n} \sqrt{a_i}", r"S_{i=1}^{n} v{a_i}", "summation_with_radical"),
    # Integral with summation inside
    (r"\int_{0}^{1} \sum_{i=1}^{n} a_i x^i dx", r"\int_{0}^{1} S_{i=1}^{n} a_i x^i dx", "integral_with_summation"),
]

# Similar-looking symbols in different roles
held_out_controls_expanded = [
    # d as variable name (not substitution)
    (r"\frac{d}{dx} f(x)", r"\frac{d}{dx} f(x)", "d_as_derivative_notation"),
    # S as set name (not substitution)
    (r"S = \{x : x > 0\}", r"S = \{x : x > 0\}", "S_as_set_name"),
    # I as identity matrix (not substitution)
    (r"I \cdot A = A", r"I \cdot A = A", "I_as_identity_matrix"),
    # / as division in valid expression
    (r"\frac{a}{b} + \frac{c}{d}", r"\frac{a}{b} + \frac{c}{d}", "valid_fraction_addition"),
    # Product with no substitution
    (r"\prod_{i=1}^{n} x_i", r"\prod_{i=1}^{n} x_i", "valid_product"),
    # Radical with no substitution
    (r"\sqrt{x^2 + y^2}", r"\sqrt{x^2 + y^2}", "valid_radical"),
    # Nabla with no substitution
    (r"\nabla f(x)", r"\nabla f(x)", "valid_nabla"),
    # Approximation with no substitution
    (r"x \approx y", r"x \approx y", "valid_approximation"),
    # Set membership with no substitution
    (r"x \in S", r"x \in S", "valid_set_membership"),
    # Equality with no substitution
    (r"a = b", r"a = b", "valid_equality"),
]

# Multiple simultaneous defects
held_out_multi_defect = [
    # Summation + integral both substituted
    (r"\sum_{i=1}^{n} \int_{0}^{1} f(x) dx", r"S_{i=1}^{n} I_{0}^{1} f(x) dx", "multi_sub_sum_int"),
    # Fraction + partial derivative both substituted
    (r"\frac{\partial f}{\partial x}", r"d f / d x", "multi_sub_frac_partial"),
    # Summation + radical both substituted
    (r"\sum_{i=1}^{n} \sqrt{a_i}", r"S_{i=1}^{n} v{a_i}", "multi_sub_sum_radical"),
    # Product + integral both substituted
    (r"\prod_{i=1}^{n} \int_{0}^{1} f_i(x) dx", r"P_{i=1}^{n} I_{0}^{1} f_i(x) dx", "multi_sub_prod_int"),
]

# Valid notational variants (should pass)
held_out_variants = [
    # Spacing differences
    (r"\sum_{i=1}^{n}a_i", r"\sum_{i=1}^{n} a_i", "spacing_variant"),
    # Parentheses differences
    (r"\frac{a}{b}", r"\frac{(a)}{(b)}", "parenthesis_variant"),
    # Equivalent bound notation
    (r"\sum_{i=1}^{n} a_i", r"\sum_{i=1}^{n} a_i", "identical"),
]
