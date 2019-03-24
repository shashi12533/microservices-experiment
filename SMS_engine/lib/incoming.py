#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from media_engine.helper import get_logger
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import not_empty
from media_engine.models import IncomingConfig, m_session

logger = get_logger()


@not_empty('customer_id', 'CREDIT-NULL-CUSTOMER-ID', req=True)
@not_empty('product_id', 'CREDIT-NULL-PRODUCT-ID', req=True)
def get_incoming_config_of_product(customer_id=None, product_id=None):
    logger.info('get_incoming_config_of_product :: customer_id = {} '
                'and procuct_id = {}'.format(customer_id, product_id))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    incoming_config = m_session.query(
        IncomingConfig
    ).filter(
        IncomingConfig.account_id == account_id,
        IncomingConfig.incoming_product_id == product_id,
        IncomingConfig.deleted_on.is_(None)
    ).first()

    if not incoming_config:
        raise NotFoundError('INCOMING-CONFIG-FOUND')
    return incoming_config


def save_incoming_config_of_product(**kwargs):
    pass