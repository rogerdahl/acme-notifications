#!/usr/bin/env python

"""Add a message to the Redis queue from the command line.
"""

import argparse
import logging

import redis

DEBUG = False

log = logging.getLogger(__name__)


def main():
    # noinspection PyArgumentList
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format="%(levelname)-8s %(message)s",
        force=True,
    )
    # log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("msg")
    args = parser.parse_args()
    redis_client = redis.Redis()
    redis_client.rpush("msg", args.msg)


if __name__ == "__main__":
    main()
