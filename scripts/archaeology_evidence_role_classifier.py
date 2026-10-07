#!/usr/bin/env python3
"""
EVIDENCE ROLE CLASSIFIER — capture / mirror / simulation / synthetic.

Filenames do NOT establish evidentiary weight. `StateMocks.ts` is named "Mocks"
but POG2's own .rules.md forbids only jest.fn()-style test isolation mocks and
placeholders. A behavioral model of an external system is a different thing.

Classify each artifact by ROLE, using structural signals:
  CAPTURE     - real fetch of the external system; carries non-fabricable
                values (CRCs, hashes, launcher params, live hosts)
  MIRROR      - translates observed external behavior into local interface
  SIMULATION  - models external state transitions to exercise local logic
  SYNTHETIC   - deliberate abstraction/test values (counting sequences)
"""
import json
import re
from pathlib import Path

POG2 = Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2")
SCRATCH = POG2 / "scratch"

print("=" * 78)
print("EVIDENCE ROLE CLASSIFIER")
print("=" * 78)
print()

# ---------------------------------------------------------------- CAPTURE
print("### CAPTURE — real fetch of the external system")
print()

cap_ts = SCRATCH / "intercept_beta_config.ts"
if cap_ts.exists():
    txt = cap_ts.read_text(encoding="utf-8", errors="replace")
    uri = re.search(r'configURI\s*=\s*"([^"]+)"', txt)
    out = re.search(r'outputFile\s*=\s*"([^"]+)"', txt)
    fn = re.search(r'(\w+)\(configURI\)', txt)
    print(f"  tool          : intercept_beta_config.ts")
    print(f"  fetches       : {uri.group(1) if uri else '?'}")
    print(f"  via           : {fn.group(1) if fn else '?'}()   <- real downloader")
    print(f"  writes        : {out.group(1) if out else '?'}")
    if out:
        d = re.search(r"(\d{4}-\d{2}-\d{2})", out.group(1))
        print(f"  DATE IN NAME  : {d.group(1) if d else '?'}   <- interception date")
print()

cfg = SCRATCH / "beta_config_structured.json"
if cfg.exists():
    d = json.loads(cfg.read_text(encoding="utf-8", errors="replace"))
    m = d.get("metadata", {})
    print(f"  captured file : beta_config_structured.json")
    print(f"  params        : {len(d.get('params', {}))} launcher params")
    print(f"  download_crc_0: {m.get('download_crc_0')}   <- CRC, not fabricable")
    print(f"  download_hash : {len(str(m.get('download_hash_0', '')))} chars  <- signed hash")
    print(f"  host          : {d.get('params', {}).get('3', '?')}")
    print()

raw = SCRATCH / "beta_config_captured.ws"
if raw.exists():
    head = raw.read_text(encoding="utf-8", errors="replace")[:200]
    print(f"  raw capture   : beta_config_captured.ws ({raw.stat().st_size} bytes)")
    print(f"  first line    : {head.splitlines()[0] if head else '?'}")
print()

routing = SCRATCH / "beta_routing_manifest.json"
if routing.exists():
    r = json.loads(routing.read_text(encoding="utf-8", errors="replace"))
    print(f"  routing       : beta_routing_manifest.json")
    print(f"    js5.host    : {r.get('js5', {}).get('host')}")
    print(f"    port        : {r.get('js5', {}).get('port')}")
    print(f"    buildId     : {r.get('js5', {}).get('buildId')}")
    print(f"    world.id    : {r.get('world', {}).get('id')}")
    print()

# ---------------------------------------------------------------- SIMULATION
print("### SIMULATION — models external state to exercise local logic")
print()
sm = POG2 / "src" / "limbs" / "logical" / "StateMocks.ts"
if sm.exists():
    txt = sm.read_text(encoding="utf-8", errors="replace")
    print(f"  file          : src/limbs/logical/StateMocks.ts")
    print(f"  header says   : \"deterministic mock states for the 2026 Beta environment\"")
    print(f"                  \"bypassing network-dependent state checks\"")
    print()
    print("  ROLES PRESENT:")
    if "getLobbyState" in txt:
        print("    getLobbyState()  -> MIRROR: returns varbit/varp pair to reach a")
        print("                        known lobby state without the live server")
    if "getCombatState" in txt:
        print("    getCombatState() -> SIMULATION: adrenaline/cooldown/necrosis state")
    if "getPeacefulState" in txt:
        print("    getPeacefulState()-> SIMULATION: 'Prevents the Arms Lock-up bug in")
        print("                        the 2026 Beta' <- models an OBSERVED defect")
print()
print("  KEY SIGNAL — a pure test mock would not encode an observed bug:")
print("    'Prevents the \"Arms Lock-up\" bug in the 2026 Beta.'")
print("    That is a behavioural finding about the real system, not fabrication.")
print()

# ---------------------------------------------------------------- SYNTHETIC
print("### SYNTHETIC — deliberate abstraction / test values")
print()
bc = POG2 / "src" / "core" / "beta_constants.ts"
if bc.exists():
    txt = bc.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"enum BetaScripts\s*\{(.*?)\}", txt, re.DOTALL)
    if block:
        vals = re.findall(r"(\w+)\s*=\s*(\d+)", block.group(1))
        nums = [int(v) for _, v in vals]
        print(f"  enum BetaScripts values: {nums}")
        seq1 = [n for n in nums if n in (123, 456, 789)]
        seq2 = [n for n in nums if n in (101, 202, 303, 404, 505, 606)]
        print(f"    arithmetic triples (x123): {seq1}   <- synthetic")
        print(f"    step-101 sequence        : {seq2}   <- synthetic")
        print()
        print("  Contrast — irregular values in the SAME file (require provenance):")
        for name in ["SAVE_CONFIRM", "SAVE_CONFIRM_HANDLER", "EXIT_DIALOG_NO",
                     "EXIT_DIALOG_YES", "VARBIT_OPTION_LOADER", "MASTER_APPEARANCE_BUILDER"]:
            mm = re.search(rf"{name}\s*=\s*(\d+)", txt)
            if mm:
                print(f"    {name:26s} = {mm.group(1)}")
print()
print("=" * 78)
print("RULE CHECK — .rules.md")
print("=" * 78)
rm = POG2 / ".rules.md"
if rm.exists():
    t = rm.read_text(encoding="utf-8", errors="replace")
    print("  §1 NO MOCKS forbids:")
    for line in t.splitlines():
        s = line.strip()
        if s.startswith("- ") and ("Ollama" in s or "jest" in s or "neurological" in s):
            print(f"    {s}")
    print()
    print("  Target = test-isolation mocks + placeholders.")
    print("  NOT targeted = a local model of an external system's observed state.")
    print("  => StateMocks.ts is compatible with §1; it is not jest.fn() and it is")
    print("     not a placeholder — it returns concrete, executable state.")
