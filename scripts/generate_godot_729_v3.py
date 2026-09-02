#!/usr/bin/env python3
"""Generate Godot 4.x scenes for King Wen 729 ternary permutations.

Each hexagram scene contains 729 permutation nodes.
Each permutation renders 6 yao lines as 3D box meshes with:
- Yin (broken): two short segments
- Yang (solid): one long segment  
- Yao (changing): dashed/dotted pattern

Materials are driven by emotional vector from shotgun_expand().
Uses oracle GLB models as reference for visual style.

Total: 64 hexagrams x 729 permutations = 46,656 nodes.
"""

import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GODOT_DIR = ROOT / "godot"
ASSETS = ROOT / "DATASETS"
ORACLE = Path("/c/Users/krist/Desktop/oracle/src/3D")

# Create directories
(GODOT_DIR / "scenes" / "hexagrams").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scenes" / "world").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scripts").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "meshes").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "materials").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "models").mkdir(parents=True, exist_ok=True)

VOID_HEXES = {15, 20, 30, 40}

sys.path.insert(0, str(ROOT))
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS
from scripts.full_hexagram_shotgun import shotgun_expand


def generate_project_godot() -> str:
    return """; Engine configuration file.
config_version=5

[application]

config/name="King Wen 729 Ternary World"
config/description="46,656 ternary line-state permutations"
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

@export var current_hex_id: int = 1
@export var show_all_permutations: bool = false

var hex_nodes: Array[Node3D] = []

func _ready():
	print("King Wen 729 Ternary World initializing...")
	_discover_hexagrams()
	print(f"Loaded {hex_nodes.size()} hexagrams")

func _discover_hexagrams():
	hex_nodes.clear()
	var grid = get_node_or_null("HexagramGrid")
	if not grid:
		push_error("HexagramGrid not found")
		return
	
	for child in grid.get_children():
		if child.has_meta("hexagram_id"):
			hex_nodes.append(child)

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
		info_label.text = "Hexagram: %d | Show All: %s" % [
			current_hex_id,
			"ON" if show_all_permutations else "OFF"
		]
'''


def generate_hexagram_scene_tscn(hex_id: int, emotional_vector: dict) -> str:
    """Generate a .tscn scene for a hexagram with 729 permutation nodes."""
    hex_info = HEXAGRAM_BASE.get(hex_id, {})
    name = hex_info.get("name", f"Hexagram {hex_id}")
    category = hex_info.get("category", "sovereign")
    action = hex_info.get("action", "ASSERT")
    unicode_glyph = hex_info.get("unicode", "")
    binary = hex_info.get("binary_bottom_to_top", "111111")
    upper_trigram = hex_info.get("upper_trigram", "")
    lower_trigram = hex_info.get("lower_trigram", "")
    
    is_void = hex_id in VOID_HEXES
    
    # Category color
    cat_colors = {
        "sovereign": (0.788, 0.659, 0.298),
        "transformer": (0.310, 0.788, 0.659),
        "dissipator": (0.788, 0.310, 0.431),
        "boundary": (0.431, 0.620, 0.788),
    }
    base_r, base_g, base_b = cat_colors.get(category, (0.8, 0.8, 0.8))
    
    # Emotional modulation
    chaos = emotional_vector.get('chaos', 0.1)
    whimsy = emotional_vector.get('whimsy', 0.2)
    dark_tone = emotional_vector.get('darkTone', 0.1)
    coherence = emotional_vector.get('coherence', 0.85)
    voice_weight = emotional_vector.get('voiceWeight', 0.85)
    
    # Generate permutation nodes
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
            
            # Color based on emotional state
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
; Emotional: C={chaos:.2f} W={whimsy:.2f} D={dark_tone:.2f} Co={coherence:.2f} V={voice_weight:.2f}
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
{chr(10).join(perm_nodes)}
'''
    return scene


def generate_materials(hex_id: int, emotional_vector: dict):
    """Generate .tres material files for all 729 permutations of a hexagram."""
    hex_info = HEXAGRAM_BASE.get(hex_id, {})
    category = hex_info.get("category", "sovereign")
    
    cat_colors = {
        "sovereign": (0.788, 0.659, 0.298),
        "transformer": (0.310, 0.788, 0.659),
        "dissipator": (0.788, 0.310, 0.431),
        "boundary": (0.431, 0.620, 0.788),
    }
    base_r, base_g, base_b = cat_colors.get(category, (0.8, 0.8, 0.8))
    
    chaos = emotional_vector.get('chaos', 0.1)
    whimsy = emotional_vector.get('whimsy', 0.2)
    dark_tone = emotional_vector.get('darkTone', 0.1)
    coherence = emotional_vector.get('coherence', 0.85)
    voice_weight = emotional_vector.get('voiceWeight', 0.85)
    
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
    print("Generating Godot 729 Ternary World from shotgun_expand()...")
    
    # 1. Get shotgun data
    print("  Running shotgun_expand()...")
    shotgun_data = shotgun_expand(emotional_input=50)
    
    expanded = shotgun_data.get('expanded', [])
    personality = shotgun_data.get('personality_consensus', {})
    
    print(f"  Got {len(expanded)} expanded hexagrams")
    
    # Default emotional vector
    emotional_vector = {
        'chaos': personality.get('chaos', 0.1),
        'whimsy': personality.get('whimsy', 0.2),
        'dark_tone': personality.get('dark_tone', 0.1),
        'coherence': personality.get('coherence', 0.85),
        'voice_weight': personality.get('voice_weight', 0.85),
    }
    
    # 2. project.godot
    (GODOT_DIR / "project.godot").write_text(generate_project_godot(), encoding='utf-8')
    print("  Wrote project.godot")
    
    # 3. Scripts
    (GODOT_DIR / "scripts" / "yao_line.gd").write_text(generate_yao_line_script(), encoding='utf-8')
    (GODOT_DIR / "scripts" / "hexagram_controller.gd").write_text(generate_hexagram_controller_script(), encoding='utf-8')
    (GODOT_DIR / "scripts" / "kingwen_729_controller.gd").write_text(generate_world_controller_script(), encoding='utf-8')
    print("  Wrote 3 GDScripts")
    
    # 4. Generate hexagram scenes with 729 permutations each
    print("  Generating hexagram scenes...")
    
    for hex_data in expanded:
        hex_id = hex_data.get('hexagram_id', 1)
        
        # Generate scene
        scene_content = generate_hexagram_scene_tscn(hex_id, emotional_vector)
        scene_path = GODOT_DIR / "scenes" / "hexagrams" / f"hex_{hex_id:02d}.tscn"
        scene_path.write_text(scene_content, encoding='utf-8')
        
        # Generate materials
        generate_materials(hex_id, emotional_vector)
        
        if hex_id % 10 == 0:
            print(f"    Generated hexagram {hex_id}/64")
    
    print(f"  Generated 64 hexagram scenes with 729 permutations each")
    
    # 5. Generate world scene
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


if __name__ == "__main__":
    main()
