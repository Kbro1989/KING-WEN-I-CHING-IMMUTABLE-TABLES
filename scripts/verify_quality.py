import json

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

print('Papers:', data['summary']['total_papers'])
print('Expressions:', data['summary']['total_math_expressions'])
print('Chain elements:', data['summary']['total_proof_chain_elements'])
print('Errors:', data['summary']['errors'])

total_images = 0
papers_with_images = 0
for p in data['papers']:
    imgs = []
    for pg in p.get('pages', []):
        imgs.extend(pg.get('math_images', []))
    if imgs:
        papers_with_images += 1
        total_images += len(imgs)
print('Math images:', total_images, 'across', papers_with_images, 'papers')

garbled = 0
for p in data['papers']:
    for pg in p.get('pages', []):
        for block in pg.get('math_blocks', []):
            text = block.get('text', '')
            if chr(0) in text or chr(0xfffd) in text or '\r\n' in text:
                garbled += 1
print('Garbled blocks:', garbled)

types = {}
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        t = expr.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
print('Expression types:', types)

print('\n--- Sample expressions with content ---')
count = 0
for p in data['papers']:
    if p['total_math_expressions'] > 0:
        fname = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
        print(f'\n{fname}:')
        for expr in p['math_expressions']:
            text = expr.get('text', '').strip()
            if text and count < 8:
                print(f'  [{expr.get("page","?")}] {text[:200]}')
                count += 1
        if count >= 8:
            break