
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from media_engine.helper import get_worker_logger
from media_engine.models import (
    m_session, CountryInfo
)
from media_engine.lib.validators import not_empty, validate_country_code
from datetime import datetime

logger = get_worker_logger('worker')

def add_country(**params):

    country_obj = CountryInfo(
        char_code=params['char_code'],
        name=params['country_name'],
        code= params['country_code'],
        mobile_number_length= params['mobile_number_length'],
        country_code_length = params['country_code_length'],
        is_top_country= params['is_top_country'],
    )
    m_session.add(country_obj)  #inserts a record into DB
    m_session.flush()
    return country_obj

@not_empty('country_char_code', err_code='COUNTRY-CODE-NULL', req=True)
def get_country(**params):
    country_obj = m_session.query(CountryInfo).filter(
       CountryInfo.char_code == params['country_char_code'],
    ).first()

    if not country_obj:
        raise Exception("COUNTRY-NOT-EXIST")

    params_obj = m_session.query(CountryInfo).filter(
        CountryInfo.char_code == params['country_char_code']
    ).first()

    return params_obj


def update_country(**params):
        country_obj = m_session.query(CountryInfo).filter(
            CountryInfo.char_code == params['country_char_code'],
        ).first()

        if not country_obj:
            raise Exception("COUNTRY-NOT-EXIST")

        [setattr(country_obj, key, val)
         for key, val in params.items() if val is not None]
        m_session.add(country_obj)
        m_session.flush()
        return country_obj


@not_empty('country_char_code', err_code='', req=True)
def delete_country(**params):

    country_obj = m_session.query(CountryInfo).filter_by(char_code = params['country_char_code'],).first()
    if not country_obj:
        raise Exception("COUNTRY-DOES-NOT-EXISTS")

    country_obj.deleted_on = 1
    m_session.flush()
    return True

