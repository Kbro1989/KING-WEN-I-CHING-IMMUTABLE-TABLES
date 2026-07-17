export class EmotionalParser {
    parse(query) {
        const base = {
            chaos: 0.5,
            whimsy: 0.5,
            darkTone: 0.5,
            coherence: 0.5,
            voiceWeight: 0.5,
        };
        if (query.user_context) {
            this.applyContext(base, query.user_context);
        }
        if (query.emotional_input !== undefined) {
            const normalized = query.emotional_input / 100;
            base.whimsy = normalized;
            base.darkTone = 1 - normalized;
        }
        return base;
    }
    /**
     * Extract the 3-dimensional emotional tuple for the POG3 substrate.
     * Maps 5-dim EmotionalVector → [chaos, whimsy, darkTone] for IntentVector.
     */
    toIntentEmotional(vec) {
        return [vec.chaos, vec.whimsy, vec.darkTone];
    }
    applyContext(vec, ctx) {
        if (ctx.fatigue !== undefined) {
            vec.chaos = Math.min(1, vec.chaos + (ctx.fatigue / 100) * 0.3);
            vec.coherence = Math.max(0, vec.coherence - (ctx.fatigue / 100) * 0.2);
        }
    }
}
