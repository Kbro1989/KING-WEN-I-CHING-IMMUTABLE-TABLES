extends Node3D

# Hexagram Controller
# Manages 729 ternary permutations for a single hexagram

@export var hex_id: int = 1
@export var active_permutation: int = 0
@export var show_all_permutations: bool = false

var permutation_nodes: Array[Node3D] = []
var hex_name: String = ""
var hex_category: String = ""

func _ready():
	permutation_nodes = get_children()
	hex_name = get_meta("name", f"Hexagram {hex_id}")
	hex_category = get_meta("category", "sovereign")
	print(f"Hex {hex_id} ({hex_name}): {permutation_nodes.size()} permutations loaded")

func set_active_permutation(perm_index: int):
	active_permutation = clampi(perm_index, 0, 728)
	for i in range(permutation_nodes.size()):
		if permutation_nodes[i] is Node3D:
			permutation_nodes[i].visible = (i == active_permutation) or show_all_permutations

func set_all_visible(visible: bool):
	show_all_permutations = true
	for node in permutation_nodes:
		if node is Node3D:
			node.visible = visible

func get_permutation_count() -> int:
	return permutation_nodes.size()
