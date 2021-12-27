[![Build Status](https://travis-ci.com/smartgic/mycroft-rest-api-skill.svg?branch=21.2.2)](https://travis-ci.com/github/smartgic/mycroft-rest-api-skill) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-pink.svg?style=flat)](https://github.com/smartgic/mycroft-rest-api-skill/pulls) [![Skill: MIT](https://img.shields.io/badge/mycroft.ai-skill-blue)](https://mycroft.ai) [![Discord](https://img.shields.io/discord/809074036733902888)](https://discord.gg/sHM3Duz5d3)

<p align="center">
  <img alt="Mycrof REST API Skill" src="docs/mycroft-rest-api-logo.png" width="500px">
</p>

# REST API

Acts as a gateway between Mycroft AI core and Mycroft REST API.

## About

The Mycroft REST API allows an interaction with a Mycroft AI core instance without to log into it or without any voice interaction. The communication between this skill and the REST API uses an autentication token to enforce the security.

<img alt="API flow" src="docs/flow.png">


## Examples

No voice interaction because the skill will mostly interact with an API.

## Installation

Make sure to be within the Mycroft `virtualenv` before running the `msm` command.

```shell
$ . mycroft-core/venv-activate.sh
$ msm install https://github.com/smartgic/mycroft-rest-api-skill.git
```

## Configuration

This skill utilizes the `settings.json` file which allows you to configure this skill via `home.mycroft.ai` after a few seconds of having the skill installed you should see something like below in the https://home.mycroft.ai/#/skill location:

<img src='docs/rest-api-config.png' width='450'/>

The APi key should be retrieved from the Mycroft REST API `.env` file.

```ini
SECRET="557622baf088a6a4bee012c90f9097a23ec23ad6ce20eae9"
WS_URI="ws://192.168.1.97:8181/core"
ADMIN="goldyfruit"
API_KEY="bg80e453765a80d825988fe70c2c9b85d2a5494e720cecet"
```

Fill this out with your appropriate information and hit the `save` button.


## Credits

* [Smart'Gic](https://smartgic.io/)

## Category

**System**

## Tags

#api
#restapi
#websocket
#bus
