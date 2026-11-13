#!/usr/bin/env bash
# release_staged.sh — verify the staged index, then split it into isolated commits.
#
#   ./release_staged.sh check     read-only: runs every gate, changes nothing (default)
#   ./release_staged.sh commit    runs every gate, then branches and commits in 4 groups + .gitignore
#
# Env vars:
#   MANIFEST=PUBLICATION_MANIFEST.json   manifest with {"entries":[{"path":..,"sha256":..}]}
#   BRANCH=diag-pipeline-2026-11-07      branch to create (must not exist)
#   ACK_MODIFIED=1   you read the diff of the 2 modified files
#   ACK_LICENSE=1    you read the viewer-script headers and attribution is correct
#   ACK_SECRETS=1    you reviewed the grep hits (only needed if there are any)
#   VIEWER_MSG="..." commit message for the viewer-script group (write it AFTER the header check)
#   ALLOW_NO_GITLEAKS=1  skip gitleaks if not installed (not recommended)
#   EXCLUDE="path1 path2"  staged additions to keep OUT of the commits (default: the 102 MB output jsonl).
#                          They are still hashed/validated/scanned, left untracked, and added to .gitignore.
#                          Use EXCLUDE='' to exclude nothing.
set -euo pipefail

MODE="${1:-check}"
MANIFEST="${MANIFEST:-PUBLICATION_MANIFEST.json}"
BRANCH="${BRANCH:-diag-pipeline-2026-11-07}"
SNAP="cache/staged_snapshot_20261107.txt"
LOGFILE="batch_pipeline.log"
MAX_BYTES=$((95 * 1024 * 1024))
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
T="$TMP/staged.txt"

die() { echo "FAIL: $*" >&2; exit 1; }
ok()  { echo "ok:   $*"; }
[ "$MODE" = check ] || [ "$MODE" = commit ] || die "usage: $0 check|commit"
git rev-parse --git-dir >/dev/null 2>&1 || die "not in a git repo"
mkdir -p cache

# ---- groups (read a name-status file, print matching lines) -------------------
g1() { grep -P '^M\t' "$1" || true; grep -P '^A\t(docs/[^/]*\.md|scripts/[^/]*\.py)$' "$1" || true; }
g2() { grep -P '^A\t(DATASETS/.*\.jsonl?|docs/[^/]*\.json)$' "$1" || true; }
g3() { grep -P '^A\tDATASETS/(browser_api\.js|main\.js|pdf_scripting_api\.js|pdf_viewer_wrapper\.js|shared_rollup\.js|index\.css)$' "$1" || true; }
g4() { grep -P '^A\tDATASETS/d1_diagnostic_2026-11-06/page_0001/[^/]*\.png$' "$1" || true; }

echo "== 1. index inventory"
git diff --cached --name-status > "$T"
nA=$(grep -c -P '^A\t' "$T" || true)
nM=$(grep -c -P '^M\t' "$T" || true)
nAll=$(wc -l < "$T")
[ "$nA" = 702 ] && [ "$nM" = 2 ] && [ "$nAll" = 704 ] \
  || die "expected 702 A + 2 M = 704, got A=$nA M=$nM total=$nAll (other statuses: $(cut -f1 "$T" | sort | uniq -c | tr '\n' ' '))"
ok "702 additions + 2 modifications"

EXCLUDE="${EXCLUDE-DATASETS/batch_pipeline_output.jsonl}"
: > "$TMP/x.txt"
for p in $EXCLUDE; do
  esc="$(printf '%s' "$p" | sed 's/[][\.*^$]/\\&/g')"
  grep -P "^A\t${esc}\$" "$T" >> "$TMP/x.txt" || die "EXCLUDE path is not a staged addition: $p"
done
grep -vxFf "$TMP/x.txt" "$T" > "$TMP/eff.txt" || true
nX=$(wc -l < "$TMP/x.txt")
echo "excluded from commits: $nX file(s)"; cut -f2 "$TMP/x.txt" | sed 's/^/        /'

echo "== 2. group definitions partition the index"
WANT1=$((28 - $(g1 "$TMP/x.txt" | wc -l))); WANT2=$((11 - $(g2 "$TMP/x.txt" | wc -l)))
WANT3=$((6 - $(g3 "$TMP/x.txt" | wc -l)));   WANT4=$((658 - $(g4 "$TMP/x.txt" | wc -l)))
for n in 1 2 3 4; do "g$n" "$TMP/eff.txt" > "$TMP/g$n.txt"; done
c1=$(wc -l < "$TMP/g1.txt"); c2=$(wc -l < "$TMP/g2.txt"); c3=$(wc -l < "$TMP/g3.txt"); c4=$(wc -l < "$TMP/g4.txt")
[ "$c1" = "$WANT1" ] && [ "$c2" = "$WANT2" ] && [ "$c3" = "$WANT3" ] && [ "$c4" = "$WANT4" ] \
  || die "group sizes $c1/$c2/$c3/$c4, expected $WANT1/$WANT2/$WANT3/$WANT4"
cat "$TMP"/g[1-4].txt | sort > "$TMP/grouped.txt"
[ -z "$(uniq -d "$TMP/grouped.txt")" ] || die "a file matches more than one group"
left="$(sort "$TMP/eff.txt" | comm -23 - "$TMP/grouped.txt")"
[ "$left" = "$(printf 'A\t%s' "$LOGFILE")" ] || die "ungrouped leftovers are not just $LOGFILE: $left"
ok "groups $c1/$c2/$c3/$c4; only $LOGFILE is left out"

echo "== 3. staged-blob SHA-256 vs manifest (additions)"
[ -f "$MANIFEST" ] || die "manifest not found: $MANIFEST"
export MANIFEST SNAPFILE="$T"
python3 - <<'PY'
import hashlib, json, os, subprocess, sys
man = json.load(open(os.environ["MANIFEST"], encoding="utf-8"))
entries = {e["path"]: e["sha256"] for e in man["entries"]}
paths = [l.split("\t", 1)[1] for l in open(os.environ["SNAPFILE"], encoding="utf-8").read().splitlines() if l.startswith("A\t")]
assert len(paths) == 702 and len(set(paths)) == 702, f"path count {len(paths)}"
bad = []
for p in paths:
    h = hashlib.sha256(subprocess.check_output(["git", "show", f":{p}"])).hexdigest()
    if entries.get(p) != h:
        bad.append((p, entries.get(p), h))
if bad:
    for b in bad[:20]: print("MISMATCH", *b, file=sys.stderr)
    sys.exit(f"{len(bad)} mismatches")
print(f"ok:   {len(paths)} staged blobs match manifest")
PY

echo "== 4. staged blob sizes"
big=0
while IFS=$'\t' read -r _ f; do
  s=$(git cat-file -s ":$f"); [ "$s" -gt "$MAX_BYTES" ] && { echo "TOO BIG: $s $f" >&2; big=1; }
done < "$TMP/eff.txt"
[ "$big" = 0 ] || die "file(s) over 95 MB (GitHub limit is 100 MB)"
ok "no to-be-committed blob over 95 MB; largest:"
while IFS=$'\t' read -r _ f; do echo "$(git cat-file -s ":$f") $f"; done < "$TMP/eff.txt" | sort -rn | head -5 | sed 's/^/        /'

echo "== 5. JSON / JSONL validity (staged blobs)"
while IFS=$'\t' read -r _ f; do
  case "$f" in
    *.jsonl) git show ":$f" | python3 -c "
import json,sys
for i,l in enumerate(sys.stdin,1):
    if l.strip():
        try: json.loads(l)
        except Exception as e: sys.exit(f'BAD $f:{i}: {e}')" || die "invalid JSONL: $f" ;;
    *.json)  git show ":$f" | python3 -c "import json,sys; json.load(sys.stdin)" || die "invalid JSON: $f" ;;
  esac
done < "$T"
ok "all staged .json/.jsonl parse"

echo "== 6. secret scan (staged content)"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --staged --no-banner 2>/dev/null || gitleaks protect --staged --no-banner || die "gitleaks reported findings"
  ok "gitleaks clean"
elif [ "${ALLOW_NO_GITLEAKS:-0}" = 1 ]; then echo "warn: gitleaks skipped"
else die "gitleaks not installed (set ALLOW_NO_GITLEAKS=1 to skip)"; fi
XSPEC=(); for p in $EXCLUDE; do XSPEC+=(":!$p"); done
hits="$(git diff --cached -U0 -- . ':!*.png' "${XSPEC[@]}" | grep -nEi '^\+.*(api[_-]?key|secret|password|bearer|token|C:\\Users|/home/)' || true)"
if [ -n "$hits" ]; then
  echo "grep hits: $(printf '%s\n' "$hits" | wc -l) (first 40):"; printf '%s\n' "$hits" | head -40 | cut -c1-200
  [ "$MODE" = check ] || [ "${ACK_SECRETS:-0}" = 1 ] || die "review the hits above, then rerun with ACK_SECRETS=1"
else ok "no keyword hits"; fi

echo "== 7. viewer-script headers (group 3)"
cut -f2 "$TMP/g3.txt" | while read -r f; do echo "--- $f"; git show ":$f" | head -15; done
[ "$MODE" = check ] || [ "${ACK_LICENSE:-0}" = 1 ] || die "read the headers above (license + upstream credit), then rerun with ACK_LICENSE=1"

echo "== 8. diffs of the 2 modified (already-public) files"
git diff --cached --stat -- $(grep -P '^M\t' "$T" | cut -f2)
git diff --cached -- $(grep -P '^M\t' "$T" | cut -f2) | head -150
[ "$MODE" = check ] || [ "${ACK_MODIFIED:-0}" = 1 ] || die "read the diffs above, then rerun with ACK_MODIFIED=1"

if [ "$MODE" = check ]; then
  echo; echo "CHECK COMPLETE (index untouched). To commit: ACK_MODIFIED=1 ACK_LICENSE=1 [ACK_SECRETS=1] VIEWER_MSG=\"...\" $0 commit"
  exit 0
fi

# ---------------------------------- commit mode ----------------------------------
echo "== 9. commit"
[ -n "${VIEWER_MSG:-}" ] || die "set VIEWER_MSG after checking the headers (don't claim an attribution you haven't verified)"
git show-ref --verify --quiet "refs/heads/$BRANCH" && die "branch $BRANCH already exists"
[ ! -e "$SNAP" ] || die "$SNAP already exists; a previous run may have started. Inspect before rerunning"
git diff --quiet -- .gitignore || die ".gitignore has unstaged changes; commit or stash them first"

TREE="$(git write-tree)"
echo "$TREE" > cache/index_backup_tree.txt
cp "$TMP/eff.txt" "$SNAP"
echo "index saved as tree $TREE (restore with: git read-tree $TREE)"

git switch -c "$BRANCH"
git reset -q   # unstages only; working tree untouched

commit_group() {  # n want message
  local n="$1" want="$2" msg="$3"
  "g$n" "$SNAP" | cut -f2- | xargs -d '\n' git add --
  local got; got=$(git diff --cached --name-only | wc -l)
  [ "$got" = "$want" ] || die "group $n staged $got files, expected $want. Restore index: git read-tree $TREE"
  git commit -q -m "$msg"
  ok "group $n committed ($got files): $msg"
}
commit_group 1 "$WANT1" "docs and scripts: audit documentation, pipeline tools, live file edits"
commit_group 2 "$WANT2" "JSON and JSONL: pipeline, OCR, depth-run records"
commit_group 3 "$WANT3" "$VIEWER_MSG"
commit_group 4 "$WANT4" "Diagnostic PNGs: D1 component outputs"

for p in "$LOGFILE" $EXCLUDE; do grep -qxF "/$p" .gitignore 2>/dev/null || echo "/$p" >> .gitignore; done
git add .gitignore
git commit -q -m "Ignore local-only files (log, oversized pipeline output)"
ok ".gitignore committed"

[ -z "$(git diff --cached --name-only)" ] || die "index not empty after commits"
echo; git log --oneline -6
echo; echo "Not pushed. Review, then: git push -u origin $BRANCH   (and open a PR)"
