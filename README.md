[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-pink.svg?style=flat)](https://github.com/smartgic/skill-rest-api/pulls) [![Skill: MIT](https://img.shields.io/badge/ovos-skill-blue)](https://openvoiceos.org) [![Discord](https://img.shields.io/discord/809074036733902888)](https://discord.gg/sHM3Duz5d3)

# REST API

Acts as a gateway between Open Voice OS and OVOS REST API.

## About

The OVOS REST API allows an interaction with a Mycroft AI core instance without to log into it or without any voice interaction. The communication between this skill and the REST API uses an autentication token to enforce the security.

<img alt="API flow" src="docs/flow.png">


## Examples

No voice interaction because the skill will mostly interact with an API.

## Installation

Make sure to be within the Open Voice OS `virtualenv` before running the `pip` command.

```shell
. ~/.venvs/ovos/bin/activate.sh
pip3 install git+https://github.com/smartgic/skill-rest-api.git
```

## Configuration

This skill utilizes the `~/.config/mycroft/skills/skill-rest-api.smartgic/settings.json` file which allows you to configure this skill.

The API key should be retrieved from the OVOS REST API `.env` file.

```ini
SECRET="557622baf088a6a4bee012c90f9097a23ec23ad6ce20eae9"
WS_HOST="10.12.50.20"
WS_PORT="8181"
API_KEY="bg80e453765a80d825988fe70c2c9b85d2a5494e720cecet"
USERS_DB="/users.json"
```

## Credits

* [Smart'Gic](https://smartgic.io/)

## Category

**System**

## Tags

#api
#restapi
#websocket
#bus
