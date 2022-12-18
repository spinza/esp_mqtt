#!/usr/bin/env python
import logging

logger = logging.getLogger("paradox_mqtt").getChild(__name__)
from time import sleep, time
from datetime import datetime, timedelta, time
import paho.mqtt.client as mqtt

from config_defaults import *
from config import *
from pprint import pprint
from pytz import timezone

import requests


class ESP:
    def __init__(self):
        """Intialise ESP"""
        logger.debug("Initialising ESP class...")
        # mqtt client
        self.mqtt = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.on_message = self.homie_message
        # MQTT Will
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$state")
        self.mqtt.will_set(
            topic, payload="lost", qos=HOMIE_MQTT_QOS, retain=HOMIE_MQTT_RETAIN
        )

        # area
        self.area_id = ESP_AREA_ID
        self.area_name = None
        self.region_name = None

        # events
        self.events = []

        # API related
        # last update from API
        self.last_api_update = None
        self.next_api_update = datetime(1900, 1, 1, 0, 0, 0, 0, timezone(TIMEZONE))

        # API allowance
        self.api_count = None
        self.api_limit = None
        self.api_limit_type = None

        # status
        self.status_loadshedding = None
        self.status_loadshedding_start = FAR_AWAY_DATE
        self.status_loadshedding_end = FAR_AWAY_DATE
        self.status_warning_5min = None
        self.status_warning_15min = None
        self.status_note = None

        # timers
        self.homie_init_time = datetime(1900, 1, 1, 0, 0, 0, 0, timezone(TIMEZONE))
        self.homie_publish_all_time = datetime(
            1900, 1, 1, 0, 0, 0, 0, timezone(TIMEZONE)
        )
        self.esp_api_counts_refresh_time = datetime(
            1900, 1, 1, 0, 0, 0, 0, timezone(TIMEZONE)
        )
        self.next_status_time = datetime(1900, 1, 1, 0, 0, 0, 0, timezone(TIMEZONE))

        logger.debug("Initialised ESP class.")

    def mqtt_connect(self, host="localhost", port=1883, keepalive=60, bind_address=""):
        logger.info("Connecting to mqtt.")
        self.mqtt.connect(host, port, keepalive, bind_address)
        self.mqtt.loop_start()
        self.mqtt.subscribe(
            "{}/{}/{}/{}/{}/{}".format(HOMIE_BASE_TOPIC, "+", "+", "+", "set", "#")
        )
        logger.info("Connected to mqtt.")

    def homie_publish(self, topic, message):
        self.mqtt.publish(
            topic=topic, payload=message, qos=HOMIE_MQTT_QOS, retain=HOMIE_MQTT_RETAIN
        )

    def homie_message(self, client, userdata, message):
        logger.info(
            "message topic={}, message={}".format(
                message.topic, str(message.payload.decode("utf-8"))
            )
        )

        # do nothing as this is one way traffic
        pass

    def main_loop(self):
        """Wait for and then process messages."""
        while True:
            sleep(1)
            now = datetime.now(timezone(TIMEZONE))
            if now > self.homie_init_time + timedelta(seconds=HOMIE_INIT_SECONDS):
                self.homie_init()
            elif now > self.next_api_update:
                self.get_area()
                self.update_loadshedding_status()
                self.homie_publish_all()
            elif now > self.next_status_time:
                self.update_loadshedding_status()
                self.homie_publish_all()
            elif now > self.homie_publish_all_time + timedelta(
                seconds=HOMIE_PUBLISH_ALL_SECONDS
            ):
                self.update_loadshedding_status()
                self.homie_publish_all()
            elif now > self.esp_api_counts_refresh_time + timedelta(
                seconds=ESP_REFRESH_API_COUNTS_SECONDS
            ):
                self.get_api()
                self.homie_publish_all()

    def homie_publish_device_state(self, state):
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$state")
        self.homie_publish(topic, state)

    def homie_init(self):
        # device to init
        self.homie_init_device()
        self.homie_init_area()
        self.homie_init_api()
        self.homie_init_status()
        # self.homie_init_events()

        # device ready
        self.homie_publish_device_state("ready")
        self.homie_init_time = datetime.now(timezone(TIMEZONE))

    def homie_init_device(self):
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$homie")
        self.homie_publish(topic, HOMIE_DEVICE_VERSION)
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$name")
        self.homie_publish(topic, HOMIE_DEVICE_NAME)
        self.homie_publish_device_state("init")
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$nodes")
        nodes = "area,api,status"  # ,event1,event2,event3"
        self.homie_publish(topic, nodes)
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$extensions")
        self.homie_publish(topic, "")
        topic = "{}/{}/{}".format(HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, "$implementation")
        self.homie_publish(topic, HOMIE_IMPLEMENTATION)

    def homie_publish_all(self, init=False):
        self.homie_publish_area()
        self.homie_publish_api()
        # self.homie_publish_events()
        self.homie_publish_status()
        self.homie_publish_all_time = datetime.now(timezone(TIMEZONE))

    def homie_init_node(self, node_id, name, type=None, properties=None):
        topic = "{}/{}/{}/{}".format(
            HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, "$name"
        )
        self.homie_publish(topic, name)
        if type != None:
            topic = "{}/{}/{}/{}".format(
                HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, "$type"
            )
            self.homie_publish(topic, type)
        if properties != None:
            topic = "{}/{}/{}/{}".format(
                HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, "$properties"
            )
            self.homie_publish(topic, properties)

    def homie_message_boolean(self, value):
        if value:
            return "true"
        else:
            return "false"

    def homie_publish_boolean(self, topic, value):
        message = self.homie_message_boolean(value)
        self.homie_publish(topic, message)

    def homie_message_datetime(self, value):
        if value == None:
            return ""
        else:
            return value.isoformat()

    def homie_publish_property(self, node_id, property_id, datatype, value=None):
        if value != None:
            topic = "{}/{}/{}/{}".format(
                HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id
            )
            if datatype == "boolean":
                message = self.homie_message_boolean(value)
            elif datatype == "datetime":
                message = self.homie_message_datetime(value)
            else:
                message = value
            self.homie_publish(topic, message)

    def homie_init_property(
        self,
        node_id,
        property_id,
        name,
        datatype,
        format=None,
        settable=False,
        retained=True,
        unit=None,
    ):
        topic = "{}/{}/{}/{}/{}".format(
            HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$name"
        )
        self.homie_publish(topic, name)
        if datatype == "datetime":
            datatype = "string"
        topic = "{}/{}/{}/{}/{}".format(
            HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$datatype"
        )
        self.homie_publish(topic, datatype)
        if format != None:
            topic = "{}/{}/{}/{}/{}".format(
                HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$format"
            )
            self.homie_publish(topic, format)
        topic = "{}/{}/{}/{}/{}".format(
            HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$settable"
        )
        self.homie_publish_boolean(topic, settable)
        topic = "{}/{}/{}/{}/{}".format(
            HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$retained"
        )
        self.homie_publish_boolean(topic, retained)
        if unit != None:
            topic = "{}/{}/{}/{}/{}".format(
                HOMIE_BASE_TOPIC, HOMIE_DEVICE_ID, node_id, property_id, "$unit"
            )
            self.homie_publish(topic, unit)

    def homie_init_area(self):
        self.homie_init_node(
            node_id="area",
            name="Area",
            properties="areaid,areaname,regionname",
        )
        self.homie_init_property(
            node_id="area",
            property_id="areaid",
            name="Area ID",
            datatype="string",
        )
        self.homie_init_property(
            node_id="area",
            property_id="areaname",
            name="Area Name",
            datatype="string",
        )
        self.homie_init_property(
            node_id="area",
            property_id="regionname",
            name="Region Name",
            datatype="string",
        )

    def homie_init_api(self):
        self.homie_init_node(
            node_id="api",
            name="Area",
            properties="lastapiupdate,apicount,apilimit,apilimittype",
        )
        self.homie_init_property(
            node_id="api",
            property_id="lastapiupdate",
            name="Last Update",
            datatype="datetime",
        )
        self.homie_init_property(
            node_id="api",
            property_id="apicount",
            name="API Count",
            datatype="integer",
        )
        self.homie_init_property(
            node_id="api",
            property_id="apilimit",
            name="API Limit",
            datatype="integer",
        )
        self.homie_init_property(
            node_id="api",
            property_id="apilimittype",
            name="API Limit Type",
            datatype="string",
        )

    def homie_init_status(self):
        self.homie_init_node(
            node_id="status",
            name="Loadshedding status",
            properties="loadshedding,warning15min,warning5min,loadsheddingstart,loadsheddingend,note",
        )
        self.homie_init_property(
            node_id="status",
            property_id="loadshedding",
            name="Current Loadshedding",
            datatype="boolean",
        )
        self.homie_init_property(
            node_id="status",
            property_id="warning15min",
            name="Loadshedding 15 minute Warning",
            datatype="boolean",
        )
        self.homie_init_property(
            node_id="status",
            property_id="warning5min",
            name="Loadshedding 5 minute Warning",
            datatype="boolean",
        )
        self.homie_init_property(
            node_id="status",
            property_id="loadsheddingstart",
            name="Loadshedding Start Time",
            datatype="datetime",
        )
        self.homie_init_property(
            node_id="status",
            property_id="loadsheddingend",
            name="Loadshedding End Time",
            datatype="datetime",
        )
        self.homie_init_property(
            node_id="status",
            property_id="note",
            name="Status Note",
            datatype="string",
        )

    def homie_publish_status(self):
        self.homie_publish_property(
            node_id="status",
            property_id="loadshedding",
            datatype="boolean",
            value=self.status_loadshedding,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="warning5min",
            datatype="boolean",
            value=self.status_warning_5min,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="warning15min",
            datatype="boolean",
            value=self.status_warning_15min,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="loadsheddingstart",
            datatype="datetime",
            value=self.status_loadshedding_start,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="loadsheddingend",
            datatype="datetime",
            value=self.status_loadshedding_end,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="loadsheddingend",
            datatype="datetime",
            value=self.status_loadshedding_end,
        )
        self.homie_publish_property(
            node_id="status",
            property_id="note",
            datatype="string",
            value=self.status_note,
        )

    def homie_publish_area(self):
        self.homie_publish_property(
            node_id="area",
            property_id="areaid",
            datatype="string",
            value=self.area_id,
        )
        self.homie_publish_property(
            node_id="area",
            property_id="areaname",
            datatype="string",
            value=self.area_name,
        )
        self.homie_publish_property(
            node_id="area",
            property_id="regionname",
            datatype="string",
            value=self.region_name,
        )

    def homie_init_events(self):
        for i in range(1, HOMIE_MAX_EVENTS + 1):
            node_id = "event{}".format(i)
            self.homie_init_node(
                node_id=node_id,
                name="Event {}".format(i),
                type=None,
                properties="start,end,note",
            )
            self.homie_init_property(
                node_id=node_id,
                property_id="start",
                name="Start Time",
                datatype="datetime",
                settable=False,
            )
            self.homie_init_property(
                node_id=node_id,
                property_id="end",
                name="End Time",
                datatype="datetime",
                settable=False,
            )
            self.homie_init_property(
                node_id=node_id,
                property_id="node",
                name="Note",
                datatype="string",
                settable=False,
            )

    def homie_publish_events(self):
        for i in range(1, HOMIE_MAX_EVENTS + 1):
            node_id = "event{}".format(i)
            if len(self.events) >= i:
                event = self.events[i - 1]
            else:
                event = {
                    "start": None,
                    "end": None,
                    "note": None,
                }
            self.homie_publish_property(
                node_id=node_id,
                property_id="start",
                datatype="datetime",
                value=event["start"],
            )
            self.homie_publish_property(
                node_id=node_id,
                property_id="end",
                datatype="datetime",
                value=event["end"],
            )
            self.homie_publish_property(
                node_id=node_id,
                property_id="note",
                datatype="string",
                value=event["note"],
            )

    def homie_publish_api(self):
        self.homie_publish_property(
            node_id="api",
            property_id="lastapiupdate",
            datatype="datetime",
            value=self.last_api_update,
        )
        self.homie_publish_property(
            node_id="api",
            property_id="apicount",
            datatype="integer",
            value=self.api_count,
        )
        self.homie_publish_property(
            node_id="api",
            property_id="apilimit",
            datatype="integer",
            value=self.api_limit,
        )
        self.homie_publish_property(
            node_id="api",
            property_id="apilimittype",
            datatype="string",
            value=self.api_limit_type,
        )

    def seconds_until_end_of_day(self, dt):
        # type: integer
        """
        Get awxonsa until end of day on the datetime passed.
        """
        tomorrow = dt + timedelta(days=1)
        return (
            timezone(TIMEZONE).localize(datetime.combine(tomorrow, time.min)) - dt
        ).total_seconds()

    def update_next_api_update(self):
        remaining = self.api_limit - self.api_count
        if self.last_api_update != None:
            t = self.seconds_until_end_of_day(self.last_api_update)
            self.next_api_update = self.last_api_update + timedelta(
                seconds=t / (remaining + 1)
            )

    def get_api(self):
        logger.debug("Get api_allowance...")
        url = ESP_API_URL + "api_allowance"
        payload = {}
        headers = {"token": ESP_API_TOKEN}
        response = requests.request("GET", url, headers=headers, data=payload)
        r = response.json()
        self.api_count = r["allowance"]["count"]
        self.api_limit = r["allowance"]["limit"]
        self.api_limit_type = r["allowance"]["type"]
        self.update_next_api_update()
        self.esp_api_counts_refresh_time = datetime.now(timezone(TIMEZONE))

    def get_area(self):
        self.get_api()
        if self.api_limit - self.api_count > 0:
            logger.debug("Get area...")
            if ESP_TEST:
                test = "&test=current"
            else:
                test = ""
            url = ESP_API_URL + "area" + "?id=" + ESP_AREA_ID + test
            payload = {}
            headers = {"token": ESP_API_TOKEN}
            response = requests.request("GET", url, headers=headers, data=payload)
            r = response.json()
            self.events = []
            for event in r["events"]:
                event["start_string"] = event["start"]
                event["start"] = datetime.fromisoformat(event["start_string"])
                event["end_string"] = event["end"]
                event["end"] = datetime.fromisoformat(event["end_string"])
                self.events.append(event)
            self.last_api_update = datetime.now(timezone(TIMEZONE))
            self.get_api()

    def update_loadshedding_status(self):
        now = datetime.now(timezone(TIMEZONE))
        self.status_loadshedding = False
        self.status_loadshedding_start = FAR_AWAY_DATE
        self.status_loadshedding_end = FAR_AWAY_DATE
        self.status_note = "Not loadshedding"
        for event in self.events:
            if now > event["start"] and now < event["end"]:
                self.status_loadshedding = True
                self.status_loadshedding_end = event["end"]
                self.status_note = event["note"]
            if event["start"] > now:
                if self.status_loadshedding_start == None:
                    self.status_loadshedding_start = event["start"]
                elif self.status_loadshedding_start > event["start"]:
                    self.status_loadshedding_start = event["start"]
            if event["end"] > now:
                if self.status_loadshedding_end == None:
                    self.status_loadshedding_end = event["end"]
                elif self.status_loadshedding_end > event["end"]:
                    self.status_loadshedding_end = event["end"]
        self.next_status_time = now + timedelta(minutes=5)
        if self.status_loadshedding_start == None:
            self.status_warning_5min = False
            self.status_warning_15min = False
        else:
            if self.status_loadshedding_start - now < timedelta(minutes=5):
                self.status_warning_5min = True
            else:
                self.status_warning_5min = False
                self.next_status_time = self.status_loadshedding_start - timedelta(
                    minutes=5
                )
            if self.status_loadshedding_start - now < timedelta(minutes=15):
                self.status_warning_15min = True
            else:
                self.status_warning_15min = False
                self.next_status_time = self.status_loadshedding_start - timedelta(
                    minutes=5
                )
            if self.status_loadshedding_start < self.next_status_time:
                self.next_status_time = self.status_loadshedding_start
        if self.status_loadshedding_end == None:
            pass
        else:
            if self.status_loadshedding_end < self.next_status_time:
                self.next_status_time = self.status_loadshedding_end
