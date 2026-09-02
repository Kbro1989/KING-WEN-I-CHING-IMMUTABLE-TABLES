extends Node3D

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
