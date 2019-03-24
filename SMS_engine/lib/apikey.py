#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from media_engine.helper import generate_unique_api_key_hex
from media_engine.helper import get_logger
from media_engine.models import AccountApiKey, m_session
from media_engine.lib.accounting import get_account_id_by_customer_id

logger = get_logger()


def generate_api_key(customer_id=None):
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    account_api_key_obj = m_session.query(AccountApiKey)\
        .filter(AccountApiKey.account_id == account_id)\
        .filter(AccountApiKey.deleted_on.is_(None))\
        .first()

    if account_api_key_obj:
        account_api_key_obj.deleted_on = datetime.now()
        m_session.add(account_api_key_obj)

    account_api_key_obj_new = AccountApiKey(
        account_id=account_id,
        api_key=generate_unique_api_key_hex()
    )
    m_session.add(account_api_key_obj_new)
    m_session.commit()
    return account_api_key_obj_new
