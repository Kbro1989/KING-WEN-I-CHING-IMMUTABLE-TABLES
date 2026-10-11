"""Fix RELATION_MAP: use chr(92) to avoid backslash escaping issues."""
import sys

FILE = "scripts/math_recovery_tool.py"
BS = chr(92)  # single backslash character

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

start = content.find("RELATION_MAP = {")
end = content.find("\n# Relations that are NOT equations", start)

if start < 0 or end < 0:
    sys.exit("ERROR: RELATION_MAP block not found")

# Build the correct block as a proper Python string
# Each key needs: "\\command" in source = one backslash + command
block = "RELATION_MAP = {\n"
block += "    # Inequalities: solver-compatible\n"
block += f'    "{BS}BSleq": "<=", "{BS}BSgeq": ">=", "{BS}BSneq": "!=",\n'
block += f'    "{BS}BSll": "<", "{BS}BSgg": ">",\n'
block += "    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.\n"
block += "    # The solver adapter (solve_recovered) detects these and refuses to solve.\n"
block += f'    "{BS}BSapprox": "approx", "{BS}BSequiv": "equiv",\n'
block += f'    "{BS}BSsim": "sim", "{BS}BSsimeq": "simeq", "{BS}BScong": "cong",\n'
block += f'    "{BS}BSpropto": "propto",\n'
block += f'    "{BS}BSsubseteq": "subseteq", "{BS}BSsupseteq": "supseteq",\n'
block += f'    "{BS}BSsubset": "subset", "{BS}BSsupset": "supset",\n'
block += f'    "{BS}BSRelarrow": "Rightarrow", "{BS}BSLeftarrow": "Leftarrow",\n'
block += f'    "{BS}BSLeftrightarrow": "Leftrightarrow",\n'
block += f'    "{BS}BSrightarrow": "rightarrow", "{BS}BSleftarrow": "leftarrow",\n'
block += f'    "{BS}BSmapsto": "mapsto",\n'
block += f'    "{BS}BSto": "to", "{BS}BSgets": "gets",\n'
block += f'    "{BS}BSimplies": "implies", "{BS}BSiff": "iff",\n'
block += "}\n"

# Replace BS with actual backslash
block = block.replace("BS", BS)

content = content[:start] + block + content[end:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
