from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.types import Text

from media_engine.models.configure import (
    Model, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID)


class NumberingPlan(Model):
    __tablename__ = 'numbering_plan'

    id = UNIQUE_ID.copy()

    mobile_number_length = Column(Integer)
    country_code_length = Column(Integer)
    country_id = Column(String(3), ForeignKey('country_info.char_code'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def __repr__(self):
        return "{}(country_id={}, mobile_number_length={}, country_code_length={}".format(
            self.__class__.__name__, self.country_id, self.mobile_number_length, self.country_code_length
        )


class OutboundSmsQueue(Model):
    __tablename__ = 'outbound_sms_queue'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'))
    sms_data = Column(Text(convert_unicode=True), nullable=False)
    sent_at = Column(DateTime)
    status = Column(String(20))
    response = Column(String(255))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
