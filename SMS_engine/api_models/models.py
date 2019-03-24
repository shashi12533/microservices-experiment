from __future__ import absolute_import

from sqlalchemy import Column, String, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship, backref

from media_engine.api_models.configure import (
    OneHopApiModel, UNIQUE_ID, CREATED_ON, MODIFIED_ON, DELETED_ON,
    BOOLEAN_TRUE, BOOLEAN_FALSE, EXTERNAL_ID
)


class Country(OneHopApiModel):
    __tablename__ = 'country'

    code = Column(String(3), primary_key=True)
    name = Column(String(255), unique=True)
    dial_code = Column(String(8))


class Address(OneHopApiModel):
    __tablename__ = 'address'

    id = UNIQUE_ID.copy()

    merchant_id = Column(String(36), ForeignKey('merchant.id'))
    customer_id = Column(String(36), ForeignKey('customer.id'))
    partner_id = Column(String(36), ForeignKey('partner.id'))

    address_label = Column(String(30), ForeignKey('label_type.type'), default='company')
    address_line = Column(String(255))
    city = Column(String(64))
    zip = Column(String(32))
    country_code = Column(String(3), ForeignKey('country.code'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    country = relationship(Country, foreign_keys=[country_code])


class Customer(OneHopApiModel):
    __tablename__ = 'customer'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, unique=True)
    api_key = Column(String(36))

    company_name = Column(String(255))
    website = Column(String(255))
    phone = Column(String(15))
    country_code = Column(String(3), ForeignKey('country.code'))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    address = relationship(Address, uselist=False)

    def __unicode__(self):
        return "Customer {0}".format(self.id)


class Currency(OneHopApiModel):
    __tablename__ = 'currency'

    code = Column(String(3), primary_key=True)
    name = Column(String(255), unique=True)
    symbol = Column(String(15))

    def to_dict(self):
        return dict(
            code=self.code,
            name=self.name,
            symbol=self.symbol,
        )

    def __unicode__(self):
        return self.name


class ExchangeRate(OneHopApiModel):
    __tablename__ = 'exchange_rate'

    id = UNIQUE_ID.copy()
    exchange_rate = Column(Float, nullable=False)
    created_on = CREATED_ON.copy()
    currency_code = Column(String(3), ForeignKey('currency.code'), nullable=False)
    is_active = BOOLEAN_TRUE.copy()

    currency = relationship("Currency", uselist=False)

    def to_dict(self):
        return dict(
            name=self.currency.name,
            symbol=self.currency.symbol,
            exchange_rate=self.exchange_rate,
            currency_code=self.currency_code
        )

    def __unicode__(self):
        return "{0} [{1}]".format(self.currency.name, self.exchange_rate)


class Usecase(OneHopApiModel):
    __tablename__ = 'usecase'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), primary_key=True)
    is_active = Column(Integer, default=1)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
        )

    def __unicode__(self):
        return self.name


class User(OneHopApiModel):
    __tablename__ = 'user'

    id = UNIQUE_ID.copy()

    username = Column(String(255), unique=True)
    password = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    designation = Column(String(255))
    customer_id = Column(String(36), ForeignKey('customer.id'), nullable=False)
    phone = Column(String(15))

    verified = BOOLEAN_FALSE.copy()
    verified_on = CREATED_ON.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    external_id = EXTERNAL_ID.copy()

    customer = relationship('Customer', uselist=False, backref=backref('user', lazy='dynamic'))

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return self.username
