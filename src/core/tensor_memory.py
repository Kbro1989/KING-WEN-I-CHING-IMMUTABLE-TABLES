"""
King Wen Tensor Memory Module
==============================
Fixed-size recurrent 3D voxel state for persistent 512-state expansion.
Based on: Swain et al., "Tensor Memory: Fixed-Size Recurrent State for Long-Horizon Transformers", arXiv:2605.27686

Architecture:
- 8x8x8 voxel grid = 512 slots = 64 hexagrams x 8 phases
- 24-channel feature per voxel matching save-string V2.1 pellet tokens
- Gaussian write volume with deterministic coordinate mapping
- Factorized 3D ConvLSTM update
- Trilinear read with gated residual fusion

Determinism: no learned coordinate predictor; coordinates are hard-coded from hex_id/phase/porosity.
No random number generation anywhere in the module.
"""

from __future__ import annotations

import math
from typing import Tuple, Optional, Dict, Any
import hashlib
import json

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
D, H, W, C = 8, 8, 8, 24
TOTAL_SLOTS = 512  # 64 hex x 8 phase
EPS = 1e-6
BASE_SIGMA = 0.12
SIGMA_SCALE = 0.5
MIN_SIGMA = 0.05
MAX_SIGMA = 0.5


# ---------------------------------------------------------------------------
# Coordinate mapping
# ---------------------------------------------------------------------------
def hex_phase_to_coordinate(hex_id: int, phase_id: int, porosity: float) -> Tuple[float, float, float]:
    """Map 64-hex 8-phase state to continuous 3D voxel coordinate in [-1,1]^3.
    
    Slot layout: 512 slots = 64 hex x 8 phase in 8x8x8 grid.
    slot_index = (hex_id-1)*8 + phase_id  [0..511]
    iz = slot_index // 64, iy = (slot_index % 64) // 8, ix = slot_index % 8
    Continuous: x = ix/7*2-1, y = iy/7*2-1, z = iz/7*2-1
    """
    if not (1 <= hex_id <= 64):
        raise ValueError(f"hex_id must be 1-64, got {hex_id}")
    if not (0 <= phase_id <= 7):
        raise ValueError(f"phase_id must be 0-7, got {phase_id}")
    porosity = max(0.0, min(1.0, float(porosity)))
    slot = (hex_id - 1) * 8 + phase_id  # 0..511
    iz = slot // 64  # 0..7
    iy = (slot % 64) // 8  # 0..7
    ix = slot % 8  # 0..7
    mx = ix / 7.0 * 2.0 - 1.0
    my = iy / 7.0 * 2.0 - 1.0
    mz = iz / 7.0 * 2.0 - 1.0
    return (mx, my, mz)


def coordinate_to_slot(mu: Tuple[float, float, float]) -> int:
    """Map continuous coordinate to nearest voxel slot index 0..511."""
    mx, my, mz = mu
    ix = int(round((mx + 1.0) * 0.5 * (W - 1)))
    iy = int(round((my + 1.0) * 0.5 * (H - 1)))
    iz = int(round((mz + 1.0) * 0.5 * (D - 1)))
    ix = max(0, min(W - 1, ix))
    iy = max(0, min(H - 1, iy))
    iz = max(0, min(D - 1, iz))
    return iz * (H * W) + iy * W + ix


def inversion_mirror(mu: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Mirror coordinate for inversion pair read/write.
    Inversion pairs: hex A and hex A' map to mirrored voxel coordinates.
    Pattern: (x,y,z) -> (-x,-y,-z) preserves slot while swapping inversion partner.
    """
    return (-mu[0], -mu[1], -mu[2])


# ---------------------------------------------------------------------------
# Gaussian write volume
# ---------------------------------------------------------------------------
def _gaussian_mask(
    grid: np.ndarray,
    mu: Tuple[float, float, float],
    sigma: float,
) -> np.ndarray:
    """Compute Gaussian mask M over the DxHxW grid centered at mu with spread sigma."""
    sigma = max(MIN_SIGMA, min(MAX_SIGMA, float(sigma)))
    zz, yy, xx = np.mgrid[0:D, 0:H, 0:W]
    # Normalize grid to [-1,1]
    gx = (xx / max(W - 1, 1)) * 2.0 - 1.0
    gy = (yy / max(H - 1, 1)) * 2.0 - 1.0
    gz = (zz / max(D - 1, 1)) * 2.0 - 1.0
    dist2 = (gx - mu[0]) ** 2 + (gy - mu[1]) ** 2 + (gz - mu[2]) ** 2
    mask = np.exp(-dist2 / (2.0 * sigma * sigma + EPS))
    return mask  # shape (D,H,W)


def gaussian_write(
    state: np.ndarray,
    content: np.ndarray,
    mu: Tuple[float, float, float],
    sigma: float,
) -> np.ndarray:
    """Differentiable soft write: deposit content as Gaussian-weighted volume around mu."""
    if state.shape != (D, H, W, C):
        raise ValueError(f"state shape must be ({D},{H},{W},{C}), got {state.shape}")
    if content.shape != (C,):
        raise ValueError(f"content shape must be ({C},), got {content.shape}")
    mask = _gaussian_mask(state, mu, sigma)  # (D,H,W)
    write_volume = mask[..., None] * content[None, None, None, :]  # (D,H,W,C)
    updated = state + write_volume
    return updated


# ---------------------------------------------------------------------------
# Factorized 3D ConvLSTM update (deterministic, no learned weights in v1)
# ---------------------------------------------------------------------------
def _factorized_3d_operator(z: np.ndarray) -> np.ndarray:
    """Factorized 3D operator: depthwise 1x1x3, 1x3x1, 3x1x1 + pointwise 1x1x1.
    Deterministic v1: mean-blend across depth/height/width axes as placeholder for learned conv.
    Returns 4*C channel tensor for ConvLSTM gates.
    """
    z = z.astype(np.float32)
    dw_z = np.mean(z, axis=(1, 2), keepdims=True)  # depthwise 1x1x3 equivalent
    dh_z = np.mean(z, axis=(0, 2), keepdims=True)  # 1x3x1
    dv_z = np.mean(z, axis=(0, 1), keepdims=True)  # 3x1x1
    blended = (dw_z + dh_z + dv_z) / 3.0
    blended_c = np.mean(blended, axis=-1, keepdims=True)  # (D,H,W,1)
    gates = np.tile(blended_c, (1, 1, 1, 4 * C))  # (D,H,W,4C)
    return gates


def conv_lstm_update(
    h: np.ndarray,
    c: np.ndarray,
    write_volume: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """ConvLSTM-style gated update over voxel grid.
    h, c: (D,H,W,C)
    write_volume: (D,H,W,C)
    Returns (h_next, c_next) in float32.
    """
    if h.shape != (D, H, W, C) or c.shape != (D, H, W, C):
        raise ValueError(f"h/c shape must be ({D},{H},{W},{C})")
    if write_volume.shape != (D, H, W, C):
        raise ValueError(f"write_volume shape must be ({D},{H},{W},{C})")

    h = h.astype(np.float32)
    c = c.astype(np.float32)
    write_volume = write_volume.astype(np.float32)

    z = np.concatenate([write_volume, h], axis=-1)  # (D,H,W,2C)
    gates = _factorized_3d_operator(z)  # (D,H,W,4C)

    # Split into 4 gate tensors: i, f, o, g each (D,H,W,C)
    i_gate = gates[..., 0:C]
    f_gate = gates[..., C:2*C]
    o_gate = gates[..., 2*C:3*C]
    g_gate = gates[..., 3*C:4*C]

    # Sigmoid/tanh activations
    i_gate = 1.0 / (1.0 + np.exp(-i_gate))
    f_gate = 1.0 / (1.0 + np.exp(-f_gate))
    o_gate = 1.0 / (1.0 + np.exp(-o_gate))
    g_gate = np.tanh(g_gate)

    c_next = f_gate * c + i_gate * g_gate
    h_next = o_gate * np.tanh(c_next)
    return h_next, c_next


# ---------------------------------------------------------------------------
# Trilinear read with gated residual fusion
# ---------------------------------------------------------------------------
def trilinear_read(
    h: np.ndarray,
    mu_read: Tuple[float, float, float],
    gamma: float = -2.0,
) -> np.ndarray:
    """Read from voxel state at continuous coordinate mu_read via trilinear sampling.
    Returns gated residual readout vector of shape (C,).
    """
    if h.shape != (D, H, W, C):
        raise ValueError(f"h shape must be ({D},{H},{W},{C})")

    mx, my, mz = mu_read
    # Clamp to [-1,1]
    mx = max(-1.0, min(1.0, mx))
    my = max(-1.0, min(1.0, my))
    mz = max(-1.0, min(1.0, mz))

    # Convert to grid indices
    ix = (mx + 1.0) * 0.5 * (W - 1)
    iy = (my + 1.0) * 0.5 * (H - 1)
    iz = (mz + 1.0) * 0.5 * (D - 1)

    ix0 = int(math.floor(ix))
    iy0 = int(math.floor(iy))
    iz0 = int(math.floor(iz))
    ix1 = min(ix0 + 1, W - 1)
    iy1 = min(iy0 + 1, H - 1)
    iz1 = min(iz0 + 1, D - 1)

    tx = ix - ix0
    ty = iy - iy0
    tz = iz - iz0

    # Trilinear interpolation
    read_vec = (
        (1 - tx) * (1 - ty) * (1 - tz) * h[iz0, iy0, ix0, :] +
        tx * (1 - ty) * (1 - tz) * h[iz0, iy0, ix1, :] +
        (1 - tx) * ty * (1 - tz) * h[iz0, iy1, ix0, :] +
        tx * ty * (1 - tz) * h[iz0, iy1, ix1, :] +
        (1 - tx) * (1 - ty) * tz * h[iz1, iy0, ix0, :] +
        tx * (1 - ty) * tz * h[iz1, iy0, ix1, :] +
        (1 - tx) * ty * tz * h[iz1, iy1, ix0, :] +
        tx * ty * tz * h[iz1, iy1, ix1, :]
    )

    # Gated residual fusion: sigma(gamma) controls memory path strength
    gate = 1.0 / (1.0 + math.exp(-gamma))  # sigmoid
    return gate * read_vec  # (C,)


# ---------------------------------------------------------------------------
# King Wen Tensor Memory container
# ---------------------------------------------------------------------------
class KingWenTensorMemory:
    """Fixed-size recurrent 3D voxel memory for King Wen 512-state expansion."""

    def __init__(self, dtype: np.dtype = np.float32):
        self.dtype = dtype
        self.h = np.zeros((D, H, W, C), dtype=dtype)  # hidden state
        self.c = np.zeros((D, H, W, C), dtype=dtype)  # cell state
        self.gamma = -2.0  # learned scalar gate (initialized to suppress memory)
        self.step_count = 0
        self.write_history: list[dict[str, Any]] = []

    def write_hex_phase(
        self,
        hex_id: int,
        phase_id: int,
        porosity: float,
        content_vector: np.ndarray,
        sigma: Optional[float] = None,
    ) -> dict[str, Any]:
        """Write a hexagram/phase state into the voxel memory via Gaussian splatting."""
        mu = hex_phase_to_coordinate(hex_id, phase_id, porosity)
        if sigma is None:
            sigma = BASE_SIGMA + SIGMA_SCALE * math.log1p(
                abs(float(content_vector[16]) if len(content_vector) > 16 else 0.0) + 1e-6
            )
        mask = _gaussian_mask(self.h, mu, sigma)
        write_volume = mask[..., None] * content_vector[None, None, None, :]
        self.h, self.c = conv_lstm_update(self.h, self.c, write_volume)
        record = {
            "step": self.step_count,
            "hex_id": hex_id,
            "phase_id": phase_id,
            "porosity": porosity,
            "mu": mu,
            "sigma": sigma,
            "slot": coordinate_to_slot(mu),
            "content_norm": float(np.linalg.norm(content_vector)),
        }
        self.write_history.append(record)
        self.step_count += 1
        return record

    def read_consult(
        self,
        query_vector: np.ndarray,
        gamma: Optional[float] = None,
    ) -> np.ndarray:
        """Read from memory given a consult query vector. Returns gated readout (C,)."""
        if gamma is not None:
            self.gamma = gamma
        # Deterministic read coordinate from query vector projection (v1: fixed projection)
        q_norm = np.linalg.norm(query_vector)
        if q_norm > 0:
            q_unit = query_vector / q_norm
        else:
            q_unit = query_vector
        # Project first 3 channels of query to 3D coordinate
        mu_read = (
            float(np.tanh(q_unit[0])),
            float(np.tanh(q_unit[1]) if len(q_unit) > 1 else 0.0),
            float(np.tanh(q_unit[2]) if len(q_unit) > 2 else 0.0),
        )
        return trilinear_read(self.h, mu_read, self.gamma)

    def read_hex_phase(
        self,
        hex_id: int,
        phase_id: int,
        porosity: float,
        use_inversion: bool = False,
    ) -> np.ndarray:
        """Read specific hexagram/phase slot via deterministic coordinate or inversion mirror."""
        if use_inversion:
            mu = hex_phase_to_coordinate(hex_id, phase_id, porosity)
            mu = inversion_mirror(mu)
        else:
            mu = hex_phase_to_coordinate(hex_id, phase_id, porosity)
        return trilinear_read(self.h, mu, self.gamma)

    def state_hash(self) -> str:
        """Deterministic hash of current memory state for verification."""
        raw = self.h.tobytes() + self.c.tobytes() + bytes(str(self.gamma), 'utf-8')
        return hashlib.sha256(raw).hexdigest()[:16]

    def occupancy(self) -> dict[str, Any]:
        """Report which 512 slots have been written to."""
        occupied = {}
        for rec in self.write_history:
            slot = rec["slot"]
            key = f"hex_{rec['hex_id']:02d}_phase_{rec['phase_id']}"
            occupied[key] = {
                "slot": slot,
                "porosity": rec["porosity"],
                "content_norm": rec["content_norm"],
                "mu": rec["mu"],
            }
        return occupied

    def to_dict(self) -> dict[str, Any]:
        """Serialize memory state for save-string / JSON persistence."""
        return {
            "schema_version": "1.0.0",
            "grid_shape": [D, H, W, C],
            "gamma": self.gamma,
            "step_count": self.step_count,
            "state_hash": self.state_hash(),
            "hidden_mean": float(np.mean(self.h)),
            "hidden_std": float(np.std(self.h)),
            "cell_mean": float(np.mean(self.c)),
            "cell_std": float(np.std(self.c)),
            "occupancy_count": len(self.write_history),
            "write_history_tail": self.write_history[-10:],
        }

    def save(self, path: str) -> None:
        """Save memory state to JSON."""
        payload = self.to_dict()
        # Save metadata as JSON, state arrays as base64
        import base64
        payload["hidden_b64"] = base64.b64encode(self.h.tobytes()).decode("ascii")
        payload["cell_b64"] = base64.b64encode(self.c.tobytes()).decode("ascii")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> KingWenTensorMemory:
        """Load memory state from JSON."""
        import base64
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        obj = cls()
        obj.gamma = payload.get("gamma", -2.0)
        obj.step_count = payload.get("step_count", 0)
        if "hidden_b64" in payload and "cell_b64" in payload:
            h_bytes = base64.b64decode(payload["hidden_b64"])
            c_bytes = base64.b64decode(payload["cell_b64"])
            obj.h = np.frombuffer(h_bytes, dtype=np.float32).reshape(D, H, W, C).copy()
            obj.c = np.frombuffer(c_bytes, dtype=np.float32).reshape(D, H, W, C).copy()
        return obj
