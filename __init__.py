"""api entrypoint skill
"""
from mycroft import MycroftSkill
from mycroft.api import DeviceApi
from mycroft.messagebus.message import Message
from mycroft.configuration import Configuration
from mycroft.util.network_utils import _connected_google
from .utils import check_auth
from .constants import CONSTANT_MSG_TYPE


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

        # Network
        self.add_event(CONSTANT_MSG_TYPE["connectivity"],
                       self._handle_connectivity)

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
            if _connected_google:
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
            self.bus.emit(
                Message(CONSTANT_MSG_TYPE["info"],
                        data={**data_api, **data_local},
                        context={"authenticated": self.authenticated})
            )

    def _handle_connectivity(self, message):
        """When mycroft.api.connectivity event is detected on the bus,
        this function will use the _connected_google() function from mycroft
        core to detect if the instance is connected to Internet.
        """
        check_auth(self, message)
        if self.authenticated:
            self.bus.emit(
                Message(CONSTANT_MSG_TYPE["connectivity"],
                        data=_connected_google(),
                        context={"authenticated": self.authenticated})
            )


def create_skill():
    """Main function to register the skill
    """
    return Api()
