#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
from importlib import import_module

from media_engine.api_models import oa_session, Customer
from media_engine.api_models.product import Product
from media_engine.helper import get_worker_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import not_empty
from media_engine.models import (
    m_session, Account, ServiceProvider, ServiceProviderParam, ServiceProviderConfig
)

logger = get_worker_logger('worker')


def get_account_api_access(account_id):
    logger.info("get_account_info :: account_id = {}".format(account_id))
    account_obj = m_session.query(Account).filter(
        Account.id == account_id
    ).with_entities(
        Account.id, Account.is_api_access
    ).first()

    if account_obj is None:
        raise NotFoundError("ACCOUNT-NOT-FOUND")

    logger.info("get_account_info :: account_id = {} and is_api_access = {}".format(
        account_obj.id, account_obj.is_api_access))
    return account_obj.is_api_access


def get_country_code(account_id):
    logger.info("get_country_code :: account_id = {}".format(account_id))
    customer_obj = oa_session.query(Customer).filter(
        Customer.account_id == account_id
    ).with_entities(
        Customer.account_id, Customer.country_code
    ).first()

    if customer_obj is None:
        raise NotFoundError("CUSTOMER-NOT-FOUND")

    logger.info("get_country_code :: country_code = {}".format(
        customer_obj.country_code))
    return customer_obj.country_code


def get_product_name(product_id):
    logger.info("get_product_details :: product_id = {}".format(product_id))
    product_obj = oa_session.query(Product).filter(
        Product.id == product_id).with_entities(Product.name).first()
    if product_obj:
        return product_obj.name
    else:
        raise NotFoundError("PRODUCT-NOT-FOUND")


def get_product_details(product_id):
    logger.info("get_product_details :: product_id = {}".format(product_id))
    product_obj = oa_session.query(Product).filter(
        Product.id == product_id
    ).first()

    if product_obj is None:
        raise NotFoundError("PRODUCT-NOT-FOUND")

    media_product_obj = product_obj.media_product
    if media_product_obj is None:
        raise NotFoundError("MEDIA-PRODUCT-NOT-FOUND")

    pack_type = media_product_obj.pack_type
    if pack_type is None:
        raise NotFoundError("PACK-TYPE-NOT-FOUND")

    merchant = product_obj.merchant
    if merchant is None:
        raise NotFoundError("MERCHANT-NOT-FOUND")

    module = merchant.module
    if module is None:
        raise NotFoundError("MODULE-NOT-FOUND")

    provider = get_provider(module, pack_type)
    price = media_product_obj.outbound_price
    currency = product_obj.base_currency
    country_code = product_obj.country_code
    logger.info("get_product_details :: provider = {}, price = {}, "
                "currency = {}".format(provider, price, currency))
    return provider, price, currency, country_code


def get_provider(module, pack_type):
    """
    :param module: provider module name
    :param pack_type: premium or regular
    :return: instance of a class from chosen provider module
    """
    logger.info("get_provider :: module = {} and pack_type = {}".format(
        module, pack_type))

    service_provider = m_session.query(ServiceProvider, ServiceProviderConfig).filter(
        ServiceProviderConfig.module == module,
        ServiceProvider.sp_config_id == ServiceProviderConfig.id,
        ServiceProvider.pack_type == pack_type)\
        .filter(ServiceProvider.deleted_on.is_(None)).with_entities(ServiceProvider.id, ServiceProviderConfig.api_url).first()
    if service_provider is None:
        raise NotFoundError("SERVICE-PROVIDER-NOT-FOUND")
    logger.info("get_provider :: service_provider : {}".format(service_provider.id))

    api_url = service_provider.api_url
    if api_url is None:
        raise NotFoundError("API-URL-NOT-FOUND")
    provider_id = service_provider.id

    params = get_provider_params(provider_id)
    cls = get_provider_dynamically(module)
    return cls(provider_id, api_url, params)


def get_provider_dynamically(module):
    logger.info("get_provider_dynamically :: module = {}".format(module))
    import_name = '{}.{}'.format('media_engine.lib.providers', module)
    module_object = import_module(import_name)
    class_name = module.capitalize()
    cls = getattr(module_object, class_name)
    return cls


def get_provider_params(provider_id):
    logger.info("get_provider_params :: provider_id = {}".format(provider_id))
    service_provider_params_obj = m_session.query(ServiceProviderParam).filter(
        ServiceProviderParam.service_provider_id == provider_id) \
        .filter(ServiceProviderParam.deleted_on.is_(None)) \
        .filter(ServiceProviderParam.encoding.is_(True)).all()

    if service_provider_params_obj is None:
        raise NotFoundError("SERVICE-PROVIDER-PARAMS-NOT-FOUND")

    params = [
        (
            a_param_obj.param_name,
            a_param_obj.param_value,
            a_param_obj.run_time_value,
            a_param_obj.encoding,
            a_param_obj.in_query_string,
            a_param_obj.is_mms_param
        )
        for a_param_obj in service_provider_params_obj
        ]
    logger.info("get_provider_params :: params = {}".format(params))
    return params


@not_empty('customer_id', 'ACCOUNT-NULL-CUSTOMER-ID', req=True)
def create_account(**params):
    account_obj = m_session.query(Account).filter(
        Account.customer_id == params['customer_id']).first()

    if not account_obj:
        account_obj = Account(customer_id=params['customer_id'])
        account_obj.is_api_access = False
        m_session.add(account_obj)
        m_session.flush()
    return account_obj


@not_empty('customer_id', 'ACCOUNT-NULL-CUSTOMER-ID', req=True)
@not_empty('is_api_access', 'ACCOUNT-BAD-IS-API-ACCESS', req=False, var_type=bool)
@not_empty('is_email_enabled', 'ACCOUNT-BAD-IS-EMAIL-ENABLED', req=False, var_type=bool)
@not_empty('is_test_account', 'ACCOUNT-BAD-IS-TEST-ACCOUNT', req=False, var_type=bool)
@not_empty('is_office_hours_opt_out', 'ACCOUNT-BAD-IS-OFFICE-HOURS-OPT-OUT', req=False, var_type=bool)
@not_empty('is_verified', 'ACCOUNT-BAD-IS-VERIFIED', req=False, var_type=bool)
@not_empty('is_mms_enabled', 'ACCOUNT-BAD-IS-MMS-ENABLED', req=False, var_type=bool)
def update_account(**kwargs):
    account = m_session.query(Account).filter(
        Account.customer_id == kwargs.get('customer_id')).first()

    if account is None:
        raise NotFoundError("ACCOUNT-NOT-FOUND")

    [setattr(account, key, val)
     for key, val in kwargs.items() if val is not None]

    m_session.add(account)
    m_session.flush()
    return account


@not_empty('customer_id', 'ACCOUNT-NULL-CUSTOMER-ID', req=True)
def get_account_flag_details(**kwargs):
    account = m_session.query(Account).filter(
        Account.customer_id == kwargs.get('customer_id')).first()

    if account is None:
        raise NotFoundError("ACCOUNT-NOT-FOUND")

    return account



@not_empty('customer_id', err_code='ACCOUNT-NULL-CUSTOMER-ID', req=True)
def delete_account(customer_id=None):
    account = m_session.query(Account) \
        .filter(Account.customer_id == customer_id) \
        .filter(Account.deleted_on.is_(None)) \
        .first()
    if not account:
        raise NotFoundError('ACCOUNT-BAD-ACCOUNT-ID')
    account.deleted_on = datetime.now()
    m_session.add(account)
    m_session.flush()
    return True


@not_empty('customer_id', err_code='ACCOUNT-NULL-CUSTOMER-ID', req=True)
def get_account_id_by_customer_id(customer_id=None):
    logger.info('get_account_id_by_customer_id :: customer_id = {}'.format(
        customer_id))
    account = m_session.query(Account).filter(
        Account.customer_id == customer_id
    ).with_entities(Account.id, Account.customer_id).first()
    if not account:
        raise NotFoundError('WRONG-CUSTOMER-ID')
    logger.info('get_account_id_by_customer_id :: account_id = {}'.format(account.id))
    return account.id


if __name__ == '__main__':
    delete_account('80001470')
