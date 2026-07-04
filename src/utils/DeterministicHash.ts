// SHA256-based deterministic selection — no Math.random()

export async function deterministicHash(input: string): Promise<Uint8Array> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  return new Uint8Array(await crypto.subtle.digest('SHA-256', data));
}

export async function deterministicIndex(
  input: string,
  maxExclusive: number
): Promise<number> {
  const hash = await deterministicHash(input);
  const view = new DataView(hash.buffer);
  const int = view.getUint32(0);
  return int % maxExclusive;
}

export async function deterministicHexagramSelect(
  tick: number,
  sessionId: string,
  previousHex: number,
  selector: string
): Promise<number> {
  const input = `${tick}:${sessionId}:${previousHex}:${selector}`;
  return (await deterministicIndex(input, 64)) + 1;
}
