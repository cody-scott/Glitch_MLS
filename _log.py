import os
from flask import has_request_context, request
from flask.logging import default_handler

import datetime
import logging
from logging import Formatter


def setup_logger():
    nw = datetime.datetime.now()
    log_file = os.path.join(".data/logs", "Log_{}{}{}".format(nw.year, nw.month, nw.day))


    root = logging.getLogger()


    class RequestFormatter(Formatter):
        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            else:
                # print("no app context")
                record.url = None
                record.remote_addr = None

            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s]\t%(remote_addr)s requested %(url)s\t%(levelname)s\t%(module)s\t%(message)s'
    )


    default_handler.setFormatter(formatter)
    root.addHandler(default_handler)
    root.setLevel(logging.INFO)

    f_handler = logging.FileHandler(log_file)
    f_handler.setFormatter(formatter)
    f_handler.setLevel(logging.INFO)
    root.addHandler(f_handler)