/**
 * King Wen 64 Sovereign Engine — Cloudflare Edge Middleware
 * Handles CORS preflight, King Wen Link acoustic protocol headers, and request timing.
 */
export async function onRequest(context) {
  const { request, next } = context;

  // Handle CORS OPTIONS preflight request
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-KingWenLink-Protocol, X-KingWen-Phase',
        'Access-Control-Max-Age': '86400',
      },
    });
  }

  const startTime = Date.now();
  const response = await next();
  const durationMs = Date.now() - startTime;

  // Clone headers and add King Wen Engine Edge metadata
  const headers = new Headers(response.headers);
  headers.set('Access-Control-Allow-Origin', '*');
  headers.set('X-KingWen-Engine-Version', '3.2.0');
  headers.set('X-KingWen-Edge-Region', context.request.cf?.colo || 'UNKNOWN');
  headers.set('X-Response-Time-Ms', durationMs.toString());
  headers.set('X-KingWenLink-Protocol', 'v1.0-acoustic-wavepacket');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
