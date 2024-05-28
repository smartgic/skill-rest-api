"""rest-api entrypoint skill
"""

import json
import platform
from pathlib import Path
from ovos_bus_client.message import Message
from ovos_config.config import Configuration
from ovos_core import version
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_workshop.skills import OVOSSkill

# from mycroft.configuration.config import LocalConf, USER_CONFIG
# from mycroft.skills.msm_wrapper import create_msm, build_msm_config
from ovos_utils.network_utils import is_connected
from .utils import check_auth, send  # , delete
from .constants import MSG_TYPE, SLEEP_MARK  # , SKILLS_CONFIG_DIR, TTS_CACHE_DIR


class RestApiSkill(OVOSSkill):
    """This is the place where all the magic happens for the api skill."""

    @property
    def api_key(self):
        return self.settings.get("api_key")

    @classproperty
    def runtime_requirements(self):
        """Check for skill functionalities requirements before trying to
        start the skill.
        """
        return RuntimeRequirements(
            internet_before_load=True,
            network_before_load=True,
            gui_before_load=False,
            requires_internet=True,
            requires_network=True,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )

    def _setup(self) -> None:
        """Provision initialized variables and retrieve configuration
        from settings.json file.
        """

        # Make sure the requirements are fulfill.
        if not self.api_key:
            LOG.warning("api key is not defined")
        else:
            self.configured = True
            LOG.info("api key has been registered")

        self.add_event(MSG_TYPE["info"], self._handle_info)
        self.add_event(MSG_TYPE["internet"], self._handle_internet_connectivity)
        self.add_event(MSG_TYPE["sleep"], self._handle_sleep)
        self.add_event(MSG_TYPE["wake_up"], self._handle_wake_up)
        self.add_event(MSG_TYPE["is_awake"], self._handle_is_awake)

    # def handle_events(self) -> None:
    #     """Handle the events sent on the bus and trigger functions when
    #     received.
    #     """
    #     # System
    #     self.add_event(MSG_TYPE["info"],
    #                    self._handle_info)
    #     self.add_event(MSG_TYPE["config"],
    #                    self._handle_config)
    #     self.add_event(MSG_TYPE["cache"],
    #                    self._handle_cache)
    #     # Skill
    #     self.add_event(MSG_TYPE["skill_settings"],
    #                    self._handle_skill_settings)
    #     self.add_event(MSG_TYPE["skill_install"],
    #                    self._handle_skill_install)
    #     self.add_event(MSG_TYPE["skill_uninstall"],
    #                    self._handle_skill_uninstall)

    def _handle_info(self, message: Message) -> None:
        """When ovos.api.info event is detected on the bus, this function
        will collect some information
        """
        check_auth(self, message)
        if self.authenticated:
            config = Configuration()
            data: dict = {}
            data = {
                "core_version": version.OVOS_VERSION_STR,
                "name": config["listener"]["wake_word"],
                "audio_backend": config["Audio"]["default-backend"],
                "city": config["location"]["city"]["name"],
                "country": config["location"]["city"]["state"]["country"]["name"],
                "lang": config["lang"],
                "timezone": config["location"]["timezone"]["code"],
                "tts_engine": config["tts"]["module"],
                "stt_engine": config["stt"]["module"],
                "log_level": config["log_level"],
                "architecture": platform.machine(),
                "system": platform.system(),
                "kernel": platform.release(),
            }
            send(self, f'{MSG_TYPE["info"]}.answer', data=data)

    def _handle_internet_connectivity(self, message: Message) -> None:
        """When ovos.api.internet event is detected on the bus,
        this function will use the is_connected() function from ovos-utils
        to detect if the instance is connected to the Internet.
        """
        check_auth(self, message)
        if self.authenticated:
            send(
                self, f'{MSG_TYPE["internet"]}.answer', data={"status": is_connected()}
            )

    # def _handle_websocket_connectivity(self, message: Message) -> None:
    #     """When ovos.api.websocket event is detected on the bus,
    #     this function will use the _connected_google() function from ovos
    #     core to detect if the instance is connected to Internet.
    #     """
    #     check_auth(self, message)
    #     if self.authenticated:
    #         send(self, f'{MSG_TYPE["websocket"]}.answer', data={"listening": True})

    # def _handle_config(self, message: dict) -> None:
    #     """When mycroft.api.config event is detected on the bus, this function
    #     will use the LocalConf() function from mycroft core to retrieve the
    #     "custom" configuration from mycroft.conf.

    #     If message.data.get('core') is True then the core and local
    #     configurations will be retrieved.
    #     """
    #     self.log.debug("mycroft.api.config message detected")
    #     check_auth(self, message)
    #     if self.authenticated:
    #         data: dict = LocalConf(USER_CONFIG)
    #         if message.data.get('core'):
    #             data = self.config_core
    #         send(self, f'{MSG_TYPE["config"]}.answer',
    #              data=data)

    # def _handle_skill_settings(self, message: dict) -> None:
    #     """When mycroft.api.skill_settings event is detected on the bus,
    #     this function will look for a settings.json file from the skill config
    #     directory and read load the content as JSON.
    #     """
    #     self.log.debug("mycroft.api.skill_settings message detected")
    #     check_auth(self, message)
    #     if self.authenticated:
    #         home: str = str(Path.home())
    #         skill: str = message.data.get('skill')
    #         file: str = f"{home}/{SKILLS_CONFIG_DIR}/{skill}/settings.json"
    #         if Path(file).is_file():
    #             try:
    #                 with open(file, encoding="utf-8") as settings_json:
    #                     send(self,
    #                          f'{MSG_TYPE["skill_settings"]}.answer',
    #                          data=json.load(settings_json))
    #             except IOError as err:
    #                 self.log.error("unable to retrieve skill settings")
    #                 self.log.debug(err)
    #         send(self, f'{MSG_TYPE["skill_settings"]}.answer',
    #              data={"error": "no settings.json file found"})

    def _handle_sleep(self, message: dict) -> None:
        """When recognizer_loop:sleep event is detected on the bus,
        this function will create an empty file into /tmp. This file
        will be looked up by the _handle_is_awake() method to determine if
        mycroft is into sleep mode or awake.
        """
        check_auth(self, message)
        if self.authenticated:
            try:
                Path(SLEEP_MARK).touch()
                send(
                    self,
                    f'{MSG_TYPE["sleep_answer"]}.answer',
                    data={"mark": SLEEP_MARK},
                )
            except IOError as err:
                LOG.error("unable to generate the sleep mark")
                LOG.debug(err)

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
                    send(
                        self,
                        f'{MSG_TYPE["wake_up_answer"]}.answer',
                        data={"mark": "sleep mark deleted"},
                    )
                send(
                    self,
                    f'{MSG_TYPE["wake_up_answer"]}.answer',
                    data={"mark": "no sleep mark to delete"},
                )
            except IOError as err:
                LOG.error("unable to delete the sleep mark")
                LOG.debug(err)

    def _handle_is_awake(self, message: dict) -> None:
        """When ovos.api.is_awake event is detected on the bus,
        this function will looke for a /tmp/sleep.mark file to
        determine if mycroft is into sleep mode or awake.
        """
        check_auth(self, message)
        if self.authenticated:
            is_awake: bool = True
            try:
                if Path(SLEEP_MARK).is_file():
                    is_awake = False
                send(
                    self, f'{MSG_TYPE["is_awake"]}.answer', data={"is_awake": is_awake}
                )
            except IOError as err:
                LOG.error("unable to retrieve sleep mark")
                LOG.debug(err)

    # def _handle_cache(self, message: dict) -> None:
    #     """When ovos.api.cache event is detected on the bus,
    #     this function remove cache (files and/or directories) related to the
    #     type.

    #     For now only TTS cache removal is supported.
    #     """
    #     check_auth(self, message)
    #     if self.authenticated:
    #         cache_type: str = message.data.get("cache_type")
    #         status: bool = False
    #         if cache_type == "tts":
    #             tts: str = self.config_core["tts"]["module"].capitalize()
    #             tts_path: str = f"{TTS_CACHE_DIR}/{tts}TTS"
    #             if tts == "Mimic" or tts == "Mimic2":
    #                 tts_path: str = f"{TTS_CACHE_DIR}/{tts}"
    #             try:
    #                 status = delete(self, tts_path)
    #             except IOError as err:
    #                 self.log.error("unable to clear tts cache")
    #                 self.log.debug(err)
    #         send(self, f'{MSG_TYPE["cache"]}.answer',
    #              data={"cache_type": cache_type, "status": status})

    # def _handle_skill_install(self, message: dict) -> None:
    #     """When mycroft.api.skill_install event is detected on the bus,
    #     this function install a skill based on the Git repository provided.
    #     """
    #     self.log.debug("mycroft.api.skill_install message detected")
    #     check_auth(self, message)
    #     if self.authenticated:
    #         skill: str = message.data.get("skill")
    #         confirm: bool = message.data.get("confirm")
    #         try:
    #             msm_config = build_msm_config(self.config_core)
    #             msm = create_msm(msm_config)
    #             msm.install(skill)
    #             if confirm:
    #                 utterance: str = message.data.get("dialog")
    #                 lang: str = message.data.get("lang")
    #                 send(self, MSG_TYPE["speak"],
    #                      data={"utterance": utterance, "lang": lang})
    #             send(self, f'{MSG_TYPE["skill_install"]}.answer',
    #                  data={"skill": skill})
    #         except AlreadyInstalled:
    #             send(self, f'{MSG_TYPE["skill_install"]}.answer',
    #                  data={"skill": "already installed"})
    #         except InstallException as err:
    #             self.log.error("unable to install the skill")
    #             self.log.debug(err)

    # def _handle_skill_uninstall(self, message: dict) -> None:
    #     """When mycroft.api.skill_uninstall event is detected on the bus,
    #     this function uninstall a skill based on the skill ID.
    #     """
    #     self.log.debug("mycroft.api.skill_uninstall message detected")
    #     check_auth(self, message)
    #     if self.authenticated:
    #         skill: str = message.data.get("skill")
    #         confirm: bool = message.data.get("confirm")
    #         try:
    #             msm_config = build_msm_config(self.config_core)
    #             msm = create_msm(msm_config)
    #             msm.remove(skill)
    #             if confirm:
    #                 utterance: str = message.data.get("dialog")
    #                 lang: str = message.data.get("lang")
    #                 send(self, MSG_TYPE["speak"],
    #                      data={"utterance": utterance, "lang": lang})
    #             send(self, f'{MSG_TYPE["skill_uninstall"]}.answer',
    #                  data={"skill": skill})
    #         except AlreadyRemoved:
    #             send(self, f'{MSG_TYPE["skill_uninstall"]}.answer',
    #                  data={"skill": "already uninstalled"})
    #         except MultipleSkillMatches as err:
    #             send(self, f'{MSG_TYPE["skill_uninstall"]}.answer',
    #                  data={"skill": "multiple matches found, not uninstalled"})
    #             self.log.warning("unable to uninstall because of "
    #                              "mutliple matches")
    #             self.log.debug(err)
    #         except RemoveException as err:
    #             self.log.error("unable to uninstall the skill")
    #             self.log.debug(err)

    def initialize(self) -> None:
        """The initialize method is called after the Skill is fully
        constructed and registered with the system. It is used to perform
        any final setup for the Skill including accessing Skill settings.
        https://openvoiceos.github.io/ovos-technical-manual/skill_structure/#initialize
        """
        self.authenticated: bool = False
        self.configured: bool = False

        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self) -> None:
        """Each OVOS device will check for updates to a users settings
        regularly, and write these to the skill's settings.json.
        https://openvoiceos.github.io/ovos-technical-manual/skill_settings
        """
        self._setup()
