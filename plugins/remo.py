from slackeventsapi import SlackEventAdapter

import os
import re
import json

# generate client
from nature_api_client.api_client import ApiClient as NatureApiClient, Configuration as NatureConfig
from nature_api_client.api import DefaultApi as NatureApi

nature_config = NatureConfig()
nature_config.access_token = API_TOKEN = os.getenv("NATURE_ACCESS_TOKEN")
nature_api_client = NatureApiClient(configuration=nature_config)
nature_api = NatureApi(nature_api_client)

def room_info(event_data):
    message = event_data["event"]
    if message.get("subtype") is None and "room" in message.get('text'):
        channel = message["channel"]

    nature_device_status = nature_api.v1_devices_get()

    status_lines = []
    for device in nature_device_status:
        lines = "{}:".format(device["name"])
        if "newest_events" not in device:
            continue
        events = device["newest_events"]
        if "te" in events:
            lines += " {: .3g}℃".format(float(events["te"]["val"]))
        if "hu" in events:
            lines += " {: .3g}%".format(float(events["hu"]["val"]))
        if "il" in events:
            lines += " {}Light".format(events["il"]["val"])
        status_lines.append(lines)

    message.send("\n".join(status_lines))