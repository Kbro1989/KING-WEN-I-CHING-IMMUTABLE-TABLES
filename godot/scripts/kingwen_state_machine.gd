extends Node3D

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
