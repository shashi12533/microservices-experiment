#!/usr/bin/env python
# -*- coding: utf-8 -*-

from media_engine.helper import get_worker_logger, required_param
from media_engine.lib import accounting, routing, common, sms_history
from media_engine.lib.errors import APIDisabled, StatdException, ProductNotFoundError
from media_engine.lib.inventory import get_delivery_url
from media_engine.lib.sms import push_delivery_reports_to_url
from media_engine.lib.validators import not_empty
from media_engine.config import config
from datetime import datetime
from media_engine.lib.routing import check_global_product
from media_engine.lib.common import get_numeric_number

logger = get_worker_logger('worker')


@not_empty('sms_id', required_param('sms_id'), req=True, var_type=unicode)
@not_empty('account_id', required_param('account_id'), req=True, var_type=(int, long))
@not_empty('label', required_param('label'), req=False)
@not_empty('sms_text', required_param('sms_text'), req=True)
@not_empty('sender_id', required_param('sender_id'), req=True)
@not_empty('mobile_number', required_param('mobile_number'), req=True)
@not_empty('source', required_param('source'), req=False, var_type=(int, long))
@not_empty('encoding', required_param('encoding'), req=False)
def onehop(sms_id, account_id, label, sms_text, sender_id, mobile_number,
           source=config.DEFAULT_SOURCE, encoding=None):
    logger.debug('onehop :: payload = {}'.format({
        'sms_id': sms_id,
        'account_id': account_id,
        'label': label,
        'sms_text': sms_text,
        'sender_id': sender_id,
        'mobile_number': mobile_number,
        'source': source,
        'encoding': encoding
    }))

    if not source:
        source = config.DEFAULT_SOURCE

    encoding_dict = {'plaintext': 1, 'unicode': 2}
    encoding = encoding_dict.get(encoding, None)
    number_of_sms = 1
    charge = False
    used_credits = 0
    # mobile_number = get_numeric_number(mobile_number)
    formatted_mobile_number = product_id = currency_code = service_provider_id = None
    dlr_payload = None
    try:
        # format sms text and get encoding and number of sms parts
        sms_text, encoding, number_of_sms = common.format_sms_text(sms_text, encoding)
        # Truncate sender_id to 11 characters if alphanumeric
        sender_id = common.truncate_sender_id(sender_id)

        # Get Country Code
        # if not mobile_number.startswith('+'):
        #     mobile_number = '+' + mobile_number
        mobile_number = filter(str.isdigit, mobile_number.encode('ascii', 'ignore'))

        if len(mobile_number) > 10 and not mobile_number.startswith('+'):
            mobile_number = '+' + mobile_number
            logger.debug("Mobile NUmber is update with + : {}".format(mobile_number))

        country_code = common.country_code_from_mobile_number(mobile_number)

        logger.debug("Country Code from Mobile Number : {}".format(country_code))

        # Get product from label and accountId
        product = routing.get_product(
            account_id,
            label,
            country_code,
            sender_id,
            mobile_number
        )

        if product is None:
            raise ProductNotFoundError()

        if (product.is_global):
            logger.debug("SMS is sending through Global Product")
            global_product_dict = check_global_product(product.id, product.customer_country_code)
            # global_product_dict = check_global_product(product.id, product.country_code)
            logger.debug("Found GLobal Product {}".format(global_product_dict))
            service_provider_id = global_product_dict[0].id
            product.provider = global_product_dict[0]
            product.outbound_price = global_product_dict[1]
            currency_code = global_product_dict[2]

        else:
            logger.debug("SMS is Sending through Non Global Product")
            service_provider_id = product.provider.id
            currency_code = product.base_currency

        formatted_mobile_number = product.formatted_mobile_number
        product_id = product.id

        # Set sms source for provider to select senderId
        product.provider.sms_source = source

        # Check for api access
        api_access = accounting.get_account_api_access(account_id)
        if not api_access:
            raise APIDisabled("NO-API-ACCESS")

        charge = True
        # Send sms api call
        response = product.send_sms(
            senderId=sender_id,
            mobilenumber=formatted_mobile_number,
            smsText=sms_text,
            encoding=encoding,
            messageTag=0
        )

    except Exception as exc:
        logger.error('Account {} : error {}'.format(account_id, exc.message))
        response = ('error', mobile_number, exc.message)
        if exc.message == 'LABEL-NOT-ACTIVE':
            product_id = exc.product_id
        if exc.message in config.CHARGABLE_ERROR_LIST:
            charge = True

        if exc.message in config.SEND_DLR_LIST:
            dlr_payload = dict(
                sms_id=sms_id,
                mobile_number=formatted_mobile_number or mobile_number,
                delivery_status='failed : {}'.format(exc.message),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                label=label,
                http_method='POST',
                delivery_url=get_delivery_url(account_id, product_id)
            )

    if charge:
        try:
            used_credits = product.update_balance(number_of_sms)
        except Exception as exc:
            logger.error('Account {} : error {}'.format(account_id, exc.message))
            used_credits = 0

    response = sms_history.parse_response(response)

    sms_history.log_sms(
        sms_id, account_id, product_id, label, response, sender_id,
        mobile_number, formatted_mobile_number, sms_text, number_of_sms,
        encoding, service_provider_id, used_credits, currency_code, source
    )

    statd_status = config.success if response['sent_status'] != 'error' else config.failed

    try:
        config.statsd.incr(statd_status)
    except StatdException as exc:
        logger.error('Account {} : error {}'.format(account_id, exc.message))
    else:
        logger.info('Account {} : stats : {}'.format(account_id, statd_status))

    if dlr_payload:
        logger.info("delivery payload : {}".format(dlr_payload))
        sms_history.update_delivery_status_in_sms_history(
            sms_id, dlr_payload['delivery_status'], dlr_payload['timestamp'])
        delivery_task_id = push_delivery_reports_to_url(dlr_payload)
        logger.info("delivery task id : {}".format(delivery_task_id))


if __name__ == '__main__':
    import uuid

    # # code with Label and Country Code
    # payload = {
    #     u'sms_id': unicode(uuid.uuid4()),
    #     u'account_id': 10000004,
    #     u'sms_text': u'test sms from screen magic, please ignore.',
    #     u'source': config.DEFAULT_SOURCE,
    #     u'sender_id': u'Test12',
    #     u'mobile_number': u'18486284673',
    #     u'label': u'us-100024-short-code',
    # }
    # onehop(**payload)

    # # code with No Label and  Country Code
    payload = {
        u'sms_id': unicode(uuid.uuid4()),
        u'account_id': 10000004,
        u'sms_text': u'test sms from screen magic, please ignore.',
        u'source': config.DEFAULT_SOURCE,
        u'sender_id': u'Test12',
        u'mobile_number': u'18486284673'
    }
    onehop(**payload)

    # code with Label and No Country Code.
    # payload = {
    #     u'sms_id': unicode(uuid.uuid4()),
    #     u'account_id': 10000004,
    #     u'label': u'us-100024-short-code',
    #     u'sms_text': u'test sms, please ignore.',
    #     u'source': config.DEFAULT_SOURCE,
    #     u'sender_id': u'Test12',
    #     u'mobile_number': u'8486284673'
    # }
    # onehop(**payload)

    # # code with No Label and No Country Code
    # payload = {
    #     u'sms_id': unicode(uuid.uuid4()),
    #     u'account_id': 10000004,
    #     u'sms_text': u'test sms from screen magic, please ignore.',
    #     u'source': config.DEFAULT_SOURCE,
    #     u'sender_id': u'Test12',
    #     u'mobile_number': u'8486284673'
    # }
    # onehop(**payload)
    # print "Hello"
