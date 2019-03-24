#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from media_engine.helper import get_worker_logger
from media_engine.models import (
    m_session, ServiceProvider, ServiceProviderParam, ServiceProviderConfig
)
from media_engine.lib.validators import not_empty, validate_country_code
from datetime import datetime

logger = get_worker_logger('worker')

@not_empty('provider_name', err_code='PROVIDER-NULL-PROVIDER-NAME', req=True)
@not_empty('api_url', err_code='PROVIDER-NULL-PROVIDER-API-URL', req=True)
@not_empty('country_code', err_code='PROVIDER-NULL-COUNTRY-CODE', req=True)
@not_empty('send_sms_function', err_code='PROVIDER-NULL-SENDSMS-FUNCTION', req=True)
@not_empty('module', err_code='PROVIDER-NULL-MODULE-NAME', req=True)
@not_empty('is_mms_enabled', err_code='PROVIDER-NULL-IS-MMS-VALUE', req=True)
def add_provider(**params):
    provider_obj = ServiceProvider(
        name=params['provider_name'],
        address=params['address'],
        contact = params['contact'],
        api_url = params['api_url'],
        api_port = params['api_port'],
        country_code = params['country_code'],
        send_sms_function = params['send_sms_function'],
        is_default = params['is_default'],
        dummy_status = params['dummy_status'],
        module = params['module'],
        pack_type = params['pack_type'],
        route_tag = params['route_tag'] if params['route_tag'] else None,
        balance_check_url = params['balance_check_url'] if params['balance_check_url'] else None,
        route_type = params['route_type'] if params['route_type'] else None,
        is_mms_enabled = params['is_mms_enabled'] if params['is_mms_enabled'] else 0,
        mms_api_url = params['mms_api_url'] if params['mms_api_url'] else None,

    )
    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj


@not_empty('id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def update_provider(**params):
    provider_obj = m_session.query(ServiceProvider).filter(
        ServiceProvider.id == params['id'],
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    [setattr(provider_obj, key, val)
     for key, val in params.items() if val is not None]

    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj

@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def delete_provider(**params):
    provider_obj = m_session.query(ServiceProvider).filter(
        ServiceProvider.id == params['service_provider_id'],
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    provider_obj.deleted_on = datetime.now()
    m_session.add(provider_obj)
    m_session.flush()
    return True

@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def get_provider(**params):
    provider_obj = m_session.query(ServiceProvider).filter(
        ServiceProvider.id == params['service_provider_id']
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    return provider_obj


@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
@not_empty('param_name', err_code='PROVIDER-NULL-PARAM-NAME', req=True)
@not_empty('param_value', err_code='PROVIDER-NULL-PARAM-VALUE', req=True)
@not_empty('run_time_value', err_code='PROVIDER-NULL-RUNTIME-VALUE', req=True)
@not_empty('encoding', err_code='PROVIDER-NULL-PARAM-ENCODING', req=True)
@not_empty('in_query_string', err_code='PROVIDER-NULL-IN-QUERYSTRING', req=True)
@not_empty('is_mms_param', err_code='PROVIDER-NULL-IS-MMS-VALUE', req=True)
def add_params(**params):
    provider_obj = m_session.query(ServiceProvider).filter(
        ServiceProvider.id == params['service_provider_id']).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    provider_param_obj = ServiceProviderParam(
        service_provider_id= params["service_provider_id"],
        param_name = params["param_name"],
        param_value = params["param_value"],
        run_time_value = params["run_time_value"],
        encoding = params["encoding"],
        in_query_string = params["in_query_string"],
        is_mms_param = params["is_mms_param"]
    )
    m_session.add(provider_param_obj)
    m_session.flush()
    return provider_param_obj


@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def get_params(**params):
    provider_obj = m_session.query(ServiceProvider).filter(
        ServiceProvider.id == params["service_provider_id"]
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    params_obj = m_session.query(ServiceProviderParam).filter(
        ServiceProviderParam.service_provider_id == params['service_provider_id']
    ).all()

    return params_obj

@not_empty('provider_param_id', err_code='PROVIDER-NULL-PARAM-ID', req=True)
def delete_provider_params(**params):
    params_obj = m_session.query(ServiceProviderParam).filter(
        ServiceProviderParam.id == params['provider_param_id']
    ).first()
    if not params_obj:
        raise Exception('PROVIDER-PARAM-NOT-FOUND')
    params_obj.deleted_on = datetime.now()
    m_session.add(params_obj)
    m_session.flush()
    return True

@not_empty('id', err_code='PROVIDER-NULL-PARAM-ID', req=True)
@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def update_provider_param(**params):
    param_obj = m_session.query(ServiceProviderParam)\
        .filter(
        ServiceProviderParam.id == params['id']
    ).filter(ServiceProviderParam.service_provider_id == params['service_provider_id']).first()

    if not param_obj:
        raise Exception('PROVIDER-PARAM-NOT-PRESENT')

    [setattr(param_obj, key, val)
     for key, val in params.items() if val is not None]

    m_session.add(param_obj)
    m_session.flush()
    return param_obj

@not_empty('provider_name', err_code='PROVIDER-NULL-PROVIDER-NAME', req=True)
@not_empty('api_url', err_code='PROVIDER-NULL-PROVIDER-API-URL', req=True)
@not_empty('country_code', err_code='PROVIDER-NULL-COUNTRY-CODE', req=True)
@not_empty('send_sms_function', err_code='PROVIDER-NULL-SENDSMS-FUNCTION', req=True)
@not_empty('module', err_code='PROVIDER-NULL-MODULE-NAME', req=True)
@not_empty('is_mms_enabled', err_code='PROVIDER-NULL-IS-MMS-VALUE', req=True)
def add_provider_config(**params):
    provider_obj = ServiceProviderConfig(
        name=params['name'],
        address=params['address'],
        contact = params['contact'],
        api_url = params['api_url'],
        api_port = params['api_port'],
        send_sms_function = params['send_sms_function'],
        dummy_status = params['dummy_status'],
        module = params['module'],
        route_tag = params['route_tag'] if params['route_tag'] else None,
        balance_check_url = params['balance_check_url'] if params['balance_check_url'] else None,
        route_type = params['route_type'] if params['route_type'] else None,
        mms_api_url = params['mms_api_url'] if params['mms_api_url'] else None,

    )
    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj


@not_empty('id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def update_provider_config(**params):
    provider_obj = m_session.query(ServiceProviderConfig).filter(
        ServiceProvider.id == params['id'],
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    [setattr(provider_obj, key, val)
     for key, val in params.items() if val is not None]

    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj

@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def delete_provider_config(**params):
    provider_obj = m_session.query(ServiceProviderConfig).filter(
        ServiceProviderConfig.id == params['service_provider_id'],
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    provider_obj.deleted_on = datetime.now()
    m_session.add(provider_obj)
    m_session.flush()
    return True

@not_empty('service_provider_id', err_code='PROVIDER-NULL-PROVIDER-ID', req=True)
def get_provider_config(**params):
    provider_obj = m_session.query(ServiceProviderConfig).filter(
        ServiceProviderConfig.id == params['service_provider_id']
    ).first()

    if not provider_obj:
        raise Exception("PROVIDER-DOES-NOT-EXISTS")

    return provider_obj
