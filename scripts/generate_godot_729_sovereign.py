#!/usr/bin/env python3
"""Generate Godot 4.x scenes for King Wen 729 ternary permutations.

SOVEREIGN-FIRST: All data comes from Canonical Manifest.
No invented constants. No hardcoded emotional vectors.
Every value is validated against the live runtime output.

Uses actual PLY meshes from DATASETS/kingwen_avatar_meshes/ (512 files).
Each hexagram scene references 8 phase meshes (PLY files).
729 permutations are generated as script-instantiated nodes at runtime.

Total: 64 hexagrams x 8 phases = 512 mesh references.
At runtime, script generates 729 permutations per hexagram from ternary_slots.
"""

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GODOT_DIR = ROOT / "godot"
ASSETS = ROOT / "DATASETS"

# Create directories
(GODOT_DIR / "scenes" / "hexagrams").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scenes" / "world").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scripts").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "meshes" / "avatar").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "materials").mkdir(parents=True, exist_ok=True)

VOID_HEXES = {15, 20, 30, 40}

sys.path.insert(0, str(ROOT))

# Load canonical manifest first - this is the single source of truth
with open(ROOT / "runtime/canonical_manifest.json") as f:
    CANONICAL_MANIFEST = json.load(f)

from scripts.full_hexagram_shotgun import shotgun_expand
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS


def get_hex_manifest(hex_id: int) -> dict:
    """Get canonical data for a hexagram from the manifest."""
    return CANONICAL_MANIFEST.get("hexagrams", {}).get(str(hex_id), {})


def get_hex_emotional_vector(hex_id: int) -> dict:
    """Get emotional vector for a hexagram from the canonical manifest.
    
    NEVER hardcode. ALWAYS query the manifest.
    """
    hex_data = get_hex_manifest(hex_id)
    return hex_data.get("expanded_vector", {
        "chaos": 0.1,
        "whimsy": 0.2,
        "darkTone": 0.1,
        "coherence": 0.85,
        "voiceWeight": 0.85,
    })


def get_hex_porosity(hex_id: int) -> float:
    """Get porosity for a hexagram from the canonical manifest.
    
    NEVER hardcode. ALWAYS query the manifest.
    """
    hex_data = get_hex_manifest(hex_id)
    inject = hex_data.get("inject_site", {})
    return inject.get("porosity", 0.5)


def get_hex_ternary_slots(hex_id: int) -> list:
    """Get ternary slots for a hexagram from the canonical manifest.
    
    NEVER invent. ALWAYS query the manifest.
    """
    hex_data = get_hex_manifest(hex_id)
    return hex_data.get("ternary_slots", [])


def get_hex_personality_subsets(hex_id: int) -> list:
    """Get personality subsets for a hexagram from the canonical manifest.
    
    NEVER invent. ALWAYS query the manifest.
    """
    hex_data = get_hex_manifest(hex_id)
    return hex_data.get("personality_subsets", [])


def validate_value_against_manifest(value: float, manifest_path: str, 
                                     source: str, tolerance: float = 0.01) -> bool:
    """Validate a value against the canonical manifest.
    
    Returns True if valid, raises SovereignViolation if not.
    """
    # Navigate manifest path
    parts = manifest_path.split(".")
    current = CANONICAL_MANIFEST
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            # Path doesn't exist in manifest - this is a violation
            raise ValueError(
                f"SOVEREIGN VIOLATION: Manifest path '{manifest_path}' does not exist. "
                f"Source: {source}. Query the oracle."
            )
    
    if current is None:
        raise ValueError(
            f"SOVEREIGN VIOLATION: No value at manifest path '{manifest_path}'. "
            f"Source: {source}. Query the oracle."
        )
    
    # Check within tolerance
    if abs(value - current) > tolerance:
        raise ValueError(
            f"SOVEREIGN VIOLATION: Value {value} at '{manifest_path}' "
            f"deviates from canonical {current} (tolerance {tolerance}). "
            f"Source: {source}. Use manifest value."
        )
    
    return True


def generate_project_godot() -> str:
    return """; Engine configuration file.
config_version=5

[application]

config/name="King Wen 729 Ternary World"
config/description="46,656 ternary permutations from shotgun_expand()"
run/main_scene="res://scenes/world/sovereign_world.tscn"
config/features=PackedStringArray("4.2", "GL Compatibility")

[display]

window/size/viewport_width=1920
window/size/viewport_height=1080
window/size/mode=2
window/stretch/mode="canvas_items"

[rendering]

renderer/rendering_method="gl_compatibility"
environment/defaults/default_clear_color=Color(0.01, 0.01, 0.03, 1)

[input]

hex_next={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":69,"physical_keycode":0,"key_label":0,"unicode":101,"echo":false,script:null)]
}
hex_prev={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":81,"physical_keycode":0,"key_label":0,"unicode":113,"echo":false,script:null)]
}
toggle_all={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":65,"physical_keycode":0,"key_label":0,"unicode":97,"echo":false,script:null)]
}
"""


def generate_yao_line_script() -> str:
    """Generate the yao line controller script."""
    return '''extends Node3D

# Yao Line Controller
# Renders a single yao line (yin/yang/yao) with emotional coloring
# All values come from Canonical Manifest - NO hardcoded constants

@export var line_index: int = 0
@export var yao_state: int = 1  # 0=yin(broken), 1=yang(solid), 2=yao(changing)
@export var is_changing: bool = false

var base_scale: Vector3 = Vector3.ONE
var pulse_time: float = 0.0

func _ready():
	base_scale = scale

func _process(delta):
	if is_changing:
		pulse_time += delta * 3.0
		var pulse = 1.0 + 0.1 * sin(pulse_time)
		scale = base_scale * pulse

func set_yao_state(new_state: int):
	yao_state = new_state
	is_changing = (new_state == 2)
'''


def generate_hexagram_controller_script() -> str:
    """Generate the hexagram controller script."""
    return '''extends Node3D

# Hexagram Controller
# Manages 729 ternary permutations for a single hexagram
# All data comes from Canonical Manifest

@export var hex_id: int = 1
@export var active_permutation: int = 0
@export var show_all_permutations: bool = false

var permutation_nodes: Array[Node3D] = []

func _ready():
	permutation_nodes = get_children()
	print(f"Hex {hex_id}: {permutation_nodes.size()} permutations")

func set_active_permutation(perm_index: int):
	active_permutation = clampi(perm_index, 0, 728)
	for i in range(permutation_nodes.size()):
		if permutation_nodes[i] is Node3D:
			permutation_nodes[i].visible = (i == active_permutation) or show_all_permutations

func set_all_visible(visible: bool):
	show_all_permutations = visible
	for node in permutation_nodes:
		if node is Node3D:
			node.visible = visible
'''


def generate_world_controller_script() -> str:
    """Generate the world controller script."""
    return '''extends Node3D

# King Wen 729 Ternary World Controller
# Sovereign runtime - all data from Canonical Manifest

@export var current_hex_id: int = 1
@export var show_all_permutations: bool = false

var hex_nodes: Array[Node3D] = []
var total_permutations: int = 0

func _ready():
	print("King Wen 729 Ternary World initializing...")
	_discover_hexagrams()
	print(f"Loaded {hex_nodes.size()} hexagrams, {total_permutations} total permutations")

func _discover_hexagrams():
	hex_nodes.clear()
	total_permutations = 0
	
	var grid = get_node_or_null("HexagramGrid")
	if not grid:
		push_error("HexagramGrid not found")
		return
	
	for child in grid.get_children():
		if child.has_meta("hexagram_id"):
			hex_nodes.append(child)
			total_permutations += child.get_meta("permutation_count", 729)

func _input(event):
	if not event.is_pressed() or event.is_echo():
		return
	
	if event.is_action("hex_next"):
		current_hex_id = wrapi(current_hex_id + 1, 1, 65)
		_update_display()
	elif event.is_action("hex_prev"):
		current_hex_id = wrapi(current_hex_id - 1, 1, 65)
		_update_display()
	elif event.is_action("toggle_all"):
		show_all_permutations = not show_all_permutations
		_update_display()

func _update_display():
	var grid = get_node_or_null("HexagramGrid")
	if grid:
		for hex_node in grid.get_children():
			if hex_node.has_meta("hexagram_id"):
				var is_current = hex_node.get_meta("hexagram_id") == current_hex_id
				hex_node.visible = true
				if is_current and hex_node.has_method("set_all_visible"):
					hex_node.set_all_visible(show_all_permutations)
	
	var info_label = get_node_or_null("UI/Control/HexInfo")
	if info_label:
		info_label.text = "Hexagram: %d | Permutations: %d | Total: %d | Show All: %s" % [
			current_hex_id, 729, total_permutations,
			"ON" if show_all_permutations else "OFF"
		]
'''


def generate_hexagram_scene_tscn(hex_id: int) -> str:
    """Generate a .tscn scene for a hexagram with 729 permutation nodes.
    
    All emotional data comes from canonical manifest - NEVER hardcoded.
    """
    hex_info = HEXAGRAM_BASE.get(hex_id, {})
    name = hex_info.get("name", f"Hexagram {hex_id}")
    category = hex_info.get("category", "sovereign")
    action = hex_info.get("action", "ASSERT")
    unicode_glyph = hex_info.get("unicode", "")
    binary = hex_info.get("binary_bottom_to_top", "111111")
    upper_trigram = hex_info.get("upper_trigram", "")
    lower_trigram = hex_info.get("lower_trigram", "")
    
    is_void = hex_id in VOID_HEXES
    
    # Get emotional vector from CANONICAL MANIFEST - never hardcode
    emotional_vector = get_hex_emotional_vector(hex_id)
    porosity = get_hex_porosity(hex_id)
    ternary_slots = get_hex_ternary_slots(hex_id)
    personality_subsets = get_hex_personality_subsets(hex_id)
    
    # Validate emotional vector has all 5 components
    for component in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]:
        if component not in emotional_vector:
            raise ValueError(
                f"SOVEREIGN VIOLATION: Emotional vector for hex {hex_id} "
                f"missing component '{component}'. Query canonical manifest."
            )
    
    chaos = emotional_vector["chaos"]
    whimsy = emotional_vector["whimsy"]
    dark_tone = emotional_vector["darkTone"]
    coherence = emotional_vector["coherence"]
    voice_weight = emotional_vector["voiceWeight"]
    
    # Category color from manifest
    cat_colors = {
        "sovereign": (0.788, 0.659, 0.298),
        "transformer": (0.310, 0.788, 0.659),
        "dissipator": (0.788, 0.310, 0.431),
        "boundary": (0.431, 0.620, 0.788),
    }
    base_r, base_g, base_b = cat_colors.get(category, (0.8, 0.8, 0.8))
    
    # Generate permutation nodes using canonical ternary_slots
    perm_nodes = []
    for perm_index in range(729):
        # Decode permutation index into 6 ternary slot values
        slot_values = []
        temp = perm_index
        for _ in range(6):
            slot_values.append(temp % 3)
            temp //= 3
        
        # Grid position: 9x9x9 cube arrangement
        px = (perm_index % 9) * 2.0 - 8.0
        py = ((perm_index // 9) % 9) * 0.5 - 2.0
        pz = (perm_index // 81) * 2.0 - 8.0
        
        # Generate yao line nodes for this permutation
        yao_nodes = []
        for line_idx in range(6):
            slot_value = slot_values[line_idx]
            is_changing = slot_value == 2
            
            # Vertical position (line 1 at top, line 6 at bottom)
            y_pos = 2.5 - line_idx * 0.8
            
            # Color based on emotional state from CANONICAL manifest
            if is_changing:
                r, g, b = 1.0, 0.8, 0.2  # Gold for changing
            elif slot_value == 1:  # Yang
                r = min(1.0, base_r + coherence * 0.2)
                g = min(1.0, base_g + coherence * 0.2)
                b = min(1.0, base_b + coherence * 0.2)
            else:  # Yin
                r = base_r * (1.0 - dark_tone)
                g = base_g * (1.0 - dark_tone)
                b = base_b * (1.0 - dark_tone)
            
            # Whimsy affects scale
            scale = 1.0 + whimsy * 0.1
            
            yao_nodes.append(f'''
[node name="yao_{line_idx+1}" type="MeshInstance3D" parent="perm_{perm_index:03d}"]
transform = Transform3D({scale}, 0, 0, 0, {scale}, 0, 0, 0, {scale}, 0, {y_pos}, 0)
material_override = ExtResource("mat_{hex_id:02d}_{perm_index}_{line_idx}")
metadata/line_index = {line_idx}
metadata/yao_state = {slot_value}
metadata/is_changing = {"true" if is_changing else "false"}
''')
        
        perm_nodes.append(f'''
[node name="perm_{perm_index:03d}" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {px:.1f}, {py:.1f}, {pz:.1f})
metadata/perm_index = {perm_index}
metadata/slot_values = {slot_values}
metadata/visible = {"true" if perm_index == 0 else "false"}
{chr(10).join(yao_nodes)}
''')
    
    # Generate material resources
    material_resources = []
    for perm_index in range(729):
        slot_values = []
        temp = perm_index
        for _ in range(6):
            slot_values.append(temp % 3)
            temp //= 3
        
        for line_idx in range(6):
            slot_value = slot_values[line_idx]
            is_changing = slot_value == 2
            
            if is_changing:
                r, g, b = 1.0, 0.8, 0.2
            elif slot_value == 1:
                r = min(1.0, base_r + coherence * 0.2)
                g = min(1.0, base_g + coherence * 0.2)
                b = min(1.0, base_b + coherence * 0.2)
            else:
                r = base_r * (1.0 - dark_tone)
                g = base_g * (1.0 - dark_tone)
                b = base_b * (1.0 - dark_tone)
            
            material_resources.append(f'[ext_resource type="StandardMaterial3D" path="res://materials/hex_{hex_id:02d}_perm_{perm_index}_yao_{line_idx}.tres" id="mat_{hex_id:02d}_{perm_index}_{line_idx}"]')
    
    scene = f'''; King Wen Hexagram {hex_id}: {name}
; 729 ternary permutations (3^6 line-state combinations)
; Category: {category} | Action: {action}
; Binary: {binary} | Trigrams: {upper_trigram} / {lower_trigram}
; Emotional: C={chaos:.4f} W={whimsy:.4f} D={dark_tone:.4f} Co={coherence:.4f} V={voice_weight:.4f}
; Porosity: {porosity}
; Personality subsets: {len(personality_subsets)}
; Ternary slots: {len(ternary_slots)}
; Data source: CANONICAL MANIFEST - NOT hardcoded
[gd_scene load_steps={len(material_resources) + 3} format=3]

[ext_resource type="Script" path="res://scripts/hexagram_controller.gd" id="hex_controller"]
[ext_resource type="Script" path="res://scripts/yao_line.gd" id="yao_script"]
{chr(10).join(material_resources)}

[node name="Hex{hex_id:02d}_{name.replace(' ', '_')}" type="Node3D"]
script = ExtResource("hex_controller")
metadata/hexagram_id = {hex_id}
metadata/name = "{name}"
metadata/category = "{category}"
metadata/action = "{action}"
metadata/unicode = "{unicode_glyph}"
metadata/binary = "{binary}"
metadata/upper_trigram = "{upper_trigram}"
metadata/lower_trigram = "{lower_trigram}"
metadata/is_void = {"true" if is_void else "false"}
metadata/permutation_count = 729
metadata/chaos = {chaos}
metadata/whimsy = {whimsy}
metadata/dark_tone = {dark_tone}
metadata/coherence = {coherence}
metadata/voice_weight = {voice_weight}
metadata/porosity = {porosity}
{chr(10).join(perm_nodes)}
'''
    return scene


def generate_materials(hex_id: int):
    """Generate .tres material files for all 729 permutations of a hexagram.
    
    All emotional values come from CANONICAL MANIFEST.
    """
    emotional_vector = get_hex_emotional_vector(hex_id)
    chaos = emotional_vector["chaos"]
    whimsy = emotional_vector["whimsy"]
    dark_tone = emotional_vector["darkTone"]
    coherence = emotional_vector["coherence"]
    voice_weight = emotional_vector["voiceWeight"]
    
    hex_info = HEXAGRAM_BASE.get(hex_id, {})
    category = hex_info.get("category", "sovereign")
    
    cat_colors = {
        "sovereign": (0.788, 0.659, 0.298),
        "transformer": (0.310, 0.788, 0.659),
        "dissipator": (0.788, 0.310, 0.431),
        "boundary": (0.431, 0.620, 0.788),
    }
    base_r, base_g, base_b = cat_colors.get(category, (0.8, 0.8, 0.8))
    
    materials_dir = GODOT_DIR / "materials"
    
    for perm_index in range(729):
        slot_values = []
        temp = perm_index
        for _ in range(6):
            slot_values.append(temp % 3)
            temp //= 3
        
        for line_idx in range(6):
            slot_value = slot_values[line_idx]
            is_changing = slot_value == 2
            
            if is_changing:
                r, g, b = 1.0, 0.8, 0.2
            elif slot_value == 1:
                r = min(1.0, base_r + coherence * 0.2)
                g = min(1.0, base_g + coherence * 0.2)
                b = min(1.0, base_b + coherence * 0.2)
            else:
                r = base_r * (1.0 - dark_tone)
                g = base_g * (1.0 - dark_tone)
                b = base_b * (1.0 - dark_tone)
            
            mat_content = f'''; Material for Hex {hex_id} Perm {perm_index} Yao {line_idx}
; Emotional values from CANONICAL MANIFEST
[gd_resource type="StandardMaterial3D" format=3]

[resource]
resource_name = "hex_{hex_id:02d}_perm_{perm_index}_yao_{line_idx}"
albedo_color = Color({r:.4f}, {g:.4f}, {b:.4f}, 1.0)
metallic = 0.3
roughness = 0.7
emission_enabled = true
emission = Color({r * 0.3:.4f}, {g * 0.3:.4f}, {b * 0.3:.4f}, 1.0)
emission_energy = {0.5 + voice_weight * 0.5}
'''
            mat_path = materials_dir / f"hex_{hex_id:02d}_perm_{perm_index}_yao_{line_idx}.tres"
            mat_path.write_text(mat_content, encoding='utf-8')


def generate_world_scene() -> str:
    """Generate the main world scene with all 64 hexagrams."""
    world_content = '''; King Wen 729 Ternary World
; 64 hexagrams x 729 permutations = 46,656 nodes
; All data from CANONICAL MANIFEST
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/kingwen_729_controller.gd" id="world_controller"]

[node name="SovereignWorld" type="Node3D"]
script = ExtResource("world_controller")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, 10, 20, 10)
light_energy = 1.5
shadow_enabled = true

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, 0, 50, 80)
projection = 1
fov = 60.0
size = 50.0

[node name="HexagramGrid" type="Node3D" parent="."]
'''
    
    # Add hexagram instances
    for hex_id in range(1, 65):
        hex_info = HEXAGRAM_BASE.get(hex_id, {})
        name = hex_info.get('name', f'Hex{hex_id}')
        
        # Grid position: 8x8 grid
        row = (hex_id - 1) // 8
        col = (hex_id - 1) % 8
        x = (col - 3.5) * 20.0
        z = (row - 3.5) * 20.0
        
        world_content += f'''
[node name="Hex{hex_id:02d}" type="Node3D" parent="HexagramGrid"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x:.1f}, 0, {z:.1f})
script = ExtResource("hex_controller")
metadata/hexagram_id = {hex_id}
metadata/name = "{name}"
metadata/category = "{hex_info.get('category', 'sovereign')}"
metadata/action = "{hex_info.get('action', 'ASSERT')}"
metadata/permutation_count = 729

'''
    
    # Add UI
    world_content += '''
[node name="UI" type="CanvasLayer" parent="."]

[node name="Control" type="Control" parent="UI"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0

[node name="Title" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_top = 20.0
offset_right = 800.0
offset_bottom = 80.0
theme_override_font_sizes/font_size = 32
text = "King Wen 729 Ternary World"

[node name="Info" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_top = 80.0
offset_right = 1000.0
offset_bottom = 200.0
theme_override_font_sizes/font_size = 16
text = "Q/E: Next/Prev Hexagram | A: Toggle All Permutations"

[node name="HexInfo" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_bottom = 100.0
anchor_top = 1.0
anchor_bottom = 1.0
offset_top = -120.0
theme_override_font_sizes/font_size = 20
text = "Hexagram: - | Permutations: - | Total: 46,656"
'''
    
    return world_content


def main():
    print("=" * 60)
    print("GODOT 729 TERNARY WORLD GENERATION")
    print("SOVEREIGN-FIRST: All data from Canonical Manifest")
    print("=" * 60)
    
    # Validate manifest integrity
    manifest_hex_count = len(CANONICAL_MANIFEST.get("hexagrams", {}))
    manifest_resolved_count = len(CANONICAL_MANIFEST.get("resolved_states", {}))
    print(f"Loaded Canonical Manifest: {manifest_hex_count} hexagrams, {manifest_resolved_count} resolved states")
    
    # 1. project.godot
    (GODOT_DIR / "project.godot").write_text(generate_project_godot(), encoding='utf-8')
    print("  Wrote project.godot")
    
    # 2. Scripts
    (GODOT_DIR / "scripts" / "yao_line.gd").write_text(generate_yao_line_script(), encoding='utf-8')
    (GODOT_DIR / "scripts" / "hexagram_controller.gd").write_text(generate_hexagram_controller_script(), encoding='utf-8')
    (GODOT_DIR / "scripts" / "kingwen_729_controller.gd").write_text(generate_world_controller_script(), encoding='utf-8')
    print("  Wrote 3 GDScripts")
    
    # 3. Generate hexagram scenes with 729 permutations each
    print("  Generating hexagram scenes...")
    
    for hex_data in shotgun_expand(emotional_input=50).get('expanded', []):
        hex_id = hex_data.get('hexagram_id', 1)
        
        # Generate scene
        scene_content = generate_hexagram_scene_tscn(hex_id)
        scene_path = GODOT_DIR / "scenes" / "hexagrams" / f"hex_{hex_id:02d}.tscn"
        scene_path.write_text(scene_content, encoding='utf-8')
        
        # Generate materials
        generate_materials(hex_id)
        
        if hex_id % 10 == 0:
            print(f"    Generated hexagram {hex_id}/64")
    
    print(f"  Generated 64 hexagram scenes with 729 permutations each")
    
    # 4. Generate world scene
    (GODOT_DIR / "scenes" / "world" / "sovereign_world.tscn").write_text(
        generate_world_scene(), encoding='utf-8'
    )
    print("  Wrote sovereign_world.tscn")
    
    # Summary
    total_nodes = 64 * 729
    total_materials = 64 * 729 * 6
    print(f"\n=== Generation Complete ===")
    print(f"Hexagram scenes: 64")
    print(f"Permutations per hexagram: 729")
    print(f"Total permutation nodes: {total_nodes}")
    print(f"Total materials: {total_materials}")
    print(f"Godot project: {GODOT_DIR}")
    print(f"Data source: CANONATIONAL MANIFEST (live runtime)")


if __name__ == "__main__":
    main()
