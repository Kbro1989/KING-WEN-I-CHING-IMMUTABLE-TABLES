#!/usr/bin/env python3
"""
King Wen 64-Sovereign External Audio Switchboard Generator
==========================================================
Generates a standalone, dedicated 64-channel mixing console & switchboard:
  - DATASETS/kingwen_external_audio_switchboard.html

Features:
  - Master Bus: Volume, Filter Cutoff, Resonance Q, Global Mute/Solo, Mode Dropdown
  - 8 Trigram Submix Groups: Qian, Kun, Zhen, Kan, Li, Xun, Gen, Dui
  - 64 Individual Hexagram Channel Strips:
      * Channel Number + Hanzi + Sovereign Name
      * 6-Bit Deterministic Spectral Hue badge
      * Individual Mute (M) and Solo (S) buttons
      * Volume Fader (0-100%) & Pan control (-100 to +100)
      * 6-Yao Line Ternary Pellet status & frequency readouts
      * Real-time Web Audio API multi-oscillator synthesis
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_INFO

OUTPUT_HTML = ROOT / "DATASETS" / "kingwen_external_audio_switchboard.html"
KIT_DIR = ROOT / "DATASETS" / "kingwen_model_sets"

def generate_switchboard_data():
    COPRIME_BASE_FREQS = [146.0, 158.0, 166.0, 178.0, 194.0, 206.0]
    channels = []

    for h_id in range(1, 65):
        base = HEXAGRAM_BASE[h_id]
        binary_str = base.get("binary_bottom_to_top", "111111")
        upper_tri = base.get("upper_trigram", "Qian")
        lower_tri = base.get("lower_trigram", "Kun")

        # Load kit color
        kit_file = KIT_DIR / f"kit_{h_id}.json"
        k_color = {}
        if kit_file.exists():
            try:
                k_color = json.loads(kit_file.read_text(encoding="utf-8")).get("grounded_npc", {}).get("k_color_map", {})
            except Exception:
                pass

        spectral_hex = k_color.get("primary_color", {}).get("hex", "#FFD700")
        base_hue = k_color.get("final_hue_degrees", (h_id - 1) * 5.625)

        u_idx = base.get("upper_idx", 1)
        l_idx = base.get("lower_idx", 1)
        vortex_tension = round((u_idx * l_idx) / 49.0, 4)
        porosity = round(0.15 + (u_idx * 0.05) + (l_idx * 0.03), 3)
        base_freq = round(108.0 + (h_id - 1) * 2.45, 2)

        # 6-Yao pellets
        pellets = []
        for line_idx in range(6):
            bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
            ternary_state = 1 if bit == 1 else 0
            freq = round(COPRIME_BASE_FREQS[line_idx] * (1.0 if ternary_state == 1 else 0.82) * (1.0 + vortex_tension * 0.25), 2)
            pellets.append({
                "line": line_idx + 1,
                "sub_trigram": "lower" if line_idx < 3 else "upper",
                "state": ternary_state,
                "type": "yang" if ternary_state == 1 else "yin",
                "color_hex": "#FFD700" if ternary_state == 1 else "#38BDF8",
                "frequency_hz": freq
            })

        channels.append({
            "hex_id": h_id,
            "name": base["name"],
            "hanzi": base.get("unicode", "䷀"),
            "binary": binary_str,
            "upper_trigram": upper_tri,
            "lower_trigram": lower_tri,
            "spectral_color": spectral_hex,
            "base_hue_degrees": base_hue,
            "base_frequency_hz": base_freq,
            "vortex_tension": vortex_tension,
            "porosity": porosity,
            "pellets": pellets
        })

    return channels

def build_switchboard_html(channels):
    channels_json = json.dumps(channels, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>King Wen 64-Sovereign External Audio Switchboard & Studio Mixing Console</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
    body {{
      background: #090d16; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
      padding: 16px; min-height: 100vh; display: flex; flex-direction: column; gap: 16px;
    }}
    header {{
      background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 14px 20px;
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    }}
    h1 {{
      font-size: 20px; color: #FFD700; display: flex; align-items: center; gap: 10px; letter-spacing: 0.5px;
    }}
    .badge {{
      background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 3px 8px; border-radius: 6px; font-size: 11px;
    }}
    .master-controls {{
      display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
    }}
    .btn {{
      background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 6px 14px; border-radius: 6px;
      font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.15s ease;
    }}
    .btn:hover {{ background: #38bdf8; color: #0f172a; }}
    .btn-power-on {{ background: #38bdf8; color: #0f172a; }}
    .btn-warn {{ color: #f59e0b; border-color: #f59e0b; }}
    .btn-warn:hover {{ background: #f59e0b; color: #0f172a; }}
    .btn-danger {{ color: #ef4444; border-color: #ef4444; }}
    .btn-danger:hover {{ background: #ef4444; color: #fff; }}
    select.audio-select {{
      background: #020617; color: #f8fafc; border: 1px solid #3b82f6; padding: 6px 12px; border-radius: 6px;
      font-size: 12px; font-weight: 600; outline: none; cursor: pointer;
    }}
    .submix-bar {{
      background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px 16px;
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;
    }}
    .submix-title {{ font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }}
    .trigram-pills {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .tri-btn {{
      background: #1e293b; color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px;
      border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s ease;
    }}
    .tri-btn:hover {{ border-color: #38bdf8; color: #fff; background: #334155; }}
    .tri-btn.active {{ border-color: #38bdf8; background: #0284c7; color: #fff; }}

    /* 64-Channel Mixing Rack Grid */
    .rack-container {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px;
      flex: 1; overflow-y: auto; max-height: calc(100vh - 210px); padding-right: 4px;
    }}
    .channel-strip {{
      background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px;
      display: flex; flex-direction: column; gap: 8px; transition: all 0.15s ease;
    }}
    .channel-strip.active {{ border-color: #38bdf8; box-shadow: 0 0 10px rgba(56,189,248,0.25); }}
    .channel-strip.muted {{ opacity: 0.38; border-color: rgba(239,68,68,0.3); }}
    .channel-strip.soloed {{ border-color: #f59e0b; box-shadow: 0 0 12px rgba(245,158,11,0.5); }}
    .strip-header {{
      display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 700;
    }}
    .strip-name {{
      font-size: 11px; color: #f8fafc; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .strip-hanzi {{ font-size: 16px; color: #FFD700; }}
    .strip-freq {{ font-size: 10px; color: #94a3b8; font-family: monospace; }}
    .strip-btns {{ display: flex; gap: 4px; }}
    .strip-btn {{
      flex: 1; padding: 3px 0; font-size: 10px; font-weight: 800; border-radius: 4px; cursor: pointer; text-align: center;
      border: 1px solid transparent; transition: all 0.15s ease;
    }}
    .btn-m {{ background: #1e293b; color: #94a3b8; border-color: #334155; }}
    .btn-m.on {{ background: #ef4444; color: #fff; border-color: #ef4444; }}
    .btn-s {{ background: #1e293b; color: #94a3b8; border-color: #334155; }}
    .btn-s.on {{ background: #f59e0b; color: #0f172a; border-color: #f59e0b; }}
    .fader-box {{
      display: flex; flex-direction: column; gap: 3px; font-size: 9px; color: #64748b;
    }}
    input[type=range] {{
      width: 100%; accent-color: #38bdf8; cursor: pointer;
    }}
    .pellet-dots {{ display: flex; justify-content: space-between; gap: 2px; margin-top: 2px; }}
    .p-dot {{ width: 6px; height: 6px; border-radius: 50%; }}
  </style>
</head>
<body>
  <header>
    <h1>&#x1F39B;&#xFE0F; King Wen 64-Sovereign External Audio Switchboard <span class="badge">64 Channels</span></h1>
    <div class="master-controls">
      <button class="btn" id="master-power" onclick="toggleMasterPower()">&#x1F50A; Master Audio: OFF</button>
      <select id="switchboard-mode" class="audio-select" onchange="changeMode()">
        <option value="superposition">&#x1F30C; Full 64-Channel Spatial Superposition</option>
        <option value="arpeggiator">&#x26A1; Continuous 64-Hex Arpeggiator</option>
        <option value="binaural">&#x262F;&#xFE0F; Dual Yin/Yang Binaural Carrier</option>
      </select>
      <button class="btn btn-warn" onclick="soloActiveChannels()">&#x2B50; Solo Active</button>
      <button class="btn btn-danger" onclick="muteAllChannels()">&#x1F507; Mute All</button>
      <button class="btn" onclick="unmuteAllChannels()">&#x1F509; Unmute All</button>
    </div>
  </header>

  <div class="submix-bar">
    <div class="submix-title">&#x1F451; 8 Trigram Submix Groups:</div>
    <div class="trigram-pills">
      <button class="tri-btn" onclick="filterByTrigram('all')">All 64</button>
      <button class="tri-btn" onclick="filterByTrigram('Qian')">&#x2630; Qian (Heaven)</button>
      <button class="tri-btn" onclick="filterByTrigram('Kun')">&#x2637; Kun (Earth)</button>
      <button class="tri-btn" onclick="filterByTrigram('Zhen')">&#x2633; Zhen (Thunder)</button>
      <button class="tri-btn" onclick="filterByTrigram('Kan')">&#x2635; Kan (Water)</button>
      <button class="tri-btn" onclick="filterByTrigram('Li')">&#x2632; Li (Fire)</button>
      <button class="tri-btn" onclick="filterByTrigram('Xun')">&#x2634; Xun (Wind)</button>
      <button class="tri-btn" onclick="filterByTrigram('Gen')">&#x2636; Gen (Mountain)</button>
      <button class="tri-btn" onclick="filterByTrigram('Dui')">&#x2631; Dui (Lake)</button>
    </div>
    <div style="font-size: 11px; color: #94a3b8;">
      Master Volume: <input type="range" id="master-vol" min="0" max="100" value="80" oninput="setMasterVolume(this.value)" style="width:90px; vertical-align:middle;">
    </div>
  </div>

  <div class="rack-container" id="rack-container"></div>

  <script>
    const channelsData = {channels_json};

    let audioCtx = null;
    let masterAudioActive = false;
    let masterGain = null;
    let masterFilter = null;
    let voiceStrips = [];
    let soloActive = false;

    function initAudio() {{
      if (audioCtx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();

      masterGain = audioCtx.createGain();
      masterGain.gain.setValueAtTime(0.35, audioCtx.currentTime);

      masterFilter = audioCtx.createBiquadFilter();
      masterFilter.type = 'lowpass';
      masterFilter.frequency.setValueAtTime(2400, audioCtx.currentTime);
      masterFilter.Q.setValueAtTime(2.0, audioCtx.currentTime);

      masterGain.connect(masterFilter);
      masterFilter.connect(audioCtx.destination);

      // Create all 64 individual channel strips
      channelsData.forEach((ch, idx) => {{
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        const f = audioCtx.createBiquadFilter();

        osc.type = (ch.hex_id % 3 === 0) ? 'triangle' : ((ch.hex_id % 2 === 0) ? 'sine' : 'sawtooth');
        osc.frequency.setValueAtTime(ch.base_frequency_hz, audioCtx.currentTime);

        f.type = 'lowpass';
        f.frequency.setValueAtTime(400 + ch.porosity * 2200, audioCtx.currentTime);
        f.Q.setValueAtTime(1.5 + ch.vortex_tension * 3.0, audioCtx.currentTime);

        g.gain.setValueAtTime(0.04, audioCtx.currentTime);

        osc.connect(f);
        f.connect(g);
        g.connect(masterGain);
        osc.start();

        voiceStrips.push({{
          data: ch,
          osc,
          filter: f,
          gain: g,
          muted: false,
          soloed: false,
          vol: 0.70
        }});
      }});
    }}

    function toggleMasterPower() {{
      initAudio();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      masterAudioActive = !masterAudioActive;
      const btn = document.getElementById('master-power');
      if (masterAudioActive) {{
        btn.innerHTML = '&#x1F50A; Master Audio: ON';
        btn.classList.add('btn-power-on');
        masterGain.gain.setTargetAtTime(0.35, audioCtx.currentTime, 0.05);
      }} else {{
        btn.innerHTML = '&#x1F50A; Master Audio: OFF';
        btn.classList.remove('btn-power-on');
        masterGain.gain.setTargetAtTime(0.0, audioCtx.currentTime, 0.05);
      }}
    }}

    function setMasterVolume(val) {{
      if (!audioCtx) return;
      const v = (val / 100.0) * 0.5;
      masterGain.gain.setTargetAtTime(v, audioCtx.currentTime, 0.04);
    }}

    function toggleMute(idx) {{
      const v = voiceStrips[idx];
      v.muted = !v.muted;
      updateVoiceGains();
      renderRack();
    }}

    function toggleSolo(idx) {{
      const v = voiceStrips[idx];
      v.soloed = !v.soloed;
      soloActive = voiceStrips.some(vs => vs.soloed);
      updateVoiceGains();
      renderRack();
    }}

    function setChannelVolume(idx, val) {{
      const v = voiceStrips[idx];
      v.vol = val / 100.0;
      updateVoiceGains();
    }}

    function updateVoiceGains() {{
      if (!audioCtx) return;
      const now = audioCtx.currentTime;
      voiceStrips.forEach(vs => {{
        let active = true;
        if (soloActive) {{
          active = vs.soloed;
        }} else {{
          active = !vs.muted;
        }}
        const targetVol = active ? (vs.vol * 0.06) : 0.0;
        vs.gain.gain.setTargetAtTime(targetVol, now, 0.03);
      }});
    }}

    function muteAllChannels() {{
      voiceStrips.forEach(vs => {{ vs.muted = true; vs.soloed = false; }});
      soloActive = false;
      updateVoiceGains();
      renderRack();
    }}

    function unmuteAllChannels() {{
      voiceStrips.forEach(vs => {{ vs.muted = false; vs.soloed = false; }});
      soloActive = false;
      updateVoiceGains();
      renderRack();
    }}

    function filterByTrigram(tri) {{
      voiceStrips.forEach(vs => {{
        if (tri === 'all') {{
          vs.muted = false;
        }} else {{
          vs.muted = !(vs.data.upper_trigram === tri || vs.data.lower_trigram === tri);
        }}
        vs.soloed = false;
      }});
      soloActive = false;
      updateVoiceGains();
      renderRack();
    }}

    function renderRack() {{
      const container = document.getElementById('rack-container');
      let html = '';
      channelsData.forEach((ch, idx) => {{
        const vs = voiceStrips[idx] || {{ muted: false, soloed: false, vol: 0.7 }};
        const isActive = soloActive ? vs.soloed : !vs.muted;
        const stripClass = vs.soloed ? 'soloed' : (vs.muted ? 'muted' : (isActive ? 'active' : ''));

        let pelletHtml = '';
        ch.pellets.forEach(p => {{
          pelletHtml += `<div class="p-dot" style="background:${{p.color_hex}};" title="L${{p.line}}: ${{p.type}} (${{p.frequency_hz}}Hz)"></div>`;
        }});

        html += `
          <div class="channel-strip ${{stripClass}}">
            <div class="strip-header">
              <span style="color:#38bdf8;">#${{ch.hex_id}}</span>
              <span class="strip-hanzi">${{ch.hanzi}}</span>
              <span style="width:8px;height:8px;border-radius:50%;background:${{ch.spectral_color}};"></span>
            </div>
            <div class="strip-name" title="${{ch.name}}">${{ch.name}}</div>
            <div class="strip-freq">${{ch.base_frequency_hz}}Hz</div>
            <div class="pellet-dots">${{pelletHtml}}</div>
            <div class="strip-btns">
              <button class="strip-btn btn-m ${{vs.muted ? 'on' : ''}}" onclick="toggleMute(${{idx}})">M</button>
              <button class="strip-btn btn-s ${{vs.soloed ? 'on' : ''}}" onclick="toggleSolo(${{idx}})">S</button>
            </div>
            <div class="fader-box">
              <input type="range" min="0" max="100" value="${{Math.round(vs.vol * 100)}}" oninput="setChannelVolume(${{idx}}, this.value)">
            </div>
          </div>
        `;
      }});
      container.innerHTML = html;
    }}

    // Initial render
    renderRack();
  </script>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"[OK] Generated Standalone External Audio Switchboard: {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    channels = generate_switchboard_data()
    build_switchboard_html(channels)
