import re

COLOR_MAP = {
    "cyan": "#00f2fe",
    "blue": "#00f2fe",
    "sky": "#38bdf8",
    "green": "#10b981",
    "emerald": "#10b981",
    "neon green": "#22c55e",
    "pink": "#f43f5e",
    "magenta": "#ec4899",
    "rose": "#f43f5e",
    "yellow": "#eab308",
    "gold": "#f59e0b",
    "orange": "#f97316",
    "purple": "#a855f7",
    "white": "#ffffff"
}

def parse_voice_command(text):
    """
    Parses spoken voice command string and returns structured action + voice confirmation.
    """
    if not text:
        return {"action": "NONE", "message": "No voice input detected."}

    text_clean = text.lower().strip()

    # 1. Clear Canvas
    if any(k in text_clean for k in ["clear", "clean", "reset", "erase all", "delete all"]):
        return {
            "action": "CLEAR_CANVAS",
            "message": "Canvas cleared successfully."
        }

    # 2. Save Drawing
    if any(k in text_clean for k in ["save", "download", "export", "snapshot", "keep"]):
        return {
            "action": "SAVE_CANVAS",
            "message": "Saving your artwork to gallery."
        }

    # 3. Undo Stroke
    if any(k in text_clean for k in ["undo", "step back", "revert"]):
        return {
            "action": "UNDO",
            "message": "Last stroke undone."
        }

    # 4. Eraser Mode
    if any(k in text_clean for k in ["eraser", "erase", "rubber", "duster"]):
        return {
            "action": "SET_TOOL",
            "tool": "eraser",
            "message": "Switched to Eraser tool."
        }

    # 5. Pen / Brush Mode
    if any(k in text_clean for k in ["pen", "brush", "draw", "pencil", "paint"]):
        return {
            "action": "SET_TOOL",
            "tool": "pen",
            "message": "Switched to Neon Pen."
        }

    # 6. Brush Size adjustments
    if any(k in text_clean for k in ["small", "thin", "fine"]):
        return {
            "action": "SET_SIZE",
            "size": 4,
            "message": "Brush size set to Fine."
        }
    if any(k in text_clean for k in ["medium", "normal", "regular"]):
        return {
            "action": "SET_SIZE",
            "size": 10,
            "message": "Brush size set to Medium."
        }
    if any(k in text_clean for k in ["large", "thick", "heavy", "big", "fat"]):
        return {
            "action": "SET_SIZE",
            "size": 22,
            "message": "Brush size set to Thick."
        }

    # 7. Color Changes
    for color_name, hex_code in COLOR_MAP.items():
        if color_name in text_clean:
            return {
                "action": "SET_COLOR",
                "color": hex_code,
                "color_name": color_name.capitalize(),
                "message": f"Color changed to {color_name.capitalize()}."
            }

    # 8. Magic Shape Toggle
    if any(k in text_clean for k in ["shape", "magic", "snap", "circle", "rectangle"]):
        return {
            "action": "TOGGLE_SHAPE",
            "message": "Smart Shape Snapping toggled."
        }

    return {
        "action": "UNKNOWN",
        "raw_text": text,
        "message": f"Heard '{text}', but command not recognized."
    }
