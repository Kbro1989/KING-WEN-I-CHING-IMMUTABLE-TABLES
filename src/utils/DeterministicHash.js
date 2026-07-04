export async function deterministicHash(input) {
  const data = new TextEncoder().encode(input);
  return new Uint8Array(await crypto.subtle.digest('SHA-256', data));
}

export async function deterministicIndex(input, maxExclusive) {
  const hash = await deterministicHash(input);
  const view = new DataView(hash.buffer, hash.byteOffset, hash.byteLength);
  const int = view.getUint32(0);
  return int % maxExclusive;
}

export async function deterministicHexagramSelect(tick, sessionId, previousHex, selector) {
  const input = `${tick}:${sessionId}:${previousHex}:${selector}`;
  return (await deterministicIndex(input, 64)) + 1;
}
