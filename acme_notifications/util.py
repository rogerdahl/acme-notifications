import logging
import logging.config
import os
import pprint
import sys


def dump(o, msg="Object", logger=logging.debug):
    logger(f"{msg}:\n{pprint.pformat(o)}")


def abs_path(rel_path):
    return os.path.abspath(
        os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), rel_path)
    )


def setup_logging():
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {"format": "%(asctime)s %(levelname)s %(message)s",}
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "DEBUG", "handlers": ["wsgi"]},
        }
    )
