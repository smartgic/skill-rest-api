"""Constants used across the skill
"""
MSG_PREFIX = "mycroft.api"
CONSTANT_MSG_TYPE = {
    "info": f"{MSG_PREFIX}.info",
    "connectivity": f"{MSG_PREFIX}.connectivity",
    "config": f"{MSG_PREFIX}.config",
    "skill_settings": f"{MSG_PREFIX}.skill_settings",
    "sleep": f"{MSG_PREFIX}.sleep",
}
SKILLS_CONFIG_DIR = ".config/mycroft/skills"
TMP_DIR = "/tmp/mycroft"
