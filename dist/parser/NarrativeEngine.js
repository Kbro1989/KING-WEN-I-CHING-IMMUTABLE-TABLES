export class NarrativeEngine {
    temporalReflections;
    emotionalWeights;
    constructor(reflectionsJson, weightsJson) {
        this.temporalReflections = new Map();
        this.emotionalWeights = new Map();
        for (const [id, data] of Object.entries(reflectionsJson)) {
            this.temporalReflections.set(parseInt(id), data);
        }
        for (const [id, data] of Object.entries(weightsJson)) {
            this.emotionalWeights.set(parseInt(id), data);
        }
    }
    generateReflections(hexagram, temporal, emotional) {
        const reflections = this.temporalReflections.get(hexagram.id);
        if (!reflections)
            throw new Error(`No reflections for hexagram ${hexagram.id}`);
        const weights = this.emotionalWeights.get(hexagram.id);
        const past = this.modulateVoice(reflections.past, 'past', temporal, emotional, weights);
        const present = this.modulateVoice(reflections.present, 'present', temporal, emotional, weights);
        const future = this.modulateVoice(reflections.future, 'future', temporal, emotional, weights);
        const weave = this.weaveUnified(past, present, future, temporal);
        return { past, present, future, unified_weave: weave };
    }
    modulateVoice(baseText, phaseName, temporal, emotional, weights) {
        return baseText;
    }
    weaveUnified(past, present, future, temporal) {
        const dominant = ['past', 'present', 'future'][temporal.dominantPhase];
        return `[${dominant.toUpperCase()} VOICE LEADS]\n\n${present}\n\n[Echoes:]\nFrom what was: ${past.slice(0, 120)}...\nFrom what could be: ${future.slice(0, 120)}...`;
    }
}
