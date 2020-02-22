import time

import flask
import redis


def get_client():
    redis_client = getattr(flask.g, "_redis", None)
    if redis_client is None:
        redis_client = flask.g._redis = redis.Redis()
    return redis_client


def push(msg_str):
    app = flask.current_app
    app.logger.info(f"Pushed to Redis: {msg_str}")
    get_client().rpush("msg", msg_str)


def pop():
    app = flask.current_app
    try:
        app.logger.info(f"Queue empty. Waiting for new msg...")
        redis_client = redis.Redis()
        msg_key, msg_bytes = redis_client.blpop("msg")
        msg_str = msg_bytes.decode("utf-8")
    except Exception as e:
        app.logger.info(f"Pop from queue failed. Retrying. Error: {e}")
        time.sleep(flask.current_app.config["REDIS_RETRY_DELAY"])
    else:
        app.logger.info(f"Popped new msg: {msg_str}")
        return msg_str


def close():
    redis_client = getattr(flask.g, "_redis", None)
    if redis_client is not None:
        redis_client.close()
