#!/usr/bin/env python

import os
import sys

import flask


def create_app(config=None):
    """Construct the core application."""
    app = flask.Flask(
        __name__,
        instance_path="/home/pi/web/acme-notifications/acme_notifications/instance",
        instance_relative_config=True,
    )
    app.config.from_object("acme_notifications.instance.settings")

    if "FLASK_CONF" in os.environ:
        app.config.from_envvar("FLASK_CONF")

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith(".py"):
            app.config.from_pyfile(config)

    # Set globals
    # db = SQLAlchemy()
    # redis_store = FlaskRedis()

    with app.app_context():
        # Set global values
        # redis_store.endpoint = app.config['ENDPOINT']
        # redis_store.post_query = app.config['POST_QUERY']

        # Initialize globals
        # redis_store.init_app(app)

        # Set up routes
        from acme_notifications.views import misc
        from acme_notifications.views import slack_

    return app


app = create_app()


if __name__ == "__main__":
    # Enable profiler
    # from werkzeug.contrib.profiler import ProfilerMiddleware
    # app.config['PROFILE'] = True
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # Note: Don't access app before app.run here. It causes the app to be implicitly
    # instantiated a second time or some such.

    try:
        app.run(
            host=app.config["HOST_INTERFACE"],
            port=app.config["HOST_PORT"],
            debug=app.config["DEBUG"],
            use_reloader=True,
            use_debugger=True,
            threaded=False,
        )

    except KeyboardInterrupt:
        sys.exit(0)
