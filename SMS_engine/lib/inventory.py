#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from media_engine.helper import get_logger
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.validators import not_empty
from media_engine.models import m_session, AccountInfo, IncomingConfig

logger = get_logger()


@not_empty('customer_id', 'INVENTORY-NULL-CUSTOMER-ID', req=True, var_type=unicode)
@not_empty('product_id', 'INVENTORY-NULL-PRODUCT-ID', req=True)
def get_inventory(customer_id=None, product_id=None):
    logger.info('get_inventory for {}'.format(customer_id))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)

    try:
        acknowledgement_url, delivery_report_url = m_session.query(AccountInfo) \
        .filter(AccountInfo.account_id == account_id) \
        .filter(AccountInfo.product_id == product_id) \
        .filter(AccountInfo.deleted_on.is_(None))\
        .with_entities(AccountInfo.incoming_url, AccountInfo.delivery_report_url)\
        .first()
    except:
        acknowledgement_url = None
        delivery_report_url = None

    try:
        incoming_url, short_code = m_session.query(IncomingConfig) \
        .filter(IncomingConfig.account_id == account_id) \
        .filter(IncomingConfig.incoming_product_id == product_id) \
        .filter(IncomingConfig.deleted_on.is_(None))\
        .with_entities(IncomingConfig.push_to_url, IncomingConfig.short_code)\
        .first()
    except:
        incoming_url = None

    return {
        'product_id': product_id,
        'incoming_url': incoming_url,
        'delivery_report_url': delivery_report_url,
        'acknowledgement_url': acknowledgement_url
    }


@not_empty('account_id', 'NULL-ACCOUNT-ID', req=True, var_type=long)
@not_empty('product_id', 'NULL-PRODUCT-ID', req=True)
@not_empty('delivery_report_url', 'NULL-DR-URL', req=False)
@not_empty('acknowledgement_url', 'NULL-ACK-URL', req=False)
def save_delivery_ack_url(**kwargs):
    account_id = kwargs['account_id']
    product_id = kwargs['product_id']
    delivery_report_url = kwargs.get('delivery_report_url')
    acknowledgement_url = kwargs.get('acknowledgement_url')

    logger.info(
        'save_delivery_url for account_id : {}, product_id: {}, delivery_report_url: {}, acknowledgement_url: {}'.format(
            account_id,
            product_id,
            delivery_report_url,
            acknowledgement_url,
        )
    )
    account_info_obj = m_session.query(AccountInfo)\
        .filter(AccountInfo.account_id == account_id)\
        .filter(AccountInfo.product_id == product_id)\
        .filter(AccountInfo.deleted_on.is_(None)).first()

    if not account_info_obj:
        account_info_obj = AccountInfo(
            account_id=account_id,
            product_id=product_id,
            delivery_report_url=delivery_report_url,
            incoming_url=acknowledgement_url,
        )
    # incoming url is stored in Incoming Config
    # Now, incoming_url is placeholder for acknowledgement url in account_info table
    account_info_obj.incoming_url = acknowledgement_url
    account_info_obj.delivery_report_url = delivery_report_url

    m_session.add(account_info_obj)
    m_session.flush()
    return account_info_obj


@not_empty('account_id', 'NULL-ACCOUNT-ID', req=True, var_type=long)
@not_empty('product_id', 'NULL-PRODUCT-ID', req=True)
@not_empty('incoming_url', 'NULL-INCOMING-URL', req=False)
def save_incoming_url(**kwargs):
    account_id = kwargs['account_id']
    product_id = kwargs['product_id']
    incoming_url = kwargs['incoming_url']
    incoming_obj = m_session.query(IncomingConfig)\
        .filter(IncomingConfig.account_id == account_id)\
        .filter(IncomingConfig.incoming_product_id == product_id)\
        .filter(IncomingConfig.deleted_on.is_(None)).first()

    if not incoming_obj:
        # dummy values will be changed after admin updates them
        incoming_obj = IncomingConfig(
            account_id=account_id,
            incoming_product_id=product_id,
            push_to_url=incoming_url,
            keyword='dummy',
            country_id='US',
        )
    else:
        incoming_obj.push_to_url = incoming_url
    m_session.add(incoming_obj)
    m_session.flush()
    return incoming_obj


def get_delivery_url(account_id, product_id):
    try:
        account_info = m_session.query(AccountInfo) \
            .filter_by(account_id=account_id) \
            .filter_by(product_id=product_id) \
            .first()
    except Exception as exc:
        logger.error("error in get_delivery_url: {}".format(exc.message))
        account_info = None
    return account_info.delivery_report_url if account_info else ''
