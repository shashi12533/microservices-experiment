# -*- coding: utf-8 -*-


MEDIA_PRODUCT_TYPE_LIST = [
    dict(type='sms'),
    dict(type='mms'),
    dict(type='voice'),
    dict(type='email'),
]


INCOMING_PRODUCT_TYPE_LIST = [
    dict(type='long_code'),
    dict(type='short_code'),
    dict(type='1800'),
]

PRODUCT_CATEGORY_LIST = [
    dict(category='incoming_product'),
    dict(category='media_product'),
]

LABEL_TYPE_LIST = [
    dict(type='office'),
    dict(type='company')
]

PLAN_TYPE_LIST = [
    dict(type='frequency'),
    dict(type='lock_in'),
    dict(type='media'),
]
