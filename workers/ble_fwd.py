#!/usr/bin/env python

import logging
import time

import redis

import uwatch2lib
from acme_notifications.instance import settings

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
    log.info("Starting forwarding from Redis to BLE")
    while True:
        try:
            msg_str = pop_msg()
            forward_to_watch(msg_str)
        except KeyboardInterrupt:
            return
        except Exception:
            log.exception("")
            time.sleep(settings.REDIS_RETRY_DELAY)


def pop_msg():
    """Pop the next message from the Redis queue"""
    while True:
        try:
            log.debug("Waiting for new message on Redis queue")
            with redis.Redis() as r:
                msg_key, msg_bytes = r.blpop("msg")
        except Exception as e:
            log.error(f"Pop from Redis failed. Retrying.")
            log.error(f"  Error: {e}")
            time.sleep(settings.REDIS_RETRY_DELAY)
        else:
            return msg_bytes.decode("utf-8")


def forward_to_watch(msg_str):
    while True:
        try:
            with uwatch2lib.Uwatch2(settings.UWATCH2_MAC) as watch:
                watch.send_message(msg_str)
        except Exception as e:
            log.error(f"Forward to watch failed. Retrying.")
            log.error(f"  Error: {e}")
            log.error(f"  Msg: {msg_str}")
            time.sleep(settings.RETRY_DELAY_SEC)
        else:
            log.error(f"Forwarded to watch: {msg_str}")
            break


if __name__ == "__main__":
    main()
