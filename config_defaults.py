#!/usr/bin/env python
import logging
from datetime import datetime
from pytz import timezone

# Default configuration.
# Do not edit this.  Copy config_sample.py to config.py and edit that.

# Logging
LOGGING_LEVEL_CONSOLE = logging.INFO
LOGGING_LEVEL_FILE = logging.ERROR
LOGGING_FILE = None  # or set to file path LOGGING_FILE="/var/log/esp_mqtt.log"

# MQTT
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_BIND_ADDRESS = ""
MQTT_CLIENT_ID = "esp_mqtt"

# ESP API
ESP_API_URL = "https://developer.sepush.co.za/business/2.0/"
ESP_AREA_ID = "capetown-7-gardens"
ESP_TEST = False
ESP_REFRESH_API_COUNTS_SECONDS = 10 * 60  # 10 minutes

# Homie Standard Items
# https://homieiot.github.io/specification/spec-core-v4_0_0/

HOMIE_BASE_TOPIC = "homie"
HOMIE_DEVICE_ID = "eskomsepush"
HOMIE_DEVICE_NAME = "Eskom Loadshedding Schedule"
HOMIE_DEVICE_VERSION = "4.0.0"
HOMIE_DEVICE_EXTENSIONS = ""
HOMIE_INIT_SECONDS = 3600 * 24  # Daily
HOMIE_MQTT_QOS = 1
HOMIE_MQTT_RETAIN = True
HOMIE_PUBLISH_ALL_SECONDS = 60
HOMIE_IMPLEMENTATION = "esp_mqtt"
HOMIE_MAX_EVENTS = 3

# TZ
TIMEZONE = "Africa/Johannesburg"
FAR_AWAY_DATE = datetime(2099, 1, 1, 9, 9, 9, 0, timezone(TIMEZONE))
