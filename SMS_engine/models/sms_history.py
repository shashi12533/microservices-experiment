from media_engine.helper import get_date_time
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, TIMESTAMP
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Text

from media_engine.models.configure import (
    Model, UNIQUE_ID, MODIFIED_ON, CREATED_ON
)


class SmsHistory(Model):
    __tablename__ = 'sms_history'

    id = UNIQUE_ID.copy()
    mobile_number = Column(String(20), nullable=False)
    sender_id = Column(String(255), nullable=False)
    encoding = Column(Integer, nullable=True)
    source = Column(Integer, nullable=False)
    text = Column(Text(convert_unicode=True), nullable=False)
    number_of_sms = Column(Integer, nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=True)

    formatted_mobile_number = Column(String(20), nullable=True)
    provider_response_id = Column(String(255), nullable=True)
    product_id = Column(String(36), index=True, nullable=True)
    label = Column(String(100), nullable=True, index=True)
    delivery_status = Column(String(255), nullable=True)

    # comes from provider
    response_id = Column(String(255), nullable=True)
    sent_status = Column(String(255), nullable=False)
    status_message = Column(Text(convert_unicode=True), nullable=True)

    service_provider_id = Column(Integer, ForeignKey(
        'service_provider.id'), nullable=True)
    credits = Column(Float, nullable=True)
    currency_code = Column(String(3), ForeignKey('currency.code'),
                           nullable=True)
    resend_on = Column(DateTime, nullable=True)
    created_on = Column(DateTime, default=get_date_time, nullable=True)
    modified_on = MODIFIED_ON.copy()

    sms_history_snapshot = relationship("SmsHistorySnapshot",
                                        backref=backref('sms_history'), uselist=False)

    media_url = relationship("MediaUrl", uselist=True)
    is_international = Column(TINYINT(1), default=0, nullable=True)
    dr_received_on = Column(TIMESTAMP, nullable=True)


class SmsHistorySnapshot(Model):
    __tablename__ = 'sms_history_snapshot'

    id = UNIQUE_ID.copy()
    created_on = CREATED_ON.copy()
    sms_id = Column(ForeignKey('sms_history.id'), nullable=False, unique=True)
    message_id = Column(String(255), nullable=False)
    account_id = Column(ForeignKey('account.id'), nullable=False)


class MediaUrl(Model):
    __tablename__ = 'media_url'
    id = UNIQUE_ID.copy()
    url = Column(Text(convert_unicode=True), nullable=False)
    created_on = CREATED_ON.copy()
    sms_id = Column(ForeignKey('sms_history.id'), nullable=False, unique=False)


class SmsQueue(Model):
    __tablename__ = 'sms_queue'
    sms_id = Column(String(36), primary_key=True)
    label = Column(String(100), nullable=True, index=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=True)
    sms_text = Column(Text(convert_unicode=True), nullable=False)
    sender_id = Column(String(255), nullable=False)
    mobile_number = Column(String(20), nullable=False)
    source = Column(Integer, nullable=True)
    encoding = Column(String(255), nullable=True)

