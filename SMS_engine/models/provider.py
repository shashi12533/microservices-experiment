from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship,backref
from media_engine.models.configure import (
    Model, BOOLEAN_TRUE, BOOLEAN_FALSE, CREATED_ON, MODIFIED_ON, DELETED_ON
)

from media_engine.models.configure import UNIQUE_ID


class ServiceProvider(Model):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    sp_config_id=Column(Integer,ForeignKey('service_provider_config.id'),nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text(convert_unicode=True))
    contact = Column(String(20))
    api_url = Column(String(255))
    api_port = Column(String(10))
    country_code = Column(String(3), ForeignKey('country_info.char_code'),
                          nullable=False)
    send_sms_function = Column(String(255))
    is_default = BOOLEAN_FALSE.copy()
    dummy_status = BOOLEAN_FALSE.copy()
    module = Column(String(255), nullable=False)
    pack_type = Column(String(255), nullable=False)
    route_tag = Column(String(255))
    balance_check_url = Column(String(255))
    route_type = BOOLEAN_FALSE.copy()
    is_mms_enabled = BOOLEAN_FALSE.copy()
    mms_api_url = Column(String(255))
    sp_config = relationship('ServiceProviderConfig', uselist=False, backref=backref('service_provider', lazy='dynamic'))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class ServiceProviderConfig(Model):
    __tablename__ = 'service_provider_config'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text(convert_unicode=True))
    contact = Column(String(20))
    api_url = Column(String(255))
    api_port = Column(String(10))
    send_sms_function = Column(String(255))
    dummy_status = BOOLEAN_FALSE.copy()
    module = Column(String(255), nullable=False)
    route_tag = Column(String(255))
    balance_check_url = Column(String(255))
    route_type = BOOLEAN_FALSE.copy()
    mms_api_url = Column(String(255))
    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

class ServiceProviderParam(Model):
    __tablename__ = 'service_provider_params'

    id = Column(Integer, primary_key=True)

    service_provider_id = Column(Integer, ForeignKey('service_provider.id'),
                                 nullable=False)
    param_name = Column(String(255))
    param_value = Column(String(255))
    run_time_value = BOOLEAN_FALSE.copy()
    encoding = Column(Integer, nullable=False)
    in_query_string = BOOLEAN_TRUE.copy()
    is_mms_param = BOOLEAN_FALSE.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class DefaultProduct(Model):
    __tablename__ = 'default_product'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), index=True)
    product_id = Column(String(36), nullable=False)
    country_code = Column(String(36), ForeignKey('country_info.char_code'),
                          nullable=True)
    subtype = Column(String(20), nullable=False)
    is_active = BOOLEAN_TRUE.copy()
    country_info = relationship("CountryInfo")
