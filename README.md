# ACME Notifications

Notification hub with Slack integration

## Setup

### Dependencies

Using locally compiled `uwsgi`, installed with `pip`. Had mysterious errors with packaged version.

```
$ sudo apt install redis
$ sudo apt remove '*uwsgi*'
$ pip install slackclient[optional] slackeventsapi uwsgi redis
```

#### Scopes

- channels:history
- channels:read
- channels:write
- chat:write
- groups:history
- groups:read
- groups:write
- im:history
- im:read
- im:write
- mpim:history
- mpim:read
- mpim:write
- reactions:read
- reactions:write
- users:read

### Database

Initialize the database

    $ sqlite3 acme_notifications/instance/db.sqlite < schema.sql

### Services

Set services up to start on boot. 

```
$ sudo bash -c '
  cd config
  rsync *.service /etc/systemd/system
  rsync acme-notifications.ini /etc/uwsgi
  systemctl enable emperor.uwsgi.service
  systemctl start  emperor.uwsgi.service
  systemctl enable acme-workers.service
  systemctl start  acme-workers.service
  ln -srf acme-notifications.conf /etc/nginx/sites-enabled/acme-notifications.conf 
'
```

Initialize the database

    $ sqlite3 acme_notifications/instance/db.sqlite < schema.sql


## Usage

Check for messages in the Redis queue:

    $ redis-cli
    127.0.0.1:6379> get msg

Monitor the services:

    $ tail -f /var/log/nginx/*.log /var/log/uwsgi/*.log /var/log/syslog

Add a message to the queue from the command line:

    $ push-msg "a message"

## Notes about Slack apps

- Apps are created in one primary workspace that can't be changed later
- Apps can then be distributed to other workspaces
- Deleting the app in the primary workspace deletes it everywhere
- To work with the app itself, go in through api.slack.org
- To install the app in a workspace, go in through slack.org
- Installing the app in its primary workspace does not cause Slack to hit the OAUTH2 endpoint on the app, so it can't be tested that way.

## Resources

- App management page: https://api.slack.com/apps
- Using OAuth 2.0: https://api.slack.com/docs/oauth
- Slack button: https://api.slack.com/docs/slack-button
- Edit scopes and get credentials: https://api.slack.com/apps
- Python client documentation: https://slack.dev/python-slackclient

