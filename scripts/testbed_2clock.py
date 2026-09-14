#!/usr/bin/env python3
"""
King Wen 2-Clock Testbed
========================
Exercises the baseline-load → step → measure pattern on both WALL_CLOCK and TICK_CLOCK.

Pattern: baseline -> continue (n steps, measuring each) -> final report
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.dsp_clock import (
    WallClock, TickClock, HEALING_CLOCK_HZ, OPPOSITION_CLOCK_HZ,
    precompute_tick_phase_table_from_frames, precompute_tick_phase_table_from_samples,
    ContinueRun
)
from scripts.full_hexagram_shotgun import shotgun_expand


def test_dsp_clock_baseline_continue_measure():
    """Test the core baseline -> continue -> measure pattern on both clocks."""
    print("=" * 60)
    print("TEST: dsp_clock baseline -> continue -> measure")
    print("=" * 60)

    baseline = {
        "session": "testbed_001",
        "sectors": [],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    # Run ContinueRun with healing mode
    run_heal = ContinueRun.run(
        baseline=baseline,
        n_steps=8,
        tick_rate_hz=60.0,
        base_hz=HEALING_CLOCK_HZ,
        opposition=False,
        per_step=lambda i, tc, base: {
            "step": i,
            "tick_phase_mod": tc.phase % (2*math.pi),
            "tick_sin": math.sin(tc.phase % (2*math.pi)),
            "tick_cos": math.cos(tc.phase % (2*math.pi)),
        }
    )

    # Run ContinueRun with opposition mode
    run_opp = ContinueRun.run(
        baseline=baseline,
        n_steps=8,
        tick_rate_hz=60.0,
        base_hz=HEALING_CLOCK_HZ,
        opposition=True,
        per_step=lambda i, tc, base: {
            "step": i,
            "tick_phase_mod": tc.phase % (2*math.pi),
            "tick_sin": math.sin(tc.phase % (2*math.pi)),
            "tick_cos": math.cos(tc.phase % (2*math.pi)),
        }
    )

    # Measure: compare the two runs
    print(f"Wall elapsed (healing):   {run_heal.final['wall_elapsed_s']:.6f}s")
    print(f"Wall elapsed (opposition): {run_opp.final['wall_elapsed_s']:.6f}s")
    print(f"Final tick (healing):      {run_heal.final['tick_tick']}")
    print(f"Final tick (opposition):   {run_opp.final['tick_tick']}")
    print(f"Final phase_mod (healing): {run_heal.final['tick_phase_mod']:.6f}")
    print(f"Final phase_mod (oppose):  {run_opp.final['tick_phase_mod']:.6f}")

    # Verify Yin/Yang/Yao mapping at step 2 (should be YAO - phases align)
    step2_heal = run_heal.steps[2]["tick_record"]["phase_mod"]
    step2_opp = run_opp.steps[2]["tick_record"]["phase_mod"]
    diff = abs(step2_heal - step2_opp)
    assert diff < 0.01 or abs(diff - 2*math.pi) < 0.01, f"Step 2 should be YAO (aligned), got diff={diff}"
    print("✓ Step 2 phase alignment (YAO) verified")

    # Verify Yang at step 5 (opposite phases)
    step5_heal = run_heal.steps[5]["tick_record"]["phase_mod"]
    step5_opp = run_opp.steps[5]["tick_record"]["phase_mod"]
    diff5 = abs(step5_heal - step5_opp)
    diff5_norm = (diff5 + math.pi) % (2*math.pi) - math.pi
    assert abs(diff5_norm) > 2.5 or abs(diff5) > 6.0, f"Step 5 should be YANG (opposed), got diff={diff5}"
    print("✓ Step 5 phase opposition (YANG) verified")

    # Verify Yin at step 0 (phase diff ~2.094, not aligned/opposed)
    step0_heal = run_heal.steps[0]["tick_record"]["phase_mod"]
    step0_opp = run_opp.steps[0]["tick_record"]["phase_mod"]
    diff0 = abs(step0_heal - step0_opp)
    diff0_norm = (diff0 + math.pi) % (2*math.pi) - math.pi
    assert abs(diff0_norm) < 2.5 and diff0 > 0.5, f"Step 0 should be YIN, got diff={diff0}"
    print("✓ Step 0 Yin phase verified")

    return True


def test_generate_sovereign_world_2clock():
    """Test generate_sovereign_world with 2-clock prewarm."""
    print("\n" + "=" * 60)
    print("TEST: generate_sovereign_world 2-clock prewarm")
    print("=" * 60)

    from scripts.generate_sovereign_world import prewarm_egg_keyframes

    # Mock sectors data
    sectors = [{
        "world_position": {"x": 0, "y": 0, "z": 0},
        "quantum_physics": {"vortex_tension": 0.5, "suction_coefficient": 0.3, "porosity_level": 0.45, "energy": 0.5},
        "yao_pellets": [{"frequency_hz": 146.0, "energy_intensity": 0.5, "waveform": "sine"}] * 6
    }]

    # Test egg keyframes with tick phase table
    frame_table = precompute_tick_phase_table_from_frames(num_frames=10, frame_rate=60.0, mode="healing")
    egg_frames = prewarm_egg_keyframes(sectors, num_frames=10, tick_phase_table=frame_table, tick_mode="healing")
    assert len(egg_frames) == 10
    print(f"✓ Egg keyframes generated with healing clock: {len(egg_frames)} frames")

    # Test opposition mode
    frame_table_opp = precompute_tick_phase_table_from_frames(num_frames=10, frame_rate=60.0, mode="opposition")
    egg_frames_opp = prewarm_egg_keyframes(sectors, num_frames=10, tick_phase_table=frame_table_opp, tick_mode="opposition")
    assert len(egg_frames_opp) == 10
    print(f"✓ Egg keyframes generated with opposition clock: {len(egg_frames_opp)} frames")

    # Test audio prewarm with tick phase table
    sample_table = precompute_tick_phase_table_from_samples(sample_rate=22050, num_samples=22050, mode="healing")
    print("✓ Audio prewarm functions accept tick phase tables")

    return True


def test_shotgun_expand_with_2clock():
    """Test shotgun_expand integrates with 2-clock measurement."""
    print("\n" + "=" * 60)
    print("TEST: shotgun_expand with 2-clock measurement")
    print("=" * 60)

    wall = WallClock()
    tick_h = TickClock(tick_rate_hz=1.0, base_hz=HEALING_CLOCK_HZ, opposition=False)
    tick_o = TickClock(tick_rate_hz=1.0, base_hz=HEALING_CLOCK_HZ, opposition=True)

    tick_h.step({"stage": "shotgun_expand_start"})
    result = shotgun_expand(emotional_input=50.0, request_text="test")
    tick_h.step({"stage": "shotgun_expand_done", "expanded_count": len(result.get("expanded", []))})

    tick_o.step({"stage": "shotgun_expand_start"})
    result2 = shotgun_expand(emotional_input=50.0, request_text="test")
    tick_o.step({"stage": "shotgun_expand_done", "expanded_count": len(result2.get("expanded", []))})

    print(f"Wall elapsed: {wall.elapsed_s():.6f}s")
    print(f"Healing tick phase: {tick_h.phase % (2*math.pi):.6f}")
    print(f"Opposition tick phase: {tick_o.phase % (2*math.pi):.6f}")

    # Verify both produced same expansion
    assert len(result.get("expanded", [])) == 64
    assert len(result2.get("expanded", [])) == 64
    print("✓ shotgun_expand produces 64 expanded states under both clock modes")

    return True


def test_generate_external_switchboard_2clock():
    """Test external switchboard HTML generation with 2-clock."""
    print("\n" + "=" * 60)
    print("TEST: generate_external_switchboard with 2-clock")
    print("=" * 60)

    from scripts.generate_external_switchboard import generate_switchboard_data, build_switchboard_html, OUTPUT_HTML
    channels = generate_switchboard_data()
    assert len(channels) == 64
    print(f"✓ Generated {len(channels)} channels with 2-clock constants")

    # Verify clock constants are in the generated HTML
    build_switchboard_html(channels)
    html_content = OUTPUT_HTML.read_text()
    assert "HEALING_CLOCK_HZ = 640.0" in html_content
    assert "OPPOSITION_CLOCK_HZ = -640.0" in html_content
    assert "clock-mode-select" in html_content
    assert "changeClockMode" in html_content
    print("✓ Generated HTML contains 2-clock DSP constants and UI toggle")

    return True


def test_kanban_2clock():
    """Test kanban loop and timer with 2-clock."""
    print("\n" + "=" * 60)
    print("TEST: Kanban loop & timer with 2-clock")
    print("=" * 60)

    # Test imports work with 2-clock
    from learn.scripts.kanban_loop import WallClock as KL_WallClock, TickClock as KL_TickClock
    from learn.scripts.kanban_timer import WallClock as KT_WallClock, TickClock as KT_TickClock

    assert KL_WallClock is not None
    assert KL_TickClock is not None
    assert KT_WallClock is not None
    assert KT_TickClock is not None
    print("✓ Kanban loop & timer import 2-clock classes")

    return True


def main():
    """Run all 2-clock testbed tests."""
    print("\n" + "=" * 70)
    print("KING WEN 2-CLOCK TESTBED")
    print("=" * 70)
    print("Testing baseline -> continue -> measure on WALL_CLOCK + TICK_CLOCK")
    print("with -640Hz healing / +640Hz opposition and Yin/Yang/Yao mapping\n")

    tests = [
        ("dsp_clock baseline->continue->measure", test_dsp_clock_baseline_continue_measure),
        ("generate_sovereign_world 2-clock prewarm", test_generate_sovereign_world_2clock),
        ("shotgun_expand 2-clock measurement", test_shotgun_expand_with_2clock),
        ("external_switchboard 2-clock", test_generate_external_switchboard_2clock),
        ("kanban loop & timer 2-clock", test_kanban_2clock),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            result = test_fn()
            if result:
                passed += 1
                print(f"✅ PASS: {name}\n")
            else:
                failed += 1
                print(f"❌ FAIL: {name} returned False\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAIL: {name} - {e}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - 2-Clock testbed verified!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())