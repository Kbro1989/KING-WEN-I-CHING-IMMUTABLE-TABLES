/**
 * King Wen 64 Sovereign Engine — King Wen Link Acoustic Protocol
 *
 * Routes:
 *   GET/POST /api/kingwen-link?hex=1&phase=0
 *     → acoustic carrier packet for the resolved 9-bit state
 *
 *   GET/POST /api/kingwen-link/decode?address=0..511
 *     → structured state packet: hexagram/phase/yao/porosity/vector placeholder
 *
 *   POST /api/kingwen-link/decode
 *     body: { address: number } | { hexagram_id: number, phase_id: number }
 *
 * The acoustic layer is a physical encoding of the same 9-bit truth the
 * King Wen engine already computes. The decoder route exists so downstream
 * consumers (OpenJarvis consult tool, Megatron pipeline, agents) can receive
 * structured JSON instead of raw sound.
 */
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const pathname = url.pathname.replace(/\/$/, '');

  // Normalize inputs
  let hexId = parseInt(url.searchParams.get('hex') || '1', 10);
  let phaseId = parseInt(url.searchParams.get('phase') || '0', 10);
  let address = url.searchParams.get('address');

  if (request.method === 'POST') {
    try {
      const body = await request.json();
      if (body.address != null) address = String(body.address);
      if (body.hexagram_id) hexId = parseInt(body.hexagram_id, 10);
      if (body.phase_id) phaseId = parseInt(body.phase_id, 10);
    } catch (e) {
      // Fallback to query params
    }
  }

  // If address provided, resolve to hex/phase
  if (address != null && address !== '') {
    const addr = Math.max(0, Math.min(511, parseInt(address, 10)));
    hexId = Math.floor(addr / 8) + 1;   // 1..64
    phaseId = addr % 8;                  // 0..7
  }

  hexId = Math.max(1, Math.min(64, hexId));
  phaseId = Math.max(0, Math.min(7, phaseId));

  // Load topology once per request
  let topo = { sectors: [] };
  try {
    const assetReq = new Request(new URL('/DATASETS/kingwen_sovereign_world_topology.json', request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);
    if (assetRes.ok) topo = await assetRes.json();
  } catch (e) {
    // Proceed with empty topology — decoder still returns structural envelope
  }

  const sector = (topo.sectors || []).find(s => s.hexagram_id === hexId) || {};
  const vhdlAddr = (hexId - 1) * 8 + phaseId;
  const pellets = sector.yao_pellets || [];

  const carrierFreqs = pellets.map(p => p.frequency_hz || 146.0);
  const wavepacketHash = pellets.map(p => `${p.line_position}:${p.ternary_state}:${p.frequency_hz}`).join('|');

  // State packet returned by both acoustic and decode routes.
  // emotional_vector is a placeholder here; OpenJarvis consult tool
  // enriches it with the real 5-axis vector from collapse_full_128().
  const statePacket = {
    protocol: 'King Wen Link Acoustic Peer-to-Peer Protocol v1.0',
    hexagram_id: hexId,
    phase_id: phaseId,
    phase_temporal: phaseId === 0 ? 'past' : phaseId === 1 ? 'present' : 'future',
    vhdl_resolved_address_9bit: vhdlAddr,
    hexagram_name: sector.hexagram_name || 'Heaven',
    binary_pattern: sector.binary || '111111',
    ternary_state: sector.ternary || '000000',
    category: sector.category || 'sovereign',
    action: sector.action || 'unbound',
    yao_pellets: pellets.map(p => ({
      line_position: p.line_position,
      ternary_state: p.ternary_state,
      waveform: p.waveform,
      frequency_hz: p.frequency_hz,
      energy_intensity: p.energy_intensity
    })),
    emotional_vector: {
      voiceWeight: 0.0,
      coherence: 0.0,
      chaos: 0.0,
      whimsy: 0.0,
      darkTone: 0.0,
      porosity: sector.quantum_physics?.porosity_level ?? 0.0,
      _note: 'enrich_via_openjarvis_consult_tool'
    },
    quantum_physics: sector.quantum_physics || {},
    acoustic_carriers: {
      yao_line_frequencies_hz: carrierFreqs,
      wavepacket_signature: wavepacketHash,
      fundamental_freq_hz: sector.quantum_physics?.fundamental_frequency_hz || 108.0,
      vortex_tension: sector.quantum_physics?.vortex_tension || 0.5
    },
    peer_handshake: {
      status: 'SYNCHRONIZED',
      consensus_mode: 'UNBOUND_SUPERPOSITION',
      timestamp: new Date().toISOString()
    }
  };

  // Decode route: structured JSON for AI consumers
  if (pathname.endsWith('/decode')) {
    return Response.json(statePacket, {
      headers: {
        'X-KingWenLink-Protocol': 'v1.0-decode',
        'Content-Type': 'application/json; charset=utf-8'
      }
    });
  }

  // Default acoustic route: carrier packet only
  return Response.json(statePacket, {
    headers: {
      'X-KingWenLink-Protocol': 'v1.0-acoustic-wavepacket',
      'Content-Type': 'application/json; charset=utf-8'
    }
  });
}
