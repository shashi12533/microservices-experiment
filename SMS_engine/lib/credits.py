#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from media_engine.helper import get_logger
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.currency import convert_currency
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import not_empty
from media_engine.models import Credit, m_session
from media_engine.models.configure import _OnehopMediaSession, orm
logger = get_logger()


@not_empty('account_id', 'CREDIT-NULL-ACCOUNT-ID', req=True, var_type=(int, long))
def get_all_credits(account_id=None):
    logger.info("get_all_credits :: account_id = {} ".format(account_id))
    credit_objs = m_session.query(Credit)\
        .filter(Credit.account_id == account_id) \
        .filter(Credit.deleted_on.is_(None))\
        .with_entities(Credit.account_id, Credit.product_id,
                       Credit.used_balance, Credit.balance,
                       Credit.currency_code)

    if not credit_objs:
        raise NotFoundError('CREDIT-NO-CREDITS')
    return credit_objs


@not_empty('account_id', 'CREDIT-NULL-ACCOUNT-ID', req=True, var_type=(int, long))
@not_empty('product_id', 'CREDIT-NULL-PRODUCT-ID', req=True)
def get_available_balance(account_id=None, product_id=None):
    logger.info("get_available_balance :: account_id = {} "
                "and product_id".format(account_id, product_id))
    credit_obj = m_session.query(Credit)\
        .filter(Credit.account_id == account_id) \
        .filter(Credit.product_id == product_id) \
        .filter(Credit.deleted_on.is_(None))\
        .with_entities(Credit.account_id, Credit.product_id,
                       Credit.deleted_on, Credit.balance).first()

    if not credit_obj:
        raise NotFoundError('CREDIT-NO-CREDIT-FOUND')
    logger.info("get_available_balance :: balance = {}".format(credit_obj.balance))
    return credit_obj.balance


@not_empty('customer_id', 'CREDIT-NULL-CUSTOMER-ID', req=True)
@not_empty('product_id', 'CREDIT-NULL-PRODUCT-ID', req=True)
def get_credits_of_product(customer_id=None, product_id=None):
    logger.info('get_credits_of_product :: customer_id = {} '
                'and procuct_id = {}'.format(customer_id, product_id))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    credit_obj = m_session.query(Credit).filter(
        Credit.account_id == account_id,
        Credit.product_id == product_id,
        Credit.deleted_on.is_(None)).first()

    if not credit_obj:
        raise NotFoundError('CREDIT-NO-CREDIT-FOUND')

    return credit_obj


@not_empty('customer_id', 'CREDIT-NULL-CUSTOMER-ID', req=True, var_type=unicode)
@not_empty('product_id', 'CREDIT-NULL-PRODUCT-ID', req=True)
@not_empty('balance', 'CREDIT-NULL-BALANCE', req=True, var_type=float)
@not_empty('currency_code', 'CREDIT-NULL-CURRENCY-CODE', req=True)
def upsert_credits(customer_id=None, product_id=None, balance=None, currency_code=None):
    logger.info('upsert_credits :: {}'.format(customer_id))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    return update_credits_by_account_id(account_id, product_id, balance, currency_code)


def update_credits_by_account_id(account_id, product_id, balance, currency_code):
    credits_dict = dict(
        account_id=account_id,
        product_id=product_id,
        balance=balance,
        currency_code=currency_code,
    )
    logger.info("update_credits_by_account_id :: params = {}".format(credits_dict))

    credit_obj = m_session.query(Credit)\
        .filter(Credit.account_id == account_id)\
        .filter(Credit.product_id == product_id)\
        .filter(Credit.deleted_on.is_(None))\
        .with_lockmode('update').first()

    if not credit_obj:
        credit_obj = Credit(**credits_dict)
        credit_obj.used_balance = 0.0
        logger.info("update_credits_by_account_id :: Create credits")
        m_session.add(credit_obj)

    else:
        # If deduct credits, then balance parameter is in negative,
        if balance < 0.0:
            used_credits = convert_currency(
                from_currency=currency_code,
                to_currency=credit_obj.currency_code,
                value=-balance
            )
            credit_obj.used_balance += used_credits
            logger.info("update_credits_by_account_id :: Used Credits "
                        "after currency conversion = {}".format(used_credits))

        added_credits = convert_currency(
            from_currency=currency_code,
            to_currency=credit_obj.currency_code,
            value=balance
        )
        logger.info("update_credits_by_account_id :: Added/Deducted Credits "
                    "after currency conversion = {}".format(added_credits))
        credit_obj.balance += added_credits

    logger.info("update_credits_by_account_id :: balance = {} and "
                "used_balance = {}".format(
                credit_obj.balance, credit_obj.used_balance))

    return credit_obj


@not_empty('customer_id', 'PRODUCT-CREDIT-BAD-CUSTOMER-ID', req=True)
def get_products_with_credit(customer_id=None):
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    products_credit_obj_list = m_session.query(Credit).filter(Credit.account_id == account_id).all()
    return products_credit_obj_list
