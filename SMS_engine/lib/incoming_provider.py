#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from media_engine.helper import get_worker_logger
from media_engine.models import (
    m_session
)
from media_engine.helper import generate_unique_business_id

from media_engine.lib.validators import not_empty, validate_country_code
from datetime import datetime
from media_engine.models.incoming import IncomingProvider, IncomingProviderParams

logger = get_worker_logger('worker')


@not_empty('name', err_code='INCOMING-PROVIDER-EMPTY-PROVIDER-NAME')
@not_empty('api_name', err_code='INCOMING-PROVIDER-EMPTY-PROVIDER-API')
@not_empty('http_push_method', err_code='INCOMING-PROVIDER-EMPTY-HTTPPUSH-METHOD')
@not_empty('country_id', err_code='INCOMING-PROVIDER-EMPTY-COUNTRY-ID')
@not_empty('http_url', err_code='INCOMING-PROVIDER-EMPTY-HTTP-URL')
def add_incoming_provider(**params):
    provider_obj = IncomingProvider(
        name=params['name'],
        api_name=params['api_name'],
        http_push_method=params['http_push_method'],
        country_id=params['country_id'],
        http_url=params['http_url'],
    )
    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj

@not_empty('service_provider_id', err_code='INCOMING-PROVIDER-NULL-PROVIDER-ID')
def get_incoming_provider(**params):
    provider_obj = m_session.query(IncomingProvider).filter(
        IncomingProvider.id == params['service_provider_id']
    ).first()

    if not provider_obj:
        raise Exception('PROVIDER-NOT-PRESENT')

    provider_params_obj = m_session.query(IncomingProvider).filter(
        IncomingProvider.id == params['service_provider_id']
    ).first()

    return provider_obj

@not_empty('incoming_provider_id', err_code='INCOMING-PROVIDER-NULL-PROVIDER-ID')
@not_empty('param_name', err_code='INCOMING-PROVIDER-NULL-PARAM-NAME')
@not_empty('param-value', err_code='INCOMING-PROVIDER-NULL-PARAM-VALUE')
def add_incoming_provider_param(**params):
    provider_obj = m_session.query(IncomingProvider).filter(
        IncomingProvider.id == params['incoming_provider_id']
    ).first()

    if not provider_obj:
        raise Exception('PROVIDER-NOT-FOUND')

    provider_param_obj = IncomingProviderParams(
        incoming_provider_id=params['incoming_provider_id'],
        param_name=params['param_name'],
        sm_param_name=params['sm_param_name']
    )
    m_session.add(provider_param_obj)
    m_session.flush()
    return provider_param_obj

@not_empty('incoming_provider_id', err_code='INCOMING-PROVIDER-NULL-PROVIDER-ID')
def get_incoming_provider_params(**params):
    provider_param_obj = m_session.query(IncomingProviderParams).filter(
        IncomingProviderParams.incoming_provider_id == params['incoming_provider_id']
    ).first()

    if not provider_param_obj:
        raise Exception('PROVIDER-NOT-FOUND')

    provider_param_obj = m_session.query(IncomingProviderParams).filter(
        IncomingProviderParams.incoming_provider_id == params['incoming_provider_id']
    ).all()

    return provider_param_obj

@not_empty('provider_param_id', err_code='INCOMING-PROVIDER-NULL-PARAM-ID', req=True)
def delete_provider_param(**params):
    incoming_provider_param = m_session.query(IncomingProviderParams).filter(
        IncomingProviderParams.id == params['provider_param_id']
    ).first()

    if not incoming_provider_param:
        raise Exception('PROVIDER-PARAM-NOT-PRESENT')

    incoming_provider_param.deleted_on = datetime.now()
    m_session.add(incoming_provider_param)
    m_session.flush()
    return True

@not_empty('provider_id', err_code='INCOMING-PROVIDER-NULL-PROVIDER-ID')
def delete_provider(**params):
    incoming_provider = m_session.query(IncomingProvider).filter(
        IncomingProvider.id == params['provider_id']
    ).first()

    if not incoming_provider:
        raise Exception('PROVIDER-ID-NOT-PRESENT')

    incoming_provider.deleted_on = datetime.now()
    m_session.add(incoming_provider)
    m_session.flush()
    return True

@not_empty('provider_param_id', err_code='INCOMING-PROVIDER-NULL-PARAM-ID')
def update_incoming_provider_param(**params):
    provider_param = m_session.query(IncomingProviderParams).filter(
        IncomingProviderParams.id == params['provider_param_id']
    ).first()

    if not provider_param:
        raise Exception('PROVIDER-PARAM-NOT-FOUND')

    [setattr(provider_param, key, val)
     for key, val in params.items() if val is not None]

    m_session.add(provider_param)
    m_session.flush()
    return provider_param

@not_empty('provider_id', err_code='INCOMING-PROVIDER-NULL-PROVIDER-ID')
def update_incoming_provider(**params):
    provider_obj = m_session.query(IncomingProvider).filter(
        IncomingProvider.id == params['provider_id']
    ).first()

    if not provider_obj:
        raise Exception('PROVIDER-NOT-FOUND')

    [setattr(provider_obj, key, val)
     for key, val in params.items() if val is not None]

    m_session.add(provider_obj)
    m_session.flush()
    return provider_obj
