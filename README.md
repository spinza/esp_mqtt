# Introduction

This code takes EskomSePush API loadshedding schedule for a particular area and publishes as a MQTT update for home automation or other purposes.

# Usage

1. Get a token for the API [from here](https://eskomsepush.gumroad.com/l/api).
2. Get your area ID as follows replacing gardens with a string to search for.  Look through the results to find the area ID you need.
```
curl --location --request GET 'https://developer.sepush.co.za/business/2.0/areas_search?text=gardens' --header 'token: ABCDEF-ABCDEF-ABCDEF-ABCDEF'
```
3. Create a `config.py` file.  Below an example file:
```python
!/usr/bin/env python
import logging

#Logging
LOGGING_LEVEL_CONSOLE = logging.INFO
LOGGING_LEVEL_FILE = logging.ERROR
LOGGING_FILE = None

# MQTT
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# ESP API
ESP_API_TOKEN = "ABCDEF-ABCDEF-ABCDEF-ABCDEF"
ESP_AREA_ID = "capetown-7-gardens"
```
3. Look at `config_defaults.py` for further settings that can be overwritten in `config.py`.
4. The service should publish details of upcoming (or current) loadshedding to MQTT using the [Homie convention](https://homieiot.github.io/).  
5. Use the above in your home automation (for example using the [MQTT binding in Openhab](https://www.openhab.org/addons/bindings/mqtt/)). Openhab should automatically pick up variou Things as it recognises the Homie convention.

# What is published?

TBD
