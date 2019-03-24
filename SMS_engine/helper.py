#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import uuid
import logging
import logging.config
import hashlib

from media_engine.config import get_config
from celery.utils.log import get_task_logger

__logging_configured = False
__worker_logging_configured = False
config = get_config()


def get_date_time():
    return datetime.now()


def generate_unique_business_id():
    # when UUIDs are produced on separate machines, uuid1 is recommended
    return str(uuid.uuid4())


def generate_unique_api_key_hex():
    # when UUIDs are produced on separate machines, uuid1 is recommended
    return 'sm' + uuid.uuid4().hex


def md5_encrypt(val):
    return hashlib.md5(val).hexdigest()


def get_logger(logger_name=None):
    global __logging_configured
    if not __logging_configured:
        logging.config.dictConfig(config.LOGGING_CONFIG)
        __logging_configured = True
    logger = logging.getLogger(logger_name or config.DEFAULT_LOGGER_NAME)
    return logger


def get_worker_logger(logger_name=None):
    global __worker_logging_configured
    if not __worker_logging_configured:
        logging.config.dictConfig(config.LOGGING_CONFIG)
        __worker_logging_configured = True
    logger = get_task_logger(logger_name)
    return logger


def required_param(param):
    return 'missing parameter: {}'.format(param)
