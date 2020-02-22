import flask

from acme_notifications import db, flask_redis

app = flask.current_app


@app.route("/", methods=["GET", "POST"])
def hello():
    return "Hello there!\n"


@app.route("/add", methods=["POST"])
def add_notification():
    title_str = ""
    body_str = flask.request.form["msg"]
    flask_redis.push(body_str)
    db.add_message(title_str, body_str)
    return "ok"


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = flask.url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return "\n".join(f"{a} {b}" for a, b in links)
