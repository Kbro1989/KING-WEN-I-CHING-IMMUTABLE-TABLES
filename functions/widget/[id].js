/**
 * King Wen 64 Sovereign Engine — /widget/:id Edge Endpoint
 * Serves lightweight standalone HTML widgets for individual hexagrams (1..64),
 * 6-yao line pellet visualizers, or the master 512-state oracle switchboard when :id is 'all' or '512'.
 */
export async function onRequestGet(context) {
  const { request, params, env } = context;
  const url = new URL(request.url);
  const rawId = (params.id || 'all').toLowerCase();

  try {
    const assetUrl = new URL('/DATASETS/kingwen_sovereign_world_topology.json', url.origin);
    const assetRes = await env.ASSETS ? env.ASSETS.fetch(assetUrl) : await fetch(assetUrl);
    const topo = assetRes.ok ? await assetRes.json() : { sectors: [] };
    const sectors = topo.sectors || [];

    if (rawId === 'all' || rawId === '512' || rawId === 'grid') {
      // Render Master 64-Sovereign Widget Grid
      const html = generateMasterGridWidgetHTML(sectors, url.origin);
      return new Response(html, {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=3600' }
      });
    }

    const hexId = parseInt(rawId, 10);
    if (isNaN(hexId) || hexId < 1 || hexId > 64) {
      return new Response('<h1>404 Widget Not Found</h1><p>Hexagram ID must be between 1 and 64, or "all".</p>', {
        status: 404,
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      });
    }

    const sector = sectors.find(s => s.hexagram_id === hexId) || {};
    const html = generateSingleHexagramWidgetHTML(sector, url.origin);

    return new Response(html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=3600' }
    });
  } catch (err) {
    return new Response(`<h1>500 Widget Edge Error</h1><p>${err.message}</p>`, {
      status: 500,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
}

function generateSingleHexagramWidgetHTML(s, origin) {
  const pellets = s.yao_pellets || [];
  const sc = s.spectral_color || { hex: '#FFD700' };

  const pelletItems = pellets.map(p => `
    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:4px; margin-bottom:4px; font-size:11px;">
      <span style="color:${p.color_hex}; font-weight:700;">Line ${p.line_position} (${p.line_type.toUpperCase()})</span>
      <span style="font-family:monospace; color:#38bdf8;">${p.frequency_hz}Hz</span>
    </div>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Citadel #${s.hexagram_id || 1} ${s.hexagram_name || ''} Widget</title>
  <style>
    body { margin:0; padding:16px; background:#0b0f19; color:#f8fafc; font-family:sans-serif; }
    .card { background:rgba(15,23,42,0.95); border:1px solid ${sc.hex}; border-radius:12px; padding:16px; box-shadow:0 0 20px ${sc.hex}44; max-width:320px; }
    .title { font-size:18px; font-weight:800; color:${sc.hex}; margin-bottom:4px; display:flex; align-items:center; justify-content:space-between; }
    .meta { font-size:11px; color:#94a3b8; margin-bottom:12px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="title">
      <span>#${s.hexagram_id} ${s.hexagram_name}</span>
      <span style="font-size:24px;">${s.hanzi || '䷀'}</span>
    </div>
    <div class="meta">${s.regional_biome?.name || 'Solar Domain'} | VHDL Address: ${(s.hexagram_id - 1) * 8}</div>
    <div style="font-size:11px; font-weight:700; color:#c4b5fd; margin-bottom:6px;">6-YAO ACOUSTIC SOUND PELLETS</div>
    ${pelletItems}
  </div>
</body>
</html>`;
}

function generateMasterGridWidgetHTML(sectors, origin) {
  const gridItems = sectors.map(s => {
    const sc = s.spectral_color || { hex: '#FFD700' };
    return `
      <a href="/widget/${s.hexagram_id}" style="text-decoration:none;">
        <div style="background:rgba(15,23,42,0.9); border:1px solid ${sc.hex}88; border-radius:8px; padding:8px; text-align:center; transition:all 0.2s ease;">
          <div style="font-size:20px;">${s.hanzi || '䷀'}</div>
          <div style="font-size:10px; font-weight:700; color:${sc.hex}; margin-top:2px;">#${s.hexagram_id} ${s.hexagram_name}</div>
        </div>
      </a>
    `;
  }).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>King Wen 64 Sovereign Widget Grid</title>
  <style>
    body { margin:0; padding:20px; background:#070913; color:#f8fafc; font-family:sans-serif; }
    .grid { display:grid; grid-template-columns:repeat(8, 1fr); gap:10px; max-width:960px; margin:0 auto; }
    h1 { text-align:center; color:#c4b5fd; font-size:20px; margin-bottom:20px; }
  </style>
</head>
<body>
  <h1>👑 KING WEN 64 SOVEREIGN UNIFIED WIDGET GRID</h1>
  <div class="grid">${gridItems}</div>
</body>
</html>`;
}
