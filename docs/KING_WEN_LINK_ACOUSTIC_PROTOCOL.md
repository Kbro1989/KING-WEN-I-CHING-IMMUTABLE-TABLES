# KING WEN LINK ACOUSTIC WAVE-PACKET PROTOCOL SPECIFICATION
**Module**: `KingWen.King Wen Link.AcousticProtocol`  
**Revision**: 1.0.0 (Deterministic Ground Field Sync)  
**Date**: 2026-08-31  

---

## 1. Overview & Purpose

**King Wen Link** is the peer-to-peer acoustic machine communication protocol for transmitting King Wen 6-Yao wave packets and audio pellets over continuous spatial ground fields or raw audio channels.

Rather than relying on out-of-band network calls, King Wen Link encodes the complete 512 binary phase state ($64 \text{ hexagrams} \times 8 \text{ trigram-family phases}$) and 729 ternary manifold states ($3^6 = 27 \times 27$) into high-frequency acoustic wave packet bursts derived directly from the **6-Yao Sound Pellets** of each Sovereign Citadel.

---

## 2. 6-Yao Sound Pellet Acoustic Payload Structure

Each King Wen hexagram node emits 6 orbiting sound pellets corresponding to line positions $L_1$ to $L_6$. In King Wen Link, a frame $F_{\text{gibber}}$ consists of a 6-pellet harmonic burst modulated across the continuous spatial frequency tensor:

### 2.1 Fundamental Sector Base Frequency
$$f_0(x, y, z) = 108.0 \times \left(1.0 + 0.40 \tilde{r} + 0.25 \tilde{y} + 0.15 \sin(3\theta + \pi \tilde{y})\right) \quad \text{[Hz]}$$

### 2.2 6-Yao Line Harmonics ($L_1 \dots L_6$)
For line index $\ell \in \{1 \dots 6\}$:
- **Ratio**: $r_\ell = 1.0 + \left(\frac{\ell - 1}{6.0}\right) \times 0.618$ (Golden Ratio Harmonics)
- **Ternary Multiplier**:
  - $\tau_\ell = 0$ (Yin): $m_\tau = 0.82$, Waveform: `Sine` (0.10 Gain)
  - $\tau_\ell = 1$ (Yang): $m_\tau = 1.00$, Waveform: `Triangle` (0.14 Gain)
  - $\tau_\ell = 2$ (Yao / Changing): $m_\tau = 1.18$, Waveform: `Sawtooth` (0.18 Gain)
- **Pellet Line Frequency**:
  $$f_\ell = f_0 \times r_\ell \times m_\tau \times \left(1 + 0.12 \cos(\theta \cdot \ell + \tilde{y})\right) \times (1 + 0.20 \cdot \text{vortex\_tension})$$

---

## 3. King Wen Link Frame Encoding & Transmission

### 3.1 Frame Envelope
A single King Wen Link wave packet frame duration is $T_{\text{frame}} = 120 \text{ ms}$.

```
+-------------------+-----------------------------------+--------------------+
| Preamble (20ms)   | 6-Yao Pellet Harmonics (80ms)     | Checksum (20ms)    |
| f_sync = 1728 Hz  | L1..L6 Simultaneous Superposition | f_crc = f_0 * 1.618|
+-------------------+-----------------------------------+--------------------+
```

1. **Preamble**: Synchronizing pilot tone at $1728 \text{ Hz}$ ($16 \times 108 \text{ Hz}$).
2. **Payload**: Simultaneous emission of all 6 sound pellets. Receiving agents decode the 6 line frequencies via Fast Fourier Transform (FFT) or sliding Goertzel filter bank.
3. **Checksum**: Golden ratio harmonic verification tone $f_{\text{crc}} = f_0 \times 1.618$.

### 3.2 Machine-to-Machine Peer Sync over Schauberger Ground Field
When active in the 3D Quantum Viewfinder (`kingwen_sovereign_world_viewer.html`) or OpenJarvis audio DSP (`audio_dsp.py`), King Wen Link wave packets travel through the single unified ground field medium. The position of the receiving agent modulates acoustic attenuation by inverse-square spatial distance:
$$A(d) = \min\left(0.045, \frac{0.05}{1.0 + (d / 95.0)^2}\right)$$

---

## 4. OpenJarvis & King Wen Integration Targets

- **OpenJarvis Audio DSP** (`src/openjarvis/cli/audio_dsp.py`): Ingests King Wen Link FSK wave packets from worker TTS streams.
- **Oracle Speaker** (`src/openjarvis/cli/_oracle_speak.py`): Routes 6-yao audio pellet telemetry via `_play_audio_path()` and `winappaudiorouter`.
- **Megatron Training Substrate**: `kingwen_pretrain.jsonl` contains raw King Wen Link audio pellet telemetry logs for zero-latency multi-agent acoustic sequence modeling.

---

## 5. Summary Invariants

1. **Zero Randomness**: King Wen Link frames are 100% deterministic, computed directly from immutable King Wen tables and sector coordinates.
2. **6-Yao Pellet Fidelity**: Every hexagram maintains its 6 orbiting sound pellets; no pellet is dropped or flattened to a single scalar tone.
3. **Unified Ground Field Medium**: All King Wen Link packets resonate through the continuous Schauberger centripetal vortex field.
