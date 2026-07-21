#!/usr/bin/env python3
"""
kingwen_training.py — POG3 King Wen Training Program (Pooled Weights)
=======================================================================
Ingests wiki data from multiple sources, maps to 512-state hexagram space,
and generates Megatron-compatible batch training data.

WEIGHTS ARE NOT HARDCODED.
- Base identity comes from immutable tables: id, name, trigrams, category, action, binary
- Emotional vectors are pooled from live collapse_full_128(emotional_input) output
- Pooled mean/std computed across matching resolved states for each hexagram/phase
- Intent enters via emotional_input, which changes the 512-state expansion
- Domain-agnostic: same math works for wiki, scribunto, coordinates, weirdgloop

Sources:
  - Weird Gloop API (exchange, runescape, news, vos, merchant, pylon, osseous)
  - MediaWiki Bucket (infobox_item, infobox_monster, dropsline, infobox_quest, exchange, infobox_location)
  - mwparserfromhell local fork (math nodes, headings, links, comments)
  - RuneScape Wiki Lua/Scribunto modules
  - Coordinate calculators (dev/map/geo transforms)

Outputs:
  - expanded_source.jsonl — raw wiki→hexagram mappings with pooled vectors
  - resolved_source.jsonl — tokenizable text records with live weights
  - megatron_weights.csv — 512 rows (64 hexagrams × 8 phases) with pooled stats
  - kingwen_train_corpus.jsonl — Megatron ingestion format
  - consensus_gaussian.json — per-hex/phase mean/std from pooled samples

Author: Hermes / POG3 Sovereign Stack
Updated: 2026-07-11 — removed hardcoded weights; all vectors from live pooling
"""

from __future__ import annotations

import sys
import json
import csv
import hashlib
import math
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from datetime import datetime

# ============================================================
# SECTION 1: IMMUTABLE IDENTITY TABLES
# ============================================================
# These are structural identities only. NO emotional weights here.
# Weights come from live pooling in SECTION 3.

TRIGRAMS = {
    "Kun":  {"idx": 0, "binary": "000", "nature": "Earth", "yin": 3, "yang": 0},
    "Dui":  {"idx": 1, "binary": "011", "nature": "Lake",  "yin": 1, "yang": 2},
    "Li":   {"idx": 2, "binary": "101", "nature": "Fire",  "yin": 1, "yang": 2},
    "Zhen": {"idx": 3, "binary": "001", "nature": "Thunder","yin": 2, "yang": 1},
    "Xun":  {"idx": 4, "binary": "110", "nature": "Wind",  "yin": 2, "yang": 1},
    "Kan":  {"idx": 5, "binary": "010", "nature": "Water", "yin": 2, "yang": 1},
    "Gen":  {"idx": 6, "binary": "100", "nature": "Mountain","yin": 2, "yang": 1},
    "Qian": {"idx": 7, "binary": "111", "nature": "Heaven","yin": 0, "yang": 3},
}

PHASES = [
    "past", "present", "future", "transition",
    "resolution", "dissolution", "crystallization", "void"
]

YAO_STATES = [
    "young_yin", "old_yin", "stable_yin",
    "new_yao", "old_yao", "stable_yao",
    "old_yang", "new_yang", "stable_yang"
]

# Structural identity only: name, trigrams, category, action, binary, porosity.
# NO voiceWeight, coherence, chaos, whimsy, darkTone here.
HEXAGRAMS_IDENTITY = [
    {"id": 1,  "name": "The Creative", "chinese": "乾", "pinyin": "qián", "binary": "111111", "upper": "Qian", "lower": "Qian", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 2,  "name": "The Receptive", "chinese": "坤", "pinyin": "kūn", "binary": "000000", "upper": "Kun", "lower": "Kun", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 3,  "name": "Difficulty at the Beginning", "chinese": "屯", "pinyin": "zhūn", "binary": "010001", "upper": "Zhen", "lower": "Kan", "category": "dissipator", "action": "ADAPT", "porosity": 0.50},
    {"id": 4,  "name": "Youthful Folly", "chinese": "蒙", "pinyin": "méng", "binary": "100010", "upper": "Kan", "lower": "Gen", "category": "transformer", "action": "WAIT", "porosity": 0.50},
    {"id": 5,  "name": "Waiting", "chinese": "需", "pinyin": "xū", "binary": "010111", "upper": "Qian", "lower": "Kan", "category": "dissipator", "action": "WAIT", "porosity": 0.50},
    {"id": 6,  "name": "Conflict", "chinese": "訟", "pinyin": "sòng", "binary": "111010", "upper": "Kan", "lower": "Qian", "category": "transformer", "action": "ASSERT", "porosity": 1.00},
    {"id": 7,  "name": "The Army", "chinese": "師", "pinyin": "shī", "binary": "000010", "upper": "Kan", "lower": "Kun", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 8,  "name": "Holding Together", "chinese": "比", "pinyin": "bǐ", "binary": "010000", "upper": "Kun", "lower": "Kan", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 9,  "name": "Taming Power of the Small", "chinese": "小畜", "pinyin": "xiǎo chù", "binary": "110111", "upper": "Qian", "lower": "Xun", "category": "dissipator", "action": "ADAPT", "porosity": 0.50},
    {"id": 10, "name": "Treading", "chinese": "履", "pinyin": "lǚ", "binary": "111011", "upper": "Dui", "lower": "Qian", "category": "sovereign", "action": "ADAPT", "porosity": 0.50},
    {"id": 11, "name": "Peace", "chinese": "泰", "pinyin": "tài", "binary": "000111", "upper": "Qian", "lower": "Kun", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 12, "name": "Standstill", "chinese": "否", "pinyin": "pǐ", "binary": "111000", "upper": "Kun", "lower": "Qian", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 13, "name": "Fellowship with Men", "chinese": "同人", "pinyin": "tóng rén", "binary": "101111", "upper": "Qian", "lower": "Li", "category": "transformer", "action": "ASSERT", "porosity": 0.50},
    {"id": 14, "name": "Possession in Great Measure", "chinese": "大有", "pinyin": "dà yǒu", "binary": "111101", "upper": "Li", "lower": "Qian", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 15, "name": "Modesty", "chinese": "謙", "pinyin": "qiān", "binary": "001000", "upper": "Kun", "lower": "Gen", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 16, "name": "Enthusiasm", "chinese": "豫", "pinyin": "yù", "binary": "000100", "upper": "Zhen", "lower": "Kun", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 17, "name": "Following", "chinese": "隨", "pinyin": "suí", "binary": "100110", "upper": "Zhen", "lower": "Dui", "category": "transformer", "action": "YIELD", "porosity": 0.50},
    {"id": 18, "name": "Work on Decayed", "chinese": "蠱", "pinyin": "gǔ", "binary": "011001", "upper": "Xun", "lower": "Gen", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 19, "name": "Approach", "chinese": "臨", "pinyin": "lín", "binary": "110000", "upper": "Kun", "lower": "Dui", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 20, "name": "Contemplation", "chinese": "觀", "pinyin": "guān", "binary": "000011", "upper": "Xun", "lower": "Kun", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 21, "name": "Biting Through", "chinese": "噬嗑", "pinyin": "shì kè", "binary": "100101", "upper": "Zhen", "lower": "Li", "category": "transformer", "action": "ASSERT", "porosity": 0.50},
    {"id": 22, "name": "Grace", "chinese": "賁", "pinyin": "bì", "binary": "101001", "upper": "Li", "lower": "Gen", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 23, "name": "Splitting Apart", "chinese": "剝", "pinyin": "bō", "binary": "000001", "upper": "Kun", "lower": "Gen", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 24, "name": "Return", "chinese": "復", "pinyin": "fù", "binary": "100000", "upper": "Zhen", "lower": "Kun", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 25, "name": "Innocence", "chinese": "无妄", "pinyin": "wú wàng", "binary": "100111", "upper": "Zhen", "lower": "Qian", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 26, "name": "Taming Power of the Great", "chinese": "大畜", "pinyin": "dà chù", "binary": "111001", "upper": "Qian", "lower": "Gen", "category": "boundary", "action": "ADAPT", "porosity": 0.50},
    {"id": 27, "name": "Corners of the Mouth", "chinese": "頤", "pinyin": "yí", "binary": "100001", "upper": "Zhen", "lower": "Gen", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 28, "name": "Preponderance of the Great", "chinese": "大過", "pinyin": "dà guò", "binary": "011110", "upper": "Xun", "lower": "Dui", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 29, "name": "The Abysmal", "chinese": "坎", "pinyin": "kǎn", "binary": "010010", "upper": "Kan", "lower": "Kan", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 30, "name": "The Clinging", "chinese": "離", "pinyin": "lí", "binary": "101101", "upper": "Li", "lower": "Li", "category": "boundary", "action": "ADAPT", "porosity": 0.50},
    {"id": 31, "name": "Influence", "chinese": "咸", "pinyin": "xián", "binary": "001110", "upper": "Gen", "lower": "Dui", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 32, "name": "Duration", "chinese": "恆", "pinyin": "héng", "binary": "011100", "upper": "Xun", "lower": "Zhen", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 33, "name": "Retreat", "chinese": "遯", "pinyin": "dùn", "binary": "001111", "upper": "Gen", "lower": "Qian", "category": "boundary", "action": "YIELD", "porosity": 0.50},
    {"id": 34, "name": "Power of the Great", "chinese": "大壯", "pinyin": "dà zhuàng", "binary": "111100", "upper": "Qian", "lower": "Zhen", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 35, "name": "Progress", "chinese": "晉", "pinyin": "jìn", "binary": "000101", "upper": "Kun", "lower": "Li", "category": "transformer", "action": "ADAPT", "porosity": 0.50},
    {"id": 36, "name": "Darkening of the Light", "chinese": "明夷", "pinyin": "míng yí", "binary": "101000", "upper": "Li", "lower": "Kun", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 37, "name": "The Family", "chinese": "家人", "pinyin": "jiā rén", "binary": "101011", "upper": "Li", "lower": "Xun", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 38, "name": "Opposition", "chinese": "睽", "pinyin": "kuí", "binary": "110101", "upper": "Dui", "lower": "Li", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 39, "name": "Obstruction", "chinese": "蹇", "pinyin": "jiǎn", "binary": "010100", "upper": "Gen", "lower": "Kan", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 40, "name": "Deliverance", "chinese": "解", "pinyin": "xiè", "binary": "001010", "upper": "Kan", "lower": "Zhen", "category": "transformer", "action": "ADAPT", "porosity": 0.50},
    {"id": 41, "name": "Decrease", "chinese": "損", "pinyin": "sǔn", "binary": "100011", "upper": "Dui", "lower": "Gen", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 42, "name": "Increase", "chinese": "益", "pinyin": "yì", "binary": "110001", "upper": "Zhen", "lower": "Xun", "category": "transformer", "action": "ASSERT", "porosity": 0.25},
    {"id": 43, "name": "Breakthrough", "chinese": "夬", "pinyin": "guài", "binary": "111110", "upper": "Qian", "lower": "Dui", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 44, "name": "Coming to Meet", "chinese": "姤", "pinyin": "gòu", "binary": "011111", "upper": "Xun", "lower": "Qian", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 45, "name": "Gathering Together", "chinese": "萃", "pinyin": "cuì", "binary": "000110", "upper": "Kun", "lower": "Dui", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 46, "name": "Pushing Upward", "chinese": "升", "pinyin": "shēng", "binary": "011000", "upper": "Xun", "lower": "Kun", "category": "transformer", "action": "ADAPT", "porosity": 0.50},
    {"id": 47, "name": "Oppression", "chinese": "困", "pinyin": "kùn", "binary": "010110", "upper": "Kan", "lower": "Dui", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 48, "name": "The Well", "chinese": "井", "pinyin": "jǐng", "binary": "011010", "upper": "Xun", "lower": "Kan", "category": "boundary", "action": "YIELD", "porosity": 0.50},
    {"id": 49, "name": "Revolution", "chinese": "革", "pinyin": "gé", "binary": "101110", "upper": "Li", "lower": "Dui", "category": "transformer", "action": "ASSERT", "porosity": 0.50},
    {"id": 50, "name": "The Cauldron", "chinese": "鼎", "pinyin": "dǐng", "binary": "011101", "upper": "Xun", "lower": "Li", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 51, "name": "The Arousing", "chinese": "震", "pinyin": "zhèn", "binary": "100100", "upper": "Zhen", "lower": "Zhen", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 52, "name": "Keeping Still", "chinese": "艮", "pinyin": "gèn", "binary": "001001", "upper": "Gen", "lower": "Gen", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 53, "name": "Development", "chinese": "漸", "pinyin": "jiàn", "binary": "001011", "upper": "Gen", "lower": "Xun", "category": "transformer", "action": "ADAPT", "porosity": 0.50},
    {"id": 54, "name": "The Marrying Maiden", "chinese": "歸妹", "pinyin": "guī mèi", "binary": "110100", "upper": "Dui", "lower": "Zhen", "category": "dissipator", "action": "YIELD", "porosity": 0.75},
    {"id": 55, "name": "Abundance", "chinese": "豐", "pinyin": "fēng", "binary": "001101", "upper": "Li", "lower": "Zhen", "category": "sovereign", "action": "ASSERT", "porosity": 0.25},
    {"id": 56, "name": "The Wanderer", "chinese": "旅", "pinyin": "lǚ", "binary": "101100", "upper": "Gen", "lower": "Li", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 57, "name": "The Gentle", "chinese": "巽", "pinyin": "xùn", "binary": "011011", "upper": "Xun", "lower": "Xun", "category": "boundary", "action": "YIELD", "porosity": 0.50},
    {"id": 58, "name": "The Joyous", "chinese": "兌", "pinyin": "duì", "binary": "110110", "upper": "Dui", "lower": "Dui", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 59, "name": "Dispersion", "chinese": "渙", "pinyin": "huàn", "binary": "010011", "upper": "Kan", "lower": "Xun", "category": "dissipator", "action": "ADAPT", "porosity": 0.75},
    {"id": 60, "name": "Limitation", "chinese": "節", "pinyin": "jié", "binary": "110010", "upper": "Dui", "lower": "Kan", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 61, "name": "Inner Truth", "chinese": "中孚", "pinyin": "zhōng fú", "binary": "110011", "upper": "Dui", "lower": "Xun", "category": "transformer", "action": "YIELD", "porosity": 0.25},
    {"id": 62, "name": "Preponderance of the Small", "chinese": "小過", "pinyin": "xiǎo guò", "binary": "001100", "upper": "Zhen", "lower": "Gen", "category": "dissipator", "action": "WAIT", "porosity": 0.75},
    {"id": 63, "name": "After Completion", "chinese": "既濟", "pinyin": "jì jì", "binary": "101010", "upper": "Li", "lower": "Kan", "category": "boundary", "action": "WAIT", "porosity": 0.50},
    {"id": 64, "name": "Before Completion", "chinese": "未濟", "pinyin": "wèi jì", "binary": "010101", "upper": "Kan", "lower": "Li", "category": "transformer", "action": "ADAPT", "porosity": 0.75},
]

# ============================================================
# SECTION 2: DATA CLASSES
# ============================================================

@dataclass
class WikiSource:
    """A single wiki data point before hexagram mapping."""
    source_type: str
    source_endpoint: str
    raw_content: str
    extracted_features: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

@dataclass
class HexagramPhaseVector:
    """A resolved vector for one hexagram at one phase, from pooled states."""
    hexagram_id: int
    phase: str
    yao_composition: Dict[str, int]
    voiceWeight: float
    coherence: float
    chaos: float
    whimsy: float
    darkTone: float
    porosity_norm: float
    dominant_axis: str
    pool_mean: Dict[str, float] = field(default_factory=dict)
    pool_std: Dict[str, float] = field(default_factory=dict)
    pool_n: int = 0

@dataclass
class MegatronTrainingRecord:
    """Final format for Megatron ingestion."""
    text: str
    hexagram_id: int
    phase: str
    vector: List[float]
    source_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# SECTION 3: LIVE POOLING ENGINE — replaces hardcoded weights
# ============================================================

class LivePoolEngine:
    """Computes emotional vectors from live 512-state expansion.

    No hardcoded weights. All 5-axis vectors come from collapse_full_128()
    resolved states, pooled by hexagram_id and phase.
    """

    def __init__(self, kingwen_root: Optional[Path] = None):
        self.kingwen_root = kingwen_root or Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
        sys.path.insert(0, str(self.kingwen_root))
        from emotional_engine import collapse_full_128  # noqa: E402
        self._collapse = collapse_full_128

    def pool_all(self, emotional_input: float = 0.5) -> Dict[str, Any]:
        """Return pooled consensus from all 512 resolved states."""
        data = self._collapse(emotional_input=emotional_input)
        consensus = data.get('consensus') or {}
        resolved = data.get('resolved', [])
        expanded = data.get('expanded', [])

        # Pool per hexagram
        hex_groups: Dict[int, List[Dict]] = defaultdict(list)
        for r in resolved:
            hid = int(r.get('hexagram_id') or 0)
            if hid:
                hex_groups[hid].append(r)

        pooled = {}
        for hid in range(1, 65):
            vecs = hex_groups.get(hid, [])
            pooled[str(hid)] = self._pool_hex(hid, vecs)

        return {
            'emotional_input': emotional_input,
            'consensus': consensus,
            'pooled': pooled,
            'total_resolved': len(resolved),
            'total_expanded': len(expanded),
        }

    def pool_hex(self, hex_id: int, emotional_input: float = 0.5) -> Dict[str, Any]:
        """Pool ALL resolved states for this hex_id at this emotional_input.

        This is the real aggregation path: usually 8 states per hex,
        giving mean/std across phases instead of single-state noise."""
        data = self._collapse(emotional_input=emotional_input)
        resolved = data.get('resolved', [])
        vecs = [r for r in resolved if int(r.get('hexagram_id') or 0) == hex_id]
        return self._pool_hex(hex_id, vecs)

    def _pool_hex(self, hex_id: int, vecs: List[Dict]) -> Dict[str, Any]:
        axes = ['chaos', 'whimsy', 'darkTone', 'coherence', 'voiceWeight']
        if not vecs:
            return {
                'hexagram_id': hex_id,
                'n': 0,
                'mean': {ax: 0.0 for ax in axes},
                'std': {ax: 0.0 for ax in axes},
            }
        means = {}
        stds = {}
        for ax in axes:
            vals = [float((r.get('resolved_vector') or {}).get(ax, 0.0)) for r in vecs]
            n = len(vals)
            means[ax] = sum(vals) / n
            if n > 1:
                var = sum((v - means[ax]) ** 2 for v in vals) / n
                stds[ax] = var ** 0.5
            else:
                stds[ax] = 0.0
        return {
            'hexagram_id': hex_id,
            'n': len(vecs),
            'mean': means,
            'std': stds,
        }

# ============================================================
# SECTION 4: DETERMINISTIC HASH ENGINE
# ============================================================

class KingWenHashEngine:
    """Deterministic hash — no pseudo-RNG."""

    @staticmethod
    def hash_input(text: str, tick: int = 0) -> int:
        hasher = hashlib.sha256()
        hasher.update(f"{text}:{tick}".encode("utf-8"))
        digest = hasher.digest()
        return int.from_bytes(digest[:4], "big")

    @staticmethod
    def hexagram_from_text(text: str, tick: int = 0) -> Dict[str, Any]:
        h = KingWenHashEngine.hash_input(text, tick)
        hex_id = (h % 64) + 1
        identity_table = {h["id"]: h for h in HEXAGRAMS_IDENTITY}
        return identity_table[hex_id]

    @staticmethod
    def phase_from_text(text: str, hex_id: int, tick: int = 0) -> str:
        h = KingWenHashEngine.hash_input(f"{text}:{hex_id}", tick)
        phase_idx = h % 8
        return PHASES[phase_idx]

    @staticmethod
    def coords_to_hexagram(z: int, x: int, y: int, tick: int = 0) -> Dict[str, Any]:
        hex_id = ((z * 17 + x * 13 + y * 7 + tick) % 64) + 1
        identity_table = {h["id"]: h for h in HEXAGRAMS_IDENTITY}
        return identity_table[hex_id]

# ============================================================
# SECTION 5: WIKI INGESTORS
# ============================================================

class WikiIngestor:
    def ingest(self, source: str) -> List[WikiSource]:
        raise NotImplementedError
    def extract_features(self, raw: str) -> Dict[str, Any]:
        raise NotImplementedError

class WeirdGloopIngestor(WikiIngestor):
    ENDPOINTS = ["exchange", "runescape", "news", "vos", "merchant", "pylon", "osseous"]

    def ingest(self, source: str) -> List[WikiSource]:
        records = []
        if source.endswith(".json"):
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            for item in data.get("items", []):
                records.append(WikiSource(
                    source_type="weirdgloop",
                    source_endpoint=source,
                    raw_content=json.dumps(item),
                    extracted_features=self.extract_features(json.dumps(item))
                ))
        return records

    def extract_features(self, raw: str) -> Dict[str, Any]:
        data = json.loads(raw)
        return {
            "name": data.get("name", ""),
            "price": data.get("price", 0),
            "volume": data.get("volume", 0),
            "category": data.get("category", "unknown"),
            "members": data.get("members", False),
        }

class MediaWikiBucketIngestor(WikiIngestor):
    TABLES = ["infobox_item", "infobox_monster", "dropsline", "infobox_quest", "exchange", "infobox_location"]

    def ingest(self, source: str) -> List[WikiSource]:
        records = []
        if source.endswith(".json"):
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            for row in data.get("rows", []):
                records.append(WikiSource(
                    source_type="mediawiki_bucket",
                    source_endpoint=source,
                    raw_content=json.dumps(row),
                    extracted_features=row
                ))
        return records

    def extract_features(self, raw: str) -> Dict[str, Any]:
        return json.loads(raw)

class MwparserfromhellIngestor(WikiIngestor):
    def __init__(self, mwparser_path: str = r"C:\Users\krist\Desktop\mwparserfromhell_local"):
        self.mwparser_path = mwparser_path
        self._init_mwparser()

    def _init_mwparser(self):
        sys.path.insert(0, self.mwparser_path)
        try:
            from mwparserfromhell import parse as mw_parse
            self.mw_parse = mw_parse
        except ImportError:
            self.mw_parse = None

    def ingest(self, source: str) -> List[WikiSource]:
        records = []
        if source.endswith(".wikitext.txt"):
            wikitext = Path(source).read_text(encoding="utf-8")
            records.append(WikiSource(
                source_type="mwparser",
                source_endpoint=source,
                raw_content=wikitext,
                extracted_features=self.extract_features(wikitext)
            ))
        return records

    def extract_features(self, raw: str) -> Dict[str, Any]:
        if self.mw_parse is None:
            return {"error": "mwparserfromhell not available"}
        code = self.mw_parse(raw)
        return {
            "headings": [str(h) for h in code.ifilter_headings()],
            "math_nodes": [
                str(n) for n in code.ifilter(
                    matches=lambda n: hasattr(n, "tag")
                    and str(getattr(n, "tag", "")).lower() in {"math", "ce", "chem", "sub", "sup"}
                )
            ],
            "links": [str(l) for l in code.ifilter_external_links()],
            "comments": [str(c) for c in code.ifilter_comments()],
            "source_chars": len(raw),
        }

class ScribuntoIngestor(WikiIngestor):
    def ingest(self, source: str) -> List[WikiSource]:
        records = []
        if source.endswith(".lua"):
            lua_text = Path(source).read_text(encoding="utf-8")
            records.append(WikiSource(
                source_type="scribunto",
                source_endpoint=source,
                raw_content=lua_text,
                extracted_features=self.extract_features(lua_text)
            ))
        return records

    def extract_features(self, raw: str) -> Dict[str, Any]:
        functions = re.findall(r"function\s+(\w+)", raw)
        requires = []
        for match in re.finditer(r"require\s*\(", raw):
            start = match.end()
            quote = raw[start:start+1]
            if quote in ('"', "'"):
                end = raw.find(quote, start + 1)
                if end > start:
                    requires.append(raw[start+1:end])
        return {
            "functions": functions,
            "requires": requires,
            "function_count": len(functions),
            "line_count": len(raw.splitlines()),
        }

class CoordinateIngestor(WikiIngestor):
    def ingest(self, source: str) -> List[WikiSource]:
        records = []
        if source.endswith(".json"):
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            for coord in data.get("coordinates", []):
                records.append(WikiSource(
                    source_type="coordinate",
                    source_endpoint=source,
                    raw_content=json.dumps(coord),
                    extracted_features=coord
                ))
        return records

    def extract_features(self, raw: str) -> Dict[str, Any]:
        data = json.loads(raw)
        return {
            "z": data.get("z", 0),
            "x": data.get("x", 0),
            "y": data.get("y", 0),
            "map_id": data.get("map_id", 0),
            "format": data.get("format", "unknown"),
        }

# ============================================================
# SECTION 6: EMOTIONAL INPUT DERIVATION (domain agnostic)
# ============================================================

def derive_emotional_input(features: Dict[str, Any]) -> float:
    """Derive emotional_input from intent/structure of input, not preset weights.

    Gates are generic feature detectors:
    - price magnitude → volatility/exposure
    - math density → structural dominance
    - chaos field → explicit entropy signal
    - coordinate distance → spatial removal from center
    - function/require count → code complexity
    - heading depth → document hierarchy
    """
    emotional = 0.5
    if "price" in features and isinstance(features["price"], (int, float)) and features["price"] > 1000000:
        emotional = max(emotional, 0.8)
    if "math_nodes" in features and isinstance(features["math_nodes"], list) and len(features["math_nodes"]) > 2:
        emotional = max(emotional, 0.3)
    if "chaos" in features and isinstance(features["chaos"], (int, float)):
        emotional = max(emotional, float(features["chaos"]))
    if "x" in features and "y" in features:
        try:
            dist = math.sqrt(float(features.get("x", 0))**2 + float(features.get("y", 0))**2)
            emotional = max(emotional, min(1.0, dist / 10000))
        except Exception:
            pass
    if "function_count" in features and isinstance(features["function_count"], int):
        emotional = max(emotional, min(1.0, features["function_count"] / 50))
    if "headings" in features and isinstance(features["headings"], list):
        emotional = max(emotional, min(1.0, len(features["headings"]) / 20))
    return round(emotional, 4)

# ============================================================
# SECTION 7: VECTOR COMPOSER — live pooled weights
# ============================================================

class VectorComposer:
    def __init__(self, pool_engine: Optional[LivePoolEngine] = None):
        self.hex_table = {h["id"]: h for h in HEXAGRAMS_IDENTITY}
        self.pool_engine = pool_engine or LivePoolEngine()
        self._cache: Dict[str, Dict] = {}

    def compose(self, hex_id: int, phase: str, emotional_input: float = 0.5) -> HexagramPhaseVector:
        cache_key = f"{hex_id}_{phase}_{emotional_input}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        hexagram = self.hex_table[hex_id]
        pool = self.pool_engine.pool_hex(hex_id, emotional_input)
        mean = pool.get('mean', {})
        std = pool.get('std', {})
        n = pool.get('n', 0)

        axes = ['chaos', 'whimsy', 'darkTone', 'coherence', 'voiceWeight']
        blended = {ax: round(float(mean.get(ax, 0.0)), 5) for ax in axes}
        dominant = max(blended, key=blended.get) if blended else 'coherence'

        yao_comp = self._phase_yao_distribution(hex_id, PHASES.index(phase))

        vector = HexagramPhaseVector(
            hexagram_id=hex_id,
            phase=phase,
            yao_composition=yao_comp,
            voiceWeight=blended['voiceWeight'],
            coherence=blended['coherence'],
            chaos=blended['chaos'],
            whimsy=blended['whimsy'],
            darkTone=blended['darkTone'],
            porosity_norm=hexagram['porosity'],
            dominant_axis=dominant,
            pool_mean=blended,
            pool_std={ax: round(float(std.get(ax, 0.0)), 5) for ax in axes},
            pool_n=n,
        )
        self._cache[cache_key] = vector
        return vector

    def _phase_yao_distribution(self, hex_id: int, phase_idx: int) -> Dict[str, int]:
        hexagram = self.hex_table[hex_id]
        binary = hexagram["binary"]
        yang_count = binary.count("1")
        yin_count = 6 - yang_count

        distribution = {state: 0 for state in YAO_STATES}
        distribution["stable_yang"] = yang_count
        distribution["stable_yin"] = yin_count

        shift = (phase_idx + 1) % 4
        if yang_count > 0 and shift > 0:
            move = min(shift, yang_count)
            distribution["stable_yang"] -= move
            distribution["old_yang"] = move // 2
            distribution["new_yang"] = move - distribution["old_yang"]

        if yin_count > 0 and shift > 0:
            move = min(shift, yin_count)
            distribution["stable_yin"] -= move
            distribution["old_yin"] = move // 2
            distribution["new_yin"] = move - distribution["old_yin"]

        if phase_idx >= 4:
            yao_inject = (phase_idx - 3)
            distribution["stable_yao"] = min(yao_inject, 2)
            if distribution["stable_yang"] >= distribution["stable_yao"]:
                distribution["stable_yang"] -= distribution["stable_yao"]
            else:
                distribution["stable_yin"] -= distribution["stable_yao"]

        return {k: v for k, v in distribution.items() if v > 0}

# ============================================================
# SECTION 8: MEGATRON FORATTER
# ============================================================

class MegatronFormatter:
    def format_record(self, wiki_source: WikiSource, vector: HexagramPhaseVector) -> MegatronTrainingRecord:
        features = wiki_source.extracted_features
        hex_identity = {h["id"]: h for h in HEXAGRAMS_IDENTITY}[vector.hexagram_id]
        text_parts = [
            f"<|hexagram|>{vector.hexagram_id:02d}",
            f"<|phase|>{vector.phase}",
            f"<|action|>{hex_identity['action']}",
            f"<|dominant|>{vector.dominant_axis}",
            f"<|porosity|>{vector.porosity_norm:.2f}",
            f"<|source|>{wiki_source.source_type}",
        ]

        if "name" in features:
            text_parts.append(f"<|name|>{features['name']}")
        if "category" in features:
            text_parts.append(f"<|category|>{features['category']}")
        if "headings" in features:
            for h in features["headings"][:3]:
                text_parts.append(f"<|heading|>{h}")
        if "math_nodes" in features:
            for m in features["math_nodes"][:2]:
                text_parts.append(f"<|math|>{m}")
        if "functions" in features:
            text_parts.append(f"<|functions|>{','.join(features['functions'][:5])}")
        if "z" in features and "x" in features and "y" in features:
            text_parts.append(f"<|coord|>{features['z']},{features['x']},{features['y']}")

        text = " ".join(text_parts)
        source_hash = hashlib.sha256(wiki_source.raw_content.encode()).hexdigest()[:16]

        return MegatronTrainingRecord(
            text=text,
            hexagram_id=vector.hexagram_id,
            phase=vector.phase,
            vector=[
                vector.voiceWeight,
                vector.coherence,
                vector.chaos,
                vector.whimsy,
                vector.darkTone,
                vector.porosity_norm,
            ],
            source_hash=source_hash,
            metadata={
                "source_type": wiki_source.source_type,
                "source_endpoint": wiki_source.source_endpoint,
                "timestamp": wiki_source.timestamp,
                "yao_composition": vector.yao_composition,
                "dominant_axis": vector.dominant_axis,
                "pool_mean": vector.pool_mean,
                "pool_std": vector.pool_std,
                "pool_n": vector.pool_n,
            }
        )

    def to_jsonl(self, records: List[MegatronTrainingRecord], path: str):
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    def to_csv(self, records: List[MegatronTrainingRecord], path: str):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "hexagram_id", "phase", "voiceWeight", "coherence", "chaos",
                "whimsy", "darkTone", "porosity_norm", "dominant_axis", "text"
            ])
            for r in records:
                writer.writerow([
                    r.hexagram_id, r.phase,
                    r.vector[0], r.vector[1], r.vector[2],
                    r.vector[3], r.vector[4], r.vector[5],
                    r.metadata["dominant_axis"], r.text[:200]
                ])

# ============================================================
# SECTION 9: ORCHESTRATOR
# ============================================================

class KingWenTrainingOrchestrator:
    def __init__(self, output_dir: str, kingwen_root: Optional[Path] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hash_engine = KingWenHashEngine()
        self.pool_engine = LivePoolEngine(kingwen_root)
        self.composer = VectorComposer(self.pool_engine)
        self.formatter = MegatronFormatter()
        self.ingestors = {
            "weirdgloop": WeirdGloopIngestor(),
            "mediawiki_bucket": MediaWikiBucketIngestor(),
            "mwparser": MwparserfromhellIngestor(),
            "scribunto": ScribuntoIngestor(),
            "coordinate": CoordinateIngestor(),
        }
        self.expanded_records: List[Dict] = []
        self.resolved_records: List[MegatronTrainingRecord] = []

    def ingest_source(self, source_path: str, source_type: str, tick: int = 0) -> List[WikiSource]:
        ingestor = self.ingestors.get(source_type)
        if not ingestor:
            raise ValueError(f"Unknown source type: {source_type}")
        sources = ingestor.ingest(source_path)
        for src in sources:
            hexagram = self.hash_engine.hexagram_from_text(src.raw_content, tick)
            phase = self.hash_engine.phase_from_text(src.raw_content, hexagram["id"], tick)
            emotional = derive_emotional_input(src.extracted_features)
            vector = self.composer.compose(hexagram["id"], phase, emotional)
            record = self.formatter.format_record(src, vector)
            self.expanded_records.append({
                "source_type": src.source_type,
                "source_endpoint": src.source_endpoint,
                "hexagram_id": hexagram["id"],
                "hexagram_name": hexagram["name"],
                "phase": phase,
                "emotional_input": emotional,
                "vector": asdict(vector),
                "source_hash": record.source_hash,
            })
            self.resolved_records.append(record)
        return sources

    def build_consensus(self) -> Dict[str, Any]:
        if not self.resolved_records:
            return {}
        groups = defaultdict(list)
        for r in self.resolved_records:
            key = (r.hexagram_id, r.phase)
            groups[key].append(r.vector)
        consensus = {}
        for (hex_id, phase), vectors in groups.items():
            mean_vector = [sum(v[i] for v in vectors) / len(vectors) for i in range(6)]
            if len(vectors) > 1:
                std_vector = [
                    math.sqrt(sum((v[i] - mean_vector[i])**2 for v in vectors) / len(vectors))
                    for i in range(6)
                ]
            else:
                std_vector = [0.0] * 6
            consensus[f"{hex_id:02d}_{phase}"] = {
                "hexagram_id": hex_id,
                "phase": phase,
                "mean": [round(x, 5) for x in mean_vector],
                "std": [round(x, 5) for x in std_vector],
                "sample_count": len(vectors),
            }
        return consensus

    def export(self):
        expanded_path = self.output_dir / "expanded_source.jsonl"
        with open(expanded_path, "w", encoding="utf-8") as f:
            for r in self.expanded_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        resolved_path = self.output_dir / "resolved_source.jsonl"
        self.formatter.to_jsonl(self.resolved_records, str(resolved_path))

        csv_path = self.output_dir / "megatron_weights.csv"
        self.formatter.to_csv(self.resolved_records, str(csv_path))

        consensus = self.build_consensus()
        consensus_path = self.output_dir / "consensus_gaussian.json"
        with open(consensus_path, "w", encoding="utf-8") as f:
            json.dump(consensus, f, indent=2, ensure_ascii=False)

        # Export learned summary from live pool, not hardcoded weights
        learned = {}
        for hex_id in range(1, 65):
            hex_identity = {h["id"]: h for h in HEXAGRAMS_IDENTITY}[hex_id]
            hex_records = [r for r in self.resolved_records if r.hexagram_id == hex_id]
            phases_found = list(set(r.phase for r in hex_records))
            # Pool live vector stats across all matched states for this hex
            pooled = self.pool_engine.pool_hex(hex_id, emotional_input=0.5)
            learned[str(hex_id)] = {
                "name": hex_identity["name"],
                "binary": hex_identity["binary"],
                "upper_trigram": hex_identity["upper"],
                "lower_trigram": hex_identity["lower"],
                "category": hex_identity["category"],
                "action": hex_identity["action"],
                "base_porosity": hex_identity["porosity"],
                "pool_mean": pooled.get("mean", {}),
                "pool_std": pooled.get("std", {}),
                "pool_n": pooled.get("n", 0),
                "phases_found": phases_found,
                "phase_count": len(phases_found),
                "record_count": len(hex_records),
            }
        learned_path = self.output_dir / "learned_sequential_64.json"
        with open(learned_path, "w", encoding="utf-8") as f:
            json.dump(learned, f, indent=2, ensure_ascii=False)

        return {
            "expanded_source": str(expanded_path),
            "resolved_source": str(resolved_path),
            "megatron_weights": str(csv_path),
            "consensus_gaussian": str(consensus_path),
            "learned_sequential_64": str(learned_path),
            "total_records": len(self.resolved_records),
            "unique_hexagrams": len(set(r.hexagram_id for r in self.resolved_records)),
            "unique_phases": len(set(r.phase for r in self.resolved_records)),
        }

    def run_pipeline(self, sources: List[Tuple[str, str]], tick: int = 0) -> Dict[str, Any]:
        for source_path, source_type in sources:
            print(f"[INGEST] {source_type}: {source_path}")
            self.ingest_source(source_path, source_type, tick)
        print(f"[COMPOSE] {len(self.expanded_records)} expanded records")
        print(f"[RESOLVE] {len(self.resolved_records)} resolved records")
        results = self.export()
        print(f"[EXPORT] {results['total_records']} total records")
        print(f"[EXPORT] {results['unique_hexagrams']}/64 hexagrams covered")
        print(f"[EXPORT] {results['unique_phases']}/8 phases covered")
        return results

# ============================================================
# SECTION 10: CLI ENTRY POINT
# ============================================================

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="King Wen Training Program — Pooled Weights")
    parser.add_argument("--output", "-o", default="./kingwen_train_data", help="Output directory")
    parser.add_argument("--source", "-s", action="append", nargs=2, metavar=("PATH", "TYPE"),
                        help="Source file and type (weirdgloop, mediawiki_bucket, mwparser, scribunto, coordinate)")
    parser.add_argument("--tick", "-t", type=int, default=0, help="Deterministic tick offset")
    parser.add_argument("--kingwen-root", default=None, help="Path to KING-WEN-I-CHING-IMMUTABLE-TABLES")
    args = parser.parse_args()

    orchestrator = KingWenTrainingOrchestrator(
        args.output,
        kingwen_root=Path(args.kingwen_root) if args.kingwen_root else None,
    )

    if args.source:
        results = orchestrator.run_pipeline(args.source, args.tick)
        print("\n[COMPLETE] Files generated:")
        for key, path in results.items():
            if key not in ("total_records", "unique_hexagrams", "unique_phases"):
                print(f"  {key}: {path}")
    else:
        print("[DEMO] Generating 512 baseline records from live pooled weights...")
        for hex_id in range(1, 65):
            for phase in PHASES:
                vector = orchestrator.composer.compose(hex_id, phase, emotional_input=0.5)
                identity = orchestrator.composer.hex_table[hex_id]
                src = WikiSource(
                    source_type="baseline",
                    source_endpoint="immutable_table",
                    raw_content=f"hex_{hex_id:02d}_{phase}",
                    extracted_features={"hexagram_id": hex_id, "phase": phase, "name": identity["name"]},
                )
                record = orchestrator.formatter.format_record(src, vector)
                orchestrator.expanded_records.append({
                    "source_type": "baseline",
                    "hexagram_id": hex_id,
                    "phase": phase,
                    "vector": asdict(vector),
                })
                orchestrator.resolved_records.append(record)
        results = orchestrator.export()
        print(f"[DEMO] {results['total_records']} baseline records generated")
        print(f"[DEMO] Files in: {args.output}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
