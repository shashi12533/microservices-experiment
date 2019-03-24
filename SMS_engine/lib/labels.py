#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
from functools import wraps

from media_engine.helper import get_logger
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import not_empty, validate_country_code
from media_engine.models import m_session, Label, Credit

logger = get_logger()


def get_label_obj(account_id, label):
    logger.info("get_label_obj :: account_id = {} and label = {}".format(
        account_id, label))
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id, Label.label == label).first()
    if not label_obj:
        raise NotFoundError("LABEL-NOT-FOUND")
    return label_obj


@not_empty('customer_id', 'LABEL-NULL-CUSTOMER-ID', req=True)
def list_labels_with_details(customer_id=None):
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    label_object_list = m_session.query(Label)\
        .filter(Label.account_id == account_id)\
        .filter(Label.deleted_on.is_(None))\
        .all()
    logger.info("list_labels_with_details :: Got labels list = {}".format(
        bool(label_object_list)))
    return label_object_list


@not_empty('account_id', 'LABEL-NULL-ACCOUNT-ID', req=True, var_type=long)
def list_labels(account_id=None):
    label_obj_list = m_session.query(Label)\
        .filter(Label.account_id == account_id)\
        .filter(Label.deleted_on.is_(None))\
        .filter(Label.is_active.is_(True))\
        .with_entities(Label.label)\
        .all()
    logger.info("list_labels :: Got labels list = {}".format(
        bool(label_obj_list)))
    return sorted([label[0] for label in label_obj_list])


@not_empty('account_id', 'LABEL-NULL-ACCOUNT-ID', req=True, var_type=(int, long))
@not_empty('product_id', 'LABEL-NULL-PRODUCT-ID', req=True)
def list_labels_for_product(account_id, product_id):
    label_obj_list = m_session.query(Label)\
        .filter(Label.account_id == account_id)\
        .filter(Label.deleted_on.is_(None))\
        .filter(Label.is_active.is_(True))\
        .filter(Label.product_id == product_id)\
        .with_entities(Label.label)\
        .all()
    logger.info("list_labels :: Got labels list = {}".format(
        bool(label_obj_list)))
    return sorted([label[0] for label in label_obj_list])




def validate_product_for_labeling(message):
    def wrapper(fn):
        # A side effect of using decorators is that the function that gets wrapped loses it's
        # natural __name__, __doc__, and __module__ attributes.
        # wraps decorator takes a function used in a decorator and adds the functionality of
        # copying over the function name, docstring, arguments list, etc.
        @wraps(fn)
        def decorator(*args, **kwargs):
            account_id = get_account_id_by_customer_id(customer_id=kwargs['customer_id'])
            credit_obj = m_session.query(Credit).filter(Credit.account_id == account_id).filter(
                Credit.product_id == kwargs['product_id']).filter(Credit.deleted_on.is_(None)).first()
            if credit_obj:
                return fn(*args, **kwargs)
            else:
                raise ValueError(message)
        return decorator

    return wrapper


@not_empty('label_id', 'LABEL-BAD-LABEL-ID', req=False)
@not_empty('customer_id', 'LABEL-NULL-CUSTOMER-ID', req=True)
@not_empty('product_id', 'LABEL-NULL-PRODUCT-ID', req=True)
@not_empty('comment', 'LABEL-BAD-COMMENT', req=False)
@not_empty('country_code', 'LABEL-NULL-COUNTRY-CODE', req=True)
@validate_country_code('country_code', 'LABEL-UNSUPPORTED-COUNTRY-CODE')
@not_empty('label', 'LABEL-NULL-LABEL', req=True)
@not_empty('is_active', 'LABEL-NULL-IS-ACTIVE', req=True, var_type=bool)
# @validate_product_for_labeling('LABEL-INVALID-PRODUCT-ID')
def label_mapping_upsert(label_id=None, customer_id=None, product_id=None,
                         comment=None, country_code=None, label=None,
                         is_active=None):
    logger.info(
        "label_mapping_upsert :: label_id = {}, customer_id = {}, "
        "product_id = {}, comment = {}, country_code = {}, label = {}, "
        "is_active = {}".format(
            label_id, customer_id, product_id, comment, country_code, label,
            is_active)
    )
    account_id = get_account_id_by_customer_id(customer_id=customer_id)

    label_obj = m_session.query(Label)\
        .filter(Label.account_id == account_id)\
        .filter(Label.label == label)\
        .filter(Label.product_id == product_id).first()

    if not label_obj:
        label_obj = Label(
            account_id=account_id,
            label=label,
            comment=comment,
            is_active=is_active,
            product_id=product_id,
            country_code=country_code
        )
    else:
        label_obj.label = label
        label_obj.is_active = is_active
        label_obj.comment = comment
        label_obj.product_id = product_id
        label_obj.country_code = country_code
        label_obj.deleted_on = None

    m_session.add(label_obj)
    m_session.flush()
    return label_obj


@not_empty('customer_id', 'LABEL-NULL-CUSTOMER-ID', req=True)
@not_empty('label_id', 'LABEL-NULL-LABEL-ID', req=True)
def delete_label(customer_id=None, label_id=None):
    logger.info("delete_label :: customer_id = {} and label_id = {}".format(
        customer_id, label_id))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id,
        Label.id == label_id).first()
    if not label_obj:
        raise NotFoundError('LABEL-NO-LABEL-FOUND')
    label_obj.deleted_on = datetime.now()
    label_obj.is_active = False
    m_session.add(label_obj)
    m_session.flush()
    return label_obj


@not_empty('customer_id', 'LABEL-NULL-CUSTOMER-ID', req=True)
@not_empty('product_id', 'LABEL-NULL-PRODUCT-ID', req=True)
@not_empty('comment', 'LABEL-BAD-COMMENT', req=False)
@not_empty('country_code', 'LABEL-NULL-COUNTRY-CODE', req=True)
@validate_country_code('country_code', 'LABEL-UNSUPPORTED-COUNTRY-CODE')
@not_empty('label', 'LABEL-NULL-LABEL', req=True)
@not_empty('is_active', 'LABEL-NULL-IS-ACTIVE', req=True, var_type=bool)
def add_label(customer_id=None, product_id=None, label=None, comment=None,
              country_code=None, is_active=None):
    logger.info("add_label :: customer_id = {}, product_id = {}, comment = {}"
                ", country_code = {}, label = {}, is_active = {}".format(
        customer_id, product_id, comment, country_code, label, is_active))
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id,
        Label.label == label,
        Label.deleted_on.is_(None)
    ).first()
    if label_obj:
        raise Exception("LABEL-EXISTS")

    # In Add label, default value of is_active is True
    # In Update label, label can be set inactive
    is_active = True
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id,
        Label.label == label,
        Label.deleted_on.isnot(None)
    ).first()
    if label_obj:
        label_obj.deleted_on = None
        label_obj.comment = comment
        label_obj.is_active = is_active
        label_obj.product_id = product_id
        label_obj.country_code = country_code
    else:
        label_obj = Label(
            account_id=account_id,
            label=label,
            comment=comment,
            is_active=is_active,
            product_id=product_id,
            country_code=country_code
        )

    m_session.add(label_obj)
    m_session.flush()
    return label_obj


@not_empty('label_id', 'LABEL-BAD-LABEL-ID', req=False)
@not_empty('customer_id', 'LABEL-NULL-CUSTOMER-ID', req=True)
@not_empty('product_id', 'LABEL-NULL-PRODUCT-ID', req=True)
@not_empty('comment', 'LABEL-BAD-COMMENT', req=False)
@not_empty('country_code', 'LABEL-NULL-COUNTRY-CODE', req=True)
@validate_country_code('country_code', 'LABEL-UNSUPPORTED-COUNTRY-CODE')
@not_empty('label', 'LABEL-NULL-LABEL', req=True)
@not_empty('is_active', 'LABEL-NULL-IS-ACTIVE', req=True, var_type=bool)
def update_label(label_id=None, customer_id=None, product_id=None,
                 comment=None, country_code=None, label=None, is_active=None):
    logger.info(
        "update_label :: label_id = {}, customer_id = {}, "
        "product_id = {}, comment = {}, country_code = {}, label = {}, "
        "is_active = {}".format(
            label_id, customer_id, product_id, comment, country_code, label,
            is_active)
    )
    account_id = get_account_id_by_customer_id(customer_id=customer_id)
    label_obj = m_session.query(Label).filter(
        Label.account_id == account_id,
        Label.id == label_id,
    ).first()

    if not label_obj:
        raise Exception("LABEL-NOT-EXISTS")

    label_obj.label = label
    label_obj.deleted_on = None
    label_obj.comment = comment
    label_obj.is_active = is_active
    label_obj.product_id = product_id
    label_obj.country_code = country_code

    m_session.add(label_obj)
    m_session.flush()
    return label_obj

if __name__ == '__main__':
    print list_labels(account_id=10000000L)
