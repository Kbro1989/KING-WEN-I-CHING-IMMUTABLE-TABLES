import json
import re

# Extract the computeHamiltonian function from the J-space widget
with open("DATASETS/kingwen-jspace-widget-updated.html", "r") as f:
    content = f.read()

def extract_function(content, func_name):
    """Extract a full function from JavaScript content."""
    # Find the function declaration
    pattern = rf'function {func_name}\s*\([^)]*\)\s*\{{'
    match = re.search(pattern, content)
    if not match:
        return None
    
    start = match.start()
    brace_count = 0
    in_string = False
    string_char = None
    escape_next = False
    
    for i in range(start, len(content)):
        c = content[i]
        
        if escape_next:
            escape_next = False
            continue
            
        if in_string:
            if c == '\\':
                escape_next = True
            elif c == string_char:
                in_string = False
                string_char = None
        else:
            if c in '"\'`':
                in_string = True
                string_char = c
            elif c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    return content[start:end]
    
    return content[start:]

# Extract functions
for func_name in ['computeHamiltonian', 'computeAllHamiltonians', 'gaussianSmooth', 'computeBroadcastSet']:
    func = extract_function(content, func_name)
    if func:
        print(f"=== {func_name} ===")
        print(func[:3000])
        print()
    else:
        print(f"=== {func_name} NOT FOUND ===")
        print()