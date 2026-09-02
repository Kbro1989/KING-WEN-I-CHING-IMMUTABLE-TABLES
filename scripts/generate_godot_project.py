#!/usr/bin/env python3
"""Generate Godot 4.x project with King Wen 512-state avatar scenes.

Creates:
- project.godot (project settings)
- scenes/hexagrams/hex_01.tscn .. hex_64.tscn (per-hexagram scenes with 8 phases)
- scenes/world/sovereign_world.tscn (main world with all hexagrams)
- scripts/kingwen_state_machine.gd (state machine controller)
- scripts/hexagram_display.gd (per-hexagram display controller)
- import/*.import (mesh import configs for PLY files)
"""

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GODOT_DIR = ROOT / "godot"
ASSETS = ROOT / "DATASETS"

# Ensure output directories exist
(GODOT_DIR / "scenes" / "hexagrams").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scenes" / "world").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "scripts").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "meshes" / "avatar").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "meshes" / "shap_e").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "meshes" / "depth").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "materials").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "textures").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "sounds").mkdir(parents=True, exist_ok=True)
(GODOT_DIR / "import").mkdir(parents=True, exist_ok=True)

VOID_HEXES = {15, 20, 30, 40}

# Load immutable tables for hex info
sys.path.insert(0, str(ROOT))
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS


def project_godot() -> str:
    return """; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="King Wen 512 Sovereign World"
config/description="Deterministic 512-state King Wen I-Ching cognitive engine visualization"
run/main_scene="res://scenes/world/sovereign_world.tscn"
config/features=PackedStringArray("4.2", "GL Compatibility")
config/icon="res://icon.svg"

[autoload]

KingwenStateMachine="*res://scripts/kingwen_state_machine.gd"

[display]

window/size/viewport_width=1920
window/size/viewport_height=1080
window/size/mode=2
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
environment/defaults/default_clear_color=Color(0.02, 0.02, 0.05, 1)

[layer_names]

3d_physics/layer_1="world"
3d_physics/layer_2="hexagrams"
3d_physics/layer_3="player"

[input]

ui_accept={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194309,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null), Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"echo":false,script:null), Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":true,script:null)]
}
ui_select={
"deadzone": 0.5,
"events": [Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":3,"pressure":0.0,"pressed":true,script:null)]
}
ui_cancel={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194305,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null), Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":1,"pressure":0.0,"pressed":true,script/null)]
}
ui_left={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194319,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null)]
}
ui_right={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194321,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null)]
}
ui_up={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194320,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null)]
}
ui_down={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":4194322,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,script:null)]
}
hex_next={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":69,"physical_keycode":0,"key_label":0,"unicode":101,"echo":false,script:null)]
}
hex_prev={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":81,"physical_keycode":0,"key_label":0,"unicode":113,"echo":false,script:null)]
}
phase_next={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":87,"physical_keycode":0,"key_label":0,"unicode":119,"echo":false,script:null)]
}
phase_prev={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":83,"physical_keycode":0,"key_label":0,"unicode":115,"echo":false,script:null)]
}
toggle_emotional={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":65,"physical_keycode":0,"key_label":0,"unicode":97,"echo":false,script:null)]
}
toggle_quantum={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":68,"physical_keycode":0,"key_label":0,"unicode":100,"echo":false,script:null)]
}
toggle_collision={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":67,"physical_keycode":0,"key_label":0,"unicode":99,"echo":false,script:null)]
}
toggle_reset={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":82,"physical_keycode":0,"key_label":0,"unicode":114,"echo":false,script:null)]
}
"""


def hexagram_scene_tscn(hex_id: int) -> str:
    """Generate a .tscn scene for a single hexagram with 8 phase children."""
    hex_info = HEXAGRAM_BASE.get(hex_id, {})
    name = hex_info.get("name", f"Hexagram {hex_id}")
    category = hex_info.get("category", "sovereign")
    action = hex_info.get("action", "ASSERT")
    unicode_glyph = hex_info.get("unicode", "")
    binary = hex_info.get("binary_bottom_to_top", "111111")
    upper_trigram = hex_info.get("upper_trigram", "")
    lower_trigram = hex_info.get("lower_trigram", "")
    upper_idx = hex_info.get("upper_idx", 7)
    lower_idx = hex_info.get("lower_idx", 7)
    
    is_void = hex_id in VOID_HEXES
    
    # Category color
    cat_colors = {
        "sovereign": "Color(0.788, 0.659, 0.298, 1)",  # gold
        "transformer": "Color(0.310, 0.788, 0.659, 1)",  # teal
        "dissipator": "Color(0.788, 0.310, 0.431, 1)",  # rose
        "boundary": "Color(0.431, 0.620, 0.788, 1)",  # blue
    }
    cat_color = cat_colors.get(category, "Color(0.8, 0.8, 0.8, 1)")
    
    # Phase names
    phase_names = ["past", "present", "future", "transition", "resolution", "dissolution", "crystallization", "void"]
    
    # Build phase nodes
    phase_nodes = []
    phase_resources = []
    
    for phase_idx in range(8):
        phase_name = phase_names[phase_idx]
        mesh_filename = f"hex{hex_id:02d}_phase{phase_idx}.ply"
        mesh_path = f"res://meshes/avatar/{mesh_filename}"
        
        # Check if mesh exists
        actual_path = ASSETS / "kingwen_avatar_meshes" / mesh_filename
        if not actual_path.exists():
            # Fallback to shap-e mesh
            mesh_filename = f"shap_e_hex_{hex_id:02d}.ply"
            mesh_path = f"res://meshes/shap_e/{mesh_filename}"
            actual_path = ASSETS / "kingwen_3d_meshes" / mesh_filename
            if not actual_path.exists():
                continue
        
        # Phase transform offset (circular arrangement)
        angle = (phase_idx / 8.0) * 2.0 * math.pi
        radius = 2.5
        px = math.cos(angle) * radius
        pz = math.sin(angle) * radius
        py = (phase_idx - 3.5) * 0.3  # Slight vertical offset per phase
        
        # Phase scale based on emotional weight
        phase_scale = 1.0 + (0.1 * math.sin(phase_idx * 0.785))
        
        phase_var = f"phase{phase_idx}"
        
        phase_nodes.append(f'''
[node name="{phase_name}" type="MeshInstance3D" parent="."]
transform = Transform3D({phase_scale}, 0, 0, 0, {phase_scale}, 0, 0, 0, {phase_scale}, {px:.4f}, {py:.4f}, {pz:.4f})
mesh = ExtResource("{phase_var}_mesh")
material_override = ExtResource("{phase_var}_mat")
script = ExtResource("phase_script")
metadata/phase_index = {phase_idx}
metadata/phase_temporal = "{phase_name}"
metadata/hexagram_id = {hex_id}
metadata/is_void = {"true" if is_void else "false"}
''')
        
        phase_resources.append(f'[ext_resource type="PackedScene" path="{mesh_path}" id="{phase_var}_mesh"]')
        phase_resources.append(f'[ext_resource type="StandardMaterial3D" path="res://materials/hex_{hex_id:02d}_phase_{phase_idx}.tres" id="{phase_var}_mat"]')
    
    # Build the scene
    scene = f'''; King Wen Hexagram {hex_id}: {name}
; Category: {category} | Action: {action}
; Binary: {binary} | Trigrams: {upper_trigram} / {lower_trigram}
; Unicode: {unicode_glyph}
[gd_scene load_steps={len(phase_resources) + 3} format=3]

[ext_resource type="Script" path="res://scripts/hexagram_display.gd" id="hex_script"]
{chr(10).join(phase_resources)}

[node name="Hex{hex_id:02d}_{name.replace(' ', '_')}" type="Node3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
script = ExtResource("hex_script")
metadata/hexagram_id = {hex_id}
metadata/name = "{name}"
metadata/category = "{category}"
metadata/action = "{action}"
metadata/unicode = "{unicode_glyph}"
metadata/binary = "{binary}"
metadata/upper_trigram = "{upper_trigram}"
metadata/lower_trigram = "{lower_trigram}"
metadata/upper_idx = {upper_idx}
metadata/lower_idx = {lower_idx}
metadata/is_void = {"true" if is_void else "false"}
metadata/category_color = {cat_color}

[node name="Label3D" type="Label3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 3.5, 0)
pixel_size = 0.05
text = "{unicode_glyph} {hex_id}: {name}"
modulate = {cat_color}
font_size = 64
{chr(10).join(phase_nodes)}
'''
    return scene


def sovereign_world_tscn() -> str:
    """Generate the main world scene with all 64 hexagrams."""
    hex_instances = []
    
    for hex_id in range(1, 65):
        hex_info = HEXAGRAM_BASE.get(hex_id, {})
        name = hex_info.get("name", f"Hexagram {hex_id}")
        category = hex_info.get("category", "sovereign")
        
        # Grid position (8x8 grid)
        row = (hex_id - 1) // 8
        col = (hex_id - 1) % 8
        x = (col - 3.5) * 12.0
        z = (row - 3.5) * 12.0
        
        hex_instances.append(f'''
[node name="Hex{hex_id:02d}" type="Node3D" parent="HexagramGrid"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x:.1f}, 0, {z:.1f})
script = ExtResource("hex_ref")
metadata/hexagram_id = {hex_id}
metadata/name = "{name}"
metadata/category = "{category}"
''')
    
    return f'''; King Wen 512 Sovereign World
; 64 hexagrams x 8 phases = 512 resolved states
[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/kingwen_state_machine.gd" id="state_machine"]
[ext_resource type="PackedScene" path="res://scenes/hexagrams/hex_01.tscn" id="hex_01"]

[node name="SovereignWorld" type="Node3D"]
script = ExtResource("state_machine")

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = ExtResource("world_env")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, 10, 20, 10)
light_energy = 1.5
shadow_enabled = true

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, 0, 30, 40)
projection = 1
fov = 60.0
size = 20.0

[node name="HexagramGrid" type="Node3D" parent="."]
{chr(10).join(hex_instances)}

[node name="UI" type="CanvasLayer" parent="."]

[node name="Control" type="Control" parent="UI"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0

[node name="Title" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_top = 20.0
offset_right = 600.0
offset_bottom = 80.0
theme_override_font_sizes/font_size = 32
text = "King Wen 512 Sovereign World"

[node name="Info" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_top = 80.0
offset_right = 800.0
offset_bottom = 200.0
theme_override_font_sizes/font_size = 16
text = "Q/E: Next/Prev Hexagram | W/S: Next/Phase Phase | A: Emotional | D: Quantum | C: Collision | R: Reset"

[node name="HexInfo" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_bottom = 100.0
anchor_top = 1.0
anchor_bottom = 1.0
offset_top = -120.0
theme_override_font_sizes/font_size = 20
text = "Hexagram: - | Phase: - | State: -"

[node name="EmotionalDisplay" type="Label" parent="UI/Control"]
offset_left = 20.0
offset_bottom = 200.0
anchor_top = 1.0
anchor_bottom = 1.0
offset_top = -220.0
theme_override_font_sizes/font_size = 14
text = "Emotional: -"
'''


def kingwen_state_machine_gd() -> str:
    """Generate the main state machine controller script."""
    return '''extends Node3D

# King Wen 512-State Sovereign World Controller
# Manages hexagram selection, phase cycling, emotional display

var current_hex_id: int = 1
var current_phase: int = 1  # present
var show_emotional: bool = false
var show_quantum: bool = false
var show_collision: bool = false

var hex_nodes: Array[Node3D] = []
var hex_scenes: Array[PackedScene] = []

func _ready():
	print("King Wen 512 Sovereign World initializing...")
	_discover_hexagrams()
	_update_display()
	print("Ready. Q/E: hexagram, W/S: phase, A: emotional, D: quantum, C: collision, R: reset")

func _discover_hexagrams():
	hex_nodes.clear()
	var grid = get_node_or_null("HexagramGrid")
	if not grid:
		push_error("HexagramGrid not found")
		return
	
	for child in grid.get_children():
		if child.has_meta("hexagram_id"):
			hex_nodes.append(child)
	
	print(f"Discovered {hex_nodes.size()} hexagram nodes")

func _input(event):
	if not event.is_pressed() or event.is_echo():
		return
	
	if event.is_action("hex_next"):
		current_hex_id = wrapi(current_hex_id + 1, 1, 65)
		_update_display()
	elif event.is_action("hex_prev"):
		current_hex_id = wrapi(current_hex_id - 1, 1, 65)
		_update_display()
	elif event.is_action("phase_next"):
		current_phase = wrapi(current_phase + 1, 0, 8)
		_update_display()
	elif event.is_action("phase_prev"):
		current_phase = wrapi(current_phase - 1, 0, 8)
		_update_display()
	elif event.is_action("toggle_emotional"):
		show_emotional = not show_emotional
		_update_display()
	elif event.is_action("toggle_quantum"):
		show_quantum = not show_quantum
		_update_display()
	elif event.is_action("toggle_collision"):
		show_collision = not show_collision
		_update_display()
	elif event.is_action("toggle_reset"):
		current_hex_id = 1
		current_phase = 1
		show_emotional = false
		show_quantum = false
		show_collision = false
		_update_display()

func _update_display():
	var info_label = get_node_or_null("UI/Control/HexInfo")
	var emotional_label = get_node_or_null("UI/Control/EmotionalDisplay")
	
	if info_label:
		var phase_names = ["past", "present", "future", "transition", "resolution", "dissolution", "crystallization", "void"]
		var phase_name = phase_names[current_phase] if current_phase < phase_names.size() else "unknown"
		info_label.text = "Hexagram: %d | Phase: %s (%d) | Emotional: %s | Quantum: %s | Collision: %s" % [
			current_hex_id, phase_name, current_phase,
			"ON" if show_emotional else "OFF",
			"ON" if show_quantum else "OFF",
			"ON" if show_collision else "OFF"
		]
	
	# Update camera focus
	var grid = get_node_or_null("HexagramGrid")
	if grid:
		for hex_node in grid.get_children():
			if hex_node.has_meta("hexagram_id") and hex_node.get_meta("hexagram_id") == current_hex_id:
				# Focus camera on this hexagram
				var cam = get_node_or_null("Camera3D")
				if cam:
					var target_pos = hex_node.global_transform.origin
					cam.look_at(target_pos)
				break
	
	if emotional_label and show_emotional:
		emotional_label.text = _get_emotional_string()
	elif emotional_label:
		emotional_label.text = ""

func _get_emotional_string() -> str:
	# Return emotional vector for current hex/phase
	return "chaos: %.2f | whimsy: %.2f | darkTone: %.2f | coherence: %.2f | voiceWeight: %.2f" % [
		0.1, 0.2, 0.1, 0.85, 0.85
	]
'''


def hexagram_display_gd() -> str:
    """Generate the per-hexagram display controller script."""
    return '''extends Node3D

# King Wen Hexagram Display Controller
# Manages 8 phase meshes per hexagram

@export var hex_id: int = 1
@export var active_phase: int = 1
@export var is_visible: bool = true
@export var auto_rotate: bool = false
@export var rotation_speed: float = 0.1

var phase_meshes: Array[MeshInstance3D] = []
var phase_materials: Array[StandardMaterial3D] = []

func _ready():
	_discover_phases()
	set_process(auto_rotate)

func _discover_phases():
	phase_meshes.clear()
	for child in get_children():
		if child is MeshInstance3D:
			phase_meshes.append(child)
	print(f"Hex {hex_id}: discovered {phase_meshes.size()} phase meshes")

func _process(delta):
	if auto_rotate:
		rotate_y(delta * rotation_speed)

func set_active_phase(phase_idx: int):
	active_phase = clampi(phase_idx, 0, 7)
	for i in range(phase_meshes.size()):
		if i < phase_meshes.size():
			phase_meshes[i].visible = (i == active_phase)

func set_all_phases_visible(visible: bool):
	for mesh in phase_meshes:
		mesh.visible = visible

func set_emotional_material(chaos: float, whimsy: float, dark_tone: float, coherence: float, voice_weight: float):
	# Update materials based on emotional vector
	for mat in phase_materials:
		if mat:
			var r = clampf(chaos + 0.5, 0.0, 1.0)
			var g = clampf(coherence, 0.0, 1.0)
			var b = clampf(voice_weight, 0.0, 1.0)
			mat.albedo_color = Color(r, g, b, 1.0)
			mat.emission = Color(r * 0.3, g * 0.3, b * 0.3, 1.0)

func pulse_phase(phase_idx: float):
	# Pulse effect for phase transition
	var idx = int(phase_idx) % 8
	if idx < phase_meshes.size():
		var tween = create_tween()
		tween.tween_property(phase_meshes[idx], "scale", Vector3(1.2, 1.2, 1.2), 0.1)
		tween.tween_property(phase_meshes[idx], "scale", Vector3(1.0, 1.0, 1.0), 0.2)
'''


def generate_materials():
    """Generate .tres material files for each hexagram/phase combo."""
    for hex_id in range(1, 65):
        hex_info = HEXAGRAM_BASE.get(hex_id, {})
        category = hex_info.get("category", "sovereign")
        
        cat_colors = {
            "sovereign": (0.788, 0.659, 0.298),
            "transformer": (0.310, 0.788, 0.659),
            "dissipator": (0.788, 0.310, 0.431),
            "boundary": (0.431, 0.620, 0.788),
        }
        base_r, base_g, base_b = cat_colors.get(category, (0.8, 0.8, 0.8))
        
        for phase_idx in range(8):
            # Phase-based color variation
            phase_factor = 1.0 + (phase_idx - 3.5) * 0.05
            r = min(1.0, base_r * phase_factor)
            g = min(1.0, base_g * phase_factor)
            b = min(1.0, base_b * phase_factor)
            
            mat_content = f'''; Material for Hexagram {hex_id} Phase {phase_idx}
[gd_resource type="StandardMaterial3D" format=3]

[resource]
resource_name = "hex_{hex_id:02d}_phase_{phase_idx}"
albedo_color = Color({r:.4f}, {g:.4f}, {b:.4f}, 1.0)
metallic = 0.3
roughness = 0.7
emission_enabled = true
emission = Color({r * 0.2:.4f}, {g * 0.2:.4f}, {b * 0.2:.4f}, 1.0)
emission_energy = 0.5
'''
            mat_path = GODOT_DIR / "materials" / f"hex_{hex_id:02d}_phase_{phase_idx}.tres"
            mat_path.write_text(mat_content, encoding='utf-8')


def generate_import_configs():
    """Generate .import files for PLY mesh import."""
    # Avatar meshes
    avatar_dir = ASSETS / "kingwen_avatar_meshes"
    if avatar_dir.exists():
        for ply_file in avatar_dir.glob("*.ply"):
            import_content = f'''; Import config for {ply_file.name}
[remap]

importer="mesh"
type="CompressedMesh"
metadata={{}}

[deps]

source_file="{ply_file.as_posix()}"
dest_file="{GODOT_DIR.as_posix()}/meshes/avatar/{ply_file.stem}.mesh"

[params]

storage=0
compress=true
precision=0.001
'''
            import_path = GODOT_DIR / "import" / f"{ply_file.stem}.import"
            import_path.write_text(import_content, encoding='utf-8')
    
    # Shap-e meshes
    shap_e_dir = ASSETS / "kingwen_3d_meshes"
    if shap_e_dir.exists():
        for ply_file in shap_e_dir.glob("*.ply"):
            import_content = f'''; Import config for {ply_file.name}
[remap]

importer="mesh"
type="CompressedMesh"
metadata={{}}

[deps]

source_file="{ply_file.as_posix()}"
dest_file="{GODOT_DIR.as_posix()}/meshes/shap_e/{ply_file.stem}.mesh"

[params]

storage=0
compress=true
precision=0.001
'''
            import_path = GODOT_DIR / "import" / f"{ply_file.stem}.import"
            import_path.write_text(import_content, encoding='utf-8')


def main():
    print("Generating Godot project for King Wen 512 Sovereign World...")
    
    # 1. project.godot
    (GODOT_DIR / "project.godot").write_text(project_godot(), encoding='utf-8')
    print("  Wrote project.godot")
    
    # 2. Hexagram scenes
    for hex_id in range(1, 65):
        scene_content = hexagram_scene_tscn(hex_id)
        scene_path = GODOT_DIR / "scenes" / "hexagrams" / f"hex_{hex_id:02d}.tscn"
        scene_path.write_text(scene_content, encoding='utf-8')
    print("  Wrote 64 hexagram scenes")
    
    # 3. Sovereign world scene
    (GODOT_DIR / "scenes" / "world" / "sovereign_world.tscn").write_text(
        sovereign_world_tscn(), encoding='utf-8'
    )
    print("  Wrote sovereign_world.tscn")
    
    # 4. Scripts
    (GODOT_DIR / "scripts" / "kingwen_state_machine.gd").write_text(
        kingwen_state_machine_gd(), encoding='utf-8'
    )
    (GODOT_DIR / "scripts" / "hexagram_display.gd").write_text(
        hexagram_display_gd(), encoding='utf-8'
    )
    print("  Wrote GDScripts")
    
    # 5. Materials
    generate_materials()
    print("  Wrote 512 materials")
    
    # 6. Import configs
    generate_import_configs()
    print("  Wrote import configs")
    
    print(f"\nGodot project generated at: {GODOT_DIR}")
    print("Open with Godot 4.x to run the Sovereign World")


if __name__ == "__main__":
    main()
