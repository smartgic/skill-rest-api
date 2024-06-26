"""Functions used across the skill
"""

from base64 import b64encode
from pathlib import Path
from ovos_bus_client.message import Message
from ovos_utils.log import LOG
from shutil import rmtree


def check_auth(self, message: dict) -> bool:
    """This function checks for authentication between this skill and the
    REST API based on a Bearer token declared on the API configuration and
    on the skill's settings.

    api_key contains the value registred settings.json and app_key
    contains the key sent by API during a call.

    To authenticate, both variables should match.
    """
    if self.configured:
        api_key: bytes = b64encode(self.api_key.encode("utf-8"))
        app_key: str = message.data.get("app_key")
        if api_key.decode("utf-8") == app_key:
            LOG.debug("api and skill are authenticated")
            self.authenticated = True
            return True
        self.bus.emit(
            Message(
                str(message.msg_type) + ".answer",
                data={"error": "both keys don't match"},
                context={"authenticated": False},
            )
        )
        LOG.debug("both keys don't match")
        return False
    self.bus.emit(
        Message(
            str(message.msg_type) + ".answer",
            data={"error": "no api key detected from home.mycroft.ai"},
            context={"authenticated": False},
        )
    )
    self.log.debug("no api key found in settings.json")

    return False


def delete(self, directory: str, parent: bool = False) -> bool:
    """Delete files and directories from a parent directory

    Parent directory is not removed by default, the parent option need to
    defined to True.
    """
    directory = Path(directory)
    try:
        for item in directory.iterdir():
            if item.is_dir():
                rmtree(item)
            else:
                item.unlink()
        if parent:
            rmtree(directory)
            LOG.debug(f"parent directory {directory} has been removed")
        return True
    except OSError as err:
        LOG.debug(f"unable to delete {directory} directory: {err}")
        return False


def send(self, msg_type: str, data: dict) -> None:
    """This function is a wrapper to send message to the bus with pre-exiting
    data.

    It wraps self.bus.emit(Message()) which avoid to have to load twice the
    same library and avoid code duplication.
    """
    self.bus.emit(
        Message(msg_type, data=data, context={"authenticated": self.authenticated})
    )
