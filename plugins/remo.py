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

def signed_number(i):
    i = str(i)
    try:
        i = int(i)
    except ValueError:
        i = float(i)
    return f"{i: }" if i == 0 else f"{i:+}"

def appliance_name_with_device(device_name, appliance_nickname):
    if appliance_nickname.lower().startswith(device_name.lower()):
        return device_name + ": " + appliance_nickname[len(device_name):].lstrip()
    else:
        return device_name + ": " + appliance_nickname

def post_action_nature_remo(slack_client, channel):
    nature_appliances = nature_api.v1_appliances_get()
    device_options = [{"text": appliance_name_with_device(app.device.name, app.nickname), "value": app.id} for app in nature_appliances]

    attachments = [
        {
            "text": "Please select target device, and operation.",
            "fallback": "Omoikane: IR Remote Control function by nature remo",
            "color": "#258ab5",
            "attachment_type": "default",
            "callback_id": "nature_remo",
            "actions": [
                {
                    "name": "select_device",
                    "text": "Select device",
                    "type": "select",
                    "options": device_options
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
    origical_message = request["original_message"]
    post_ts = request["message_ts"]
    attachments = origical_message["attachments"]

    actions = attachments[0]["actions"]
    selected_field = request["actions"][0]["name"]
    selected_value = request["actions"][0]["selected_options"][0]["value"] if "selected_options" in request["actions"][0] else None

    # device info
    if selected_field == "select_device":
        selected_device = selected_value
        selected_device_option = [opt for opt in actions[0]["options"] if opt["value"] == selected_device]
        actions = actions[0:1]
        actions[0]["selected_options"] = selected_device_option
        selected_device_name = actions[0]["selected_options"][0]["text"]
    else:
        selected_device = actions[0]["selected_options"][0]["value"]
        selected_device_name = actions[0]["selected_options"][0]["text"]

    nature_appliances = nature_api.v1_appliances_get()
    device_info = [app for app in nature_appliances if app.id == selected_device][0]
    device_type = device_info.type

    if device_type == "AC":
        current_setting = device_info.settings

        # merge button into mode
        if selected_field == "select_mode":
            selected_mode = selected_value
            current_setting.mode = selected_mode if selected_mode != "off" else current_setting.mode
            current_setting.button = "power-off" if selected_mode == "off" else "power-on"
        else:
            selected_mode = current_setting.mode if current_setting.button != "power-off" else "off"

        # on device change or on mode changes, re-populate actions
        if selected_field in ("select_device", "select_mode"):
            actions = actions[0:1]

            modes = device_info.aircon.range.modes
            mode_options = [{"text": "mode: off", "value": "off"}] + [{"text": "mode: {}".format(mode), "value": mode} for mode in modes.attribute_map.keys()]
            selected_mode_options = [opt for opt in mode_options if opt["value"] == selected_mode]
            actions.append({
                        "name": "select_mode",
                        "text": "Select mode",
                        "type": "select",
                        "options": mode_options,
                        "selected_options": selected_mode_options})

            if selected_mode != "off":
                # temperture
                temps = getattr(device_info.aircon.range.modes, current_setting.mode).temp
                if selected_mode in ("auto", "dry"):
                    temp_options = [{"text": "temp: {}".format(signed_number(temp)), "value": temp} for temp in temps]
                    current_setting.temp = "0"
                else:
                    temp_options = [{"text": "temp: " + str(temp) + "℃", "value": temp } for temp in temps]
                    if selected_mode == "warm":
                        current_setting.temp = "18"
                    elif selected_mode == "cool":
                        current_setting.temp = "27"

                selected_temp_options = [opt for opt in temp_options if opt["value"] == current_setting.temp]
                if len(selected_temp_options) == 0:
                    selected_temp_options = temp_options[0:1]
                    current_setting.temp = selected_temp_options[0]["value"]
                actions.append({
                            "name": "select_temp",
                            "text": "Select temperture",
                            "type": "select",
                            "options": temp_options,
                            "selected_options": selected_temp_options})

                # volume
                vols = getattr(device_info.aircon.range.modes, selected_mode).vol
                vol_options = [{"text": "volume: {}".format(vol), "value": vol} for vol in vols]
                selected_vol_options = [opt for opt in vol_options if opt["value"] == current_setting.vol]
                if len(selected_vol_options) == 0:
                    selected_vol_options = [opt for opt in vol_options if opt["value"] == "auto"]
                    current_setting.vol = selected_vol_options[0]["value"]
                if len(selected_vol_options) == 0:
                    selected_vol_options = vol_options[0:1]
                    current_setting.vol = selected_vol_options[0]["value"]
                actions.append({
                            "name": "select_vol",
                            "text": "Select volume",
                            "type": "select",
                            "options": vol_options,
                            "selected_options": selected_vol_options})

                # direction
                dirs = getattr(device_info.aircon.range.modes, selected_mode).dir
                dir_options = [{"text": "direction: {}".format(d), "value": d} for d in dirs]
                selected_dir_options = [opt for opt in dir_options if opt["value"] == current_setting.dir]
                if len(selected_dir_options) == 0:
                    selected_dir_options = [opt for opt in dir_options if opt["value"] == "still"]
                    current_setting.dir = selected_dir_options[0]["value"]
                if len(selected_dir_options) == 0:
                    selected_dir_options = dir_options[0:1]
                    current_setting.dir = selected_dir_options[0]["value"]
                actions.append({
                            "name": "select_dir",
                            "text": "Select direction",
                            "type": "select",
                            "options": dir_options,
                            "selected_options": selected_dir_options})

            # update actions
            attachments[0]["actions"] = actions
            slack_client.api_call(
                "chat.update",
                channel=channel,
                ts=post_ts,
                attachments=attachments
            )

        # temperture update
        if selected_field == "select_temp":
            current_setting.temp = selected_value

        # volume update
        if selected_field == "select_vol":
            current_setting.vol = selected_value

        # direction update
        if selected_field == "select_dir":
            current_setting.dir = selected_value

        if selected_field != "select_device":
            result = nature_api.v1_appliances_appliance_aircon_settings_post(
                selected_device,
                button=current_setting.button, operation_mode=current_setting.mode, 
                temperature=current_setting.temp,
                air_volume=current_setting.vol, air_direction=current_setting.dir)
            slack_client.api_call(
                "chat.postMessage",
                channel="#omoikane-test",
                text=f"Remo Send IR to {selected_device_name}: mode {selected_mode} - target temperture: {current_setting.temp} - air_volume: {current_setting.vol} - air_direction: {current_setting.dir}"
            )

    else: # device_type == "IR"
        if selected_field in ("select_device"):
            actions = actions[0:1]

            signals = device_info.signals
            sig_options = [{"text": sig.name, "value": sig.id} for sig in signals]
            actions.append({
                        "name": "select_sig",
                        "text": "Select signal",
                        "type": "select",
                        "options": sig_options})

            actions.append({
                        "name": "send_again",
                        "text": "Send Signal Again",
                        "type": "button"})

            # update actions
            attachments[0]["actions"] = actions
            slack_client.api_call(
                "chat.update",
                channel=channel,
                ts=post_ts,
                attachments=attachments
            )

        if selected_field != "select_device":
            signals = device_info.signals
            if selected_field == "select_sig":
                selected_signal = selected_value
                selected_sig_options = [{"text": sig.name, "value": sig.id} for sig in signals if sig.id == selected_signal]
                selected_signal_name = selected_sig_options[0]["text"]
                actions[1]["selected_options"] = selected_sig_options

                # update actions
                attachments[0]["actions"] = actions
                slack_client.api_call(
                    "chat.update",
                    channel=channel,
                    ts=post_ts,
                    attachments=attachments
                )

            else: # selected_field == "send_again"
                if "selected_options" not in actions[1]:
                    return
                selected_option = actions[1]["selected_options"][0]
                selected_signal = selected_option["value"]
                selected_signal_name = selected_option["text"]

            result = nature_api.v1_signals_signal_send_post(selected_signal)
            slack_client.api_call(
                "chat.postMessage",
                channel="#omoikane-test",
                text=f"Remo Send IR to {selected_device_name}: signal {selected_signal_name} "
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