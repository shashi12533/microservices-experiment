#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask_restful import abort
from media_engine.helper import get_logger
from media_engine.models import CountryInfo
from media_engine.models import m_session, AccountApiKey, Account
from sqlalchemy import exc


def is_authenticated(api_key):
    try:
        account_api_key = m_session.query(AccountApiKey) \
            .filter(AccountApiKey.api_key == api_key) \
            .filter(AccountApiKey.deleted_on.is_(None)) \
            .first()
    except exc.SQLAlchemyError as e:
        crash_log = get_logger('crash')
        crash_log.error(e)
        raise abort(401, message='NO-DB-CONNECTION', status='error')
    except Exception as e:
        crash_log = get_logger('crash')
        crash_log.error(e)
        raise abort(401, message='MEDIA-ENGINE-ERROR', status='error')

    if not account_api_key:
        raise abort(401, message='BAD-API-KEY', status='error')
    account = account_api_key.account
    if not account.is_api_access:
        raise abort(401, message='NO-API-ACCESS', status='error')
    return account_api_key.account_id


def verify_account_id(account_id):
    account_obj = m_session.query(Account).filter(Account.id == account_id).first()
    return account_obj.is_verified


def get_all_country_char_codes():
    country_obj = m_session.query(CountryInfo).with_entities(
        CountryInfo.char_code).all()

    if not country_obj:
        raise Exception("COUNTRY-NOT-EXIST")

    return zip(*country_obj)[0]


if __name__ == '__main__':
    print(get_all_country_char_codes())