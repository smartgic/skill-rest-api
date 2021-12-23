"""Constants used across the skill
"""
MSG_PREFIX = "mycroft.api"
CONSTANT_MSG_TYPE = {
    "info": f"{MSG_PREFIX}.info",
    "connectivity": f"{MSG_PREFIX}.connectivity",
    "config": f"{MSG_PREFIX}.config",
    "skill_settings": f"{MSG_PREFIX}.skill_settings",
    "sleep": "recognizer_loop:sleep",
    "sleep_answer": f"{MSG_PREFIX}.sleep",
    "wake_up": "recognizer_loop:wake_up",
    "wake_up_answer": f"{MSG_PREFIX}.wake_up",
    "is_awake": f"{MSG_PREFIX}.is_awake",
    "cache": f"{MSG_PREFIX}.cache",
}
SKILLS_CONFIG_DIR = ".config/mycroft/skills"
TMP_DIR = "/tmp/mycroft"
TTS_CACHE_DIR = f"{TMP_DIR}/cache/tts"
SLEEP_MARK = f"{TMP_DIR}/sleep.mark"
