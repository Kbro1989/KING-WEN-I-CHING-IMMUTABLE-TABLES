import re

path = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\scripts\vision_comparison_pipeline.py'
with open(path, 'r') as f:
    lines = f.readlines()

# Find the return block at the end of detect_border_contamination
# It's the last return in the function, around line 802-811
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if "return {" in line and i > 790:
        start_idx = i
        # find closing brace
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == "}":
                end_idx = j
                break
        break

assert start_idx is not None, "Return block not found"
assert end_idx is not None, "Closing brace not found"

# Build the new return block with bracket tracking
new_block = '''    # --- Bracket tracking at borders ---
    # Detect open/close bracket pairs at borders. A vertical stroke at a border
    # without its matching stroke at the opposite border indicates a clipped
    # bracket/delimiter. Stretched symbols (>50% height) are flagged.
    min_stroke_height = max(3, h // 4)
    bracket_contacts = {'top': [], 'bottom': [], 'left': [], 'right': []}

    # Left border: check for vertical strokes (potential brackets/delimiters)
    if left_count > 0:
        col_profile = np.sum(gray[:, :border_px] < threshold, axis=1)
        in_stroke = False
        stroke_start = 0
        for y in range(h):
            if col_profile[y] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = y
            elif col_profile[y] == 0 and in_stroke:
                in_stroke = False
                if y - stroke_start >= min_stroke_height:
                    bracket_contacts['left'].append('vertical_stroke')
        if in_stroke and h - stroke_start >= min_stroke_height:
            bracket_contacts['left'].append('vertical_stroke')

    # Right border: check for vertical strokes
    if right_count > 0:
        col_profile = np.sum(gray[:, -border_px:] < threshold, axis=1)
        in_stroke = False
        stroke_start = 0
        for y in range(h):
            if col_profile[y] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = y
            elif col_profile[y] == 0 and in_stroke:
                in_stroke = False
                if y - stroke_start >= min_stroke_height:
                    bracket_contacts['right'].append('vertical_stroke')
        if in_stroke and h - stroke_start >= min_stroke_height:
            bracket_contacts['right'].append('vertical_stroke')

    # Top border: check for horizontal strokes (bracket caps)
    if top_count > 0:
        row_profile = np.sum(gray[:border_px, :] < threshold, axis=0)
        in_stroke = False
        stroke_start = 0
        for x in range(w):
            if row_profile[x] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = x
            elif row_profile[x] == 0 and in_stroke:
                in_stroke = False
                if x - stroke_start >= min(w // 4, 10):
                    bracket_contacts['top'].append('horizontal_stroke')
        if in_stroke and w - stroke_start >= min(w // 4, 10):
            bracket_contacts['top'].append('horizontal_stroke')

    # Bottom border: check for horizontal strokes
    if bottom_count > 0:
        row_profile = np.sum(gray[-border_px:, :] < threshold, axis=0)
        in_stroke = False
        stroke_start = 0
        for x in range(w):
            if row_profile[x] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = x
            elif row_profile[x] == 0 and in_stroke:
                in_stroke = False
                if x - stroke_start >= min(w // 4, 10):
                    bracket_contacts['bottom'].append('horizontal_stroke')
        if in_stroke and w - stroke_start >= min(w // 4, 10):
            bracket_contacts['bottom'].append('horizontal_stroke')

    has_left_vertical = len(bracket_contacts['left']) > 0
    has_right_vertical = len(bracket_contacts['right']) > 0

    # Unmatched brackets: vertical stroke at one border without matching
    # stroke at opposite border indicates clipped bracket/delimiter
    unmatched_brackets_at_border = []
    if has_left_vertical and not has_right_vertical:
        unmatched_brackets_at_border.append('left')
    if has_right_vertical and not has_left_vertical:
        unmatched_brackets_at_border.append('right')

    # Stretched symbols: vertical strokes spanning >50% of image height
    stretched_at_border = []
    for border_name, col_slice in [('left', gray[:, :border_px]),
                                   ('right', gray[:, -border_px:])]:
        col_profile = np.sum(col_slice < threshold, axis=1)
        max_run = 0
        current_run = 0
        for y in range(h):
            if col_profile[y] > 0:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        if max_run > h * 0.5:
            stretched_at_border.append(border_name)

    # --- End bracket tracking ---

    return {
        'contaminated': border_contact,
        'border_contact': border_contact,
        'suspected_clipping': suspected_clipping,
        'confirmed_information_loss': False,  # Requires external verification
        'borders': borders,
        'edge_pixel_counts': counts,
        'border_density': round(border_density, 6),
        'overall_density': round(overall_density, 6),
        'bracket_contacts': bracket_contacts,
        'vertical_border_strokes': {
            'left': len(bracket_contacts['left']),
            'right': len(bracket_contacts['right']),
        },
        'horizontal_border_strokes': {
            'top': len(bracket_contacts['top']),
            'bottom': len(bracket_contacts['bottom']),
        },
        'unmatched_brackets_at_border': unmatched_brackets_at_border,
        'stretched_symbols_at_border': stretched_at_border,
        'has_left_vertical': has_left_vertical,
        'has_right_vertical': has_right_vertical,
    }
'''

# Replace from start_idx to end_idx (inclusive)
new_lines = lines[:start_idx] + [new_block + '\n'] + lines[end_idx + 1:]
with open(path, 'w') as f:
    f.writelines(new_lines)
print("Patch applied. Replaced lines", start_idx + 1, "through", end_idx + 1)
"