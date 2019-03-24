from media_engine.core.incoming import push_incoming_message_to_url
from media_engine.config import get_config
from media_engine.models import (
    m_session, IncomingSms
)
from datetime import datetime, timedelta
from media_engine.helper import get_logger


config=get_config()
logger = get_logger()

## repush the failed message again
def celery_repush():
    ##cron job invok this method to periodically repush incoming
    since = datetime.now() - timedelta(hours=24)
    failed_messages = m_session.query(IncomingSms).filter(
        IncomingSms.push_url_status == 0, IncomingSms.created_on > since).all()
    if failed_messages is not None and len(failed_messages) > 0:
       _call_push_incoming_message_to_url(failed_messages)

def repush_by_id(sms_list):
    # check if sms_ids is present or return with error code
    if sms_list is not None and type(sms_list) == list and len(sms_list) > 0:
        failed_messages = m_session.query(IncomingSms).filter(
            IncomingSms.id.in_(sms_list),
            IncomingSms.push_url_status == 0).all()
        logger.info(failed_messages)
        if failed_messages is not None and len(failed_messages) > 0:
            _call_push_incoming_message_to_url(failed_messages)
        else:
            logger.info('No sms ids details available in database.')
            return "No sms ids details available in database."
    else:
        logger.info('No sms list provided')
        return "No sms list provided"

def repush_by_account_id(account_list):
    # check if account_ids is present or return with error code
    if account_list is not None and type(account_list) == list and len(account_list) > 0:
        failed_messages = m_session.query(IncomingSms).filter(
            IncomingSms.account_id.in_(account_list),
            IncomingSms.push_url_status == 0).all()
        if failed_messages is not None and len(failed_messages) > 0:
            _call_push_incoming_message_to_url(failed_messages)
        else:
            logger.info('No Account id details available in database.')
            return "No account id details available in database."
    else:
        return "No account id list provided"

## this is internal logic to retry failed sms
def _call_push_incoming_message_to_url(failed_messages=None):
    # check if failed_messages is None or Not type of Incoming SMS and return error code.
    if failed_messages is not None:
        for failed_message in failed_messages:
            incoming_configs = failed_message.account.incoming_configs
            incoming_config = None
            for _config in incoming_configs:
                if _config.short_code == failed_message.short_code:
                    if not _config.inbound_number.is_shared:
                        incoming_config = _config
                        break
                    elif _config.keyword == failed_message.keyword:
                        incoming_config = _config
                        if _config.sub_keyword == failed_message.sub_keyword:
                            break

            if incoming_config is not None:
                payload = {
                    "id": failed_message.id,
                    "sent_from": failed_message.mobile_number,
                    "sent_to": incoming_config.short_code,
                    "msg": failed_message.message,
                    "url": incoming_config.push_to_url,
                    "http_method": incoming_config.http_method,
                    "timeout": config.REQUEST_TIMEOUT
                }
                logger.info('repushed payload:',payload)
                push_incoming_message_to_url(**payload)
