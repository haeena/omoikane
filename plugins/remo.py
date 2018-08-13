from slackeventsapi import SlackEventAdapter

import os
import re
import json
from pprint import pprint

# generate client
from nature_api_client.api_client import ApiClient as NatureApiClient, Configuration as NatureConfig
from nature_api_client.api import DefaultApi as NatureApi

nature_config = NatureConfig()
nature_config.access_token = API_TOKEN = os.getenv("NATURE_ACCESS_TOKEN")
nature_api_client = NatureApiClient(configuration=nature_config)
nature_api = NatureApi(nature_api_client)

def signed_number(i):
    i = str(i)
    try:
        i = int(i)
    except ValueError:
        i = float(i)
    return f"{i: }" if i == 0 else f"{i:+}"

def post_action_nature_remo(slack_client, channel):
    nature_devices = nature_api.v1_devices_get()

    options = [{"text": dev["name"], "value": dev["id"]} for dev in nature_devices]

    attachments = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#258ab5",
            "attachment_type": "default",
            "callback_id": "nature_remo",
            "actions": [
                {
                    "name": "select_room",
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

def handle_callback_nature_remo(slack_client, request):
    channel = request["channel"]["id"]
    user = request["user"]["id"]
    origical_message = request["original_message"]
    post_ts = request["message_ts"]
    attachments = origical_message["attachments"]

    actions = attachments[0]["actions"]
    selected_field = request["actions"][0]["name"]
    selected_value = request["actions"][0]["selected_options"][0]["value"]

    if selected_field == "select_room":
        selected_room = selected_value
        selected_room_option = [opt for opt in actions[0]["options"] if opt["value"] == selected_room]
        actions = actions[0:1]
        actions[0]["selected_options"] = selected_room_option

        nature_appliances = nature_api.v1_appliances_get()
        device_options = [{"text": app.nickname, "value": app.id} for app in nature_appliances if app.device.id == selected_room]

        actions.append({
                    "name": "select_device",
                    "text": "Select device",
                    "type": "select",
                    "options": device_options})

        attachments[0]["actions"] = actions

        slack_client.api_call(
            "chat.update",
            channel=channel,
            ts=post_ts,
            attachments=attachments
        )
    elif selected_field == "select_device":
        selected_device = selected_value
        selected_device_option = [opt for opt in actions[1]["options"] if opt["value"] == selected_device]
        actions = actions[0:2]
        actions[1]["selected_options"] = selected_device_option

        nature_appliances = nature_api.v1_appliances_get()
        device_info = [app for app in nature_appliances if app.id == selected_device][0]
        device_type = device_info.type

        if device_type == "AC":
            current_setting = device_info.settings
            current_mode = current_setting.mode if current_setting.button != "power-off" else "off"
            current_temp = current_setting.temp
            current_vol = current_setting.vol

            modes = device_info.aircon.range.modes
            mode_options = [{"text": "mode: off", "value": "off"}] + [{"text": "mode: {}".format(mode), "value": mode} for mode in modes.attribute_map.keys()]
            selected_mode_options = [opt for opt in mode_options if opt["value"] == current_mode]
            actions.append({
                        "name": "select_mode",
                        "text": "Select mode",
                        "type": "select",
                        "options": mode_options,
                        "selected_options": selected_mode_options})

            if current_mode not in ("off", "blow"):
                temps = getattr(device_info.aircon.range.modes, current_mode).temp
                if current_mode in ("auto", "dry"):
                    temp_options = [{"text": "temp: {}".format(signed_number(temp)), "value": temp} for temp in temps]
                    default_temp_options = [ opt for opt in temp_options if opt["value"] == "0" ]
                else:
                    temp_options = [{"text": "temp: " + str(temp) + "℃", "value": temp } for temp in temps]
                    if current_mode in ("warm"):
                        default_temp_options = [ opt for opt in temp_options if opt["value"] == "18" ]
                    else:
                        default_temp_options = [ opt for opt in temp_options if opt["value"] == "27" ]

                selected_temp_options = [opt for opt in temp_options if opt["value"] == current_temp]
                if len(selected_temp_options) == 0:
                    selected_temp_options = default_temp_options if len(default_temp_options) != 0 else temp_options[0]

                actions.append({
                            "name": "select_temp",
                            "text": "Select temperture",
                            "type": "select",
                            "options": temp_options,
                            "selected_options": selected_temp_options})

            if current_mode not in ("off"):
                vols = getattr(device_info.aircon.range.modes, current_mode).vol
                vol_options = [{"text": "volume: {}".format(vol), "value": vol} for vol in vols]
                selected_vol_options = [opt for opt in vol_options if opt["value"] == current_vol]
                if len(selected_vol_options) == 0:
                    selected_vol_options = vol_options[0]
                actions.append({
                            "name": "select_vol",
                            "text": "Select volume",
                            "type": "select",
                            "options": vol_options,
                            "selected_options": selected_vol_options})

            pprint(actions)
            attachments[0]["actions"] = actions

        else: # device_type == "IR"
            pass

        slack_client.api_call(
            "chat.update",
            channel=channel,
            ts=post_ts,
            attachments=attachments
        )

def post_room_info(slack_client, channel, user=None, ephemeral=False):
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