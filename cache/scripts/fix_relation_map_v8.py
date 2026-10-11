"""Rebuild RELATION_MAP block correctly using chr(92) for backslashes."""
import sys

FILE = "scripts/math_recovery_tool.py"
BS = chr(92)  # single backslash character

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the RELATION_MAP block
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if "RELATION_MAP = {" in line:
        start_idx = i
    if start_idx and "NON_EQUATION_RELATIONS" in line:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    sys.exit("ERROR: Could not find RELATION_MAP block")

# Build the correct block
block_lines = []
block_lines.append("RELATION_MAP = {\n")
block_lines.append("    # Inequalities: solver-compatible\n")
block_lines.append(f'    "{BS}{BS}leq": "<=", "{BS}{BS}geq": ">=", "{BS}{BS}neq": "!=",\n')
block_lines.append(f'    "{BS}{BS}ll": "<", "{BS}{BS}gg": ">",\n')
block_lines.append("    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.\n")
block_lines.append("    # The solver adapter (solve_recovered) detects these and refuses to solve.\n")
block_lines.append(f'    "{BS}{BS}approx": "approx", "{BS}{BS}equiv": "equiv",\n')
block_lines.append(f'    "{BS}{BS}sim": "sim", "{BS}{BS}simeq": "simeq", "{BS}{BS}cong": "cong",\n')
block_lines.append(f'    "{BS}{BS}propto": "propto",\n')
block_lines.append(f'    "{BS}{BS}subseteq": "subseteq", "{BS}{BS}supseteq": "supseteq",\n')
block_lines.append(f'    "{BS}{BS}subset": "subset", "{BS}{BS}supset": "supset",\n')
block_lines.append(f'    "{BS}{BS}Rightarrow": "Rightarrow", "{BS}{BS}Leftarrow": "Leftarrow",\n')
block_lines.append(f'    "{BS}{BS}Leftrightarrow": "Leftrightarrow",\n')
block_lines.append(f'    "{BS}{BS}rightarrow": "rightarrow", "{BS}{BS}leftarrow": "leftarrow",\n')
block_lines.append(f'    "{BS}{BS}mapsto": "mapsto",\n')
block_lines.append(f'    "{BS}{BS}to": "to", "{BS}{BS}gets": "gets",\n')
block_lines.append(f'    "{BS}{BS}implies": "implies", "{BS}{BS}iff": "iff",\n')
block_lines.append("}\n")

# Replace the block
new_lines = lines[:start_idx] + block_lines + lines[end_idx:]

with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("RELATION_MAP rebuilt correctly")
