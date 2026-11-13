"""
Regression test for MPRD-001: source_hash must distinguish None, "", and nonempty MathML.

Acceptance criteria (MPRD-001):
1. source_hash(None) does not raise.
2. source_hash(None), source_hash(""), and source_hash(nonempty) are all distinct.
3. None and "" produce different hashes (no collision between unavailable and empty).
4. Deterministic: same input always produces same hash.
5. occurrence_key() is unaffected by MathML content (identity is paper+locator+index).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from math_contract import source_hash, occurrence_key, SourceOccurrence


def test_source_hash_none_does_not_raise():
    """None input must not crash."""
    h = source_hash(None)
    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex


def test_source_hash_none_distinct_from_empty():
    """None (unavailable) and '' (empty) must produce distinct hashes."""
    assert source_hash(None) != source_hash("")


def test_source_hash_none_distinct_from_content():
    """None must differ from any nonempty MathML."""
    assert source_hash(None) != source_hash("<math>x</math>")


def test_source_hash_empty_distinct_from_content():
    """Empty string must differ from nonempty content."""
    assert source_hash("") != source_hash("<math>x</math>")


def test_source_hash_all_three_distinct():
    """All three representation states must be distinct."""
    h_none = source_hash(None)
    h_empty = source_hash("")
    h_content = source_hash("<math>x</math>")
    assert h_none != h_empty
    assert h_none != h_content
    assert h_empty != h_content


def test_source_hash_deterministic():
    """Same input must always produce the same hash."""
    assert source_hash(None) == source_hash(None)
    assert source_hash("") == source_hash("")
    assert source_hash("<math>x</math>") == source_hash("<math>x</math>")


def test_source_hash_none_stable_sentinel():
    """None hash must be a stable sentinel, not derived from empty string."""
    # The None hash should NOT equal the hash of any UTF-8 encoded string
    # because it uses a type-tagged sentinel.
    import hashlib
    empty_hash = hashlib.sha256(b"").hexdigest()
    assert source_hash(None) != empty_hash


def test_occurrence_key_unaffected_by_mathml():
    """Occurrence identity must not depend on MathML content."""
    occ_none = SourceOccurrence(
        paper_id="p1", paper_version="v1",
        source_locator="math[0]", occurrence_index=0,
        source_hash=source_hash(None),
        latex="x", mathml=None,
    )
    occ_empty = SourceOccurrence(
        paper_id="p1", paper_version="v1",
        source_locator="math[0]", occurrence_index=0,
        source_hash=source_hash(""),
        latex="x", mathml="",
    )
    occ_content = SourceOccurrence(
        paper_id="p1", paper_version="v1",
        source_locator="math[0]", occurrence_index=0,
        source_hash=source_hash("<math>x</math>"),
        latex="x", mathml="<math>x</math>",
    )
    # All three must produce the same occurrence key
    assert occurrence_key(occ_none) == occurrence_key(occ_empty)
    assert occurrence_key(occ_none) == occurrence_key(occ_content)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
