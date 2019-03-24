# pylint: disable=invalid-name

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from media_engine.api_models.configure import (
    UNIQUE_ID, NAME, CREATED_ON, MODIFIED_ON, DELETED_ON,
    COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE)
from media_engine.api_models.configure import OneHopApiModel
from media_engine.api_models.models import Address


class Merchant(OneHopApiModel):
    __tablename__ = 'merchant'

    id = UNIQUE_ID.copy()

    name = NAME.copy()
    code = Column(String(32), unique=True, nullable=False)
    module = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    large_logo_url = Column(String(255), nullable=True)
    small_logo_url = Column(String(255), nullable=True)
    additional_information = Column(String(255), nullable=True)
    view_type = Column(TINYINT, default=1)
    website = Column(String(255), unique=False, nullable=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    addresses = relationship(Address, backref="merchants")
