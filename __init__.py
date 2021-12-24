"""api entrypoint skill
"""
import json
from msm.exceptions import AlreadyInstalled, InstallException, AlreadyRemoved, \
    RemoveException
from mycroft import MycroftSkill
from mycroft.api import DeviceApi
from mycroft.configuration import Configuration
from mycroft.configuration.config import LocalConf, USER_CONFIG
from mycroft.skills.msm_wrapper import create_msm, build_msm_config
from mycroft.util.network_utils import _connected_google as ping_google
from pathlib import Path
from .utils import check_auth, delete, send
from .constants import MSG_TYPE, SKILLS_CONFIG_DIR, SLEEP_MARK, TTS_CACHE_DIR


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
        self.add_event(MSG_TYPE["info"],
                       self._handle_info)
        self.add_event(MSG_TYPE["config"],
                       self._handle_config)
        self.add_event(MSG_TYPE["sleep"],
                       self._handle_sleep)
        self.add_event(MSG_TYPE["wake_up"],
                       self._handle_wake_up)
        self.add_event(MSG_TYPE["is_awake"],
                       self._handle_is_awake)
        self.add_event(MSG_TYPE["cache"],
                       self._handle_cache)

        # Network
        self.add_event(MSG_TYPE["connectivity"],
                       self._handle_connectivity)

        # Skill
        self.add_event(MSG_TYPE["skill_settings"],
                       self._handle_skill_settings)
        self.add_event(MSG_TYPE["skill_install"],
                       self._handle_skill_install)
        self.add_event(MSG_TYPE["skill_uninstall"],
                       self._handle_skill_uninstall)

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
            send(self, f'{MSG_TYPE["info"]}.answer',
                 data={**data_api, **data_local})

    def _handle_connectivity(self, message: dict) -> None:
        """When mycroft.api.connectivity event is detected on the bus,
        this function will use the _connected_google() function from mycroft
        core to detect if the instance is connected to Internet.
        """
        self.log.debug("mycroft.api.connectivity message detected")
        check_auth(self, message)
        if self.authenticated:
            send(self, f'{MSG_TYPE["connectivity"]}.answer',
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
            send(self, f'{MSG_TYPE["config"]}.answer',
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
                             f'{MSG_TYPE["skill_settings"]}.answer',
                             data=json.load(settings_json))
                except IOError as err:
                    self.log.error("unable to retrieve skill settings")
                    self.log.debug(err)
            send(self, f'{MSG_TYPE["skill_settings"]}.answer',
                 data={"error": "no settings.json file found"})

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
                     f'{MSG_TYPE["sleep_answer"]}.answer',
                     data={"mark": SLEEP_MARK})
            except IOError as err:
                self.log.error("unable to generate the sleep mark")
                self.log.debug(err)

    def _handle_wake_up(self, message: dict) -> None:
        """When recognizer_loop:wake_up event is detected on the bus,
        this function will remove the sleep mark. This file
        will be looked up by the _handle_is_awake() method to determine if
        mycroft is into sleep mode or awake.
        """
        self.log.debug("recognizer_loop:wake_up message detected")
        check_auth(self, message)
        if self.authenticated:
            try:
                if Path(SLEEP_MARK).is_file():
                    Path(SLEEP_MARK).unlink()
                    send(self,
                         f'{MSG_TYPE["wake_up_answer"]}.answer',
                         data={"mark": "sleep mark deleted"})
                send(self,
                     f'{MSG_TYPE["wake_up_answer"]}.answer',
                     data={"mark": "no sleep mark to delete"})
            except IOError as err:
                self.log.error("unable to delete the sleep mark")
                self.log.debug(err)

    def _handle_is_awake(self, message: dict) -> None:
        """When mycroft.api.is_awake event is detected on the bus,
        this function will looke for a /tmp/mycroft/sleep.mark file to
        determine if mycroft is into sleep mode or awake.
        """
        self.log.debug("mycroft.api.is_awake message detected")
        check_auth(self, message)
        if self.authenticated:
            is_awake: bool = True
            try:
                if Path(SLEEP_MARK).is_file():
                    is_awake = False
                send(self,
                     f'{MSG_TYPE["is_awake"]}.answer',
                     data={"is_awake": is_awake})
            except IOError as err:
                self.log.error("unable to retrieve sleep mark")
                self.log.debug(err)

    def _handle_cache(self, message: dict) -> None:
        """When mycroft.api.cache event is detected on the bus,
        this function remove cache (files and/or directories) related to the
        type.

        For now only TTS cache removal is supported.
        """
        self.log.debug("mycroft.api.cache message detected")
        check_auth(self, message)
        if self.authenticated:
            cache_type: str = message.data.get("cache_type")
            status: bool = False
            if cache_type == "tts":
                tts: str = self.config_core["tts"]["module"].capitalize()
                tts_path: str = f"{TTS_CACHE_DIR}/{tts}TTS"
                try:
                    status = delete(self, tts_path)
                except IOError as err:
                    self.log.error("unable to clear tts cache")
                    self.log.debug(err)
            send(self, f'{MSG_TYPE["cache"]}.answer',
                 data={"cache_type": cache_type, "status": status})

    def _handle_skill_install(self, message: dict) -> None:
        """When mycroft.api.skill_install event is detected on the bus,
        this function install a skill based on the Git repository provided.
        """
        self.log.debug("mycroft.api.skill_install message detected")
        check_auth(self, message)
        if self.authenticated:
            skill: str = message.data.get("skill")
            confirm: bool = message.data.get("confirm")
            try:
                msm_config = build_msm_config(self.config_core)
                msm = create_msm(msm_config)
                msm.install(skill)
                if confirm:
                    utterance: str = message.data.get("dialog")
                    lang: str = message.data.get("lang")
                    send(self, MSG_TYPE["speak"],
                         data={"utterance": utterance, "lang": lang})
                send(self, f'{MSG_TYPE["skill_install"]}.answer',
                     data={"skill": skill})
            except AlreadyInstalled:
                send(self, f'{MSG_TYPE["skill_install"]}.answer',
                     data={"skill": "already installed"})
                pass
            except InstallException as err:
                self.log.error("unable to install the skill")
                self.log.debug(err)

    def _handle_skill_uninstall(self, message: dict) -> None:
        """When mycroft.api.skill_uninstall event is detected on the bus,
        this function uninstall a skill based on the skill ID.
        """
        self.log.debug("mycroft.api.skill_uninstall message detected")
        check_auth(self, message)
        if self.authenticated:
            skill: str = message.data.get("skill")
            confirm: bool = message.data.get("confirm")
            try:
                msm_config = build_msm_config(self.config_core)
                msm = create_msm(msm_config)
                msm.remove(skill)
                if confirm:
                    utterance: str = message.data.get("dialog")
                    lang: str = message.data.get("lang")
                    send(self, MSG_TYPE["speak"],
                         data={"utterance": utterance, "lang": lang})
                send(self, f'{MSG_TYPE["skill_uninstall"]}.answer',
                     data={"skill": skill})
            except AlreadyRemoved:
                send(self, f'{MSG_TYPE["skill_uninstall"]}.answer',
                     data={"skill": "already uninstalled"})
                pass
            except RemoveException as err:
                self.log.error("unable to uninstall the skill")
                self.log.debug(err)


def create_skill():
    """Main function to register the skill
    """
    return Api()
