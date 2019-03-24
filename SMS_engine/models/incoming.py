from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Text

from media_engine.models.configure import (
    Model, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID, BOOLEAN_FALSE,
    CREATED_ON_INDEXED
)


class InboundNumbers(Model):
    __tablename__ = 'inbound_numbers'

    __table_args__ = (
        UniqueConstraint('short_code', 'country_id', 'incoming_provider_id',
                         name='uc_short_code_country_incoming_provider'),
    )

    id = UNIQUE_ID.copy()

    short_code = Column(String(255), nullable=False)
    country_id = Column(String(3), ForeignKey('country_info.char_code'), nullable=False)
    incoming_provider_id = Column(String(36), ForeignKey('incoming_provider.id'), nullable=False)
    is_shared = BOOLEAN_FALSE.copy()
    for_keyword_sell = BOOLEAN_FALSE.copy()
    is_dummy = BOOLEAN_FALSE.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    country = relationship("CountryInfo")


class IncomingConfig(Model):
    __tablename__ = 'incoming_config'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    incoming_product_id = Column(String(36))  # reference to incoming product in onehop api
    keyword = Column(String(255), nullable=False)
    short_code = Column(String(255), ForeignKey('inbound_numbers.short_code'))
    inbound_number = relationship("InboundNumbers")
    sub_keyword = Column(String(255))
    login = Column(String(255))
    password = Column(String(255))
    push_to_url = Column(String(255))
    mobile_field_name = Column(String(255))
    message_field_name = Column(String(255))
    http_method = Column(String(255), default='get')  # enum is needed
    country_id = Column(String(3), ForeignKey('country_info.char_code'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def __repr__(self):
        return "{}(account_id={!r}, short_code={!r}, keyword={!r})".format(
            self.__class__.__name__, self.account_id, self.short_code, self.keyword
        )


class IncomingProvider(Model):
    __tablename__ = 'incoming_provider'

    id = UNIQUE_ID.copy()

    name = Column(String(255), nullable=False)
    api_name = Column(String(255))
    http_push_method = Column(String(100))
    country_id = Column(String(3), ForeignKey('country_info.char_code'), nullable=False)
    http_url = Column(String(255))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    params = relationship("IncomingProviderParams", cascade="save-update")

    def __repr__(self):
        return "{}(id={!r}, api_name={!r})".format(self.__class__.__name__, self.id, self.api_name)


class IncomingProviderParams(Model):
    __tablename__ = 'incoming_provider_params'

    id = UNIQUE_ID.copy()

    incoming_provider_id = Column(String(36), ForeignKey('incoming_provider.id'), nullable=False)
    param_name = Column(String(255), nullable=False)
    sm_param_name = Column(String(255), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def __repr__(self):
        return "{}(id={!r}, incoming_provider_id={!r}, param_name={!r}, sm_param_name={!r}".format(
            self.__class__.__name__, self.id, self.incoming_provider_id, self.param_name, self.sm_param_name
        )


class IncomingSms(Model):
    __tablename__ = 'incoming_sms'

    id = UNIQUE_ID.copy()
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False, index=True)
    account = relationship("Account")
    product_id = Column(String(36))
    short_code = Column(String(255))
    keyword = Column(String(255))
    sub_keyword = Column(String(255))
    message = Column(Text(convert_unicode=True))
    mobile_number = Column(String(255))
    response = Column(Text(convert_unicode=True))
    push_url_status = BOOLEAN_FALSE.copy()
    push_url_response = Column(Text(convert_unicode=True))
    incoming_provider_id = Column(String(36), ForeignKey('incoming_provider.id'), nullable=False)

    created_on = CREATED_ON_INDEXED.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def __repr__(self):
        return "{}(id={!r})".format(self.__class__.__name__, self.id)


class IncomingSmsParts(Model):
    __tablename__ = 'incoming_sms_parts'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), nullable=False, index=True)
    product_id = Column(String(36))
    incoming_provider_id = Column(String(36), ForeignKey('incoming_provider.id'), nullable=False)
    incoming_message_id = Column(String(36), nullable=True)  # Can't be FK as parts create incoming sms
    message_id = Column(String(100))
    short_code = Column(String(255))
    mobile_number = Column(String(255), nullable=False)
    message = Column(Text(convert_unicode=True))
    part_number = Column(Integer, nullable=False)
    total_parts = Column(Integer, nullable=False)
    reference_id = Column(Integer, index=True)
    status = BOOLEAN_FALSE.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class IncomingSmsTemp(Model):
    __tablename__ = 'incoming_sms_temp'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    product_id = Column(String(36))
    short_code = Column(String(255))
    keyword = Column(String(255))
    sub_keyword = Column(String(255))
    message = Column(Text(convert_unicode=True))
    mobile_number = Column(String(255), nullable=False)
    response = Column(Text(convert_unicode=True))
    push_url_status = BOOLEAN_FALSE.copy()
    push_url_response = Column(Text(convert_unicode=True))
    incoming_provider_id = Column(String(36), ForeignKey('incoming_provider.id'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
