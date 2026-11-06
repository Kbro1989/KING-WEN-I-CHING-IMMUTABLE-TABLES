#!/usr/bin/env python3
"""Post-run freeze manifest verification battery (Milestone 4 closure)."""
import json, hashlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES"
manifest_path = f"{REPO}/DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json"
audit_path    = f"{REPO}/DATASETS/structural_preservation/1505.05770_end_to_end_audit.json"

EXPECTED_AGG   = "b566c01fecff6ca74678644d3f56b630f8b0cb67bd8ee7eb4a6c49be4fb00bd5"
EXPECTED_PDF   = "776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a"
EXPECTED_DET   = "78651d74afc8e71d2f2de952963905a5cfb56696c071109d10cfd1903ab41949"
EXPECTED_AUDIT = "6fdc6ce984da9f01921d00202a02fdd84da5c992b201953c4435d6a1bdacba09"
EXPECTED_RECON = "ff466cce4763c9d5b0917c24ae5638dc228f5d230a4b6a773f2e3478eb1ca6da"

with open(manifest_path, encoding="utf-8") as f:
    m = json.load(f)

results = {}

# 1. 3,644 individual image hashes
img_count = len(m["individual_image_sha256_manifest"])
results["1_image_count"] = ("OK" if img_count == 3644 else "FAIL", f"{img_count}/3644")

# 2. Aggregate render hash unchanged
agg = m["render_accounting"]["aggregate_totals"]["all_renders_aggregate_sha256"]
results["2_aggregate_hash"] = ("OK" if agg == EXPECTED_AGG else "FAIL", agg[:16] + "...")

# 3. Source PDF hash unchanged
pdf_hash = m["source_pdf"]["sha256"]
results["3_source_pdf_hash"] = ("OK" if pdf_hash == EXPECTED_PDF else "FAIL", pdf_hash[:16] + "...")
results["3b_matches_expected_field"] = ("OK" if m["source_pdf"]["matches_expected"] else "FAIL", str(m["source_pdf"]["matches_expected"]))

# 4. Detector hash unchanged
det_hash = m["scripts_provenance"]["detector_script"]["sha256"]
results["4_detector_hash"] = ("OK" if det_hash == EXPECTED_DET else "FAIL", det_hash[:16] + "...")

# 5. Audit JSON in downstream_artifact_freshness
freshness = m["downstream_artifact_freshness"]
audit_key = "1505.05770_end_to_end_audit.json"
if audit_key in freshness:
    rec_hash = freshness[audit_key]["sha256"]
    results["5_audit_in_freshness"] = ("OK" if rec_hash == EXPECTED_AUDIT else "FAIL", rec_hash[:16] + "...")
else:
    results["5_audit_in_freshness"] = ("FAIL", "KEY MISSING")

# 6. Test count and reconciliation SHA
tc = m["regression_test_evidence"]["test_count"]
rsha = m["regression_test_evidence"]["reconciliation_test_sha256"]
results["6_test_count"] = ("OK" if tc == 571 else "FAIL", str(tc))
results["6b_reconciliation_sha"] = ("OK" if rsha == EXPECTED_RECON else "FAIL", rsha[:16] + "...")

# 7. Audit file on disk matches recorded hash
with open(audit_path, "rb") as f:
    disk_audit_sha = hashlib.sha256(f.read()).hexdigest()
rec_audit = freshness.get(audit_key, {}).get("sha256", "MISSING")
results["7_audit_disk_vs_recorded"] = ("OK" if disk_audit_sha == rec_audit else "FAIL",
                                        disk_audit_sha[:16] + "...")

# 8. Manifest self-hash
with open(manifest_path, "rb") as f:
    manifest_sha = hashlib.sha256(f.read()).hexdigest()
results["8_manifest_self_hash"] = ("RECORDED", manifest_sha)

# Report
print("=== FREEZE MANIFEST VERIFICATION (Milestone 4 — post audit JSON addition) ===")
all_pass = True
for key, (status, detail) in results.items():
    marker = "✓" if status in ("OK", "RECORDED") else "✗"
    if status == "FAIL":
        all_pass = False
    print(f"  {marker} [{status}] {key}: {detail}")

print()
print(f"=== OVERALL: {'ALL CHECKS PASS' if all_pass else 'ONE OR MORE FAILURES'} ===")

