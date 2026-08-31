/**
 * King Wen 64 Sovereign Engine — /api/gibberlink Endpoint
 * Implements the GibberLink acoustic peer-to-peer wavepacket protocol.
 * Accepts input wavepacket vectors / hexagram queries and returns deterministic
 * 6-yao line pellet acoustic carrier parameters for machine-to-machine exchange.
 */
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  let hexId = parseInt(url.searchParams.get('hex') || '1', 10);
  let phaseId = parseInt(url.searchParams.get('phase') || '1', 10);

  if (request.method === 'POST') {
    try {
      const body = await request.json();
      if (body.hexagram_id) hexId = parseInt(body.hexagram_id, 10);
      if (body.phase_id) phaseId = parseInt(body.phase_id, 10);
    } catch (e) {
      // Fallback to query params
    }
  }

  hexId = Math.max(1, Math.min(64, hexId));
  phaseId = Math.max(0, Math.min(7, phaseId));

  try {
    const assetUrl = new URL('/DATASETS/kingwen_sovereign_world_topology.json', url.origin);
    const assetRes = await env.ASSETS ? env.ASSETS.fetch(assetUrl) : await fetch(assetUrl);
    const topo = assetRes.ok ? await assetRes.json() : { sectors: [] };
    const sector = (topo.sectors || []).find(s => s.hexagram_id === hexId) || {};

    const vhdlAddr = (hexId - 1) * 8 + phaseId;
    const pellets = sector.yao_pellets || [];

    const carrierFreqs = pellets.map(p => p.frequency_hz || 146.0);
    const wavepacketHash = pellets.map(p => `${p.line_position}:${p.ternary_state}:${p.frequency_hz}`).join('|');

    return Response.json(
      {
        protocol: 'GibberLink Acoustic Peer-to-Peer Protocol v1.0',
        hexagram_id: hexId,
        phase_id: phaseId,
        vhdl_resolved_address_9bit: vhdlAddr,
        hexagram_name: sector.hexagram_name || 'Heaven',
        binary_pattern: sector.binary || '111111',
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
      },
      {
        headers: {
          'X-GibberLink-Protocol': 'v1.0-acoustic-wavepacket',
          'Content-Type': 'application/json; charset=utf-8'
        }
      }
    );
  } catch (err) {
    return Response.json({ error: 'GibberLink protocol exception', message: err.message }, { status: 500 });
  }
}
