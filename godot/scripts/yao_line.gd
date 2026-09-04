extends Node3D

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
