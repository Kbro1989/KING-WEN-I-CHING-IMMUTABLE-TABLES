var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// .wrangler/tmp/pages-wsD3FB/functionsWorker-0.1540224151490739.mjs
var __defProp2 = Object.defineProperty;
var __name2 = /* @__PURE__ */ __name((target, value) => __defProp2(target, "name", { value, configurable: true }), "__name");
async function onRequestGet(context) {
  const { request, params, env } = context;
  const layerId = parseInt(params.id, 10);
  if (isNaN(layerId) || layerId < 0 || layerId > 3) {
    return Response.json(
      { error: "Invalid layer ID. Supported layers: 0 (Skeleton), 1 (Physics), 2 (Pellets), 3 (Egg & Audio)." },
      { status: 400 }
    );
  }
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);
  let cachedResponse = await cache.match(cacheKey);
  if (cachedResponse) {
    const freshHeaders = new Headers(cachedResponse.headers);
    freshHeaders.set("X-Edge-Cache-Status", "HIT");
    return new Response(cachedResponse.body, {
      status: cachedResponse.status,
      headers: freshHeaders
    });
  }
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (!assetRes.ok) {
      return Response.json(
        { error: "World topology manifest not found on asset storage", status: assetRes.status },
        { status: 404 }
      );
    }
    const fullTopology = await assetRes.json();
    const sectors = fullTopology.sectors || [];
    let layerPayload = {};
    if (layerId === 0) {
      layerPayload = {
        layer: 0,
        layer_name: "Skeleton Spatial Layout",
        total_sectors: sectors.length,
        world_grid: fullTopology.world_grid || {},
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          name: s.name,
          hexagram_name: s.hexagram_name,
          hanzi: s.hanzi,
          binary: s.binary,
          upper_trigram: s.upper_trigram,
          lower_trigram: s.lower_trigram,
          grid_coordinates: s.grid_coordinates,
          world_position: s.world_position,
          sector_bounds: s.sector_bounds,
          regional_biome: s.regional_biome,
          spectral_color: s.spectral_color,
          base_hue_degrees: s.base_hue_degrees
        }))
      };
    } else if (layerId === 1) {
      layerPayload = {
        layer: 1,
        layer_name: "Quantum Physics & Vortex Geometries",
        total_sectors: sectors.length,
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          quantum_physics: s.quantum_physics || {},
          quantum_wave_packet: s.quantum_wave_packet || {},
          action_doctrine: s.action_doctrine,
          citadel_archetype: s.citadel_archetype
        }))
      };
    } else if (layerId === 2) {
      layerPayload = {
        layer: 2,
        layer_name: "384 Sound Pellets & Acoustic Field",
        total_sectors: sectors.length,
        total_pellets: sectors.length * 6,
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          yao_pellets: s.yao_pellets || []
        }))
      };
    } else if (layerId === 3) {
      layerPayload = {
        layer: 3,
        layer_name: "Master Centripetal Egg 3D Deformation & Audio Corpus",
        egg_keyframes_count: fullTopology.egg_keyframes ? fullTopology.egg_keyframes.length : 0,
        egg_keyframes: fullTopology.egg_keyframes || [],
        audio_unison_wav_b64: fullTopology.audio_unison_wav_b64 || "",
        jkd_passages_by_hex: sectors.reduce((acc, s) => {
          if (s.jkd_passages && s.jkd_passages.length > 0) {
            acc[s.hexagram_id] = s.jkd_passages;
          }
          return acc;
        }, {})
      };
    }
    const responseObj = {
      engine: "King Wen 64 Sovereign Model Engine",
      version: "3.2.0",
      cf_colo: request.cf?.colo || "EDGE",
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      data: layerPayload
    };
    const headers = new Headers({
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=7200, s-maxage=86400",
      "X-Edge-Cache-Status": "MISS",
      "X-Prewarm-Layer": layerId.toString()
    });
    const response = new Response(JSON.stringify(responseObj), {
      status: 200,
      headers
    });
    context.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  } catch (err) {
    return Response.json(
      { error: "Internal edge server error slicing pre-warm cache layer", message: err.message },
      { status: 500 }
    );
  }
}
__name(onRequestGet, "onRequestGet");
__name2(onRequestGet, "onRequestGet");
async function onRequestGet2(context) {
  const { request, params, env } = context;
  const hexId = parseInt(params.id, 10);
  if (isNaN(hexId) || hexId < 1 || hexId > 64) {
    return Response.json(
      { error: "Invalid hexagram ID. Must be an integer between 1 and 64.", status: 400 },
      { status: 400 }
    );
  }
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (!assetRes.ok) {
      return Response.json({ error: "World topology manifest not found", status: assetRes.status }, { status: 404 });
    }
    const topo = await assetRes.json();
    const sector = (topo.sectors || []).find((s) => s.hexagram_id === hexId);
    if (!sector) {
      return Response.json({ error: `Hexagram #${hexId} sector not found` }, { status: 404 });
    }
    const binaryStr = sector.binary || "111111";
    const vhdlBaseAddr = (hexId - 1) * 8;
    return Response.json(
      {
        engine: "King Wen 64 Sovereign Model Engine",
        version: "3.2.0",
        hexagram_id: hexId,
        vhdl_resolver: {
          base_address_9bit: vhdlBaseAddr,
          address_range_8_phases: [vhdlBaseAddr, vhdlBaseAddr + 7],
          binary_pattern: binaryStr
        },
        sector
      },
      {
        headers: {
          "Cache-Control": "public, max-age=3600, s-maxage=86400",
          "Content-Type": "application/json; charset=utf-8"
        }
      }
    );
  } catch (err) {
    return Response.json({ error: "Internal edge server error", message: err.message }, { status: 500 });
  }
}
__name(onRequestGet2, "onRequestGet2");
__name2(onRequestGet2, "onRequestGet");
async function onRequestGet3(context) {
  const { request, params, env } = context;
  const hexId = parseInt(params.id, 10);
  if (isNaN(hexId) || hexId < 1 || hexId > 64) {
    return Response.json(
      { error: "Invalid hexagram ID. Must be between 1 and 64.", status: 400 },
      { status: 400 }
    );
  }
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (!assetRes.ok) {
      return Response.json({ error: "World topology manifest not found" }, { status: 404 });
    }
    const topo = await assetRes.json();
    const sector = (topo.sectors || []).find((s) => s.hexagram_id === hexId);
    if (!sector) {
      return Response.json({ error: `Hexagram #${hexId} not found` }, { status: 404 });
    }
    const passages = sector.jkd_passages || [];
    return Response.json(
      {
        engine: "King Wen x JKD Megatron Wavepacket Speech Engine",
        hexagram_id: hexId,
        hexagram_name: sector.hexagram_name,
        total_passages: passages.length,
        passages
      },
      {
        headers: {
          "Cache-Control": "public, max-age=3600, s-maxage=86400",
          "Content-Type": "application/json; charset=utf-8"
        }
      }
    );
  } catch (err) {
    return Response.json({ error: "Internal edge server error", message: err.message }, { status: 500 });
  }
}
__name(onRequestGet3, "onRequestGet3");
__name2(onRequestGet3, "onRequestGet");
async function onRequestGet4(context) {
  const { request, env } = context;
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (!assetRes.ok) {
      return Response.json(
        { error: "World topology manifest not found", status: assetRes.status },
        { status: 404 }
      );
    }
    const data = await assetRes.json();
    return Response.json(
      {
        engine: "King Wen 64 Sovereign Model Engine",
        version: "3.2.0",
        cf_colo: request.cf?.colo || "LOCAL",
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        topology: data
      },
      {
        headers: {
          "Cache-Control": "public, max-age=3600, s-maxage=86400",
          "Content-Type": "application/json; charset=utf-8"
        }
      }
    );
  } catch (err) {
    return Response.json(
      { error: "Internal edge server error", message: err.message },
      { status: 500 }
    );
  }
}
__name(onRequestGet4, "onRequestGet4");
__name2(onRequestGet4, "onRequestGet");
async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const pathname = url.pathname.replace(/\/$/, "");
  let hexId = parseInt(url.searchParams.get("hex") || "1", 10);
  let phaseId = parseInt(url.searchParams.get("phase") || "0", 10);
  let address = url.searchParams.get("address");
  if (request.method === "POST") {
    try {
      const body = await request.json();
      if (body.address != null) address = String(body.address);
      if (body.hexagram_id) hexId = parseInt(body.hexagram_id, 10);
      if (body.phase_id) phaseId = parseInt(body.phase_id, 10);
    } catch (e) {
    }
  }
  if (address != null && address !== "") {
    const addr = Math.max(0, Math.min(511, parseInt(address, 10)));
    hexId = Math.floor(addr / 8) + 1;
    phaseId = addr % 8;
  }
  hexId = Math.max(1, Math.min(64, hexId));
  phaseId = Math.max(0, Math.min(7, phaseId));
  let topo = { sectors: [] };
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (assetRes.ok) topo = await assetRes.json();
  } catch (e) {
  }
  const sector = (topo.sectors || []).find((s) => s.hexagram_id === hexId) || {};
  const vhdlAddr = (hexId - 1) * 8 + phaseId;
  const pellets = sector.yao_pellets || [];
  const carrierFreqs = pellets.map((p) => p.frequency_hz || 146);
  const wavepacketHash = pellets.map((p) => `${p.line_position}:${p.ternary_state}:${p.frequency_hz}`).join("|");
  const statePacket = {
    protocol: "King Wen Link Acoustic Peer-to-Peer Protocol v1.0",
    hexagram_id: hexId,
    phase_id: phaseId,
    phase_temporal: phaseId === 0 ? "past" : phaseId === 1 ? "present" : "future",
    vhdl_resolved_address_9bit: vhdlAddr,
    hexagram_name: sector.hexagram_name || "Heaven",
    binary_pattern: sector.binary || "111111",
    ternary_state: sector.ternary || "000000",
    category: sector.category || "sovereign",
    action: sector.action || "unbound",
    yao_pellets: pellets.map((p) => ({
      line_position: p.line_position,
      ternary_state: p.ternary_state,
      waveform: p.waveform,
      frequency_hz: p.frequency_hz,
      energy_intensity: p.energy_intensity
    })),
    emotional_vector: {
      voiceWeight: 0,
      coherence: 0,
      chaos: 0,
      whimsy: 0,
      darkTone: 0,
      porosity: sector.quantum_physics?.porosity_level ?? 0,
      _note: "enrich_via_openjarvis_consult_tool"
    },
    quantum_physics: sector.quantum_physics || {},
    acoustic_carriers: {
      yao_line_frequencies_hz: carrierFreqs,
      wavepacket_signature: wavepacketHash,
      fundamental_freq_hz: sector.quantum_physics?.fundamental_frequency_hz || 108,
      vortex_tension: sector.quantum_physics?.vortex_tension || 0.5
    },
    peer_handshake: {
      status: "SYNCHRONIZED",
      consensus_mode: "UNBOUND_SUPERPOSITION",
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    }
  };
  if (pathname.endsWith("/decode")) {
    return Response.json(statePacket, {
      headers: {
        "X-KingWenLink-Protocol": "v1.0-decode",
        "Content-Type": "application/json; charset=utf-8"
      }
    });
  }
  return Response.json(statePacket, {
    headers: {
      "X-KingWenLink-Protocol": "v1.0-acoustic-wavepacket",
      "Content-Type": "application/json; charset=utf-8"
    }
  });
}
__name(onRequest, "onRequest");
__name2(onRequest, "onRequest");
async function onRequestGet5(context) {
  const { request, params, env } = context;
  const rawId = (params.id || "all").toLowerCase();
  try {
    const assetReq = new Request(new URL("/DATASETS/kingwen_sovereign_world_topology.json", request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    const topo = assetRes.ok ? await assetRes.json() : { sectors: [] };
    const sectors = topo.sectors || [];
    if (rawId === "all" || rawId === "512" || rawId === "grid") {
      const html2 = generateMasterGridWidgetHTML(sectors);
      return new Response(html2, {
        headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "public, max-age=3600" }
      });
    }
    const hexId = parseInt(rawId, 10);
    if (isNaN(hexId) || hexId < 1 || hexId > 64) {
      return new Response('<h1>404 Widget Not Found</h1><p>Hexagram ID must be between 1 and 64, or "all".</p>', {
        status: 404,
        headers: { "Content-Type": "text/html; charset=utf-8" }
      });
    }
    const sector = sectors.find((s) => s.hexagram_id === hexId) || {};
    const html = generateSingleHexagramWidgetHTML(sector);
    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "public, max-age=3600" }
    });
  } catch (err) {
    return new Response(`<h1>500 Widget Edge Error</h1><p>${err.message}</p>`, {
      status: 500,
      headers: { "Content-Type": "text/html; charset=utf-8" }
    });
  }
}
__name(onRequestGet5, "onRequestGet5");
__name2(onRequestGet5, "onRequestGet");
function generateSingleHexagramWidgetHTML(s) {
  const pellets = s.yao_pellets || [];
  const sc = s.spectral_color || { hex: "#FFD700" };
  const pelletItems = pellets.map((p) => `
    <div style="display:flex; justify-space-between; align-items:center; background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:4px; margin-bottom:4px; font-size:11px;">
      <span style="color:${p.color_hex}; font-weight:700;">Line ${p.line_position} (${p.line_type.toUpperCase()})</span>
      <span style="font-family:monospace; color:#38bdf8;">${p.frequency_hz}Hz</span>
    </div>
  `).join("");
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Citadel #${s.hexagram_id || 1} ${s.hexagram_name || ""} Widget</title>
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
      <span style="font-size:24px;">${s.hanzi || "\u4DC0"}</span>
    </div>
    <div class="meta">${s.regional_biome?.name || "Solar Domain"} | VHDL Address: ${(s.hexagram_id - 1) * 8}</div>
    <div style="font-size:11px; font-weight:700; color:#c4b5fd; margin-bottom:6px;">6-YAO ACOUSTIC SOUND PELLETS</div>
    ${pelletItems}
  </div>
</body>
</html>`;
}
__name(generateSingleHexagramWidgetHTML, "generateSingleHexagramWidgetHTML");
__name2(generateSingleHexagramWidgetHTML, "generateSingleHexagramWidgetHTML");
function generateMasterGridWidgetHTML(sectors) {
  const gridItems = sectors.map((s) => {
    const sc = s.spectral_color || { hex: "#FFD700" };
    return `
      <a href="/widget/${s.hexagram_id}" style="text-decoration:none;">
        <div style="background:rgba(15,23,42,0.9); border:1px solid ${sc.hex}88; border-radius:8px; padding:8px; text-align:center; transition:all 0.2s ease;">
          <div style="font-size:20px;">${s.hanzi || "\u4DC0"}</div>
          <div style="font-size:10px; font-weight:700; color:${sc.hex}; margin-top:2px;">#${s.hexagram_id} ${s.hexagram_name}</div>
        </div>
      </a>
    `;
  }).join("");
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
  <h1>\u{1F451} KING WEN 64 SOVEREIGN UNIFIED WIDGET GRID</h1>
  <div class="grid">${gridItems}</div>
</body>
</html>`;
}
__name(generateMasterGridWidgetHTML, "generateMasterGridWidgetHTML");
__name2(generateMasterGridWidgetHTML, "generateMasterGridWidgetHTML");
async function onRequest2(context) {
  const { request, next } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-KingWenLink-Protocol, X-KingWen-Phase",
        "Access-Control-Max-Age": "86400"
      }
    });
  }
  const startTime = Date.now();
  const response = await next();
  const durationMs = Date.now() - startTime;
  const headers = new Headers(response.headers);
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("X-KingWen-Engine-Version", "3.2.0");
  headers.set("X-KingWen-Edge-Region", context.request.cf?.colo || "UNKNOWN");
  headers.set("X-Response-Time-Ms", durationMs.toString());
  headers.set("X-KingWenLink-Protocol", "v1.0-acoustic-wavepacket");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}
__name(onRequest2, "onRequest2");
__name2(onRequest2, "onRequest");
var routes = [
  {
    routePath: "/api/cache/layer/:id",
    mountPath: "/api/cache/layer",
    method: "GET",
    middlewares: [],
    modules: [onRequestGet]
  },
  {
    routePath: "/api/hexagram/:id",
    mountPath: "/api/hexagram",
    method: "GET",
    middlewares: [],
    modules: [onRequestGet2]
  },
  {
    routePath: "/api/jkd/:id",
    mountPath: "/api/jkd",
    method: "GET",
    middlewares: [],
    modules: [onRequestGet3]
  },
  {
    routePath: "/api/world",
    mountPath: "/api",
    method: "GET",
    middlewares: [],
    modules: [onRequestGet4]
  },
  {
    routePath: "/api/kingwen-link",
    mountPath: "/api",
    method: "",
    middlewares: [],
    modules: [onRequest]
  },
  {
    routePath: "/widget/:id",
    mountPath: "/widget",
    method: "GET",
    middlewares: [],
    modules: [onRequestGet5]
  },
  {
    routePath: "/",
    mountPath: "/",
    method: "",
    middlewares: [onRequest2],
    modules: []
  }
];
function lexer(str) {
  var tokens = [];
  var i = 0;
  while (i < str.length) {
    var char = str[i];
    if (char === "*" || char === "+" || char === "?") {
      tokens.push({ type: "MODIFIER", index: i, value: str[i++] });
      continue;
    }
    if (char === "\\") {
      tokens.push({ type: "ESCAPED_CHAR", index: i++, value: str[i++] });
      continue;
    }
    if (char === "{") {
      tokens.push({ type: "OPEN", index: i, value: str[i++] });
      continue;
    }
    if (char === "}") {
      tokens.push({ type: "CLOSE", index: i, value: str[i++] });
      continue;
    }
    if (char === ":") {
      var name = "";
      var j = i + 1;
      while (j < str.length) {
        var code = str.charCodeAt(j);
        if (
          // `0-9`
          code >= 48 && code <= 57 || // `A-Z`
          code >= 65 && code <= 90 || // `a-z`
          code >= 97 && code <= 122 || // `_`
          code === 95
        ) {
          name += str[j++];
          continue;
        }
        break;
      }
      if (!name)
        throw new TypeError("Missing parameter name at ".concat(i));
      tokens.push({ type: "NAME", index: i, value: name });
      i = j;
      continue;
    }
    if (char === "(") {
      var count = 1;
      var pattern = "";
      var j = i + 1;
      if (str[j] === "?") {
        throw new TypeError('Pattern cannot start with "?" at '.concat(j));
      }
      while (j < str.length) {
        if (str[j] === "\\") {
          pattern += str[j++] + str[j++];
          continue;
        }
        if (str[j] === ")") {
          count--;
          if (count === 0) {
            j++;
            break;
          }
        } else if (str[j] === "(") {
          count++;
          if (str[j + 1] !== "?") {
            throw new TypeError("Capturing groups are not allowed at ".concat(j));
          }
        }
        pattern += str[j++];
      }
      if (count)
        throw new TypeError("Unbalanced pattern at ".concat(i));
      if (!pattern)
        throw new TypeError("Missing pattern at ".concat(i));
      tokens.push({ type: "PATTERN", index: i, value: pattern });
      i = j;
      continue;
    }
    tokens.push({ type: "CHAR", index: i, value: str[i++] });
  }
  tokens.push({ type: "END", index: i, value: "" });
  return tokens;
}
__name(lexer, "lexer");
__name2(lexer, "lexer");
function parse(str, options) {
  if (options === void 0) {
    options = {};
  }
  var tokens = lexer(str);
  var _a = options.prefixes, prefixes = _a === void 0 ? "./" : _a, _b = options.delimiter, delimiter = _b === void 0 ? "/#?" : _b;
  var result = [];
  var key = 0;
  var i = 0;
  var path = "";
  var tryConsume = /* @__PURE__ */ __name2(function(type) {
    if (i < tokens.length && tokens[i].type === type)
      return tokens[i++].value;
  }, "tryConsume");
  var mustConsume = /* @__PURE__ */ __name2(function(type) {
    var value2 = tryConsume(type);
    if (value2 !== void 0)
      return value2;
    var _a2 = tokens[i], nextType = _a2.type, index = _a2.index;
    throw new TypeError("Unexpected ".concat(nextType, " at ").concat(index, ", expected ").concat(type));
  }, "mustConsume");
  var consumeText = /* @__PURE__ */ __name2(function() {
    var result2 = "";
    var value2;
    while (value2 = tryConsume("CHAR") || tryConsume("ESCAPED_CHAR")) {
      result2 += value2;
    }
    return result2;
  }, "consumeText");
  var isSafe = /* @__PURE__ */ __name2(function(value2) {
    for (var _i = 0, delimiter_1 = delimiter; _i < delimiter_1.length; _i++) {
      var char2 = delimiter_1[_i];
      if (value2.indexOf(char2) > -1)
        return true;
    }
    return false;
  }, "isSafe");
  var safePattern = /* @__PURE__ */ __name2(function(prefix2) {
    var prev = result[result.length - 1];
    var prevText = prefix2 || (prev && typeof prev === "string" ? prev : "");
    if (prev && !prevText) {
      throw new TypeError('Must have text between two parameters, missing text after "'.concat(prev.name, '"'));
    }
    if (!prevText || isSafe(prevText))
      return "[^".concat(escapeString(delimiter), "]+?");
    return "(?:(?!".concat(escapeString(prevText), ")[^").concat(escapeString(delimiter), "])+?");
  }, "safePattern");
  while (i < tokens.length) {
    var char = tryConsume("CHAR");
    var name = tryConsume("NAME");
    var pattern = tryConsume("PATTERN");
    if (name || pattern) {
      var prefix = char || "";
      if (prefixes.indexOf(prefix) === -1) {
        path += prefix;
        prefix = "";
      }
      if (path) {
        result.push(path);
        path = "";
      }
      result.push({
        name: name || key++,
        prefix,
        suffix: "",
        pattern: pattern || safePattern(prefix),
        modifier: tryConsume("MODIFIER") || ""
      });
      continue;
    }
    var value = char || tryConsume("ESCAPED_CHAR");
    if (value) {
      path += value;
      continue;
    }
    if (path) {
      result.push(path);
      path = "";
    }
    var open = tryConsume("OPEN");
    if (open) {
      var prefix = consumeText();
      var name_1 = tryConsume("NAME") || "";
      var pattern_1 = tryConsume("PATTERN") || "";
      var suffix = consumeText();
      mustConsume("CLOSE");
      result.push({
        name: name_1 || (pattern_1 ? key++ : ""),
        pattern: name_1 && !pattern_1 ? safePattern(prefix) : pattern_1,
        prefix,
        suffix,
        modifier: tryConsume("MODIFIER") || ""
      });
      continue;
    }
    mustConsume("END");
  }
  return result;
}
__name(parse, "parse");
__name2(parse, "parse");
function match(str, options) {
  var keys = [];
  var re = pathToRegexp(str, keys, options);
  return regexpToFunction(re, keys, options);
}
__name(match, "match");
__name2(match, "match");
function regexpToFunction(re, keys, options) {
  if (options === void 0) {
    options = {};
  }
  var _a = options.decode, decode = _a === void 0 ? function(x) {
    return x;
  } : _a;
  return function(pathname) {
    var m = re.exec(pathname);
    if (!m)
      return false;
    var path = m[0], index = m.index;
    var params = /* @__PURE__ */ Object.create(null);
    var _loop_1 = /* @__PURE__ */ __name2(function(i2) {
      if (m[i2] === void 0)
        return "continue";
      var key = keys[i2 - 1];
      if (key.modifier === "*" || key.modifier === "+") {
        params[key.name] = m[i2].split(key.prefix + key.suffix).map(function(value) {
          return decode(value, key);
        });
      } else {
        params[key.name] = decode(m[i2], key);
      }
    }, "_loop_1");
    for (var i = 1; i < m.length; i++) {
      _loop_1(i);
    }
    return { path, index, params };
  };
}
__name(regexpToFunction, "regexpToFunction");
__name2(regexpToFunction, "regexpToFunction");
function escapeString(str) {
  return str.replace(/([.+*?=^!:${}()[\]|/\\])/g, "\\$1");
}
__name(escapeString, "escapeString");
__name2(escapeString, "escapeString");
function flags(options) {
  return options && options.sensitive ? "" : "i";
}
__name(flags, "flags");
__name2(flags, "flags");
function regexpToRegexp(path, keys) {
  if (!keys)
    return path;
  var groupsRegex = /\((?:\?<(.*?)>)?(?!\?)/g;
  var index = 0;
  var execResult = groupsRegex.exec(path.source);
  while (execResult) {
    keys.push({
      // Use parenthesized substring match if available, index otherwise
      name: execResult[1] || index++,
      prefix: "",
      suffix: "",
      modifier: "",
      pattern: ""
    });
    execResult = groupsRegex.exec(path.source);
  }
  return path;
}
__name(regexpToRegexp, "regexpToRegexp");
__name2(regexpToRegexp, "regexpToRegexp");
function arrayToRegexp(paths, keys, options) {
  var parts = paths.map(function(path) {
    return pathToRegexp(path, keys, options).source;
  });
  return new RegExp("(?:".concat(parts.join("|"), ")"), flags(options));
}
__name(arrayToRegexp, "arrayToRegexp");
__name2(arrayToRegexp, "arrayToRegexp");
function stringToRegexp(path, keys, options) {
  return tokensToRegexp(parse(path, options), keys, options);
}
__name(stringToRegexp, "stringToRegexp");
__name2(stringToRegexp, "stringToRegexp");
function tokensToRegexp(tokens, keys, options) {
  if (options === void 0) {
    options = {};
  }
  var _a = options.strict, strict = _a === void 0 ? false : _a, _b = options.start, start = _b === void 0 ? true : _b, _c = options.end, end = _c === void 0 ? true : _c, _d = options.encode, encode = _d === void 0 ? function(x) {
    return x;
  } : _d, _e = options.delimiter, delimiter = _e === void 0 ? "/#?" : _e, _f = options.endsWith, endsWith = _f === void 0 ? "" : _f;
  var endsWithRe = "[".concat(escapeString(endsWith), "]|$");
  var delimiterRe = "[".concat(escapeString(delimiter), "]");
  var route = start ? "^" : "";
  for (var _i = 0, tokens_1 = tokens; _i < tokens_1.length; _i++) {
    var token = tokens_1[_i];
    if (typeof token === "string") {
      route += escapeString(encode(token));
    } else {
      var prefix = escapeString(encode(token.prefix));
      var suffix = escapeString(encode(token.suffix));
      if (token.pattern) {
        if (keys)
          keys.push(token);
        if (prefix || suffix) {
          if (token.modifier === "+" || token.modifier === "*") {
            var mod = token.modifier === "*" ? "?" : "";
            route += "(?:".concat(prefix, "((?:").concat(token.pattern, ")(?:").concat(suffix).concat(prefix, "(?:").concat(token.pattern, "))*)").concat(suffix, ")").concat(mod);
          } else {
            route += "(?:".concat(prefix, "(").concat(token.pattern, ")").concat(suffix, ")").concat(token.modifier);
          }
        } else {
          if (token.modifier === "+" || token.modifier === "*") {
            throw new TypeError('Can not repeat "'.concat(token.name, '" without a prefix and suffix'));
          }
          route += "(".concat(token.pattern, ")").concat(token.modifier);
        }
      } else {
        route += "(?:".concat(prefix).concat(suffix, ")").concat(token.modifier);
      }
    }
  }
  if (end) {
    if (!strict)
      route += "".concat(delimiterRe, "?");
    route += !options.endsWith ? "$" : "(?=".concat(endsWithRe, ")");
  } else {
    var endToken = tokens[tokens.length - 1];
    var isEndDelimited = typeof endToken === "string" ? delimiterRe.indexOf(endToken[endToken.length - 1]) > -1 : endToken === void 0;
    if (!strict) {
      route += "(?:".concat(delimiterRe, "(?=").concat(endsWithRe, "))?");
    }
    if (!isEndDelimited) {
      route += "(?=".concat(delimiterRe, "|").concat(endsWithRe, ")");
    }
  }
  return new RegExp(route, flags(options));
}
__name(tokensToRegexp, "tokensToRegexp");
__name2(tokensToRegexp, "tokensToRegexp");
function pathToRegexp(path, keys, options) {
  if (path instanceof RegExp)
    return regexpToRegexp(path, keys);
  if (Array.isArray(path))
    return arrayToRegexp(path, keys, options);
  return stringToRegexp(path, keys, options);
}
__name(pathToRegexp, "pathToRegexp");
__name2(pathToRegexp, "pathToRegexp");
var escapeRegex = /[.+?^${}()|[\]\\]/g;
function* executeRequest(request) {
  const requestPath = new URL(request.url).pathname;
  for (const route of [...routes].reverse()) {
    if (route.method && route.method !== request.method) {
      continue;
    }
    const routeMatcher = match(route.routePath.replace(escapeRegex, "\\$&"), {
      end: false
    });
    const mountMatcher = match(route.mountPath.replace(escapeRegex, "\\$&"), {
      end: false
    });
    const matchResult = routeMatcher(requestPath);
    const mountMatchResult = mountMatcher(requestPath);
    if (matchResult && mountMatchResult) {
      for (const handler of route.middlewares.flat()) {
        yield {
          handler,
          params: matchResult.params,
          path: mountMatchResult.path
        };
      }
    }
  }
  for (const route of routes) {
    if (route.method && route.method !== request.method) {
      continue;
    }
    const routeMatcher = match(route.routePath.replace(escapeRegex, "\\$&"), {
      end: true
    });
    const mountMatcher = match(route.mountPath.replace(escapeRegex, "\\$&"), {
      end: false
    });
    const matchResult = routeMatcher(requestPath);
    const mountMatchResult = mountMatcher(requestPath);
    if (matchResult && mountMatchResult && route.modules.length) {
      for (const handler of route.modules.flat()) {
        yield {
          handler,
          params: matchResult.params,
          path: matchResult.path
        };
      }
      break;
    }
  }
}
__name(executeRequest, "executeRequest");
__name2(executeRequest, "executeRequest");
var pages_template_worker_default = {
  async fetch(originalRequest, env, workerContext) {
    let request = originalRequest;
    const handlerIterator = executeRequest(request);
    let data = {};
    let isFailOpen = false;
    const next = /* @__PURE__ */ __name2(async (input, init) => {
      if (input !== void 0) {
        let url = input;
        if (typeof input === "string") {
          url = new URL(input, request.url).toString();
        }
        request = new Request(url, init);
      }
      const result = handlerIterator.next();
      if (result.done === false) {
        const { handler, params, path } = result.value;
        const context = {
          request: new Request(request.clone()),
          functionPath: path,
          next,
          params,
          get data() {
            return data;
          },
          set data(value) {
            if (typeof value !== "object" || value === null) {
              throw new Error("context.data must be an object");
            }
            data = value;
          },
          env,
          waitUntil: workerContext.waitUntil.bind(workerContext),
          passThroughOnException: /* @__PURE__ */ __name2(() => {
            isFailOpen = true;
          }, "passThroughOnException")
        };
        const response = await handler(context);
        if (!(response instanceof Response)) {
          throw new Error("Your Pages function should return a Response");
        }
        return cloneResponse(response);
      } else if ("ASSETS") {
        const response = await env["ASSETS"].fetch(request);
        return cloneResponse(response);
      } else {
        const response = await fetch(request);
        return cloneResponse(response);
      }
    }, "next");
    try {
      return await next();
    } catch (error) {
      if (isFailOpen) {
        const response = await env["ASSETS"].fetch(request);
        return cloneResponse(response);
      }
      throw error;
    }
  }
};
var cloneResponse = /* @__PURE__ */ __name2((response) => (
  // https://fetch.spec.whatwg.org/#null-body-status
  new Response(
    [101, 204, 205, 304].includes(response.status) ? null : response.body,
    response
  )
), "cloneResponse");
var drainBody = /* @__PURE__ */ __name2(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
__name2(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name2(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = pages_template_worker_default;
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
__name2(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
__name2(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");
__name2(__facade_invoke__, "__facade_invoke__");
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  static {
    __name(this, "___Facade_ScheduledController__");
  }
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name2(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name2(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name2(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
__name2(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name2((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name2((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
__name2(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;

// ../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/pages-dev-util.ts
function isRoutingRuleMatch(pathname, routingRule) {
  if (!pathname) {
    throw new Error("Pathname is undefined.");
  }
  if (!routingRule) {
    throw new Error("Routing rule is undefined.");
  }
  const ruleRegExp = transformRoutingRuleToRegExp(routingRule);
  return pathname.match(ruleRegExp) !== null;
}
__name(isRoutingRuleMatch, "isRoutingRuleMatch");
function transformRoutingRuleToRegExp(rule) {
  let transformedRule;
  if (rule === "/" || rule === "/*") {
    transformedRule = rule;
  } else if (rule.endsWith("/*")) {
    transformedRule = `${rule.substring(0, rule.length - 2)}(/*)?`;
  } else if (rule.endsWith("/")) {
    transformedRule = `${rule.substring(0, rule.length - 1)}(/)?`;
  } else if (rule.endsWith("*")) {
    transformedRule = rule;
  } else {
    transformedRule = `${rule}(/)?`;
  }
  transformedRule = `^${transformedRule.replaceAll(/\./g, "\\.").replaceAll(/\*/g, ".*")}$`;
  return new RegExp(transformedRule);
}
__name(transformRoutingRuleToRegExp, "transformRoutingRuleToRegExp");

// .wrangler/tmp/pages-wsD3FB/tm5w3fsxc8a.js
var define_ROUTES_default = {
  version: 1,
  include: [
    "/api/*",
    "/widget/*"
  ],
  exclude: [
    "/*.html",
    "/favicon.ico"
  ]
};
var routes2 = define_ROUTES_default;
var pages_dev_pipeline_default = {
  fetch(request, env, context) {
    const { pathname } = new URL(request.url);
    for (const exclude of routes2.exclude) {
      if (isRoutingRuleMatch(pathname, exclude)) {
        return env.ASSETS.fetch(request);
      }
    }
    for (const include of routes2.include) {
      if (isRoutingRuleMatch(pathname, include)) {
        const workerAsHandler = middleware_loader_entry_default;
        if (workerAsHandler.fetch === void 0) {
          throw new TypeError("Entry point missing `fetch` handler");
        }
        return workerAsHandler.fetch(request, env, context);
      }
    }
    return env.ASSETS.fetch(request);
  }
};

// ../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody2 = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default2 = drainBody2;

// ../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError2(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError2(e.cause)
  };
}
__name(reduceError2, "reduceError");
var jsonError2 = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError2(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default2 = jsonError2;

// .wrangler/tmp/bundle-Y9ykpG/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__2 = [
  middleware_ensure_req_body_drained_default2,
  middleware_miniflare3_json_error_default2
];
var middleware_insertion_facade_default2 = pages_dev_pipeline_default;

// ../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__2 = [];
function __facade_register__2(...args) {
  __facade_middleware__2.push(...args.flat());
}
__name(__facade_register__2, "__facade_register__");
function __facade_invokeChain__2(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__2(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__2, "__facade_invokeChain__");
function __facade_invoke__2(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__2(request, env, ctx, dispatch, [
    ...__facade_middleware__2,
    finalMiddleware
  ]);
}
__name(__facade_invoke__2, "__facade_invoke__");

// .wrangler/tmp/bundle-Y9ykpG/middleware-loader.entry.ts
var __Facade_ScheduledController__2 = class ___Facade_ScheduledController__2 {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__2)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler2(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__2 === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__2.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__2) {
    __facade_register__2(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__2(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__2(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler2, "wrapExportedHandler");
function wrapWorkerEntrypoint2(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__2 === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__2.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__2) {
    __facade_register__2(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__2(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__2(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint2, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY2;
if (typeof middleware_insertion_facade_default2 === "object") {
  WRAPPED_ENTRY2 = wrapExportedHandler2(middleware_insertion_facade_default2);
} else if (typeof middleware_insertion_facade_default2 === "function") {
  WRAPPED_ENTRY2 = wrapWorkerEntrypoint2(middleware_insertion_facade_default2);
}
var middleware_loader_entry_default2 = WRAPPED_ENTRY2;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__2 as __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default2 as default
};
//# sourceMappingURL=tm5w3fsxc8a.js.map
