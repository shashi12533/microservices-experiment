import json

from media_engine.config import get_config, statsd, request
from media_engine.lib.validators import not_empty
from onehop_workers import celery_app
from media_engine.lib.errors import SmsWorkerError, StatdException
from media_engine.helper import get_logger, generate_unique_business_id
from media_engine.models import m_session, SmsQueue

CONFIG = get_config()
logger = get_logger()
crash_log = get_logger('crash')


#@not_empty('label', 'SEND-SMS-BAD-LABEL', req=False)
@not_empty('account_id', 'SEND-SMS-BAD-ACCOUNT-ID', req=True, var_type=(int, long))
@not_empty('sms_text', 'SEND-SMS-BAD-SMS-TEXT', req=True)
@not_empty('sender_id', 'SEND-SMS-BAD-SENDER-ID', req=True)
@not_empty('mobile_number', 'SEND-SMS-BAD-MOBILE-NUMBER', req=True)
@not_empty('source', 'SEND-SMS-BAD-SOURCE', req=False, var_type=(int, long))
@not_empty('encoding', 'SEND-SMS-BAD-ENCODING', req=False)
def send_sms(**sms_params):
    sms_params['sms_id'] = sms_id = generate_unique_business_id()
    # This logging into db is only for backup purpose,
    # when rabbitmq fails abruptly
    # This can be removed once we have rabbitmq cluster
    # This 'sms_queue' table should be purged quarterly
    try:
        log_sms_queue(**sms_params)
    except Exception as exception:
        crash_log.error('Exception  : %s' % exception)
        crash_log.exception('Exception  : %s' % exception)
        raise SmsWorkerError('SMS-QUEUE-DB-ERROR')

    try:
        statsd.incr(request)
    except StatdException as exc:
        logger.error('sms_id: {} :: error: {}'.format(sms_id, exc.message))
    else:
        logger.info('sms_id: {} :: stats: {}'.format(sms_id, request))

    try:
        result = celery_app.send_task(
            CONFIG.OUTGOING_SMS_WORKER,
            args=[json.dumps(sms_params)],
            exchange=CONFIG.EXCHANGE,
            routing_key=CONFIG.ROUTE
        )
    except Exception as exception:
        crash_log.error('Exception  : %s' % exception)
        crash_log.exception('Exception  : %s' % exception)
        return {
            'status': 'failed',
            'message': 'failed',
        }
    else:
        logger.info('sent sms with sms_id : {}'.format(sms_id))
        logger.info('task_id : %s' % result.task_id)
        return {
            'status': 'submitted',
            'message': 'queued',
            'id': sms_id
        }


def log_sms_queue(**sms_params):
    logger.info("log_sms_queue :: sms_params = {}".format(sms_params))
    sms_queue_obj = SmsQueue(**sms_params)
    m_session.add(sms_queue_obj)
    m_session.commit()


def push_delivery_reports_to_url(data):
    logger.info("Sending payload to Celery = {}".format(data))
    response = celery_app.send_task(
        'deliveryreports.async_handler.workers.push_to_delivery_url',
        (json.dumps(data), ),
        queue=CONFIG.CELERY_QUEUE_DELIVERY_REPORTS
    )
    logger.info("Celery task response = {}".format(response))
    return response


def send_sms_bulk(**sms_params):
    logger.info("send_sms_bulk :: sms_params: {}".format(sms_params))
    return [
        send_sms(account_id=sms_params['account_id'], **sms)
        for sms in sms_params['sms_list']
    ]
