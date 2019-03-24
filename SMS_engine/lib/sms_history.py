#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sqlalchemy_paginator import Paginator

from media_engine.helper import get_worker_logger, generate_unique_business_id
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.validators import not_empty
from media_engine.models import m_session, SmsHistory, SmsHistorySnapshot, IncomingSms
from media_engine.config import config

logger = get_worker_logger('worker')


# TODO : Currently search is not to be implemented
# def search(customer_id, product_id=None, label=None,
#            start_date=None, end_date=None):
#     logger.info('search :: '.format(customer_id))
#     account_id = accounting.get_account_id_by_customer_id(customer_id=customer_id)
#
#     query = m_session.query(SmsHistory).filter(
#         SmsHistory.account_id == account_id)
#     if product_id:
#         query = query.filter(SmsHistory.product_id == product_id)
#     if label:
#         product = routing.get_product(
#             account_id,
#             label
#         )
#         product_id = product.id
#         query = query.filter(SmsHistory.product_id == product_id)
#     if start_date:
#         query = query.filter(SmsHistory.created_on >= start_date)
#     if end_date:
#         query = query.filter(SmsHistory.created_on <= end_date)
#
#     sms_history_obj = query.all()
#     return sms_history_obj


# def get_number_of_sms_sent(customer_id, product_id):
#     return []


@not_empty('customer_id', 'SMS-HISTORY-NULL-CUSTOMER-ID', req=True)
@not_empty('page_size', 'SMS-HISTORY-NULL-PAGE-SIZE', req=False, default_val=10, var_type=int)
def get_sms_history(customer_id=None, page_size=None):
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    sms_history_query = m_session.query(SmsHistory).filter(
        SmsHistory.account_id == account_id).order_by(
        SmsHistory.created_on.desc())
    paginator = Paginator(sms_history_query, page_size)
    return paginator


@not_empty('customer_id', 'INCOMING-SMS-HISTORY-NULL-CUSTOMER-ID', req=True)
@not_empty('page_size', 'INCOMING-SMS-HISTORY-NULL-PAGE-SIZE', req=False, default_val=10, var_type=int)
def get_incoming_sms_history(customer_id=None, page_size=None):
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    sms_history_query = m_session.query(IncomingSms).filter(
        IncomingSms.account_id == account_id).order_by(
        IncomingSms.created_on.desc())
    paginator = Paginator(sms_history_query, page_size)
    return paginator


def log_sms(sms_id, account_id, product_id, label, response, sender_id, mobile_number,
                formatted_mobile_number, sms_text, number_of_sms, encoding,
                service_provider_id, used_credits, currency_code, source):

    sms_info = dict(
        id=sms_id,
        mobile_number=mobile_number,
        formatted_mobile_number=formatted_mobile_number,
        sender_id=sender_id,
        response_id=response['response_id'],
        sent_status=response['sent_status'],
        text=sms_text,
        account_id=account_id,
        product_id=product_id,
        label=label,
        status_message=str(response['status_message']),
        number_of_sms=number_of_sms,
        credits=used_credits,
        currency_code=currency_code,
        encoding=encoding,
        source=source,
        is_international=response['is_international'],
        service_provider_id=service_provider_id
    )

    logger.info("log_sms :: sms_info = {}".format(sms_info))
    sms_history_obj = SmsHistory(**sms_info)
    m_session.add(sms_history_obj)

    if response['sent_status'] == 'success':
        log_sms_snapshot(
            sms_id,
            response['response_id'],
            account_id
        )


def log_sms_snapshot(sms_id, message_id, account_id):
    """sms_history index on created_on, delivery status"""
    logger.info("log_sms_snapshop :: sms_id = {}, message_id = {} "
                "and account_id = {}".format(sms_id, message_id, account_id))
    snapshot_obj = SmsHistorySnapshot(
        id=generate_unique_business_id(),
        sms_id=sms_id,
        message_id=message_id,
        account_id=account_id
    )
    m_session.add(snapshot_obj)
    m_session.flush()


def parse_response(response):
    logger.info('get_response_params :: response = {}'.format(response))
    params = {
        'is_international': 0
    }
    if len(response) >= 3:
        status = response[0]
        if status == 'success':
            params.update({
                'response_id': response[2],
                'sent_status': 'success',
                'status_message': 'Success'
            })
        elif status == 'error':
            params.update({
                'response_id': 0,
                'sent_status': 'error',
                'status_message': response[2]
            })
        elif status == 'queued':
            params.update({
                'response_id': response[1],
                'sent_status': 'queued',
                'status_message': 'Scheduled'
            })
        else:
            params.update({
                'response_id': response[2],
                'sent_status': response[0],
                'status_message': response[0]
            })
        if len(response) == 4:
            params['is_international'] = response[3]
    else:
        logger.error('Error in get_response_params. '
                     'Response is not in the intended format '
                     '--> (p1, p2, p3, [p4])')
        params = {
            'response_id': 0,
            'sent_status': 'error',
            'status_message': response,
            'is_international': 0
        }

    return params


@not_empty('account_id', 'ACCOUNT-ID', req=True, var_type=long)
@not_empty('sms_id_list', 'SMS-ID-LIST', req=True, var_type=list)
def get_sms_status(account_id=None, sms_id_list=None):
    logger.info("get_sms_status :: account_id = {} and sms_id_list = {}".format(account_id, sms_id_list))
    sms_history_query = m_session.query(SmsHistory).filter(
        SmsHistory.account_id == account_id).filter(
        SmsHistory.id.in_(sms_id_list)).order_by(
        SmsHistory.created_on.desc()).with_entities(
        SmsHistory.id, SmsHistory.delivery_status, SmsHistory.dr_received_on, SmsHistory.status_message)

    result = sms_history_query.all()
    result = [
        {
            'sms_id': sms_id,
            'status':  status or ("failed : {}".format(status_message)
                                  if status_message in config.SEND_DLR_LIST
                                  else status_message),
            'delivered_on': delivered_on
        }
        for sms_id, status, delivered_on, status_message in result
    ]
    logger.info("result: {}".format(result))
    found_records = [i['sms_id'] for i in result]
    wrong_sms_id_list = [{'sms_id': sms_id, 'status': 'INVALID-SMS-ID', 'delivered_on': None}
        for sms_id in sms_id_list if sms_id not in found_records]
    logger.info("wrong_sms_id_list: {}".format(wrong_sms_id_list))
    result.extend(wrong_sms_id_list)

    logger.info("result: {}".format(result))

    return result


def update_delivery_status_in_sms_history(sms_id, status, timestamp):
    m_session.query(SmsHistory).filter_by(id=sms_id).update(
        dict(delivery_status=status, dr_received_on=timestamp)
    )
    m_session.flush()
