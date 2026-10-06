import json, os

with open('DATASETS/semantic_math_zotero_full.json', 'r') as f:
    data = json.load(f)

print("Papers:", data['summary']['total_papers'])
print("Expressions:", data['summary']['total_math_expressions'])
print("Chain elements:", data['summary']['total_proof_chain_elements'])
print("Errors:", data['summary']['errors'])

total_images = 0
papers_with_images = 0
for p in data['papers']:
    imgs = []
    for pg in p.get('pages', []):
        imgs.extend(pg.get('math_images', []))
    if imgs:
        papers_with_images += 1
        total_images += len(imgs)
print("Math images:", total_images, "across", papers_with_images, "papers")

garbled_count = 0
for p in data['papers']:
    for pg in p.get('pages', []):
        for block in pg.get('math_blocks', []):
            text = block.get('text', '')
            if chr(0) in text or chr(0xfffd) in text or '\r\n' in text:
                garbled_count += 1
print("Garbled blocks:", garbled_count)

for p in data['papers']:
    if p['total_math_expressions'] > 0:
        fname = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
        print("\nFirst paper:", fname, "- Pages:", p['total_pages'], "Exprs:", p['total_math_expressions'])
        for expr in p['math_expressions'][:3]:
            print("  Expr:", expr.get('text', '')[:100])
            print("    Ops:", expr.get('operators', []), "Funcs:", expr.get('functions', []))
        break

counts = [p['total_math_expressions'] for p in data['papers']]
nonzero = [c for c in counts if c > 0]
zero = [c for c in counts if c == 0]
print("\nPapers with math:", len(nonzero), "Papers without:", len(zero))
if nonzero:
    print("Min:", min(nonzero), "Max:", max(nonzero), "Avg:", round(sum(nonzero)/len(nonzero)))
