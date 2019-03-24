#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sqlalchemy import func

from media_engine.helper import get_logger
from media_engine.lib.validators import not_empty
from media_engine.models import SmsHistory, m_session

logger = get_logger()


@not_empty('account_id', 'SMS-HISTORY-BAD-ACCOUNT-ID', req=True)
@not_empty('product_id', 'SMS-HISTORY-BAD-PRODUCT-ID', req=True)
def get_latency(account_id=None, product_id=None):
    latency = 1
    return latency


@not_empty('account_id', 'SMS-HISTORY-BAD-ACCOUNT-ID', req=True)
@not_empty('product_id', 'SMS-HISTORY-BAD-PRODUCT-ID', req=True)
def get_delivery_ratio(account_id=None, product_id=None):
    delivery_ratio = 99.99
    return delivery_ratio


@not_empty('account_id', 'SMS-HISTORY-BAD-ACCOUNT-ID', req=True)
@not_empty('product_id', 'SMS-HISTORY-BAD-PRODUCT-ID', req=True)
def get_sms_status_count_by_product(account_id=None, product_id=None):
    """

    :param account_id:
    :param product_id:
    :return:
     message_sent: total api call made for provided product_id
     message_delivered
    """
    message_delivered = m_session.query(SmsHistory).filter(SmsHistory.account_id == account_id) \
        .filter(SmsHistory.product_id == product_id) \
        .filter(SmsHistory.delivery_status == 'delivered').count()

    message_sent = m_session.query(SmsHistory).filter(SmsHistory.account_id == account_id) \
        .filter(SmsHistory.product_id == product_id) \
        .count()
    # .filter(SmsHistory.sent_status.in_(['success', 'queued'])).count()

    return dict(
        message_delivered=message_delivered,
        message_sent=message_sent
    )


@not_empty('account_id', 'SMS-HISTORY-BAD-ACCOUNT-ID', req=True)
@not_empty('product_id', 'SMS-HISTORY-BAD-PRODUCT-ID', req=True)
def get_stats(account_id, product_id):
    """
    Get stats from statistic table
    :param account_id:
    :param product_id:
    :return:
    """
    sms_status_info_dict = get_sms_status_count_by_product(account_id=account_id, product_id=product_id)
    sms_status_info_dict.update(dict(latency=get_latency(account_id=account_id, product_id=product_id)))
    sms_status_info_dict.update(dict(latency=get_delivery_ratio(account_id=account_id, product_id=product_id)))
    return sms_status_info_dict
