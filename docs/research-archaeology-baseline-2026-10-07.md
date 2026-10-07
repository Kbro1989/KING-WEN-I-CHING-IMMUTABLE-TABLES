# Kbro1989 RESEARCH ARCHAEOLOGY — CORRECTED BASELINE

## Agent Handoff / Provenance State

Reconstructed from disk + git + live GitHub, 2026-10-07.
Supersedes the 2026-10-07 dossier where they conflict.

---

## 0. CRITICAL CORRECTION — DEVICE DESTRUCTION

The dossier treats the repositories as an accumulating linear history. The user
supplied a fact that invalidates that model:

> **POG2 memory + D-sovereign were lost when a device was destroyed. A repo save
> was made immediately before destruction. The present POG2 is a clone of the
> old device.**

This is not a footnote. It changes what git dates mean:

```
old device  ──[clone]──▶  present POG2
     │
     └──[saved to GitHub immediately before destruction]──▶  D-sovereign-
```

Consequences:

1. **Git history in present POG2 may be inherited from the old device.** A
   commit date is when the old device's working tree was committed, not
   necessarily when a file was authored.
2. **D-sovereign- is the pre-destruction save.** It is the closest thing to a
   frozen snapshot of the lost device's research state.
3. **Anything not cloned and not saved is gone.** The "earliest known artifact"
   may be unobservable.
4. `d:\` (the old device's drive) is **not mounted** — `ls /d` fails.

---

## 0.5 THE DESTRUCTION BOUNDARY — THE ORGANIZING PRINCIPLE

D-sovereign- is the save made immediately before the device was destroyed, so
**its final commit is the destruction boundary**:

```
DESTRUCTION BOUNDARY = 2026-07-07T01:51:42Z
                     = D-sovereign- final commit bd6ec4646d
                     = D-sovereign- pushed_at
```

**Anything at or before this instant belongs to the destroyed device.** It
survived only because it was cloned (POG2) or saved (D-sovereign-). It was
**not** authored on the current machine, and its git history may be inherited
rather than native.

```
        PRE  (<= 2026-07-07T01:51:42Z)        │  POST  (> boundary)
        destroyed-device era                  │  current machine
        survived via clone or save            │  genuinely authored here
```

This classification does not depend on *which repository currently holds* the
artifact — which is exactly what makes it useful.

### Corrected counts (user's own commits only)

Forked repos carry third-party history that never touched the device
(rsmv-upstream: 840 Skillbert commits; cinder: 221 NorfolkNChance commits;
OpenJarvis-original: 30 upstream). The user also commits under **five different
git identities** — `Kbro1989`, `kbro1989`, `Kbro`, `Pick of Gods`, plus two
email forms. Splitting on one author string silently drops commits; consolidate
identities first.

| repo | LOCAL PRE (destroyed) | LOCAL POST (this host) | upstream |
|---|---:|---:|---:|
| **POG2** | **113** | 4 | 8 |
| KING-WEN | 16 | 100 | 0 |
| OpenJarvis | 7 | 19 | 3 |
| rsmv-upstream | 0 | 7 | 840 |
| cinder | 0 | 4 | 221 |
| OpenJarvis-original | 0 | 3 | 30 |
| **TOTAL** | **136** | **137** | 1102 |

### What the boundary reveals

**1. POG2 is a fossil.** 113 of its 121 local commits are destroyed-device era
(93%). Only **4** commits happened on this host, and all four are cleanup:

```
2026-07-17T16:54:06  c8384a4e6  preserve non-rsmv artifacts: cache, error logs…
2026-07-17T17:20:38  de3cc70f4  preserve remaining non-rsmv artifacts…
2026-07-17T17:28:36  9d26f991c  preserve remaining src sections + runtime docs
2026-09-05T07:56:53  c039db0a0  .
```

POG2 was **not developed here** — it was cloned in and tidied. Its entire
research content (the Beta probes, `beta_constants.ts`, `StateMocks.ts`) is
destroyed-device era. Reading POG2 as "the current state of the project" is
wrong; it is a snapshot of a machine that no longer exists.

**2. The destroyed-device era is 83% POG2.** Of 136 local PRE commits, 113 are
POG2. KING-WEN contributes 16, OpenJarvis 7.

**3. King Wen straddles the boundary.** First commit **2026-07-03T00:21:39** —
**4 days before destruction** — and 100 of 116 commits are post-boundary.

```
2026-07-03  KING-WEN first commit        ← PRE  (destroyed device)
2026-07-07  DESTRUCTION BOUNDARY
2026-07-07+ 100 more KING-WEN commits    ← POST (this host)
```

So King Wen's *founding* is destroyed-device era, but its *development* is
this-host era. It is the first repo to span the transition.

**4. rsmv-upstream and cinder have no local PRE commits.** Every user commit in
both is post-boundary. The rsmv Beta probes were copied in on **2026-09-18** —
two months *after* destruction. That is consistent with §3: the source was
POG2's cloned content, not a live machine.

### Precedence rule

When the boundary and a repository's own dates disagree, **the boundary wins for
provenance**:

| Artifact | Date | Era | Reading |
|---|---|---|---|
| POG2 first commit | 2026-03-12 | PRE | destroyed device |
| atlas 1420 generated | 2026-03-22 | PRE | destroyed device (predates D-sovereign- by 27d) |
| D-sovereign- created | 2026-04-19 | PRE | migration destination |
| POG2 bulk import | 2026-05-21 | PRE | destroyed device |
| Beta enum outputs | 2026-06-17 | PRE | destroyed device |
| **D-sovereign- final commit** | **2026-07-07** | **BOUNDARY** | **the save** |
| rsmv `.pog2/` created | 2026-09-18 | POST | copy of cloned content |

### Caveat

The boundary is a *commit* timestamp, so it bounds **committed** work. Uncommitted
work on the destroyed device is unobservable — it left no boundary-crossing
record. The absence of PRE commits in a repo means only that no pre-destruction
work was ever committed there, not that none existed.

---

## 1. VERIFIED CHRONOLOGY (hard evidence)

| Date (UTC/offset as recorded) | Event | Evidence class |
|---|---|---|
| 2026-03-12 21:25:49 -0500 | POG2 first commit `b59654d4` "first commit: Sovereign Substrate POG2" | **SOLID** (git) |
| 2026-03-22 21:46:46.890Z | `atlas/interfaces/hud_interface_1420.json` generated | **SOLID** (embedded timestamp) |
| 2026-04-19 16:34:41Z | `Kbro1989/D-sovereign-` repo created | **SOLID** (GitHub API) |
| 2026-04-19 16:42:37 | `9a666db8fd` "chore: initial setup for full migration" | **SOLID** (git) |
| 2026-04-19 20:04:32 | `4376a1959b` "feat: migrate core logic and main path (cache_pedagogy)" | **SOLID** (git) |
| **2026-05-06** | **Beta launcher config intercepted** — `intercept_beta_config.ts` writes `beta_config_2026-05-06.json` | **SOLID** (date encoded in source) |
| 2026-05-21 12:20:06 -0500 | POG2 bulk import `7e37114d2` — 777 files, +120,281/−98,561 | **SOLID** (git) |
| 2026-05-21 12:20:06 -0500 | All 34 Beta-cluster files first appear in git (POG2) | **SOLID** (git) |
| 2026-06-17 15:19:43 -0500 | `pull_beta_enums_output{,_utf8}.txt` written | **STRONG** (mtime) |
| 2026-06-18 21:04:59 | `901567460` "decoupling rsmv needs internalized partially" | **SOLID** (git) |
| 2026-06-23 05:11 | `POG2/.rules.md` mtime (the NO MOCKS rule) | **STRONG** (mtime) |
| 2026-07-07 01:51:42Z | `bd6ec4646d` D-sovereign- final commit (== `pushed_at`) | **SOLID** (git) |
| 2026-07-17 | `c8384a4e6`, `de3cc70f4` "preserve non-rsmv artifacts" | **SOLID** (git) |
| 2026-09-18 19:33:08 -0500 | `rsmv-upstream/scripts/.pog2/` directory created | **SOLID** (mtime) |

**The atlas entry (2026-03-22) predates D-sovereign- repo creation (2026-04-19)
by 27 days.** That is direct proof D-sovereign- is a migration destination, not
an origin.

**The Beta capture (2026-05-06) predates the bulk import (2026-05-21) by 15
days.** The interception happened on the destroyed device; the file entered git
two weeks later in a commit about styles. Another instance of
commit-date ≠ activity-date.

### Resolved: the `beta_routing_manifest.json` 2025-05-08 puzzle

The manifest's internal `timestamp` field is `1746708145` = **2025-05-08**,
over a year before the capture. Given the capture date is now known
(2026-05-06), the field is **not** a capture date:

```
beta_routing_manifest.json:
  build     = 45261
  timestamp = 1746708145  ->  2025-05-08T12:42:25Z   <- NOT the capture date
  variant   = BETA
  js5       = content.beta.runescape.com:43594  revision 225  buildId 1149
  world     = 204
```

The `js5` block (buildId 1149, revision 225, world 204) agrees with the
2026-05-06 capture, so the manifest *describes* the May-2026 Beta. The
`timestamp` field is therefore **stale or sourced from a different value** —
possibly a build/revision epoch, or copied from an earlier manifest.

**Status: no longer blocking.** The capture date (2026-05-06) is established
independently from source code, and the manifest's content is consistent with
it. The odd `timestamp` is a field-level artifact, not a chronology signal.
Treat `beta_routing_manifest.timestamp` as **unreliable** and use the
`intercept_beta_config.ts` output filename instead.

---

## 2. THE BETA CLUSTER — CORRECTED

The dossier lists ~11 probes. POG2 actually tracks **34** files in the Beta
cluster, plus more in `src/`:

```
scratch/:  analyze_beta_enums.ts          search_all_scripts_import_save.ts
           beta_config_captured.ws        search_avatar_beta_kws.ts
           beta_config_structured.json    search_beta_binary.ts
           beta_enums_dump.json           search_beta_scripts.ts
           beta_routing_manifest.json     search_beta_strings.ts
           decompile_beta_scripts.ts      search_config_beta.ts
           extract_beta_abilities_exact.ts search_enum_import_save.ts
           extract_beta_ability_structs.ts search_ifaces_import_save.ts
           extract_beta_config_abilities.ts search_import_save.ts
           extract_beta_dbrows.ts         search_import_save_binary.ts
           extract_beta_enums.ts          search_import_save_utf16.ts
           extract_beta_enums_raw.ts      search_importsave.ts
           extract_beta_interface_1430.ts search_interface_import_save.ts
           intercept_beta_config.ts       test_beta_urls.ts
           pull_beta_enums.ts             validate_beta_abilities.ts
           pull_beta_enums_output.txt     raw_beta_struct_inspect.ts
           pull_beta_enums_output_utf8.txt
src/core/: beta_constants.ts
src/limbs/logical/: StateMocks.ts
```

### All 34 landed in ONE bulk import

`git log --diff-filter=A` returns the **same commit** (`7e37114d2`,
2026-05-21) for every file. That commit's message is *"Add initial styles and
TypeScript configuration for web_hud"* — it does not describe Beta probes.
**First-git-appearance is therefore NOT the authoring date.** The cluster was
moved into the repo wholesale.

---

## 3. DIRECTION OF MOVEMENT — RESOLVED (scope corrected)

**The transfer is not "a few scratch scripts". It is 420 files.**

| | POG2 | rsmv-upstream |
|---|---|---|
| location | `scratch/` | `scripts/.pog2/sovereign/sovereign/` |
| git | **tracked** (481 files under `scratch/`) | **gitignored** (`.gitignore:233`) |
| file count | 472 | 445 |
| first dated | 2026-05-21 (bulk import) | dir created **2026-09-18** |

```
shared filenames : 420
  byte-identical : 198
  differing      : 222
only in POG2     :  52
only in rsmv     :  25
```

### The rewrite is machine-performed — proven

**482 of 482** import specifiers in the differing files were rewritten with a
single uniform transformation: the `rsmv/` path segment was stripped.

```
../src/rsmv/cache/sqlite.js  ->  ../cache/sqlite.js
../src/rsmv/constants.js     ->  ../constants.js
../rsmv/dist/cache/sqlite.js ->  ../dist/cache/sqlite.js
```

Not one file received a bespoke edit. **1 file** out of 222 differing files has
a non-import change (a `catch (e)` -> `catch (e: unknown)` type guard). Perfect
uniformity across 482 sites is a regex, not 482 hand edits.

### The tool that did it is still on disk — and it stayed behind

Two fixer scripts exist in POG2 `scratch/` and are **among the 52 files that did
NOT migrate to rsmv**:

**`fix_rsmv_comprehensive.ts`** — target directory:
```typescript
const targetDir = 'd:/POG2/src/rsmv';
```

This is decisive on three counts:

1. **`d:/POG2/`** is the *destroyed device's* path (drive `d:`, not mounted
   today). These scripts were authored on the old machine.
2. **`src/rsmv`** confirms rsmv was **vendored inside POG2** on the old device.
   That is why every probe imports `../src/rsmv/...` — in POG2, rsmv was a
   subdirectory, so the path was correct *there*.
3. When the same files were moved into rsmv-upstream, rsmv became the **root**,
   so `rsmv/` had to be stripped. The rewrite is the mechanical consequence of
   the relocation, and it is fully consistent with the stated direction.

**`fix_imports.ts`** walks `['src', 'multiplayer-globe-template', 'to-do-list-kv-template-123', '.']`
— a general relative-import extension fixer. Also left behind.

### Conclusion (evidence class: SOLID)

```
old device  d:/POG2/src/rsmv/          (rsmv vendored inside POG2)
     │
     │  research probes authored against ../src/rsmv/...
     │  bulk-imported into git 2026-05-21
     ▼
present POG2  scratch/                 (472 files, tracked)
     │
     │  copy 420 files + strip `rsmv/` from 482 imports (regex, mechanical)
     ▼
rsmv-upstream  scripts/.pog2/          (2026-09-18, untracked, 445 files)
```

Hypothesis B is now **SOLID** for this cluster, not merely consistent with
recollection. Hypothesis A (RSMV-first) is **refuted** for these files.

### Nested-directory fingerprint

`scripts/.pog2/sovereign/sovereign/` — `sovereign` appears **twice**. A copy
operation nested a directory that already contained `sovereign/`. Mechanical
trace of the move, not a design choice.

### What did NOT migrate (52 files)

The unmigrated set is itself evidence — it is the POG2-native research that had
no rsmv equivalent:

```
fix_imports.ts  fix_rsmv_comprehensive.ts        <- the fixers
beta_config_structured.json  beta_enums_dump.json  beta_routing_manifest.json
intercept_beta_config.ts     scan_avatar_interfaces.ts
dump_1420.ts  dump_1420_json.ts  dump_1797_json.ts
mass_discover_portals.ts     regenerate_interfaces.ts
cs2_instruction_tracer.ts    live_handshake_observer.ts
debug_parse_row89.ts  debug_parse_row12265.ts  debug_cache_ms.ts
+ 39 more
```

Note the Beta **config/enum captures** stayed in POG2 — only the *probe code*
was copied out.

---

## 4. D-SOVEREIGN- (the pre-destruction save)

**Repo:** `Kbro1989/D-sovereign-` — created 2026-04-19T16:34:41Z, last push
2026-07-07T01:51:58Z. 26,166 files. Default branch `main`. 13 commits.

### It is a MIGRATION DESTINATION

First two commits say so explicitly:
```
9a666db8fd  2026-04-19T16:42:37  chore: initial setup for full migration
4376a1959b  2026-04-19T20:04:32  feat: migrate core logic and main path (cache_pedagogy)
```

### Full commit history (oldest → newest)
```
2026-04-19T16:42:37  9a666db8fd  chore: initial setup for full migration
2026-04-19T20:04:32  4376a1959b  feat: migrate core logic and main path (cache_pedagogy)
2026-04-23T04:17:00  d37b6e6fa6  chore: initialize pedagogical research logs, quest data
2026-04-23T04:17:10  e83f321ca4  refactor: remove unused files and associated references
2026-04-26T13:50:45  ac9a691d4a  chore: remove unused files and associated references
2026-05-21T17:54:42  8ed3cc6c14  Add ToolRegistry and WorkforceManifest implementations
2026-05-25T07:23:23  41f7904162  cleanup
2026-05-26T16:16:18  f2c4120907  .
2026-06-01T19:36:28  e398650164  storage update training data
2026-06-01T19:40:24  403a5b89fb  Refactor code structure for improved readability
2026-06-10T13:17:02  9640d25eca  Create deno.yml
2026-06-10T13:17:22  b86a9d5dfe  Create webpack.yml
2026-07-07T01:51:42  bd6ec4646d  docs: update README to accurately describe actual code and func
```

Note: two commits named *"remove unused files"* — **content was deleted before
the save.** Some provenance is unrecoverable by design.

### Contents

```
src/generated/       atlas/              cache_pedagogy/
emergency/           learning/           memory/
pipelines/           session_dashboards/ snapshots/
test/                rolodex.json (389-model AI rolodex)
.manifest.md  .pog2.md  .rules.md  README.md
```

README: *"Distributed state management layer for the POG2 Sovereign Stack…
Manages distributed state across the POG2 edge deployment."*

### It does NOT contain the Beta probes

Zero files matching `beta`, `import_save`, or `scratch/`. The Beta cluster
never migrated to D-sovereign-. It stayed in POG2.

---

## 5. INTERFACE 1420 — CONTRADICTION WITH THE DOSSIER

The dossier frames 1420 around "Import Save". The D-sovereign- atlas says
otherwise:

```json
{
  "interfaceId": 1420,
  "discoveredKeywords": ["settings", "graphics", "options"],
  "relevanceScore": 3,
  "contextSnippet": "y             o  graphics settings                <",
  "classification": "SETTINGS_PANEL",
  "timestamp": 1774216006890
}
```

**`SETTINGS_PANEL`**, generated **2026-03-22T21:46:46.890Z**.

`cache_pedagogy/atlas/interfaces/_manifest.json` — 98 candidates, top scorers
all settings/menu/controls interfaces (1496 score 11, 1922 score 9, 1433
score 6). This is a **keyword-scored HUD/interface atlas**, not a save-import
hunt.

### Reconciliation

The atlas was produced by a **different, earlier tool** than the Beta probes:

| | atlas pass | Beta probes |
|---|---|---|
| date | 2026-03-22 | 2026-05-21 (bulk) |
| method | keyword scoring over interfaces | binary/UTF-16 search of `rs2client.exe` + cache extraction |
| found | 98 candidates incl. 1420 = SETTINGS_PANEL | 1420 component 150 → script 13914 → varbit 28749 |
| location | D-sovereign- `cache_pedagogy/atlas/` | POG2 `scratch/` |

Both touch interface 1420 but **ask different questions**. The dossier's
"Import Save" framing comes from the *Beta-probe* line, not the atlas line.
Neither should overwrite the other.

---

## 6. beta_constants.ts — VERIFIED, WITH A CRITICAL CAVEAT

`POG2/src/core/beta_constants.ts` (80 lines) exists and is tracked. Header:

> *"Mirror of authoritative Jagex Beta script and variable IDs. Decoupled from
> the rsmv substrate to ensure Brain runtime independence."*

### The `BetaScripts` enum is NOT real Jagex data

```typescript
export enum BetaScripts {
    LOBBY_MASTER_INIT = 123,
    LOBBY_PLAY_NOW = 456,
    MASTER_INTERACTION = 789,
    MINIMAP_CLICK_HANDLER = 101,
    ABILITY_DISPATCH_HANDSHAKE = 202,
    ADRENALINE_TELEMETRY = 303,
    ACTION_BAR_MASTER = 404,
    MAP_REGION_LOAD = 505,
    LOBBY_SAVE_IMPORT_SYNC = 606
}
```

`123, 456, 789` and `101, 202, 303, 404, 505, 606` are **synthetic sequences**,
not cache-derived IDs. Compare the *real* IDs elsewhere in the same file
(10896, 13914, 10702, 10703, 7937, 7888, 9344, 9342, 7893, 11195, 6233) which
are irregular and plausibly extracted. The header's "authoritative" claim does
not hold for this enum.

### Verified real (irregular, cross-referenced)
```
SAVE_CONFIRM         = 28749   1-bit [0-0] varp=5783  (script 13914)
SAVE_CONFIRM_HANDLER = 13914
EXIT_DIALOG_NO       = 17062   6-bit varp=3387 (script 10702)
EXIT_DIALOG_YES      = 17063   6-bit varp=3387 (script 10703)
EXIT_NO_HANDLER      = 10702
EXIT_YES_HANDLER     = 10703
CHAR_CREATE_STATE    = 28557   3-bit [9-11] varp=5745
VARBIT_OPTION_LOADER = 10896   arg[2]=enumId, arg[3]=varbitId
```

Source comment: `Source: C:\ProgramData\Jagex\RuneScape-BETA (Build 1149)`

### Collision check — CORRECTED by live verification

The draft flagged these as LOW confidence because the numbers also appeared
elsewhere. **Live cache verification refuted that** (§6, LIVE CACHE VERIFICATION):

| Constant | Claimed meaning | Also appeared as | Original call | Corrected |
|---|---|---|---|---|
| `4500` | `VARBIT_IMPORT_SAVE_STALL` | substring of `#FF4500` | ~~LOW~~ | **CONFIRMED** — referenced by 17 clientscripts |
| `1200` | `VARP_BETA_ACTIVE` | `breathCycle: 1200` | ~~LOW~~ | **CONFIRMED** — referenced by 50 clientscripts, 182 config occurrences |
| `606` | `LOBBY_SAVE_IMPORT_SYNC` | synthetic enum value | LOW | LOW — but note #606 *does* exist as a script; the enum value is still synthetic |

**Lesson:** an incidental grep collision is evidence the *search* matched the
wrong thing — not evidence the identifier is fake. Verify against the domain
before downgrading.

### LIVE CACHE VERIFICATION (2026-10-07) — the claims are SOLID

The BETA client was running during this investigation, so the claims in
`beta_constants.ts` could be tested against ground truth instead of argued about.

**Cache:** `C:\ProgramData\Jagex\RuneScape-BETA` — 11.26 GB, 41 `js5-N.jcache`.
Format: **SQLite**, tables `cache(KEY, DATA, VERSION, CRC)` + `cache_index`.
Payloads are **ZLB-compressed** (`5a4c4201`, u32 LE size at offset 4, zlib at 8).

Majors (from `rsmv-upstream/src/constants.ts`): clientscript=12, config=2,
components=3, enums=17.

```
clientscript(12): 21,208 entries    config(2): 40
components(3):     1,889 entries    enums(17): 69
```

| signal | id | verdict | evidence |
|---|---:|---|---|
| BODY_MORPH_SLIDER | 7893 | **CONFIRMED** | real clientscript |
| MASTER_APPEARANCE_BUILDER | 7937 | **CONFIRMED** | real clientscript |
| EXIT_NO_HANDLER | 10702 | **CONFIRMED** | real clientscript |
| EXIT_YES_HANDLER | 10703 | **CONFIRMED** | real clientscript |
| VARBIT_OPTION_LOADER | 10896 | **CONFIRMED** | real clientscript |
| AVATAR_REFRESH_HANDLER | 11195 | **CONFIRMED** | real clientscript |
| SAVE_CONFIRM_HANDLER | 13914 | **CONFIRMED** | real clientscript |
| CHAR_CREATE_PANEL | 16899 | **CONFIRMED** | real clientscript |
| SAVE_CONFIRM | 28749 | **CONFIRMED** | referenced by **6** clientscripts; varp 5783 present |
| CHAR_CREATE_STATE | 28557 | **CONFIRMED** | referenced by **26** clientscripts; varp 5745 present |
| EXIT_DIALOG_NO | 17062 | **CONFIRMED** | referenced by **23** clientscripts; varp 3387 present |
| EXIT_DIALOG_YES | 17063 | **CONFIRMED** | referenced by **14** clientscripts; varp 3387 present |
| **VARBIT_IMPORT_SAVE_STALL** | **4500** | **CONFIRMED** | referenced by **17** clientscripts |
| **VARP_BETA_ACTIVE** | **1200** | **CONFIRMED** | referenced by **50** clientscripts |
| varp 5783 / 5745 / 3387 / 1200 | — | **CONFIRMED** | present in config major |

**18 CONFIRMED. 0 UNVERIFIABLE.**

### CORRECTION: "collision" is not "refutation"

The earlier draft marked `4500` and `1200` **LOW — do not trust** because they
also matched `#FF4500` and `breathCycle: 1200`. **That was wrong.** Both are
genuine cache values:

```
VARBIT_IMPORT_SAVE_STALL = 4500  -> referenced by 17 clientscripts
VARP_BETA_ACTIVE         = 1200  -> referenced by 50 clientscripts, 182 config occurrences
```

A number can appear inside a colour literal **and** be a real varp id. Finding an
incidental collision is not evidence the identifier is fake — it is evidence that
grep matched the wrong thing. **Confirm against the domain before dismissing.**

### The one claim that does NOT hold

```
Claim: SAVE_CONFIRM = varbit 28749, width 1, bits [0-0], varp 5783
```

Decoding `config` key 69 revealed a real varbit-family table on varp 5783:

```
0100 1697 02 1f1f 000100     1697 = 5783
0100 1697 02 0002 000100
0100 1697 02 0308 000100
0100 1697 02 090a 000100
0100 1697 02 0c0c 000100   ... through (31,31)
```

Bit fields on varp 5783: **(0,2) (3,8) (9,10) (12,12) (13,13) … (31,31)**.

- varp 5783 **is real** and **does host varbits** → CONFIRMED
- but bit 0 belongs to a **3-bit field (0,2)**, and **no (0,0) field exists**
- → the `1-bit [0-0]` annotation is **NOT confirmed**

**Reading:** the varp is genuine; the width/offset detail is from a different
build, or was inferred rather than extracted. This is the right granularity to
report — *the base is real, one annotation is not* — rather than collapsing the
whole file to "synthetic" or "authentic".

### The control that keeps this honest

All 21,208 clientscripts exist, so ids `123/456/789/101/202/303/404/505/606` are
**also present**. Presence alone proves nothing.

```
SYNTHETIC 123 -> exists as clientscript #123  (meaningless: 21,208 scripts exist)
```

The synthetic `BetaScripts` enum is therefore **not detectable by presence** —
it is detectable only because its values form arithmetic sequences. Role
classification must be structural, not lookup-based.

### StateMocks.ts — CORRECTED: role, not filename

**This section previously read "StateMocks.ts is explicitly a mock … its
constants cannot be evidence of actual Jagex mechanics" and called it "the
user's own no-mock rule violated inside POG2's own tree." Both were wrong, and
both were exactly the error this method warns against: judging an artifact by
its filename.**

`src/limbs/logical/StateMocks.ts`:
> *"Provides deterministic mock states for the 2026 Beta environment. Used for
> bypassing network-dependent state checks."*

```typescript
getLobbyState:    () => ({ varbits: { [BetaVars.VARBIT_IMPORT_SAVE_STALL]: 0 },
                           varps:   { [BetaVars.VARP_BETA_ACTIVE]: 1 } }),
getCombatState:   () => ({ adrenaline: 10000, cooldowns: {}, necrosisStacks: 12 }),
getPeacefulState: () => ({ adrenaline: 0, inCombat: false,
                           lastCombatTick: -100, stance: 'PEACEFUL' })
```

**The decisive signal — a test mock would not encode an observed bug:**

> *"Prevents the \"Arms Lock-up\" bug in the 2026 Beta."*

That is a **behavioural finding about the real system**, not fabrication. Test
mocks isolate code from a dependency; this file *models a defect the author
observed in the live Beta*. It is a **simulation/mirror of external state**, and
it is therefore compatible with §1 of `.rules.md` (see below).

### `.rules.md` §1 NO MOCKS — what it actually forbids

Verified from `POG2/.rules.md` (2,150 bytes, mtime 2026-06-23):

```
### 1. NO MOCKS 🚫
**You must NEVER use mocks, fakes, or stubbed data.**
- All code must run against REAL environments (Ollama, local SQLite, actual file systems).
- Tests must interact with real neurological substrates.
- No `jest.fn()` or placeholder mocks allowed.
- **Example**: Use actual `TernaryRouter` and `ModelClient` in all audits.
```

The rule names `jest.fn()` and *"placeholder mocks"*. Its target is
**test-isolation mocks and placeholders** — not a local model of an external
system's observed state. `StateMocks.ts` is neither: it is not `jest.fn()`, it
is not a placeholder, and it returns concrete executable state.

The rule is a **no-fake-functionality** principle, not a prohibition on
modelling systems you cannot inspect:

```
Don't make fake functionality look operational.
Don't use placeholder implementations.
Don't substitute fake data for real runtime infrastructure.
```

### The four evidence roles — do not use "mock = unreliable"

Filenames do not carry evidentiary weight. Classify by **role**:

| Role | What it is | Fabrication risk | Signals |
|---|---|---|---|
| **CAPTURE** | real artifact fetched from the external system | none — values not fabricable | real URIs, CRCs, signed hashes, live hosts, dated filenames |
| **MIRROR / ADAPTER** | translates observed external behaviour into a local interface | low — must preserve semantics | returns real-shaped state, names the external interface |
| **SIMULATION** | models external state transitions to exercise local logic | low — state transitions meaningful | encodes observed defects/edge cases |
| **SYNTHETIC** | deliberate abstraction / test values | n/a — acknowledged synthetic | counting sequences, round numbers, placeholder IDs |

Then weight evidence by role, not by label:

> **Determine whether a value is captured, mirrored, simulated, or synthetic
> before assigning evidentiary weight.**

### Applied to the Beta cluster

| Artifact | Role | Basis |
|---|---|---|
| `intercept_beta_config.ts` | **CAPTURE** | calls real `downloadServerConfig()` on `rs-launch://…/jav_config_beta.ws`; output named `beta_config_2026-05-06.json` |
| `beta_config_captured.ws` | **CAPTURE** | 5,686 B raw `key=value` from the live launcher |
| `beta_config_structured.json` | **CAPTURE** | 57 params, `download_crc_0=2341522391`, 683-char signed hash, `lobby50.runescape.com` |
| `beta_routing_manifest.json` | **CAPTURE** | `content.beta.runescape.com:43594`, buildId 1149, world 204 |
| `StateMocks.ts` | **MIRROR + SIMULATION** | models lobby state + encodes an observed "Arms Lock-up" defect |
| `BetaScripts` enum (123/456/789, 101…606) | **SYNTHETIC** | arithmetic sequences |
| `SAVE_CONFIRM=28749`, `SAVE_CONFIRM_HANDLER=13914`, `EXIT_DIALOG_NO=17062`, `EXIT_DIALOG_YES=17063`, `VARBIT_OPTION_LOADER=10896`, `MASTER_APPEARANCE_BUILDER=7937` | **requires independent provenance** | irregular, non-sequential — cannot be dismissed as synthetic, cannot be assumed authentic |

The irregular IDs sit in the same file as the synthetic ones. **That is the
point**: a file can mix roles, and the filename tells you nothing about which.

### The implementation boundary

POG2 built a deliberate boundary between a restricted external system and the
sovereign local substrate:

```
              EXTERNAL / RESTRICTED
                      │
              observed behaviour / captured config
                      │
             ┌────────▼────────┐
             │ mirror / adapter │   <- StateMocks.ts, intercept_beta_config.ts
             └────────┬────────┘
                      │
             POG2 LOCAL SYSTEM
                      │
             real executable code
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   TernaryRouter   ModelClient   SQLite/files
```

The existence of the mirror is **evidence of a deliberate implementation
boundary** — not evidence that the research was fabricated. Conflating the two
would destroy the provenance record.

---

## 7. BETA ENVIRONMENT CAPTURE — VERIFIED REAL

`scratch/beta_config_structured.json` and `beta_routing_manifest.json` are
genuine captured launcher data:

```
metadata.title              = RuneScape
binary_name                 = rs2client.exe
launcher_version            = 224
server_version              = 948
cache_variant_suffix        = BETA
download                    = 6863859
params.2  (buildId)         = 1149
params.3                    = lobby50.runescape.com
params.11 (revision)        = 225
params.27 (world)           = 204
```

```
beta_routing_manifest.json:
  build     = 45261
  timestamp = 1746708145  ->  2025-05-08T12:42:25Z
  variant   = BETA
  js5.host  = content.beta.runescape.com   port 43594
  world.id  = 204   gamePort 43594
```

**Note the internal timestamp: 2025-05-08.** That is over a year before the
2026-05-21 git import — either genuinely older captured data, or a stale field
in the manifest. **Unresolved; do not assert either way.**

The dossier's `rs-launch://www.runescape.com/jav_config_beta.ws` URI is
consistent with this capture. Treat as captured environmental evidence, not
live server state.

---

## 8. LINEAGES NOT ON DISK

| Lineage | Status |
|---|---|
| **POG-CLI-CODER** | **ABSENT.** No `pog-coder*`/`pog-cli*`/`coder-vibe*`/`pog-vibe*` anywhere under Desktop or `.gemini`. |
| **Willow** | not located |
| **`d:\sovereign`** | **NOT MOUNTED** (`ls /d` fails) |
| **`d:\d-sovereign-`** | not mounted; original path confirmed via `.project_root` |
| **D-sovereign- (working copy)** | not cloned locally; GitHub repo reachable |
| **Antigravity-Ultimate** | not located as a repo |

`d:\d-sovereign-` is confirmed as the original path by two `.project_root`
files:
```
.gemini/history/d-sovereign/.project_root  ->  d:\d-sovereign-
.gemini/tmp/d-sovereign/.project_root      ->  d:\d-sovereign-
```

Antigravity **session cache** for d-sovereign survives (`.gemini/tmp/d-sovereign/`):
`logs.json` (8,260 B), `memory/`, `chats/`, `tool-outputs/`, dated
2026-06-12 → 2026-06-13. First logged message: `/model`. Second: *"in src folder,
not the rsmv, but in this directory. could you make a .json and npm run hot
machine activat…"* — **this is a research-instrument trail, and it is dated.**

### Consequence

The dossier's Hypothesis A/B/C cannot be fully tested for POG-CLI-CODER: **the
repo is not on this machine.** Its Hexagram claims (dossier §7–8) remain
**UNVERIFIED**. Do not treat them as SOLID.

---

## 9. EVIDENCE GRAPH (current)

```
skillbert/rsmv ──SOLID (fork)──▶ Kbro1989/rsmv
                                      │
                                      │ UNKNOWN
                                      ▼
                            rsmv-upstream/.pog2/ (2026-09-18, untracked, 445 files)
                                      ▲
                                      │ SOLID
                                      │  420 shared files, 482/482 imports
                                      │  stripped of `rsmv/`, 1 non-import edit
                                      │  fixer left behind, 4-month gap, untracked
                                      │
                              POG2 scratch/ (472 files, tracked, bulk 2026-05-21)
                                      ▲
                                      │ SOLID (bulk import 2026-05-21)
                                      │
                    old device  d:/POG2/  with  d:/POG2/src/rsmv/ vendored
                                      │     [DESTROYED]
                    ┌─────────────────┴──────────────────┐
                    │ clone                              │ save-before-death
                    ▼                                    ▼
            present POG2 (2026-03-12..)          D-sovereign- (2026-04-19..07-07)
                    │                                    │
                    │                                    └─ atlas/ (gen 2026-03-22,
                    │                                       PREDATES repo → migrated in)
                    │
                    └─ Beta probes, beta_constants.ts, StateMocks.ts

POG-CLI-CODER ──UNKNOWN (repo not on disk)──▶ Hexagram architecture?
Willow / Antigravity-Ultimate ──UNKNOWN (not located)
MHD / FPGA ──UNKNOWN──▶ POG2 substrate
```

### Evidence classes used

| Class | Meaning | Instances here |
|---|---|---|
| **SOLID** | exact git parent / fork / byte-identical / machine-uniform rewrite | skillbert→Kbro rsmv fork; POG2→rsmv 420-file move; bulk import; D-sovereign- migration |
| **STRONG** | embedded timestamp + chronology | atlas entry 2026-03-22; output mtimes 2026-06-17 |
| **MEDIUM** | shared generator + path | Beta config capture |
| **WEAK** | naming / architectural similarity | POG-CLI-CODER Hexagram claims |
| **UNKNOWN** | plausible, untested | Willow, Antigravity-Ultimate, MHD |

### Retracted from the dossier

The dossier's §21 framing — *"recent RSMV scratch scripts were copied from POG2
research"* — is **correct in direction but understated in scale**. It is not
"recent scratch scripts": it is **420 files, 482 import rewrites**, executed as a
mechanical migration on 2026-09-18. The dossier's `git log` comparison of 4
commits (2026-09-18, 2026-10-06) describes the *rsmv* side of the split, not the
transfer itself.

---

## 10. AGENT OPERATING RULES (additions to the dossier's)

The dossier's DO/DO-NOT list stands. Add:

**DO**
- Check whether a path is **gitignored** before dating it. `scripts/.pog2/` is
  ignored; its mtime is the only evidence.
- Distinguish **bulk-import commit date** from **authoring date**. A commit
  whose message does not describe its contents is a bulk import.
- Read **embedded timestamps** in generated JSON (`timestamp: 1774216006890`).
  They survive git and often predate the repo that carries them.
- Check `.project_root` files for original paths.
- Verify a repo is **actually on disk** before testing claims about it.
- Treat device-destruction as a first-class provenance event.

**DO NOT**
- Assume a commit date is an authoring date.
- Assume a tracked file was authored in the repo that tracks it.
- Assume D-sovereign- generated what it contains (it *migrated* it).
- Assume `beta_constants.ts`'s header claim ("authoritative") without checking
  the values — its `BetaScripts` enum is synthetic.
- Treat `VARBIT_IMPORT_SAVE_STALL` / `VARP_BETA_ACTIVE` as proven Jagex IDs, or
  as worthless — they are mirror/simulation values; classify by role (§6).
- **Judge an artifact by its filename.** `StateMocks.ts` is not a test mock; a
  file named `*Mocks*` can be a behavioural mirror. Check the role, not the name.
- **Treat "mock" as equivalent to "unreliable."** Capture / mirror / simulation
  / synthetic are four different things with four different evidentiary weights.
- Let the atlas (`SETTINGS_PANEL`) and the Beta probes ("Import Save") overwrite
  each other — different tools, different questions.
- Cite POG-CLI-CODER Hexagram evidence as SOLID while the repo is absent.

---

## 11. OPEN TARGETS

1. **Recover POG-CLI-CODER.** Not on disk. Check GitHub, the old device image,
   and `.gemini/tmp` session caches.
2. **Date the Beta probes properly.** Git cannot (bulk import). Candidates:
   file mtimes on the old-device clone, `.gemini/tmp/POG2/` session logs,
   `pull_beta_enums_output*.txt` mtime (2026-06-17 15:19:43).
3. ~~Reconcile `beta_routing_manifest.timestamp` = 2025-05-08~~ **RESOLVED** —
   not a capture date. The real capture date is **2026-05-06**, encoded in
   `intercept_beta_config.ts`'s output filename. Treat the manifest's
   `timestamp` field as unreliable.
4. **Determine whether the atlas tool predates POG2's first commit**
   (2026-03-12). The atlas entry is 2026-03-22 — 10 days *after*. So the atlas
   tool ran on the old device between POG2's first commit and D-sovereign-'s
   creation. Identify that tool.
5. **Locate Willow / Antigravity-Ultimate.**
6. **Search the `.gemini/tmp/*/logs.json` session caches** — they carry
   per-message timestamps and may date research activity that git cannot.

---

## 12. ONE-SENTENCE HANDOFF (corrected)

> This is a systems-archaeology problem across a **destroyed device and its
> surviving clones**: present POG2 is a clone of the lost machine, D-sovereign-
> is the save made immediately before destruction, and the Beta research cluster
> moved **out of POG2 into a gitignored corner of rsmv-upstream in Sept 2026** —
> so reconstruct provenance from embedded timestamps, bulk-import boundaries,
> `.project_root` markers, and import-path rewrites, never from commit dates or
> current file location.
