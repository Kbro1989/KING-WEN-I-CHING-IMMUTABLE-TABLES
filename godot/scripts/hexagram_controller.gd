extends Node3D

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
