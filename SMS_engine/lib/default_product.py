from __future__ import absolute_import
from media_engine.helper import get_worker_logger

from media_engine.models import m_session,Account
from media_engine.models.common import CountryInfo

from media_engine.models.provider import DefaultProduct
from media_engine.lib.validators import not_empty

logger = get_worker_logger('worker')

@not_empty('product_id', err_code='PRODUCT-ID-NULL', req=True)
@not_empty('customer_id', err_code='CUSTOMER-ID-NULL', req=True)
@not_empty('subtype', err_code='SUBTYPE-NULL', req=True)
@not_empty('country_code', err_code='COUNTRY-CODE-NULL', req=True)
def save_default_product(**params):

    print 'In add_default_product() , Params: ', params

    account_obj = m_session.query(Account).filter(
        Account.customer_id == params['customer_id'],
        ).first()

    default_product_obj = m_session.query(DefaultProduct).filter(
        DefaultProduct.account_id == account_obj.id,
        DefaultProduct.product_id == params['product_id'],
        DefaultProduct.subtype == params['subtype'],
        DefaultProduct.country_code == params['country_code']
    ).first()

    if default_product_obj is None:  # insert
        default_product_obj = DefaultProduct(
            account_id=account_obj.id,
            product_id=params['product_id'],
            country_code=params['country_code'],
            subtype=params['subtype'],
            is_active=params['is_active']
        )
        m_session.add(default_product_obj)  # inserts a record into DB
        m_session.flush()

    else:  # update
        if not default_product_obj:
            raise Exception("DEFAULT-PRODUCT-NOT-EXIST")

        default_product_obj.is_active = params['is_active']

        m_session.add(default_product_obj)
        m_session.flush()

    return default_product_obj


@not_empty('product_id', err_code='PRODUCT-ID-NULL', req=True)
@not_empty('customer_id', err_code='CUSTOMER-ID-NULL', req=True)
@not_empty('subtype', err_code='SUBTYPE-NULL', req=True)
@not_empty('country_code', err_code='COUNTRY-CODE-NULL', req=True)
def get_default_product(**params):
    print 'In get_default_product()'

    account_obj = m_session.query(Account).filter(
        Account.customer_id == params['customer_id'],
    ).first()

    default_product_obj = m_session.query(DefaultProduct).filter(
        DefaultProduct.account_id == account_obj.id,
        DefaultProduct.product_id == params['product_id'],
        DefaultProduct.subtype == params['subtype'],
        DefaultProduct.country_code == params['country_code']
    ).first()

    if not default_product_obj:
        raise Exception("DEFAULT-PRODUCT-NOT-EXIST")

    return default_product_obj
