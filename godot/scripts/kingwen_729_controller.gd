extends Node3D

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
