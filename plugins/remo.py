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

def post_select_room_action(slack_client, channel, user=None, ephemeral=False):
    nature_devices = nature_api.v1_devices_get()

    options = [{"text": dev["name"], "value": dev["name"]} for dev in nature_devices]

    attachments = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#258ab5",
            "attachment_type": "default",
            "callback_id": "select_room",
            "actions": [
                {
                    "name": "device_list",
                    "text": "Select room",
                    "type": "select",
                    "options": options
                }
            ]
        }
    ]

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        attachments=attachments
    )

def room_info(slack_client, channel, user=None, ephemeral=False):
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

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="\n".join(status_lines)
    )