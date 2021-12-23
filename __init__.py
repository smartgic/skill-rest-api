"""api entrypoint skill
"""
import json
from mycroft import MycroftSkill
from mycroft.api import DeviceApi
from mycroft.configuration import Configuration
from mycroft.configuration.config import LocalConf, USER_CONFIG
from mycroft.util.network_utils import _connected_google as ping_google
from pathlib import Path
from .utils import check_auth, send
from .constants import CONSTANT_MSG_TYPE, SKILLS_CONFIG_DIR, SLEEP_MARK


class Api(MycroftSkill):
    """This is the place where all the magic happens for the api skill.
    """
    def __init__(self):
        MycroftSkill.__init__(self)

        # Initialize variables with values (or not).
        self.api_key: str
        self.authenticated: bool = False
        self.configured: bool = False
        self.settings_change_callback = None

    def _setup(self) -> None:
        """Provision initialized variables and retrieve configuration
        from home.mycroft.ai.
        """
        self.api_key = self.settings.get("api_key")

        # Make sure the requirements are fulfill.
        if not self.api_key:
            self.log.warning("api key is not defined")
        else:
            self.configured = True
            self.log.info("api key has been registered")

    def handle_events(self) -> None:
        """Handle the events sent on the bus and trigger functions when
        received.
        """
        # System
        self.add_event(CONSTANT_MSG_TYPE["info"],
                       self._handle_info)
        self.add_event(CONSTANT_MSG_TYPE["config"],
                       self._handle_config)
        self.add_event(CONSTANT_MSG_TYPE["sleep"],
                       self._handle_sleep)
        # Network
        self.add_event(CONSTANT_MSG_TYPE["connectivity"],
                       self._handle_connectivity)

        # Skill
        self.add_event(CONSTANT_MSG_TYPE["skill_settings"],
                       self._handle_skill_settings)

    def initialize(self) -> None:
        """The initialize method is called after the Skill is fully
        constructed and registered with the system. It is used to perform
        any final setup for the Skill including accessing Skill settings.
        https://tinyurl.com/4pevkdhj
        """
        self.settings_change_callback = self.on_websettings_changed
        self.on_websettings_changed()
        self.handle_events()

    def on_websettings_changed(self) -> None:
        """Each Mycroft device will check for updates to a users settings
        regularly, and write these to the Skills settings.json.
        https://tinyurl.com/f2bkymw
        """
        self._setup()

    def _handle_info(self, message: dict) -> None:
        """When mycroft.api.info event is detected on the bus, this function
        will collect information from local and remote location.

        If there is no Internet connection then only local information will
        be returned.
        """
        self.log.debug("mycroft.api.info message detected")
        check_auth(self, message)
        if self.authenticated:
            config = Configuration.get(cache=False, remote=False)
            data_local: dict = {}
            data_api: dict = {}
            if ping_google():
                api = DeviceApi().get()
                data_api = {
                    "core_version": api["coreVersion"],
                    "device_uuid": api["uuid"],
                    "name": api["name"]
                }
            data_local = {
                "audio_backend":
                    config.get("audio", "Audio")["default-backend"],
                "city": config["location"]["city"]["name"],
                "country":
                    config["location"]["city"]["state"]["country"]["name"],
                "lang": config["lang"],
                "platform": config["enclosure"].get("platform", "unknown"),
                "timezone": config["location"]["timezone"]["code"],
                "tts_engine": config["tts"]["module"]
            }
            send(self, f'{CONSTANT_MSG_TYPE["info"]}.answer',
                 data={**data_api, **data_local})

    def _handle_connectivity(self, message: dict) -> None:
        """When mycroft.api.connectivity event is detected on the bus,
        this function will use the _connected_google() function from mycroft
        core to detect if the instance is connected to Internet.
        """
        self.log.debug("mycroft.api.connectivity message detected")
        check_auth(self, message)
        if self.authenticated:
            send(self, f'{CONSTANT_MSG_TYPE["connectivity"]}.answer',
                 data=ping_google())

    def _handle_config(self, message: dict) -> None:
        """When mycroft.api.config event is detected on the bus, this function
        will use the LocalConf() function from mycroft core to retrieve the
        "custom" configuration from mycroft.conf.

        If message.data.get('core') is True then the core and local
        configurations will be retrieved.
        """
        self.log.debug("mycroft.api.config message detected")
        check_auth(self, message)
        if self.authenticated:
            data: dict = LocalConf(USER_CONFIG)
            if message.data.get('core'):
                data = self.config_core
            send(self, f'{CONSTANT_MSG_TYPE["config"]}.answer',
                 data=data)

    def _handle_skill_settings(self, message: dict) -> None:
        """When mycroft.api.skill_settings event is detected on the bus,
        this function will look for a settings.json file from the skill config
        directory and read load the content as JSON.
        """
        self.log.debug("mycroft.api.skill_settings message detected")
        check_auth(self, message)
        if self.authenticated:
            home: str = str(Path.home())
            skill: str = message.data.get('skill')
            file: str = f"{home}/{SKILLS_CONFIG_DIR}/{skill}/settings.json"
            if Path(file).is_file():
                try:
                    with open(file) as settings_json:
                        send(self,
                             f'{CONSTANT_MSG_TYPE["skill_settings"]}.answer',
                             data=json.load(settings_json))
                except IOError as err:
                    self.log.err(err)

    def _handle_sleep(self, message: dict) -> None:
        """When recognizer_loop:sleep event is detected on the bus,
        this function will create an empty file into /tmp/mycroft. This file
        will be looked up by the _handle_is_awake() method to determine if
        mycroft is into sleep mode or awake.
        """
        self.log.debug("recognizer_loop:sleep message detected")
        check_auth(self, message)
        if self.authenticated:
            try:
                Path(SLEEP_MARK).touch()
                send(self,
                     f'{CONSTANT_MSG_TYPE["sleep_answer"]}.answer',
                     data={"mark": SLEEP_MARK})
            except IOError as err:
                self.log.err(err)


def create_skill():
    """Main function to register the skill
    """
    return Api()
