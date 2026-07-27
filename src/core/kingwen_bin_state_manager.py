#!/usr/bin/env python3
"""
kingwen_bin_state_manager.py — 8-Phase .bin State Manager
=========================================================
Manages 64-byte binary records for 64 hexagram sites.
Phase bits stored in reserved field at offset 60 (uint32, 0-7).
Backward compatible with 3-phase baseline records.

Author: POG3 Sovereign Stack
Location: KING-WEN-I-CHING-IMMUTABLE-TABLES/src/core/kingwen_bin_state_manager.py
"""

from __future__ import annotations

import struct
import os
import math
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# ═════════════════════════════════════════════════════════════════════════════
# BINARY RECORD FORMAT (64 bytes per site)
# ═════════════════════════════════════════════════════════════════════════════
# Offset 0-3:   king_wen_id (uint32)        — hexagram ID 1-64
# Offset 4-7:   chaos (float32)
# Offset 8-11:  whimsy (float32)
# Offset 12-15: dark_tone (float32)
# Offset 16-19: coherence (float32)
# Offset 20-23: voice_weight (float32)      — amplitude carrier
# Offset 24-27: porosity (float32)          — duty cycle / permeability
# Offset 28-31: vortex_tension (float32)    — Hamiltonian energy proxy
# Offset 32-35: superposition_fidelity (float32)
# Offset 36-39: arm_id (uint32)
# Offset 40-43: jkd_anchor_hash (uint32)    — FNV-1a hash
# Offset 44-47: action_hash (uint32)        — FNV-1a hash
# Offset 48-51: category_hash (uint32)      — FNV-1a hash
# Offset 52-55: coder_specialty_hash (uint32) — FNV-1a hash
# Offset 56-59: rs3_actionable_hash (uint32)  — FNV-1a hash
# Offset 60-63: phase_bits (uint32)         — v2.1: 8-phase encoding (0-7)
# ═════════════════════════════════════════════════════════════════════════════

BIN_RECORD_FORMAT = "<IfffffffffIIIIII"  # little-endian, 16 fields
BIN_RECORD_SIZE = struct.calcsize(BIN_RECORD_FORMAT)  # 64 bytes
assert BIN_RECORD_SIZE == 64, f"Record size must be 64 bytes, got {BIN_RECORD_SIZE}"

# Phase bit mapping (0-7)
PHASE_BITS = {
    'void': 0,
    'past': 1,
    'present': 2,
    'future': 3,
    'transition': 4,
    'resolution': 5,
    'dissolution': 6,
    'crystallization': 7,
}

BITS_TO_PHASE = {v: k for k, v in PHASE_BITS.items()}


# ═════════════════════════════════════════════════════════════════════════════
# FNV-1a 32-bit hash
# ═════════════════════════════════════════════════════════════════════════════

def fnv1a_32(data: bytes) -> int:
    """FNV-1a 32-bit hash for string token encoding."""
    hash_val = 0x811c9dc5
    for byte in data:
        hash_val ^= byte
        hash_val = (hash_val * 0x01000193) & 0xffffffff
    return hash_val


# ═════════════════════════════════════════════════════════════════════════════
# BIN RECORD DATACLASS
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class BinRecord:
    """64-byte binary record for a single hexagram site."""
    hex_id: int
    chaos: float
    whimsy: float
    dark_tone: float
    coherence: float
    voice_weight: float
    porosity: float
    vortex_tension: float
    superposition_fidelity: float
    arm_id: int
    jkd_anchor_hash: int
    action_hash: int
    category_hash: int
    coder_specialty_hash: int
    rs3_actionable_hash: int
    phase_bits: int = 2  # v2.1: default to present (2)

    @property
    def phase_name(self) -> str:
        return BITS_TO_PHASE.get(self.phase_bits, 'present')

    @phase_name.setter
    def phase_name(self, name: str) -> None:
        self.phase_bits = PHASE_BITS.get(name, 2)

    def to_bytes(self) -> bytes:
        """Pack into 64-byte binary record."""
        return struct.pack(
            BIN_RECORD_FORMAT,
            self.hex_id,
            self.chaos,
            self.whimsy,
            self.dark_tone,
            self.coherence,
            self.voice_weight,
            self.porosity,
            self.vortex_tension,
            self.superposition_fidelity,
            self.arm_id,
            self.jkd_anchor_hash,
            self.action_hash,
            self.category_hash,
            self.coder_specialty_hash,
            self.rs3_actionable_hash,
            self.phase_bits
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "BinRecord":
        """Unpack from 64-byte binary record."""
        if len(data) != BIN_RECORD_SIZE:
            raise ValueError(f"Expected {BIN_RECORD_SIZE} bytes, got {len(data)}")

        values = struct.unpack(BIN_RECORD_FORMAT, data)
        return cls(
            hex_id=values[0],
            chaos=values[1],
            whimsy=values[2],
            dark_tone=values[3],
            coherence=values[4],
            voice_weight=values[5],
            porosity=values[6],
            vortex_tension=values[7],
            superposition_fidelity=values[8],
            arm_id=values[9],
            jkd_anchor_hash=values[10],
            action_hash=values[11],
            category_hash=values[12],
            coder_specialty_hash=values[13],
            rs3_actionable_hash=values[14],
            phase_bits=values[15]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to human-readable dict."""
        return {
            'hex_id': self.hex_id,
            'phase': self.phase_name,
            'phase_bits': self.phase_bits,
            'chaos': round(self.chaos, 4),
            'whimsy': round(self.whimsy, 4),
            'dark_tone': round(self.dark_tone, 4),
            'coherence': round(self.coherence, 4),
            'voice_weight': round(self.voice_weight, 4),
            'porosity': round(self.porosity, 4),
            'vortex_tension': round(self.vortex_tension, 4),
            'superposition_fidelity': round(self.superposition_fidelity, 4),
            'arm_id': self.arm_id,
        }


# ═════════════════════════════════════════════════════════════════════════════
# BIN STATE MANAGER
# ═════════════════════════════════════════════════════════════════════════════

class BinStateManager:
    """
    Manages 64-site .bin state files.

    File format:
      Header (64 bytes):
        - magic: "KWEN" (4 bytes)
        - version: uint32 (1 = v1.0 baseline, 2 = v2.1 8-phase)
        - timestamp: uint64 (unix epoch ms)
        - checksum: uint32 (FNV-1a of header)
        - reserved: 48 bytes padding

      Records (64 × 64 bytes = 4096 bytes):
        - 64 hexagram sites, each 64 bytes

      Total file size: 4160 bytes (4.06 KB)
    """

    MAGIC = b"KWEN"
    VERSION = 2  # v2.1 8-phase
    HEADER_SIZE = 64
    FILE_SIZE = HEADER_SIZE + (64 * BIN_RECORD_SIZE)  # 4160 bytes

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.records: Dict[int, BinRecord] = {}
        self.version = self.VERSION
        self.timestamp = 0
        self._loaded = False

    def _pack_header(self) -> bytes:
        """Pack 64-byte file header."""
        header = struct.pack(
            "<4sIQQ",  # magic(4), version(4), timestamp(8), checksum(8)
            self.MAGIC,
            self.version,
            self.timestamp,
            0  # checksum placeholder
        )
        # Pad to 64 bytes
        header += b"\x00" * (self.HEADER_SIZE - len(header))

        # Compute checksum on header (excluding checksum field itself)
        checksum = fnv1a_32(header[:16])
        # Rewrite checksum
        header = struct.pack("<4sIQQ", self.MAGIC, self.version, self.timestamp, checksum)
        header += b"\x00" * (self.HEADER_SIZE - len(header))
        return header

    def _unpack_header(self, data: bytes) -> Dict[str, Any]:
        """Unpack 64-byte file header."""
        if len(data) < self.HEADER_SIZE:
            raise ValueError("File too small for header")

        magic, version, timestamp, checksum = struct.unpack("<4sIQQ", data[:24])

        if magic != self.MAGIC:
            raise ValueError(f"Invalid magic: {magic!r} (expected {self.MAGIC!r})")

        # Verify checksum
        expected_checksum = fnv1a_32(data[:16])
        
        return {
            'magic': magic,
            'version': version,
            'timestamp': timestamp,
            'checksum': checksum,
            'is_v21': version >= 2
        }

    def create_new(self) -> None:
        """Create a new .bin file with 64 default records."""
        self.records = {}
        self.timestamp = int(time.time() * 1000)

        for hex_id in range(1, 65):
            self.records[hex_id] = BinRecord(
                hex_id=hex_id,
                chaos=0.5,
                whimsy=0.5,
                dark_tone=0.5,
                coherence=0.5,
                voice_weight=0.5,
                porosity=0.5,
                vortex_tension=0.5,
                superposition_fidelity=1.0,
                arm_id=hex_id % 10,
                jkd_anchor_hash=0,
                action_hash=0,
                category_hash=0,
                coder_specialty_hash=0,
                rs3_actionable_hash=0,
                phase_bits=2  # default: present
            )

        self._loaded = True

    def load(self) -> None:
        """Load .bin file from disk."""
        if not self.filepath.exists():
            self.create_new()
            return

        with open(self.filepath, 'rb') as f:
            data = f.read()

        if len(data) < self.HEADER_SIZE:
            raise ValueError(f"File too small: {len(data)} bytes")

        header = self._unpack_header(data)
        self.version = header['version']
        self.timestamp = header['timestamp']

        # Parse records
        record_data = data[self.HEADER_SIZE:]
        expected_records = len(record_data) // BIN_RECORD_SIZE

        self.records = {}
        for i in range(expected_records):
            offset = i * BIN_RECORD_SIZE
            record_bytes = record_data[offset:offset + BIN_RECORD_SIZE]
            if len(record_bytes) < BIN_RECORD_SIZE:
                break

            record = BinRecord.from_bytes(record_bytes)
            self.records[record.hex_id] = record

        # Backward compatibility: v1.0 files have phase_bits=0 (void)
        # Upgrade to v2.1 by setting default phase to present
        if self.version < 2:
            for record in self.records.values():
                if record.phase_bits == 0 and record.coherence > 0.3:
                    # Heuristic: high coherence = present phase
                    record.phase_bits = 2
            self.version = self.VERSION

        self._loaded = True

    def save(self) -> None:
        """Save .bin file to disk."""
        if not self._loaded:
            raise RuntimeError("No data loaded. Call create_new() or load() first.")

        self.timestamp = int(time.time() * 1000)

        with open(self.filepath, 'wb') as f:
            # Write header
            f.write(self._pack_header())

            # Write records (hex_id 1-64, sparse slots filled with defaults)
            for hex_id in range(1, 65):
                record = self.records.get(hex_id)
                if record is None:
                    # Write default record
                    record = BinRecord(
                        hex_id=hex_id,
                        chaos=0.5, whimsy=0.5, dark_tone=0.5,
                        coherence=0.5, voice_weight=0.5, porosity=0.5,
                        vortex_tension=0.5, superposition_fidelity=1.0,
                        arm_id=0, jkd_anchor_hash=0, action_hash=0,
                        category_hash=0, coder_specialty_hash=0,
                        rs3_actionable_hash=0, phase_bits=2
                    )
                f.write(record.to_bytes())

    def get_record(self, hex_id: int) -> Optional[BinRecord]:
        """Get record by hexagram ID."""
        return self.records.get(hex_id)

    def set_record(self, record: BinRecord) -> None:
        """Set record by hexagram ID."""
        self.records[record.hex_id] = record

    def set_phase(self, hex_id: int, phase_name: str) -> None:
        """Set phase for a specific hexagram site."""
        record = self.records.get(hex_id)
        if record:
            record.phase_name = phase_name

    def get_phase_distribution(self) -> Dict[str, int]:
        """Count sites per phase."""
        dist = {name: 0 for name in PHASE_BITS.keys()}
        for record in self.records.values():
            dist[record.phase_name] = dist.get(record.phase_name, 0) + 1
        return dist

    def get_dominant_phase(self) -> str:
        """Get the phase with most sites."""
        dist = self.get_phase_distribution()
        return max(dist, key=dist.get)

    def get_phase_sites(self, phase_name: str) -> List[BinRecord]:
        """Get all sites in a specific phase."""
        target_bits = PHASE_BITS.get(phase_name, -1)
        return [r for r in self.records.values() if r.phase_bits == target_bits]

    def sync_from_widget(self, widget_state: Dict[int, str]) -> None:
        """
        Sync from HTML widget phase selector.
        widget_state: {hex_id: phase_name}
        """
        for hex_id, phase_name in widget_state.items():
            self.set_phase(hex_id, phase_name)

    def export_to_widget(self) -> Dict[int, str]:
        """
        Export phase state for HTML widget.
        Returns: {hex_id: phase_name}
        """
        return {r.hex_id: r.phase_name for r in self.records.values()}

    def compute_hamiltonian_energy(self) -> float:
        """
        Compute aggregate Hamiltonian energy across all 64 sites.
        H = sum(||v - u||^2 + lambda1*(1-coherence) + lambda2*line_imbalance)
        """
        total_energy = 0.0
        lambda1 = 0.5
        lambda2 = 0.3

        for record in self.records.values():
            # ||v - u||^2 — deviation from mean state
            v_norm = (record.chaos**2 + record.whimsy**2 + record.dark_tone**2 +
                      record.coherence**2 + record.voice_weight**2 + record.porosity**2)

            # line_imbalance — how far from balanced yin/yang
            line_imbalance = abs(record.dark_tone - record.coherence)

            energy = v_norm + lambda1 * (1.0 - record.coherence) + lambda2 * line_imbalance
            total_energy += energy

        return total_energy / len(self.records) if self.records else 0.0

    def compute_gaussian_consensus(self, sigma: float = 0.5) -> float:
        """
        Compute Gaussian consensus kernel across all site pairs.
        K(v_i, v_j) = exp(-||v_i - v_j||^2 / (2*sigma^2))
        """
        records = list(self.records.values())
        if len(records) < 2:
            return 1.0

        total_kernel = 0.0
        count = 0

        for i, r1 in enumerate(records):
            for r2 in records[i+1:]:
                # Compute vector distance
                dist_sq = (
                    (r1.chaos - r2.chaos)**2 +
                    (r1.whimsy - r2.whimsy)**2 +
                    (r1.dark_tone - r2.dark_tone)**2 +
                    (r1.coherence - r2.coherence)**2 +
                    (r1.voice_weight - r2.voice_weight)**2 +
                    (r1.porosity - r2.porosity)**2
                )
                kernel = math.exp(-dist_sq / (2 * sigma**2))
                total_kernel += kernel
                count += 1

        return total_kernel / count if count > 0 else 1.0

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive file statistics."""
        if not self._loaded:
            return {}

        phases = self.get_phase_distribution()
        dominant = self.get_dominant_phase()

        return {
            'filepath': str(self.filepath),
            'version': self.version,
            'timestamp': self.timestamp,
            'total_sites': len(self.records),
            'phase_distribution': phases,
            'dominant_phase': dominant,
            'hamiltonian_energy': self.compute_hamiltonian_energy(),
            'gaussian_consensus': self.compute_gaussian_consensus(),
            'file_size': self.FILE_SIZE,
        }


# ═════════════════════════════════════════════════════════════════════════════
# WIDGET SYNC BRIDGE
# ═════════════════════════════════════════════════════════════════════════════

class WidgetSyncBridge:
    """
    Bidirectional sync between HTML widget and .bin state manager.

    The widget sends phase selections as JSON:
      {"hex_id": 43, "phase": "resolution", "timestamp": 1234567890}

    The bridge writes to .bin and returns updated state.
    """

    def __init__(self, bin_manager: BinStateManager):
        self.bin = bin_manager

    def handle_widget_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Process single widget update."""
        hex_id = update.get('hex_id')
        phase = update.get('phase')

        if hex_id and phase:
            self.bin.set_phase(hex_id, phase)
            self.bin.save()

        return {
            'acknowledged': True,
            'hex_id': hex_id,
            'phase': phase,
            'current_state': self.bin.export_to_widget()
        }

    def get_widget_state(self) -> Dict[str, Any]:
        """Get full state for widget initialization."""
        return {
            'phases': self.bin.export_to_widget(),
            'dominant_phase': self.bin.get_dominant_phase(),
            'phase_distribution': self.bin.get_phase_distribution(),
            'hamiltonian_energy': self.bin.compute_hamiltonian_energy(),
        }
