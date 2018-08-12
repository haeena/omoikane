from flask import Flask
from flask import request, make_response, Response
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os
import json
from pprint import pprint

from plugins.remo import post_room_info, post_select_room, update_select_device_in_room

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/omoikane/events", app)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(SLACK_BOT_TOKEN)

@app.route("/omoikane/interactive", methods=["POST"])
def handle_interactive_post():
    request_body = json.loads(request.form["payload"])
    pprint(request_body)

    if request_body["token"] != SLACK_SIGNING_SECRET:
        return make_response("", 400)

    channel = request_body["channel"]["id"]
    user = request_body["user"]["id"]
    callback_id = request_body["callback_id"]
    origical_message = request_body["original_message"]

    if callback_id == "nature_remo":
        room = request_body["actions"][0]["selected_options"][0]["value"]
        post_ts = request_body["message_ts"]
        update_select_device_in_room(slack_client, channel, origical_message, post_ts, room)

    return make_response("", 200)

@slack_events_adapter.on("message")
def handle_message(event_data):
    pprint(event_data)

    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        response_text = "Hello <@%s>! :tada:" % message["user"]
        slack_client.api_call("chat.postMessage", channel=channel, text=response_text)
    if message.get("subtype") is None and "room" in message.get('text'):
        channel = message["channel"]
        post_room_info(slack_client, channel)
    if message.get("subtype") is None and "ctrl" in message.get('text'):
        channel = message["channel"]
        post_select_room(slack_client, channel)

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.api_call("chat.postMessage", channel=channel, text=text)

if __name__ == "__main__":
    # Once we have our event listeners configured, we can start the
    # Flask server with the default `/events` endpoint on port 300
    app.run(host='0.0.0.0',port=3000)