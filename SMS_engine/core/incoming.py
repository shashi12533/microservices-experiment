import json
from datetime import datetime, timedelta
import requests

from sqlalchemy import func

from media_engine.config import get_config
from media_engine.lib.common import normalize_number
from media_engine.models import (
    m_session, IncomingProvider, InboundNumbers, IncomingConfig, IncomingSms,
    IncomingSmsParts
)
from media_engine.helper import get_logger
from onehop_workers import celery_app

__author__ = 'SHASHI'

logger = get_logger()
crash_logger = get_logger('crash')
CONFIG = get_config()
push_incoming_logger = get_logger('push_incoming')


def store_incoming(provider_name, request_params):
    provider, params = get_incoming_provider_and_params(
        provider_name, request_params
    )
    keyword = params.get('keyword', '')
    sub_keyword = params.get('sub_keyword', '')
    message_id = params.get('message_id', 1)
    is_cron_request = request_params.get('is_cron_request')
    message = params['message']
    mobilenumber = params['mobile_number']
    short_code = params['short_code']
    response = {'status': 'unknown'}

    incoming_config = get_incoming_config(
        keyword=keyword,
        short_code=short_code,
        sub_keyword=sub_keyword
    )
    if not incoming_config:
        raise ValueError("INCOMING-NOTFOUND-CONFIGURATION")

    is_multi_part = _is_multi_part(provider_name, params)
    if is_multi_part:
        multi_part_response = process_multipart_message(
            account_id=incoming_config.account_id,
            incoming_provider_id=provider.id,
            short_code=short_code,
            message=message,
            mobile_number=mobilenumber,
            message_id=message_id,
            total_parts=params['total_parts'],
            part_number=params['part_order_number'],
            reference_id=params['reference_id']
        )
        if multi_part_response['all_parts_received']:
            params['message'] = message = multi_part_response['message']
        else:
            response.update(
                {
                    'status': 'success',
                    'response': 'Success',
                    'id': None
                }
            )
            return response

    incoming_message = save_message(
        account_id=incoming_config.account_id,
        short_code=short_code,
        mobile_number=mobilenumber,
        incoming_provider_id=provider.id,
        message=message,
        keyword=keyword,
        sub_keyword=sub_keyword,
        response=message_id,
        product_id=incoming_config.incoming_product_id
    )
    response['id'] = incoming_message.id
    response['status'] = 'success'

    if is_multi_part or is_cron_request:
        update_status_of_multi_parts(
            mobile_number=mobilenumber,
            short_code=short_code,
            account_id=incoming_config.account_id,
            reference_id=params['reference_id'],
            incoming_message_id=incoming_message.id
        )

    # Push to url
    push_incoming_message_to_url(
        id=incoming_message.id,
        sent_from=mobilenumber,
        sent_to=short_code,
        msg=message,
        timestamp=incoming_message.created_on.strftime("%Y-%m-%d %H:%M:%S"),
        url=incoming_config.push_to_url,
        http_method=incoming_config.http_method,
        timeout=CONFIG.REQUEST_TIMEOUT
    )

    # format response before sending back to provider
    return formatted_response(provider_name, response)


def get_incoming_provider_and_params(provider_name, request_params):
    logger.info("get_incoming_provider_and_params. provider_name={}".format(provider_name))

    if not request_params or not isinstance(request_params, dict):
        raise ValueError('INCOMING-INVALID-PARAMS')

    provider = get_incoming_provider(provider_name=provider_name)

    params = {row.sm_param_name: request_params.get(row.param_name) for row in provider.params}

    try:
        mobile_number, short_code, message = \
            params['mobile_number'], params['short_code'], params['message']
    except KeyError as req:
        raise ValueError("INCOMING-REQUIRED-{}".format(req.upper()))

    if not mobile_number:
        raise ValueError("INCOMING-REQUIRED-MOBILENUMBER")
    if not short_code:
        raise ValueError("INCOMING-REQUIRED-SHORTCODE")
    if not message:
        raise ValueError("INCOMING-REQUIRED-MESSAGE")

    params['mobile_number'] = get_numeric_number(mobile_number)
    params['short_code'] = get_numeric_number(short_code)
    inbound_number = get_inbound_number(params['short_code'])
    if not inbound_number:
        raise ValueError('INCOMING-INVALID-INBOUNDNUMBER')

    country_code = inbound_number.country.code
    if len(params['short_code']) > 6:
        # In case of long code, normalize
        logger.info("inbound number is a long code, normalizing it...")
        params['short_code'] = normalize_number(params['short_code'], country_code)
        inbound_number = get_inbound_number(params['short_code'])

    if not inbound_number:
        raise ValueError('INCOMING-INVALID-INBOUNDNUMBER')

    if inbound_number.is_shared:
        # Inbound number shared
        split_message = params['message'].split(" ")
        params['keyword'] = split_message[0]
        if len(split_message) > 1:
            params['sub_keyword'] = split_message[1]

    return provider, params


def get_incoming_provider(**kwargs):
    logger.info("get_incoming_provider :: kwargs={}".format(kwargs))

    provider_name, provider_id = kwargs.get('provider_name'), kwargs.get('id')

    q_provider = m_session.query(IncomingProvider)
    if provider_name:
        q_provider = q_provider.filter(
            func.lower(IncomingProvider.api_name) == func.lower(provider_name)
        )
    elif provider_id:
        q_provider = q_provider.filter(IncomingProvider.id == provider_id)
    else:
        raise ValueError('INCOMING-INVALID-PROVIDER')

    provider = q_provider.first()
    logger.info("Provider = {}".format(provider))

    if not provider:
        raise ValueError('INCOMING-INVALID-PROVIDER')

    return provider


def get_inbound_number(short_code):
    logger.info("get_inbound_number. short_code={}".format(short_code))

    if not short_code:
        raise ValueError('INCOMING-INVALID-SHORTCODE')

    inbound = m_session.query(InboundNumbers)\
        .filter(InboundNumbers.short_code == short_code, InboundNumbers.deleted_on.is_(None))\
        .first()

    return inbound


def get_incoming_config(**kwargs):
    logger.info("incoming.get_incoming_config kwargs={}".format(kwargs))

    q = m_session.query(IncomingConfig)\
        .filter(
            func.lower(IncomingConfig.short_code) == func.lower(kwargs['short_code']),
            IncomingConfig.deleted_on.is_(None)
        )
    if kwargs.get('keyword'):
        q = q.filter(func.lower(IncomingConfig.keyword) == func.lower(kwargs['keyword']))

    if kwargs.get('sub_keyword'):
        q = q.filter(func.lower(IncomingConfig.sub_keyword) == func.lower(kwargs['sub_keyword']))

    incoming_config = q.first()
    logger.info("incoming_config = {}".format(incoming_config))

    if not incoming_config:
        raise ValueError('INCOMING-CONFIGURATION-ERROR')

    return incoming_config


def _is_multi_part(provider_name, params):
    logger.debug("_is_multi_part. provider={} and params={}".format(provider_name, params))
    multi_part = False
    if params.get('is_multi_part') and params['is_multi_part'] != 'false' and \
        params.get('total_parts') > 1:
        multi_part = True
    elif provider_name == 'openmarket' and params['UDH']:
        multi_part = True
    logger.info("multi_part = {}".format(multi_part))
    return multi_part


def save_message(**kwargs):
    logger.info("Saving incoming message. kwargs = {}".format(kwargs))
    message = IncomingSms(**kwargs)
    m_session.add(message)
    m_session.flush()
    logger.info("incoming message = {}".format(message))
    return message


def save_message_part(**kwargs):
    logger.info("Saving incoming message part. kwargs = {}".format(kwargs))
    message = IncomingSmsParts(**kwargs)
    m_session.add(message)
    m_session.flush()
    logger.info("incoming message part = {}".format(message))
    return message


def are_all_parts_received(**kwargs):
    logger.info("are_all_part_received. kwargs = {}".format(kwargs))
    parts = m_session.query(func.count().label("count"))\
        .filter(
            IncomingSmsParts.reference_id == kwargs['reference_id'],
            IncomingSmsParts.short_code == kwargs['short_code'],
            IncomingSmsParts.mobile_number == kwargs['mobile_number'],
            IncomingSmsParts.account_id == kwargs['account_id']
        )\
        .first()
    logger.info("parts = {}".format(parts))
    if parts[0] == kwargs['total_parts']:
        return True
    return False


def get_single_message_by_clubbing_all_parts(**kwargs):
    logger.info("get_single_message_by_clubbing_all_parts :: kwargs={}".format(kwargs))
    parts = m_session.query(IncomingSmsParts.message)\
        .filter(
            IncomingSmsParts.reference_id == kwargs['reference_id'],
            IncomingSmsParts.short_code == kwargs['short_code'],
            IncomingSmsParts.mobile_number == kwargs['mobile_number'],
            IncomingSmsParts.account_id == kwargs['account_id'],
            IncomingSmsParts.incoming_message_id.is_(None)
        ).order_by(IncomingSmsParts.part_number)
    message = ''
    for part in parts:
        message = "{message}{part}".format(message=message, part=part.message)
    logger.info("Final message = {}".format(message))

    return message


def process_multipart_message(**kwargs):
    logger.info("process_multipart_message :: kwargs={}".format(kwargs))
    save_message_part(**kwargs)
    all_parts_received = are_all_parts_received(**kwargs)
    response = dict(all_parts_received=all_parts_received)
    if all_parts_received:
        response['message'] = get_single_message_by_clubbing_all_parts(**kwargs)
    logger.info("process_multipart_message response = {}".format(response))

    return response


def update_status_of_multi_parts(**kwargs):
    logger.info("update_status_of_multi_parts :: kwargs={}".format(kwargs))
    response = m_session.query(IncomingSmsParts)\
        .filter(
            IncomingSmsParts.mobile_number == kwargs['mobile_number'],
            IncomingSmsParts.short_code == kwargs['short_code'],
            IncomingSmsParts.account_id == kwargs['account_id'],
            IncomingSmsParts.reference_id == kwargs['reference_id'],
            IncomingSmsParts.incoming_message_id.is_(None),
            IncomingSmsParts.status == 0
        ).update(
            dict(
                status='success', incoming_message_id=kwargs['incoming_message_id'],
                reference_id=kwargs['reference_id']
            )
        )
    logger.info("update_status_of_multi_parts response = {}".format(response))

    return response


def get_numeric_number(number):
    """
    >>> get_numeric_number('00019393')
    '19393'
    >>> get_numeric_number('akd kskdfk 020 k299')
    '20299'
    >>> get_numeric_number('101010101..2')
    '1010101012'
    >>> get_numeric_number('10.2')
    '102'
    >>> get_numeric_number('000000000000')
    '0'
    """
    logger.debug("get_numeric_number :: number={}".format(number))
    import re
    matches = re.findall('\d+', number)
    number = str(int(''.join(m for m in matches)))
    logger.debug("numeric number = {}".format(number))

    return number


def push_incoming_message_to_url(**data):
    logger.info("Sending payload to Celery = {}".format(data))
    if not data['url']:
        logger.error("push incoming url is empty. Ignoring push to url")
        return

    response = celery_app.send_task(
        'onehop_workers.celery_worker_sms_engine.push_incoming_to_url',
        (json.dumps(data), ),
        queue=CONFIG.CELERY_QUEUE_PUSH_INCOMING_TO_URL
    )
    logger.info("Celery task response = {}".format(response))
    return response


def update_push_to_url_status(sms_id, push_url_status, push_url_response):
    push_incoming_logger.info("update_push_to_url_status. sms_id={}, push_url_status={}, push_url_response={}".format(
        sms_id, push_url_status, push_url_response
    ))
    m_session.query(IncomingSms).filter(IncomingSms.id == sms_id)\
        .update(dict(push_url_status=push_url_status, push_url_response=push_url_response))


def get_all_message_parts_that_need_to_be_processed():
    push_incoming_logger.info("get_all_message_parts_that_need_to_be_processed")
    now = datetime.now()
    start_time = now - timedelta(hours=5)
    end_time = now - timedelta(hours=1)
    messages = m_session.query(IncomingSmsParts)\
        .filter(
            IncomingSmsParts.created_on >= start_time,
            IncomingSmsParts.created_on < end_time,
            IncomingSmsParts.status == 0,
            IncomingSmsParts.incoming_message_id.is_(None)
        ).group_by(IncomingSmsParts.account_id, IncomingSmsParts.reference_id)\
        .all()
    return messages


def call_incoming_sms_api(provider_name, payload):
    push_incoming_logger.info("call_incoming_sms_api. provider_name={} and payload={}".format(provider_name, payload))
    response = requests.post(
        CONFIG.INCOMING_API_URL.format(provider_name=provider_name), data=payload,
        timeout=CONFIG.REQUEST_TIMEOUT
    )
    push_incoming_logger.info("Response = {}".format(response))
    return response.status_code, response.text


def send_once_all_message_parts_are_received():
    push_incoming_logger.info("send_once_all_message_parts_are_received")
    messages = get_all_message_parts_that_need_to_be_processed()
    if not messages:
        push_incoming_logger.info("No messages to be processed")
        return

    data, payload = {}, {}
    for row in messages:
        provider_id = row.incoming_provider_id
        data = dict(
            reference_id=row.reference_id,
            short_code=row.short_code,
            mobile_number=row.mobile_number,
            account_id=row.account_id
        )
        data['message'] = get_single_message_by_clubbing_all_parts(**data)

        provider = get_incoming_provider(id=provider_id)
        params = provider.params
        for param in params:
            if data.get(param.sm_param_name):
                payload[param.param_name] = data.get(param.sm_param_name)

        payload['is_cron_request'] = 1
        # call incoming api
        try:
            response = call_incoming_sms_api(provider_name=provider.api_name, payload=payload)
            push_incoming_logger.info("Incoming API response = {}".format(response))
        except Exception as err:
            push_incoming_logger.error(err)
            crash_logger.exception(err)

    return "done"


def formatted_response(provider_name, response):
    response_dict = {
        'twilio': '''<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>''',
        'smsglobal': 'OK',
        'silverstreet': 'OK',
        'gupshup': '',
        'telerivet': '200',
        'nexmo': '200',
        'openmarket': '200',
        'aerial': '200',
        'smsportal': 'True',
        'smscentral': '0',
    }
    return response_dict.get(provider_name, json.dumps(response))
