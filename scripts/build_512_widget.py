
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_PATH = BASE / 'collapse_full_128_output.json'
OUT_PATH = BASE / 'DATASETS' / 'kingwen_512_oracle_widget.html'

d = json.loads(DATA_PATH.read_text(encoding='utf-8'))
expanded = d['expanded']
resolved = d['resolved']

hex_lookup = {h['hexagram_id']: h for h in expanded}

cat_colors = {
    'Sovereign': '#FFD700',
    'Transformer': '#4ECDC4',
    'Dissipator': '#FF6B6B',
    'Boundary': '#95E1D3',
}
action_symbols = {
    'ASSERT': '▲',
    'YIELD': '▼',
    'ADAPT': '◆',
    'WAIT': '○',
}
phase_colors = {
    'past': '#4ECDC4',
    'present': '#FFD700',
    'future': '#FF6B6B',
    'transition': '#9370DB',
    'resolution': '#FF8C00',
    'dissolution': '#708090',
    'crystallization': '#00CED1',
    'void': '#2F4F4F',
}
phase_names = [
    'past','present','future','transition','resolution','dissolution','crystallization','void'
]

hex_grid_rows = []
for hid in range(1, 65):
    h = hex_lookup.get(hid)
    if not h:
        continue
    sym = h['hexagram_symbols']
    inj = h['inject_site']
    hex_grid_rows.append({
        'id': hid,
        'name': sym.get('name', ''),
        'unicode': sym.get('unicode', ''),
        'category': sym.get('category', ''),
        'action': sym.get('action', ''),
        'upper_trigram': sym.get('upper_trigram', ''),
        'lower_trigram': sym.get('lower_trigram', ''),
        'binary': sym.get('binary', ''),
        'primary_pool': inj.get('primary_pool', ''),
        'secondary_pool': inj.get('secondary_pool', ''),
        'porosity': inj.get('porosity', 0),
        'porosity_label': inj.get('porosity_label', ''),
        'expanded_vector': h.get('expanded_vector', {}),
    })

resolved_rows = []
for r in resolved:
    sym = r.get('hexagram_symbols', {})
    inj = r.get('inject_site', {})
    resolved_rows.append({
        'hexagram_id': r.get('hexagram_id'),
        'phase_bits': r.get('phase_bits'),
        'phase_temporal': r.get('phase_temporal', ''),
        'phase_polarity': r.get('phase_polarity', ''),
        'phase_description': r.get('phase_description', ''),
        'name': sym.get('name', ''),
        'unicode': sym.get('unicode', ''),
        'category': sym.get('category', ''),
        'action': sym.get('action', ''),
        'binary': sym.get('binary', ''),
        'primary_pool': inj.get('primary_pool', ''),
        'secondary_pool': inj.get('secondary_pool', ''),
        'porosity': inj.get('porosity', 0),
        'porosity_label': inj.get('porosity_label', ''),
        'expanded_vector': r.get('expanded_vector', {}),
        'resolved_vector': r.get('resolved_vector', {}),
        'line_states': r.get('line_states', []),
        'yao_vocabulary': r.get('yao_vocabulary', {}),
        'sample_paths': r.get('sample_paths', []),
        'checklist': r.get('checklist', []),
    })

# Raw expanded for export, preserving full source-truth containers
raw_expanded_rows = []
for h in expanded:
    raw_expanded_rows.append({
        'hexagram_id': h.get('hexagram_id'),
        'request_text': h.get('request_text', ''),
        'phase_bits': h.get('phase_bits'),
        'hexagram_symbols': h.get('hexagram_symbols', {}),
        'inject_site': h.get('inject_site', {}),
        'yao_vocabulary': h.get('yao_vocabulary', {}),
        'line_states': h.get('line_states', []),
        'sample_paths': h.get('sample_paths', []),
        'expanded_vector': h.get('expanded_vector', {}),
    })

hex_json = json.dumps(hex_grid_rows, ensure_ascii=False, separators=(',', ':'))
resolved_json = json.dumps(resolved_rows, ensure_ascii=False, separators=(',', ':'))
raw_expanded_json = json.dumps(raw_expanded_rows, ensure_ascii=False, separators=(',', ':'))
cat_json = json.dumps(cat_colors, ensure_ascii=False)
act_json = json.dumps(action_symbols, ensure_ascii=False)
phase_json = json.dumps(phase_colors, ensure_ascii=False)
phase_names_json = json.dumps(phase_names, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>King Wen 512-State Oracle</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }}
#kingwen-container {{ padding: 20px; max-width: 1400px; margin: 0 auto; }}
.kw-header {{ text-align: center; margin-bottom: 24px; }}
.kw-title {{ font-size: 28px; font-weight: 700; color: #FFD700; margin: 0; letter-spacing: 2px; }}
.kw-subtitle {{ font-size: 14px; color: #888; margin-top: 8px; }}
.kw-stats {{ display: flex; justify-content: center; gap: 32px; margin: 16px 0; font-size: 13px; flex-wrap: wrap; align-items: center; }}
.kw-stat {{ text-align: center; }}
.kw-stat-value {{ font-size: 20px; font-weight: 700; color: #4ECDC4; }}
.kw-stat-label {{ color: #666; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}

.kw-tabs {{ display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }}
.kw-tab {{ padding: 8px 20px; border-radius: 20px; border: 1px solid #333; background: #1a1a2e; color: #888; cursor: pointer; font-size: 13px; transition: all 0.3s; }}
.kw-tab.active {{ background: #4ECDC4; color: #0a0a0f; border-color: #4ECDC4; font-weight: 600; }}
.kw-tab:hover {{ border-color: #4ECDC4; color: #4ECDC4; }}

.kw-panel {{ display: none; }}
.kw-panel.active {{ display: block; }}

.kw-grid {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 6px; max-width: 1000px; margin: 0 auto; }}
.kw-cell {{ aspect-ratio: 1; border-radius: 8px; border: 1px solid #2a2a3e; background: #1a1a2e; cursor: pointer; position: relative; overflow: hidden; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4px; }}
.kw-cell:hover {{ transform: scale(1.08); border-color: #FFD700; z-index: 10; box-shadow: 0 0 20px rgba(255,215,0,0.2); }}
.kw-cell-id {{ font-size: 10px; color: #666; position: absolute; top: 3px; left: 5px; }}
.kw-cell-unicode {{ font-size: 24px; line-height: 1; }}
.kw-cell-name {{ font-size: 8px; text-align: center; color: #aaa; line-height: 1.2; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; max-width: 100%; white-space: nowrap; }}
.kw-cell-action {{ font-size: 10px; position: absolute; bottom: 3px; right: 5px; }}
.kw-cell-cat {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; }}

.kw-detail {{ background: #1a1a2e; border-radius: 12px; padding: 24px; margin-top: 20px; border: 1px solid #2a2a3e; display: none; position: relative; }}
.kw-detail.active {{ display: block; }}
.kw-detail-header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
.kw-detail-unicode {{ font-size: 48px; }}
.kw-detail-title {{ font-size: 22px; font-weight: 700; color: #FFD700; }}
.kw-detail-meta {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }}
.kw-detail-tag {{ padding: 4px 12px; border-radius: 12px; font-size: 12px; background: #2a2a3e; }}
.kw-detail-tag.cat-sovereign {{ background: rgba(255,215,0,0.2); color: #FFD700; }}
.kw-detail-tag.cat-transformer {{ background: rgba(78,205,196,0.2); color: #4ECDC4; }}
.kw-detail-tag.cat-dissipator {{ background: rgba(255,107,107,0.2); color: #FF6B6B; }}
.kw-detail-tag.cat-boundary {{ background: rgba(149,225,211,0.2); color: #95E1D3; }}

.kw-vectors {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 20px 0; }}
.kw-vector {{ background: #0a0a0f; border-radius: 8px; padding: 12px; text-align: center; }}
.kw-vector-name {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
.kw-vector-bar {{ height: 6px; border-radius: 3px; background: #2a2a3e; overflow: hidden; }}
.kw-vector-fill {{ height: 100%; border-radius: 3px; transition: width 0.5s ease; }}
.kw-vector-value {{ font-size: 16px; font-weight: 700; margin-top: 6px; }}

.kw-phases {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 16px; }}
.kw-phase {{ background: #0a0a0f; border-radius: 8px; padding: 12px; border: 1px solid #2a2a3e; cursor: pointer; transition: all 0.2s; }}
.kw-phase:hover {{ border-color: #4ECDC4; }}
.kw-phase.active {{ border-color: #FFD700; background: rgba(255,215,0,0.05); }}
.kw-phase-name {{ font-size: 12px; font-weight: 600; margin-bottom: 4px; }}
.kw-phase-polarity {{ font-size: 10px; color: #888; }}

.kw-phase-grid {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 4px; max-width: 1000px; margin: 0 auto; }}
.kw-phase-cell {{ aspect-ratio: 1; border-radius: 6px; border: 1px solid #2a2a3e; background: #1a1a2e; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2px; font-size: 10px; transition: all 0.2s; }}
.kw-phase-cell:hover {{ transform: scale(1.1); z-index: 10; }}

.kw-vspace {{ position: relative; height: 520px; background: #0a0a0f; border-radius: 12px; border: 1px solid #2a2a3e; overflow: hidden; }}
.kw-vspace-plot {{ position: relative; width: 100%; height: 100%; }}
.kw-vpoint {{ position: absolute; width: 7px; height: 7px; border-radius: 50%; cursor: pointer; transition: all 0.2s; border: 1px solid rgba(255,255,255,0.2); }}
.kw-vpoint:hover {{ transform: scale(2.5); z-index: 100; border-width: 2px; }}
.kw-vaxis {{ position: absolute; font-size: 11px; color: #666; font-weight: 600; }}

.kw-legend {{ display: flex; justify-content: center; gap: 20px; margin: 16px 0; flex-wrap: wrap; }}
.kw-legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: #888; }}
.kw-legend-dot {{ width: 12px; height: 12px; border-radius: 3px; }}

.kw-close-btn {{ position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border-radius: 50%; border: 1px solid #444; background: #1a1a2e; color: #888; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px; line-height: 1; }}
.kw-close-btn:hover {{ background: #FF6B6B; color: white; border-color: #FF6B6B; }}

.kw-export-btn {{ padding: 6px 14px; border-radius: 16px; border: 1px solid #4ECDC4; background: rgba(78,205,196,0.1); color: #4ECDC4; cursor: pointer; font-size: 12px; }}
.kw-export-btn:hover {{ background: #4ECDC4; color: #0a0a0f; }}

.matrix-wrapper {{ overflow-x: auto; max-width: 100%; }}
#stateMatrix {{ border-collapse: collapse; margin: 0 auto; font-size: 10px; }}
#stateMatrix th, #stateMatrix td {{ padding: 3px 4px; border: 1px solid #2a2a3e; text-align: center; }}
#stateMatrix th {{ background: #1a1a2e; font-size: 10px; }}
#stateMatrix td {{ cursor: pointer; transition: all 0.1s; }}
#stateMatrix td:hover {{ filter: brightness(1.3); }}

select {{ padding: 8px 16px; border-radius: 8px; background: #1a1a2e; color: #e0e0e0; border: 1px solid #2a2a3e; font-size: 14px; cursor: pointer; }}
select:focus {{ outline: none; border-color: #4ECDC4; }}

@media (max-width: 768px) {{
  .kw-grid {{ grid-template-columns: repeat(4, 1fr); }}
  .kw-phase-grid {{ grid-template-columns: repeat(4, 1fr); }}
  .kw-vectors {{ grid-template-columns: repeat(3, 1fr); }}
  .kw-phases {{ grid-template-columns: repeat(2, 1fr); }}
  .kw-title {{ font-size: 20px; }}
}}
</style>
</head>
<body>
<div id="kingwen-container">
  <div class="kw-header">
    <h1 class="kw-title">KING WEN 512-STATE ORACLE</h1>
    <div class="kw-subtitle">64 Hexagrams x 8 Temporal Phases = 512 Resolved States</div>
    <div class="kw-stats">
      <div class="kw-stat"><div class="kw-stat-value">64</div><div class="kw-stat-label">Hexagrams</div></div>
      <div class="kw-stat"><div class="kw-stat-value">512</div><div class="kw-stat-label">States</div></div>
      <div class="kw-stat"><div class="kw-stat-value">8</div><div class="kw-stat-label">Phases</div></div>
      <div class="kw-stat"><div class="kw-stat-value">5</div><div class="kw-stat-label">Vectors</div></div>
      <div class="kw-stat"><button class="kw-export-btn" onclick="exportAll()">Export all 512</button></div>
    </div>
  </div>

  <div class="kw-tabs">
    <div class="kw-tab active" onclick="showTab('grid', this)">Hexagram Grid</div>
    <div class="kw-tab" onclick="showTab('phases', this)">Phase Explorer</div>
    <div class="kw-tab" onclick="showTab('vectors', this)">Vector Space</div>
    <div class="kw-tab" onclick="showTab('matrix', this)">State Matrix</div>
    <div class="kw-tab" onclick="showTab('shotgun', this)">Shotgun Blast</div>
  </div>

  <div id="tab-grid" class="kw-panel active">
    <div class="kw-legend">
      <div class="kw-legend-item"><div class="kw-legend-dot" style="background:#FFD700"></div>Sovereign</div>
      <div class="kw-legend-item"><div class="kw-legend-dot" style="background:#4ECDC4"></div>Transformer</div>
      <div class="kw-legend-item"><div class="kw-legend-dot" style="background:#FF6B6B"></div>Dissipator</div>
      <div class="kw-legend-item"><div class="kw-legend-dot" style="background:#95E1D3"></div>Boundary</div>
      <div class="kw-legend-item">&#9650; Assert</div>
      <div class="kw-legend-item">&#9660; Yield</div>
      <div class="kw-legend-item">&#9670; Adapt</div>
      <div class="kw-legend-item">&#9675; Wait</div>
    </div>
    <div class="kw-grid" id="hexGrid"></div>
    <div class="kw-detail" id="hexDetail">
      <button class="kw-close-btn" onclick="closeDetail()">&times;</button>
      <button class="kw-export-btn" style="position:absolute;top:12px;right:52px;" onclick="exportCurrentState()">Export raw</button>
      <div id="detailContent"></div>
    </div>
  </div>

  <div id="tab-phases" class="kw-panel">
    <div style="text-align:center; margin-bottom:16px;">
      <select id="phaseSelect" onchange="renderPhaseView()">
        <option value="all">All Phases</option>
        <option value="0">Past (Yin)</option>
        <option value="1">Present (Yang)</option>
        <option value="2">Future (Yao)</option>
        <option value="3">Transition (Yin-Yang)</option>
        <option value="4">Resolution (Yang-Yin)</option>
        <option value="5">Dissolution (Yin-Yao)</option>
        <option value="6">Crystallization (Yang-Yao)</option>
        <option value="7">Void (Yao-Yao)</option>
      </select>
    </div>
    <div class="kw-phase-grid" id="phaseGrid"></div>
  </div>

  <div id="tab-vectors" class="kw-panel">
    <div style="text-align:center; margin-bottom:12px;">
      <select id="xAxis" onchange="renderVectorSpace()">
        <option value="chaos">Chaos</option>
        <option value="whimsy">Whimsy</option>
        <option value="darkTone">Dark Tone</option>
        <option value="coherence" selected>Coherence</option>
        <option value="voiceWeight">Voice Weight</option>
      </select>
      <span style="color:#666; margin:0 8px;">vs</span>
      <select id="yAxis" onchange="renderVectorSpace()">
        <option value="chaos" selected>Chaos</option>
        <option value="whimsy">Whimsy</option>
        <option value="darkTone">Dark Tone</option>
        <option value="coherence">Coherence</option>
        <option value="voiceWeight">Voice Weight</option>
      </select>
      <select id="colorBy" onchange="renderVectorSpace()" style="margin-left:16px;">
        <option value="category">Color: Category</option>
        <option value="phase">Color: Phase</option>
        <option value="action">Color: Action</option>
      </select>
    </div>
    <div class="kw-vspace">
      <div class="kw-vspace-plot" id="vectorPlot"></div>
    </div>
  </div>

  <div id="tab-matrix" class="kw-panel">
    <div style="text-align:center; margin-bottom:16px; color:#888; font-size:13px;">
      64 Hexagrams (rows) x 8 Phases (columns) &mdash; Click any cell to inspect state
    </div>
    <div class="matrix-wrapper">
      <table id="stateMatrix"></table>
    </div>
  </div>

  <div id="tab-shotgun" class="kw-panel">
    <div style="text-align:center; margin-bottom:12px; color:#888; font-size:13px;">Full 512-state shotgun blast — no collapse to dominant state</div>
    <div class="kw-phase-grid" id="shotgunGrid"></div>
  </div>
</div>

<script>
const hexagrams = {hex_json};
const resolved = {resolved_json};
const rawExpanded = {raw_expanded_json};
const catColors = {cat_json};
const actionSymbols = {act_json};
const phaseColors = {phase_json};
const phases = {phase_names_json};

const vectorKeys = ['chaos','whimsy','darkTone','coherence','voiceWeight'];
const vectorLabels = {{chaos:'Chaos',whimsy:'Whimsy',darkTone:'Dark Tone',coherence:'Coherence',voiceWeight:'Voice Weight'}};
const vectorHex = {{chaos:'#FF6B6B',whimsy:'#4ECDC4',darkTone:'#8B4513',coherence:'#FFD700',voiceWeight:'#9370DB'}};

let selectedHexagram = null;
let selectedPhase = 0;

function showTab(tab, el) {{
  document.querySelectorAll('.kw-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.kw-panel').forEach(p => p.classList.remove('active'));
  if(el) el.classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  if(tab === 'phases') renderPhaseView();
  if(tab === 'vectors') renderVectorSpace();
  if(tab === 'matrix') renderMatrix();
  if(tab === 'shotgun') renderShotgun();
}}

function esc(s) {{
  if(s === null || s === undefined) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function renderGrid() {{
  const grid = document.getElementById('hexGrid');
  grid.innerHTML = '';
  hexagrams.forEach(h => {{
    const cell = document.createElement('div');
    cell.className = 'kw-cell';
    cell.style.borderColor = (catColors[h.category] || '#888') + '40';
    cell.innerHTML = '<div class=\"kw-cell-cat\" style=\"background:' + (catColors[h.category] || '#888') + '\"></div>' +
      '<div class=\"kw-cell-id\">' + h.id + '</div>' +
      '<div class=\"kw-cell-unicode\">' + esc(h.unicode) + '</div>' +
      '<div class=\"kw-cell-name\">' + esc(h.name) + '</div>' +
      '<div class=\"kw-cell-action\">' + (actionSymbols[h.action] || '') + '</div>';
    cell.onclick = () => showDetail(h.id);
    grid.appendChild(cell);
  }});
}}

function currentResolvedState() {{
  if(selectedHexagram === null) return null;
  return resolved.find(r => r.hexagram_id === selectedHexagram && r.phase_bits === selectedPhase) || null;
}}

function downloadJson(obj, filename) {{
  const blob = new Blob([JSON.stringify(obj, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'kingwen-state.json';
  a.click();
  URL.revokeObjectURL(url);
}}

function exportCurrentState() {{
  const state = currentResolvedState();
  if(!state) return;
  const raw = rawExpanded.find(x => x.hexagram_id === state.hexagram_id) || {{}};
  const payload = {{
    source: 'collapse_full_128_output',
    hexagram_id: state.hexagram_id,
    phase_bits: state.phase_bits,
    selected_state: state,
    raw_expanded: raw
  }};
  downloadJson(payload, 'kingwen-hex-' + state.hexagram_id + '-phase-' + state.phase_bits + '.json');
}}

function exportAll() {{
  const payload = {{
    source: 'collapse_full_128_output',
    total_expanded: rawExpanded.length,
    total_resolved: resolved.length,
    expanded: rawExpanded,
    resolved: resolved
  }};
  downloadJson(payload, 'kingwen-512-full.json');
}}

function showDetail(id) {{
  selectedHexagram = id;
  const h = hexagrams.find(x => x.id === id);
  const detail = document.getElementById('hexDetail');
  const content = document.getElementById('detailContent');

  const states = resolved.filter(r => r.hexagram_id === id);

  let phasesHtml = states.map((s, i) =>
    '<div class=\"kw-phase ' + (i === selectedPhase ? 'active' : '') + '\" onclick=\"selectPhase(' + i + ')\">' +
    '<div class=\"kw-phase-name\" style=\"color:' + (phaseColors[s.phase_temporal] || '#888') + '\">' + esc(s.phase_temporal) + '</div>' +
    '<div class=\"kw-phase-polarity\">' + esc(s.phase_polarity) + '</div>' +
    '<div style=\"font-size:10px; color:#666; margin-top:4px;\">' + esc(s.phase_description) + '</div></div>'
  ).join('');

  const currentState = states[selectedPhase];
  const vecKeys = [['chaos','Chaos'],['whimsy','Whimsy'],['darkTone','Dark'],['coherence','Coherence'],['voiceWeight','Voice']];

  function vecHtml(source, data) {{
    return vecKeys.map(([k,label]) =>
      '<div class=\"kw-vector\"><div class=\"kw-vector-name\">' + label + '</div>' +
      '<div class=\"kw-vector-bar\"><div class=\"kw-vector-fill\" style=\"width:' + ((data[k] || 0) * 100) + '%; background:' + vectorHex[k] + '\"></div></div>' +
      '<div class=\"kw-vector-value\" style=\"color:' + vectorHex[k] + '\">' + (data[k] || 0).toFixed(3) + '</div></div>'
    ).join('');
  }}

  let linesHtml = '';
  if(currentState && currentState.line_states && currentState.line_states.length) {{
    linesHtml = '<div style=\"margin-top:16px;\"><div style=\"font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;\">Line States</div><div style=\"display:flex; gap:8px; flex-wrap:wrap;\">' +
      currentState.line_states.map(ls => '<span style=\"padding:4px 10px; border-radius:10px; background:#2a2a3e; font-size:12px;\">' + ls.position + ': ' + esc(ls.yao_label) + '</span>').join('') +
      '</div></div>';
  }}

  let checklistHtml = '';
  if(currentState && currentState.checklist && currentState.checklist.length) {{
    checklistHtml = '<div style=\"margin-top:16px;\"><div style=\"font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;\">Checklist</div><div style=\"display:flex; gap:8px; flex-wrap:wrap;\">' +
      currentState.checklist.map(cl => '<span style=\"padding:4px 10px; border-radius:10px; background:' + (cl.status==='in_window'?'rgba(78,205,196,0.2)':'rgba(255,107,107,0.2)') + '; font-size:11px;\">' + esc(cl.axis) + ': ' + esc(cl.status) + '</span>').join('') +
      '</div></div>';
  }}

  content.innerHTML =
    '<div class=\"kw-detail-header\">' +
    '<div class=\"kw-detail-unicode\">' + esc(h.unicode) + '</div>' +
    '<div><div class=\"kw-detail-title\">' + h.id + '. ' + esc(h.name) + '</div>' +
    '<div class=\"kw-detail-meta\">' +
    '<span class=\"kw-detail-tag cat-' + esc(h.category) + '\">' + esc(h.category) + '</span>' +
    '<span class=\"kw-detail-tag\">' + esc(h.action) + '</span>' +
    '<span class=\"kw-detail-tag\">' + esc(h.upper_trigram) + ' / ' + esc(h.lower_trigram) + '</span>' +
    '<span class=\"kw-detail-tag\">' + esc(h.binary) + '</span>' +
    '<span class=\"kw-detail-tag\">' + esc(h.porosity_label) + '</span></div></div></div>' +
    '<div style=\"display:grid; grid-template-columns: 1fr 1fr; gap: 16px;\">' +
    '<div><div style=\"font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;\">Expanded Vector</div>' +
    '<div class=\"kw-vectors\">' + vecHtml('expanded', h.expanded_vector) + '</div></div>' +
    '<div><div style=\"font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;\">Resolved: ' + esc(currentState ? currentState.phase_temporal : '') + '</div>' +
    '<div class=\"kw-vectors\">' + vecHtml('resolved', currentState ? currentState.resolved_vector : {{}}) + '</div></div></div>' +
    '<div style=\"margin-top:20px;\"><div style=\"font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px;\">Temporal Phases</div>' +
    '<div class=\"kw-phases\">' + phasesHtml + '</div></div>' +
    linesHtml + checklistHtml +
    '<div style=\"margin-top:16px; font-size:12px; color:#666;\">' +
    '<strong>Pools:</strong> ' + esc(h.primary_pool) + ' → ' + esc(h.secondary_pool) + ' | ' +
    '<strong>Porosity:</strong> ' + (h.porosity || 0).toFixed(3) + ' (' + esc(h.porosity_label) + ')</div>';

  detail.classList.add('active');
  detail.scrollIntoView({{behavior: 'smooth'}});
}}

function selectPhase(idx) {{
  selectedPhase = idx;
  if(selectedHexagram) showDetail(selectedHexagram);
}}

function closeDetail() {{
  document.getElementById('hexDetail').classList.remove('active');
  selectedHexagram = null;
}}

function renderPhaseView() {{
  const select = document.getElementById('phaseSelect');
  const phaseFilter = select.value;
  const grid = document.getElementById('phaseGrid');
  grid.innerHTML = '';

  let states = resolved;
  if(phaseFilter !== 'all') {{
    states = resolved.filter(r => r.phase_bits === parseInt(phaseFilter));
  }}

  states.forEach(s => {{
    const cell = document.createElement('div');
    cell.className = 'kw-phase-cell';
    cell.style.borderColor = (phaseColors[s.phase_temporal] || '#888') + '60';
    cell.style.color = phaseColors[s.phase_temporal] || '#888';
    cell.innerHTML = '<div style=\"font-size:8px; color:#666;\">' + s.hexagram_id + '</div>' +
      '<div style=\"font-size:11px; margin:2px 0; font-weight:600;\">' + esc(s.name ? s.name.substring(0,12) : '') + '</div>' +
      '<div style=\"font-size:9px; color:#888;\">' + esc(s.phase_polarity) + '</div>';
    cell.onclick = () => {{ selectedPhase = s.phase_bits; showTab('grid', document.querySelectorAll('.kw-tab')[0]); showDetail(s.hexagram_id); }};
    grid.appendChild(cell);
  }});
}}

function renderVectorSpace() {{
  const xKey = document.getElementById('xAxis').value;
  const yKey = document.getElementById('yAxis').value;
  const colorMode = document.getElementById('colorBy').value;
  const plot = document.getElementById('vectorPlot');
  plot.innerHTML = '';

  const axisLabel = document.createElement('div');
  axisLabel.className = 'kw-vaxis';
  axisLabel.style.cssText = 'left:50%; bottom:8px; transform:translateX(-50%);';
  axisLabel.textContent = xKey;
  plot.appendChild(axisLabel);

  const axisLabelY = document.createElement('div');
  axisLabelY.className = 'kw-vaxis';
  axisLabelY.style.cssText = 'left:8px; top:50%; transform:translateY(-50%) rotate(-90deg); transform-origin:left center;';
  axisLabelY.textContent = yKey;
  plot.appendChild(axisLabelY);

  for(let i=0; i<=10; i++) {{
    const line = document.createElement('div');
    line.style.cssText = 'position:absolute; left:' + (i*10) + '%; top:0; bottom:0; width:1px; background:#2a2a3e;';
    plot.appendChild(line);
    const lineH = document.createElement('div');
    lineH.style.cssText = 'position:absolute; top:' + (i*10) + '%; left:0; right:0; height:1px; background:#2a2a3e;';
    plot.appendChild(lineH);
  }}

  resolved.forEach((r) => {{
    const xv = r.expanded_vector && r.expanded_vector[xKey] != null ? r.expanded_vector[xKey] : 0;
    const yv = r.expanded_vector && r.expanded_vector[yKey] != null ? r.expanded_vector[yKey] : 0;
    const x = xv * 100;
    const y = (1 - yv) * 100;

    let color;
    if(colorMode === 'category') {{
      const h = hexagrams.find(h => h.id === r.hexagram_id);
      color = catColors[h && h.category] || '#888';
    }} else if(colorMode === 'phase') {{
      color = phaseColors[r.phase_temporal] || '#888';
    }} else {{
      const h = hexagrams.find(h => h.id === r.hexagram_id);
      color = '#888';
    }}

    const point = document.createElement('div');
    point.className = 'kw-vpoint';
    point.style.cssText = 'left:calc(' + x + '% - 3px); top:calc(' + y + '% - 3px); background:' + color + ';';
    point.title = r.name + ' [' + r.phase_temporal + '] C:' + (r.expanded_vector ? r.expanded_vector.coherence.toFixed(2) : '');
    point.onclick = () => {{ selectedPhase = r.phase_bits; showTab('grid', document.querySelectorAll('.kw-tab')[0]); showDetail(r.hexagram_id); }};
    plot.appendChild(point);
  }});
}}

function renderMatrix() {{
  const table = document.getElementById('stateMatrix');
  let html = '<tr><th style=\"padding:4px; border:1px solid #2a2a3e; background:#1a1a2e;\">#</th>';
  phases.forEach((p, i) => {{
    html += '<th style=\"padding:4px; border:1px solid #2a2a3e; background:#1a1a2e; color:' + phaseColors[p] + '; font-size:10px;\">' + p.substring(0,4) + '<br><span style=\"color:#666\">' + i + '</span></th>';
  }});
  html += '</tr>';

  for(let hid=1; hid<=64; hid++) {{
    const h = hexagrams.find(x => x.id === hid);
    html += '<tr><td style=\"padding:3px; border:1px solid #2a2a3e; background:#1a1a2e; font-size:10px; color:' + (catColors[h && h.category] || '#888') + '; font-weight:600;\">' + hid + '</td>';
    for(let pb=0; pb<8; pb++) {{
      const state = resolved.find(r => r.hexagram_id === hid && r.phase_bits === pb);
      const c = state && state.expanded_vector && state.expanded_vector.coherence != null ? state.expanded_vector.coherence : 0;
      const n = Math.floor(c * 200);
      const r2 = Math.floor(n*0.2);
      const g2 = Math.floor(n*0.7);
      const b2 = Math.floor(n*0.5);
      html += '<td style=\"padding:3px; border:1px solid #2a2a3e; background:rgb(' + r2 + ',' + g2 + ',' + b2 + '); cursor:pointer; font-size:9px; text-align:center; color:' + (c > 0.5 ? '#ccc' : '#666') + ';\" onclick=\"selectedPhase=' + pb + ';showTab(\\'grid\\', document.querySelectorAll(\\'.kw-tab\\')[0]);showDetail(' + hid + ');\" title=\"' + (state ? state.phase_temporal : '') + ': C=' + c.toFixed(2) + '\">' + (state ? c.toFixed(1).substring(1) : '') + '</td>';
    }}
    html += '</tr>';
  }}

  table.innerHTML = html;
}}

function renderShotgun() {{
  const grid = document.getElementById('shotgunGrid');
  grid.innerHTML = '';
  resolved.forEach((r, idx) => {{
    const cell = document.createElement('div');
    cell.className = 'kw-phase-cell';
    const c = r.expanded_vector && r.expanded_vector.coherence != null ? r.expanded_vector.coherence : 0;
    const x = Math.floor(c * 200);
    cell.style.borderColor = (phaseColors[r.phase_temporal] || '#888') + '70';
    cell.style.background = 'rgba(' + Math.floor(x*0.2) + ',' + Math.floor(x*0.7) + ',' + Math.floor(x*0.5) + ',0.25)';
    cell.innerHTML = '<div style=\"font-size:8px; color:#666;\">' + r.hexagram_id + '</div>' +
      '<div style=\"font-size:14px; margin:2px 0; font-weight:700;\">' + esc(r.unicode) + '</div>' +
      '<div style=\"font-size:9px; color:#aaa;\">' + esc(r.phase_temporal) + '</div>' +
      '<div style=\"font-size:9px; color:#888;\">C ' + c.toFixed(2) + '</div>';
    cell.onclick = () => {{ selectedPhase = r.phase_bits; showTab('grid', document.querySelectorAll('.kw-tab')[0]); showDetail(r.hexagram_id); }};
    grid.appendChild(cell);
  }});
}}

renderGrid();
</script>
</body>
</html>'''

OUT_PATH.write_text(html, encoding='utf-8')
print('wrote', OUT_PATH)
print('bytes', OUT_PATH.stat().st_size)
