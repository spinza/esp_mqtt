# Introduction

This code takes EskomSePush API loadshedding schedule for a particular area and publishes as a MQTT update for home automation or other purposes.

I assume below a recent Ubuntu distro.  Probably on Debian and possibly other Linux distros.

# Usage

1. Get a token for the API [from here](https://eskomsepush.gumroad.com/l/api).
2. Get your area ID as follows replacing gardens with a string to search for.  Look through the results to find the area ID you need.
```
curl --location --request GET 'https://developer.sepush.co.za/business/2.0/areas_search?text=gardens' --header 'token: ABCDEF-ABCDEF-ABCDEF-ABCDEF'
```
3. Clone the code locally.
4. Create a `config.py` file.  Below an example file:
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
# MQTT user and password below only set if used
# MQTT_USERNAME = "user"
# MQTT_PASSWORD = "password"

# ESP API
ESP_API_TOKEN = "ABCDEF-ABCDEF-ABCDEF-ABCDEF"
ESP_AREA_ID = "capetown-7-gardens"
```
5. Look at `config_defaults.py` for further settings that can be overwritten in `config.py`.
6. Create an enviroment with `python3 -m venv venv` (run it from the code folder.)
7. Activate the environment with `source venv/bin/activate`
8. Install the requirements with `pip -f requirements.txt`
9. Run it with `python main.py`
10.  You could also create a systemd service using the example script editing paths and users as appropriate.
11. The service should publish details of upcoming (or current) loadshedding to MQTT using the [Homie convention](https://homieiot.github.io/).  
12. Use the above in your home automation (for example using the [MQTT binding in Openhab](https://www.openhab.org/addons/bindings/mqtt/)). Openhab should automatically pick up variou Things as it recognises the Homie convention.

# What is published?

The script publishes in the homie format which means it can be automatically discovered by Openhab as an example.  Below a sample dump of the topics published.  The `$` endpoints such as `$name` represent Homie specific properties and can be ignored if not using Homie.


```
homie/eskomsepush/status/$name Loadshedding status
homie/eskomsepush/status/$properties loadshedding,warning15min,warning5min,loadsheddingnextstart,loadsheddingnextend,loadsheddingend,note
homie/eskomsepush/status/loadshedding false
homie/eskomsepush/status/loadshedding/$name Current Loadshedding
homie/eskomsepush/status/loadshedding/$datatype boolean
homie/eskomsepush/status/loadshedding/$settable false
homie/eskomsepush/status/loadshedding/$retained true
homie/eskomsepush/status/warning15min false
homie/eskomsepush/status/warning15min/$name Loadshedding 15 minute Warning
homie/eskomsepush/status/warning15min/$datatype boolean
homie/eskomsepush/status/warning15min/$settable false
homie/eskomsepush/status/warning15min/$retained true
homie/eskomsepush/status/warning5min false
homie/eskomsepush/status/warning5min/$name Loadshedding 5 minute Warning
homie/eskomsepush/status/warning5min/$datatype boolean
homie/eskomsepush/status/warning5min/$settable false
homie/eskomsepush/status/warning5min/$retained true
homie/eskomsepush/status/loadsheddingnextstart 2022-12-22T02:00:00+02:00
homie/eskomsepush/status/loadsheddingnextstart/$name Loadshedding Start Time
homie/eskomsepush/status/loadsheddingnextstart/$datatype string
homie/eskomsepush/status/loadsheddingnextstart/$settable false
homie/eskomsepush/status/loadsheddingnextstart/$retained true
homie/eskomsepush/status/loadsheddingnextend 2022-12-22T04:30:00+02:00
homie/eskomsepush/status/loadsheddingnextend/$name Loadshedding End Time
homie/eskomsepush/status/loadsheddingnextend/$datatype string
homie/eskomsepush/status/loadsheddingnextend/$settable false
homie/eskomsepush/status/loadsheddingnextend/$retained true
homie/eskomsepush/status/loadsheddingend 2099-01-01T01:01:01.000001+01:52
homie/eskomsepush/status/loadsheddingend/$name Loadshedding End Time
homie/eskomsepush/status/loadsheddingend/$datatype string
homie/eskomsepush/status/loadsheddingend/$settable false
homie/eskomsepush/status/loadsheddingend/$retained true
homie/eskomsepush/status/note Not loadshedding
homie/eskomsepush/status/note/$name Status Note
homie/eskomsepush/status/note/$datatype string
homie/eskomsepush/status/note/$settable false
homie/eskomsepush/status/note/$retained true
homie/eskomsepush/$homie 4.0.0
homie/eskomsepush/$name Eskom Loadshedding Schedule
homie/eskomsepush/$state ready
homie/eskomsepush/$nodes area,api,status
homie/eskomsepush/area/$name Area
homie/eskomsepush/area/$properties areaid,areaname,regionname
homie/eskomsepush/area/areaid capetown-7-gardens
homie/eskomsepush/area/areaid/$name Area ID
homie/eskomsepush/area/areaid/$datatype string
homie/eskomsepush/area/areaid/$settable false
homie/eskomsepush/area/areaid/$retained true
homie/eskomsepush/area/areaname Gardens (7)
homie/eskomsepush/area/areaname/$name Area Name
homie/eskomsepush/area/areaname/$datatype string
homie/eskomsepush/area/areaname/$settable false
homie/eskomsepush/area/areaname/$retained true
homie/eskomsepush/area/regionname City of Cape Town
homie/eskomsepush/area/regionname/$name Region Name
homie/eskomsepush/area/regionname/$datatype string
homie/eskomsepush/area/regionname/$settable false
homie/eskomsepush/area/regionname/$retained true
homie/eskomsepush/api/$name API
homie/eskomsepush/api/$properties lastapiupdate,apicount,apilimit,apilimittype
homie/eskomsepush/api/lastapiupdate 2022-12-21T23:11:44.187581+02:00
homie/eskomsepush/api/lastapiupdate/$name Last Update
homie/eskomsepush/api/lastapiupdate/$datatype string
homie/eskomsepush/api/lastapiupdate/$settable false
homie/eskomsepush/api/lastapiupdate/$retained true
homie/eskomsepush/api/apicount 48
homie/eskomsepush/api/apicount/$name API Count
homie/eskomsepush/api/apicount/$datatype integer
homie/eskomsepush/api/apicount/$settable false
homie/eskomsepush/api/apicount/$retained true
homie/eskomsepush/api/apilimit 50
homie/eskomsepush/api/apilimit/$name API Limit
homie/eskomsepush/api/apilimit/$datatype integer
homie/eskomsepush/api/apilimit/$settable false
homie/eskomsepush/api/apilimit/$retained true
homie/eskomsepush/api/apilimittype daily
homie/eskomsepush/api/apilimittype/$name API Limit Type
homie/eskomsepush/api/apilimittype/$datatype string
homie/eskomsepush/api/apilimittype/$settable false
homie/eskomsepush/api/apilimittype/$retained true
homie/eskomsepush/$implementation esp_mqtt
```
