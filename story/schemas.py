"""
Scene JSON Field Schemas for Motion Comic Engine

Defines the expected shapes for Scene model JSONFields and provides validation.
"""

VALID_CHARACTERS = ["byte", "pixel", "nova", "dr_glitch", "narrator"]
VALID_POSITIONS = ["left", "center", "right", "far_left", "far_right"]
VALID_EXPRESSIONS = ["neutral", "happy", "worried", "determined", "surprised", "angry", "thinking"]
VALID_ENTER_ANIMATIONS = ["fade_in", "slide_left", "slide_right", "bounce", "glitch", "none"]
VALID_EXIT_ANIMATIONS = ["fade_out", "slide_left", "slide_right", "shrink", "glitch", "none"]
VALID_BUBBLE_TYPES = ["speech", "thought", "shout", "whisper", "narration"]
VALID_TYPING_SPEEDS = ["slow", "normal", "fast"]
VALID_MOTION_TYPES = [
    "screen_shake", "flash", "zoom_in", "zoom_out",
    "pan_left", "pan_right", "glitch_effect",
    "particles", "code_rain", "explosion",
]
VALID_MOTION_TRIGGERS = ["on_enter", "on_bubble", "on_exit", "with_bubble"]
VALID_NEXT_ACTIONS = ["next", "choice", "run_code", "challenge", "end"]

VALID_BACKGROUND_KEYS = [
    "shero_hq", "broken_internet", "corrupted_city", "code_forest",
    "data_river", "glitch_lair", "byte_lab", "pixel_studio",
    "nova_workshop", "boss_arena", "digital_void", "internet_highway",
    "website_ruins", "server_room", "firewall_gate",
]

CHARACTERS_ON_SCREEN_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "character": {"type": "string", "enum": VALID_CHARACTERS},
            "position": {"type": "string", "enum": VALID_POSITIONS},
            "expression": {"type": "string", "enum": VALID_EXPRESSIONS},
            "enter_animation": {"type": "string", "enum": VALID_ENTER_ANIMATIONS},
            "exit_animation": {"type": "string", "enum": VALID_EXIT_ANIMATIONS},
            "scale": {"type": "number", "default": 1.0},
            "z_index": {"type": "integer", "default": 1},
        },
        "required": ["character", "position"],
    },
}

BUBBLES_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "character": {"type": "string"},
            "text": {"type": "string"},
            "bubble_type": {"type": "string", "enum": VALID_BUBBLE_TYPES},
            "typing_speed": {"type": "string", "enum": VALID_TYPING_SPEEDS, "default": "normal"},
            "delay_ms": {"type": "integer", "default": 0},
            "auto_advance": {"type": "boolean", "default": False},
            "auto_advance_delay_ms": {"type": "integer", "default": 3000},
        },
        "required": ["character", "text"],
    },
}

MOTIONS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": VALID_MOTION_TYPES},
            "trigger": {"type": "string", "enum": VALID_MOTION_TRIGGERS, "default": "on_enter"},
            "trigger_index": {"type": "integer", "default": 0},
            "duration_ms": {"type": "integer", "default": 500},
            "intensity": {"type": "number", "default": 1.0},
        },
        "required": ["type"],
    },
}

NEXT_ACTION_PAYLOADS = {
    "next": {},
    "choice": {
        "choices": [
            {"text": "Choice text", "next_scene_order": 3},
        ],
    },
    "run_code": {
        "mission_step_number": 1,
    },
    "challenge": {
        "step_type": "multiple_choice",
        "content": {},
    },
    "end": {},
}


def validate_scene_data(scene):
    """Validates scene JSON fields against schemas. Returns list of error strings."""
    errors = []

    # Validate characters_on_screen
    if not isinstance(scene.characters_on_screen, list):
        errors.append("characters_on_screen must be a list")
    else:
        for i, char in enumerate(scene.characters_on_screen):
            if not isinstance(char, dict):
                errors.append(f"characters_on_screen[{i}] must be an object")
                continue
            if "character" not in char:
                errors.append(f"characters_on_screen[{i}] missing required field 'character'")
            if "position" not in char:
                errors.append(f"characters_on_screen[{i}] missing required field 'position'")

    # Validate bubbles
    if not isinstance(scene.bubbles, list):
        errors.append("bubbles must be a list")
    else:
        for i, bubble in enumerate(scene.bubbles):
            if not isinstance(bubble, dict):
                errors.append(f"bubbles[{i}] must be an object")
                continue
            if "character" not in bubble:
                errors.append(f"bubbles[{i}] missing required field 'character'")
            if "text" not in bubble:
                errors.append(f"bubbles[{i}] missing required field 'text'")

    # Validate motions
    if not isinstance(scene.motions, list):
        errors.append("motions must be a list")
    else:
        for i, motion in enumerate(scene.motions):
            if not isinstance(motion, dict):
                errors.append(f"motions[{i}] must be an object")
                continue
            if "type" not in motion:
                errors.append(f"motions[{i}] missing required field 'type'")

    # Validate next_action + action_payload consistency
    if scene.next_action == "choice":
        payload = scene.action_payload or {}
        if "choices" not in payload or not isinstance(payload.get("choices"), list):
            errors.append("action_payload must contain 'choices' list when next_action is 'choice'")
        else:
            for i, choice in enumerate(payload["choices"]):
                if "text" not in choice:
                    errors.append(f"action_payload.choices[{i}] missing 'text'")
                if "next_scene_order" not in choice:
                    errors.append(f"action_payload.choices[{i}] missing 'next_scene_order'")
    elif scene.next_action == "challenge":
        payload = scene.action_payload or {}
        if "step_type" not in payload:
            errors.append("action_payload must contain 'step_type' when next_action is 'challenge'")
        if "content" not in payload:
            errors.append("action_payload must contain 'content' when next_action is 'challenge'")
    elif scene.next_action == "run_code":
        payload = scene.action_payload or {}
        if not payload:
            errors.append("action_payload should not be empty when next_action is 'run_code'")

    return errors
