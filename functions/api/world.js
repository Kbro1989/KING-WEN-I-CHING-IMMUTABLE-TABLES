/**
 * King Wen 64 Sovereign Engine — /api/world Endpoint
 * Serves 64-sector macro-world topology, 60 pre-warmed 3D egg keyframes, 
 * pre-rendered 384-pellet audio WAV buffer, and depth point-cloud statistics.
 */
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  try {
    // Fetch static topology JSON from public asset root
    const assetUrl = new URL('/DATASETS/kingwen_sovereign_world_topology.json', url.origin);
    const assetRes = await env.ASSETS ? env.ASSETS.fetch(assetUrl) : await fetch(assetUrl);

    if (!assetRes.ok) {
      return Response.json(
        { error: 'World topology manifest not found', status: 404 },
        { status: 404 }
      );
    }

    const data = await assetRes.json();

    return Response.json(
      {
        engine: 'King Wen 64 Sovereign Model Engine',
        version: '3.2.0',
        cf_colo: request.cf?.colo || 'LOCAL',
        timestamp: new Date().toISOString(),
        topology: data
      },
      {
        headers: {
          'Cache-Control': 'public, max-age=3600, s-maxage=86400',
          'Content-Type': 'application/json; charset=utf-8'
        }
      }
    );
  } catch (err) {
    return Response.json(
      { error: 'Internal edge server error', message: err.message },
      { status: 500 }
    );
  }
}
