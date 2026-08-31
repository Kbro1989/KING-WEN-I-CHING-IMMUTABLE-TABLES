/**
 * King Wen 64 Sovereign Engine — /api/jkd/:id Endpoint
 * Serves JKD Megatron Wavepacket text passages, 5-axis emotion vectors,
 * and Hamiltonian energy targets for hexagram :id.
 */
export async function onRequestGet(context) {
  const { request, params, env } = context;
  const url = new URL(request.url);
  const hexId = parseInt(params.id, 10);

  if (isNaN(hexId) || hexId < 1 || hexId > 64) {
    return Response.json(
      { error: 'Invalid hexagram ID. Must be between 1 and 64.', status: 400 },
      { status: 400 }
    );
  }

  try {
    const assetUrl = new URL('/DATASETS/kingwen_sovereign_world_topology.json', url.origin);
    const assetRes = await env.ASSETS ? env.ASSETS.fetch(assetUrl) : await fetch(assetUrl);

    if (!assetRes.ok) {
      return Response.json({ error: 'World topology manifest not found' }, { status: 404 });
    }

    const topo = await assetRes.json();
    const sector = (topo.sectors || []).find(s => s.hexagram_id === hexId);

    if (!sector) {
      return Response.json({ error: `Hexagram #${hexId} not found` }, { status: 404 });
    }

    const passages = sector.jkd_passages || [];

    return Response.json(
      {
        engine: 'King Wen x JKD Megatron Wavepacket Speech Engine',
        hexagram_id: hexId,
        hexagram_name: sector.hexagram_name,
        total_passages: passages.length,
        passages: passages
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
