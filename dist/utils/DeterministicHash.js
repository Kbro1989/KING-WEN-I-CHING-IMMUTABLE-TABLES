// SHA256-based deterministic hashing & 5 coprime prime extractor — zero randomness
export async function deterministicHash(input) {
    const encoder = new TextEncoder();
    const data = encoder.encode(input);
    return new Uint8Array(await crypto.subtle.digest('SHA-256', data));
}
export async function deterministicHashHex(input) {
    const bytes = await deterministicHash(input);
    return Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
}
/**
 * Deterministic ASCII token sum matching Python _intent_to_vector in emotional_engine.py.
 */
export function computeTokenSum(tokens) {
    let sum = 0;
    for (const token of tokens) {
        for (let i = 0; i < token.length; i++) {
            sum += token.charCodeAt(i);
        }
    }
    return sum;
}
/**
 * 5 Coprime Prime Vector Perturbation: (97, 89, 83, 79, 73)
 * Exact match for Python _intent_to_vector coprime moduli extractor.
 */
export function extractCoprimePrimeVector(hashVal) {
    return {
        chaos: ((hashVal % 97) / 97.0) * 0.12,
        whimsy: ((Math.floor(hashVal / 7) % 89) / 89.0) * 0.12,
        darkTone: ((Math.floor(hashVal / 13) % 83) / 83.0) * 0.12,
        coherence: ((Math.floor(hashVal / 19) % 79) / 79.0) * 0.12,
        voiceWeight: ((Math.floor(hashVal / 23) % 73) / 73.0) * 0.12,
    };
}
export async function generateDeterministicInjectHash(sessionId, tick, queryText) {
    const input = `${tick}:${sessionId}:${queryText}`;
    return deterministicHashHex(input);
}
