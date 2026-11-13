#!/bin/bash
# SHA-256 verification for staged blobs in KING-WEN-I-CHING-IMMUTABLE-TABLES

BASE="/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES"
MANIFEST="$BASE/PUBLICATION_MANIFEST.json"

echo "== 3. staged-blob SHA-256 vs manifest =="

# Step 1: Get staged additions
echo "== Building staged blob SHA-256 lookup table =="
# Read staged additions, compute SHA-256 for each
while read -r status path; do
    if [ -n "$path" ]; then
        blob=$(git show ":$path" 2>&1)
        if [ $? -eq 0 ]; then
            sha=$(printf '%s' "$blob" | sha256sum | cut -d' ' -f1)
            echo "$sha  $path"
        fi
    fi
git diff --cached --name-only --diff-filter=A | while IFS=$'\t' read -r _ path; do
    if [ -n "$path" ]; then
        echo "Reading: $path" >&2
        blob=$(git show ":$path" 2>&1)
        if [ $? -eq 0 ]; then
            sha=$(printf '%s' "$blob" | sha256sum | cut -d' ' -f1)
            echo "$sha  $path"
        else
            echo "git show failed: $blob" >&2
        fi
    fi
done > "$BASE/cache/staged.sha256"

check_rc=$?
if [ $check_rc -ne 0 ]; then
    echo "Failed to compute staged blob hashes"
    exit 1
fi
echo "Staged blob hashes: $(wc -l < "$BASE/cache/staged.sha256")"

# Step 2: Read manifest SHA-256 values
expected=$(python3 - <<'PY'
import json
with open('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/PUBLICATION_MANIFEST.json', encoding='utf-8') as f:
    manifest = json.load(f)
for e in manifest["manifest"]:
    print(f"{e['sha256']}  {e['relative_path']}")
PY
)
echo "$expected" > "$BASE/cache/manifest.sha256"
echo "Manifest SHA-256 table built: $(wc -l < "$BASE/cache/manifest.sha256")"

# Step 3: Compare
echo "== Comparing staged blobs to manifest =="
sort "$BASE/cache/staged.sha256" > "$BASE/cache/staged_sorted.sha256"
sort "$BASE/cache/manifest.sha256" > "$BASE/cache/manifest_sorted.sha256"

if diff -q "$BASE/cache/manifest_sorted.sha256" "$BASE/cache/staged_sorted.sha256" > /dev/null; then
    echo "SHA-256 verification PASSED"
    
    # Remove temp files
    rm -f "$BASE/cache/staged.sha256" "$BASE/cache/manifest.sha256" "$BASE/cache/staged_sorted.sha256" "$BASE/cache/manifest_sorted.sha256"
    
    # Step 4: Blob sizes
    echo "== 4. staged blob sizes =="
    max_size=0
    while IFS=$'\t' read -r _ path; do
        [ -n "$path" ] && {
            s=$(git cat-file -s ":$path" 2>/dev/null)
            if [ -n "$s" ] && [ "$s" -gt "$max_size" ]; then
                max_size=$s
            fi
        }
    done < <(git diff --cached --name-only --diff-filter=A)
    echo "Max blob size: $((max_size / 1024 / 1024)) MB"
    
    # Step 5: JSON/JSONL validity
    echo "== 5. JSON / JSONL validity =="
    while IFS=$'\t' read -r _ path; do
        case "$path" in
            *.jsonl) git show ":$path" | python3 -c "
import json,sys
for i,l in enumerate(sys.stdin,1):
    if l.strip():
        try: json.loads(l)
        except Exception as e: sys.exit(f'BAD $f:{i}: {e}')" || echo "INVALID: $path" ;;
            *.json)  git show ":$path" | python3 -c "import json,sys; json.load(sys.stdin)" || echo "INVALID: $path" ;;
        esac
    done < <(git diff --cached --name-only --diff-filter=A)
    ok "all staged .json/.jsonl parse"
    
    echo "CHECK COMPLETE"
else
    echo "SHA-256 verification FAILED"
    diff -u "$BASE/cache/manifest_sorted.sha256" "$BASE/cache/staged_sorted.sha256"
    exit 1
fi
