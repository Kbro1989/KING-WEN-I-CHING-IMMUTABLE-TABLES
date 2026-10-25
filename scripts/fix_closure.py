import re

p = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/phase2c_closure_record.md'
s = open(p).read()

# Fix total mutations row
s = s.replace(
    '| **Total mutations** | **24** | | **24/24** |',
    '| **Total mutations** | **24** | | **24/24** | Overlapping stages, not 24 distinct cases |'
)

# Fix v2 row
s = s.replace(
    '| Non-identical controls v2 | 6 | **Reference and candidate DIFFER** but symbol is legitimate notational variant | 6/6 | **Partial** (tests acceptance of changed expressions, not contextual discrimination) |',
    '| Non-identical controls v2 | 6 | **Reference and candidate DIFFER** but symbol is legitimate notational variant | 6/6 | **Partial** (tests acceptance of changed expressions, not contextual discrimination) |'
)

# Add overlapping note after total mutations row
old = '| **Total mutations** | **24** | | **24/24** | Overlapping stages, not 24 distinct cases |'
new = old + '\n\n### Overlapping Stages Note\n\nThe per-stage mutation counts (4 + 8 + 12 = 24) describe overlapping evaluation stages, not 24 distinct mutation cases. The same mutation types (e.g., sum-to-S) appear across multiple stages. The 47-case aggregate (20 TP + 27 TN) is the non-overlapping total.'
s = s.replace(old, new, 1)

open(p, 'w').write(s)
print('done')
"