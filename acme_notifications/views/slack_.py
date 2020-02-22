#!/usr/bin/env python

"""Slack-cap
"""

import flask
import slack
import slackeventsapi

from acme_notifications import db, flask_redis, util
from acme_notifications.views.slack_custom import bot

app = flask.current_app


def create_slack_event_adapter(app):
    adapter = slackeventsapi.SlackEventAdapter(
        signing_secret=app.config["SIGNING_SECRET"],
        endpoint="/slack/events",
        server=app,
    )

    return adapter


adapter = create_slack_event_adapter(app)


# Slack


def get_slack_client(message_dict):
    slack_client = getattr(flask.g, "_slack", None)
    if slack_client is None:
        token = db.get_user_access_token(message_dict["authed_users"][0])
        if token is None:
            token = app.config["TOKEN"]
            app.logging.warning(f"Falling back to app token: {token}")
        slack_client = flask.g._slack_client = slack.WebClient(token)
    return slack_client


def get_user_display_name(message_dict, user_id):
    app.logger.debug(f"Looking up display_name for user_id: {user_id}")
    display_name = db.get_user_info(user_id)
    if display_name is None:
        user_dict = get_slack_client(message_dict).users_info(user=user_id)
        display_name = user_dict["user"]["real_name"]
        db.set_user_info(user_id, display_name)
        app.logger.debug(f"From Slack query: {user_id} -> {display_name}")
    else:
        app.logger.debug(f"From DB: {user_id} -> {display_name}")
    return display_name


def get_channel_name(message_dict, channel_id):
    try:
        channel = get_slack_client(message_dict).channels_info(channel=channel_id)
    except Exception as e:
        app.logger.debug(f'Error getting channel name for id "{channel_id}": {str(e)}')
        return channel_id
    else:
        util.dump(channel, "channel")
        # app.logger.debug(f"From Slack query: {channel_id} -> {channel}")
        # return channel["name"]
    return "x"


# Callbacks


def after_request_func(response):
    db.close_db()
    flask_redis.close()
    return response


# Views


@app.teardown_appcontext
def teardown_appcontext(error):
    db.close_db()
    flask_redis.close()


@app.before_first_request
def before_first_request():
    # slack_cap.util.dump(app.config, 'config')
    app.after_request(after_request_func)


@app.before_request
def before_request():
    util.dump(flask.request, "REQUEST")


@app.route("/slack/redirect")
def oauth_redirect():
    code = flask.request.args.get("code")
    client = slack.WebClient(token="")

    util.dump(f"code: {code}")
    util.dump(app.config["CLIENT_ID"])

    # Exchange verification code for an access token
    resp_dict = client.oauth_v2_access(
        client_id=app.config["CLIENT_ID"],
        client_secret=app.config["CLIENT_SECRET"],
        code=code,
        redirect_uri=app.config["OAUTH_REDIRECT_URL"],
    )

    util.dump(resp_dict, "resp_dict")

    auth_user = resp_dict["authed_user"]
    db.set_user_access_token(auth_user["id"], auth_user["access_token"])

    return "ok"


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error(f"Page not found: {error}")
    return "404 NotFound: {}".format(flask.request.url), 404


# SlackEventAdapter message handlers


@adapter.on("message")
def handle_message(message_dict):
    util.dump(message_dict, "Received Slack event: message")
    event_dict = message_dict["event"]

    if event_dict.get("subtype") is not None:
        app.logger.debug(
            f'Skipped message. Unsupported subtype: {event_dict.get("subtype")}'
        )
        return

    auth_users_list = message_dict["authed_users"]
    display_name = get_user_display_name(message_dict, event_dict["user"])
    # channel_name = get_channel_name(channel_id=event_dict["channel"])

    recv_msg_str = event_dict.get("text")
    out_msg_str = f"{display_name}: {recv_msg_str}"
    flask_redis.push(out_msg_str)

    # Further custom processing
    bot(message_dict)


@adapter.on("reaction_added")
def reaction_added(message_dict):
    util.dump(message_dict, "Received Slack event: reaction_added")
    event_dict = message_dict["event"]
    emoji = event_dict["reaction"]
    channel = event_dict["item"]["channel"]
    text = f":{emoji}:"
    # slack_client.api_call("chat.postMessage", channel=channel, text=text)


@adapter.on("error")
def error_handler(err):
    app.logger.error(str(err))


class Error(Exception):
    pass
