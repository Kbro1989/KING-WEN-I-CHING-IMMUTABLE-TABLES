/**
 * King Wen 64 Sovereign Engine — /api/hexagram/:id Endpoint
 * Serves specific hexagram metadata, VHDL 9-bit resolver address, 
 * 6-yao sound pellet frequencies, JKD passages, and depth metrics.
 */
export async function onRequestGet(context) {
  const { request, params, env } = context;
  const hexId = parseInt(params.id, 10);

  if (isNaN(hexId) || hexId < 1 || hexId > 64) {
    return Response.json(
      { error: 'Invalid hexagram ID. Must be an integer between 1 and 64.', status: 400 },
      { status: 400 }
    );
  }

  try {
    const assetReq = new Request(new URL('/DATASETS/kingwen_sovereign_world_topology.json', request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);

    if (!assetRes.ok) {
      return Response.json({ error: 'World topology manifest not found', status: assetRes.status }, { status: 404 });
    }

    const topo = await assetRes.json();
    const sector = (topo.sectors || []).find(s => s.hexagram_id === hexId);

    if (!sector) {
      return Response.json({ error: `Hexagram #${hexId} sector not found` }, { status: 404 });
    }

    const binaryStr = sector.binary || '111111';
    const vhdlBaseAddr = (hexId - 1) * 8;

    return Response.json(
      {
        engine: 'King Wen 64 Sovereign Model Engine',
        version: '3.2.0',
        hexagram_id: hexId,
        vhdl_resolver: {
          base_address_9bit: vhdlBaseAddr,
          address_range_8_phases: [vhdlBaseAddr, vhdlBaseAddr + 7],
          binary_pattern: binaryStr
        },
        sector: sector
      },
      {
        headers: {
          'Cache-Control': 'public, max-age=3600, s-maxage=86400',
          'Content-Type': 'application/json; charset=utf-8'
        }
      }
    );
  } catch (err) {
    return Response.json({ error: 'Internal edge server error', message: err.message }, { status: 500 });
  }
}
