"""Constants used across the skill
"""
MSG_PREFIX = "mycroft.api"
MSG_TYPE = {
    "cache": f"{MSG_PREFIX}.cache",
    "internet": f"{MSG_PREFIX}.internet",
    "config": f"{MSG_PREFIX}.config",
    "info": f"{MSG_PREFIX}.info",
    "is_awake": f"{MSG_PREFIX}.is_awake",
    "skill_settings": f"{MSG_PREFIX}.skill_settings",
    "skill_install": f"{MSG_PREFIX}.skill_install",
    "skill_uninstall": f"{MSG_PREFIX}.skill_uninstall",
    "sleep": "recognizer_loop:sleep",
    "speak": "speak",
    "sleep_answer": f"{MSG_PREFIX}.sleep",
    "wake_up": "recognizer_loop:wake_up",
    "wake_up_answer": f"{MSG_PREFIX}.wake_up",
    "websocket": f"{MSG_PREFIX}.websocket",
}
SKILLS_CONFIG_DIR = ".config/mycroft/skills"
TMP_DIR = "/tmp/mycroft"
TTS_CACHE_DIR = f"{TMP_DIR}/cache/tts"
SLEEP_MARK = f"{TMP_DIR}/sleep.mark"
