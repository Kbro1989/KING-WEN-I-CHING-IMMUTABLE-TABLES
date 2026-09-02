extends Node3D

# Yao Line Controller
# Manages individual yao line rendering and animation

@export var line_index: int = 0
@export var yao_state: int = 1  # 0=yin, 1=yang, 2=yao
@export var is_changing: bool = false

var base_scale: Vector3 = Vector3.ONE
var target_scale: Vector3 = Vector3.ONE
var pulse_time: float = 0.0

func _ready():
	base_scale = scale
	if is_changing:
		target_scale = base_scale * 1.1

func _process(delta):
	if is_changing:
		pulse_time += delta * 3.0
		var pulse = 1.0 + 0.1 * sin(pulse_time)
		scale = base_scale * pulse
	else:
		scale = base_scale

func set_yao_state(new_state: int):
	yao_state = new_state
	if yao_state == 2:
		is_changing = true
		target_scale = base_scale * 1.1
	else:
		is_changing = false
		target_scale = base_scale
