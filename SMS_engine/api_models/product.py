# pylint: disable=invalid-name
from media_engine.api_models import Address
from sqlalchemy import Column, String, ForeignKey, Integer, Float, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import Text

from media_engine.api_models.configure import OneHopApiModel
from media_engine.api_models.configure import (
    UNIQUE_ID, PRODUCT_ID_FOREIGN_KEY, BOOLEAN_TRUE,
    CREATED_ON, MODIFIED_ON, DELETED_ON, USER_ID_FOREIGN_KEY,
    BOOLEAN_FALSE, CURRENCY_CODE_FOREIGN_KEY_NULLABLE_FALSE,
    COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE, EXTERNAL_ID, GLOBAL_AVAILABILITY_VALUE, COUNTRY_CODE_FOREIGN_KEY, GLOBAL_ALPHA_NUMERIC_VALUE)


class PartnerLinks(OneHopApiModel):
    __tablename__ = 'partner_links'

    id = UNIQUE_ID.copy()

    parent_partner_id = Column(String(36), ForeignKey('partner.id'))
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class PartnerContacts(OneHopApiModel):
    __tablename__ = 'partner_contacts'

    id = UNIQUE_ID.copy()

    parent_partner_id = Column(String(36), ForeignKey('partner.id'))
    label = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class Partner(OneHopApiModel):
    __tablename__ = 'partner'

    id = UNIQUE_ID.copy()

    name = Column(String(255), unique=True, nullable=False)
    logo = Column(String(255), unique=True, nullable=False)
    description = Column(String(255))
    source = Column(String(255), unique=True, nullable=False)
    banner_image =Column(String(255),nullable=False)
    explanation=Column(String(255),nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    addresses = relationship(Address, uselist=True)
    partner_links = relationship(PartnerLinks, uselist=True)
    partner_contacts = relationship(PartnerContacts, uselist=True)

    def __unicode__(self):
        return self.source


class ProductUsecaseMapping(OneHopApiModel):
    __tablename__ = 'product_usecase_mapping'

    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()
    usecase_id = Column(Integer, ForeignKey('usecase.id'))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    usecase = relationship("Usecase", uselist=False)


class ProductGrouping(OneHopApiModel):
    __tablename__ = 'product_grouping'

    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()

    group_id = Column(Integer)
    searchable = Column(TINYINT(1))

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    product = relationship("Product", uselist=False)


class MediaProduct(OneHopApiModel):
    __tablename__ = 'media_product'

    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()
    # type = Column(String(20), ForeignKey('media_type.type'))

    traffic_code = BOOLEAN_TRUE.copy()  # True for 2-way, False for 1-way
    routing = Column(Integer)  # 0 for direct, 1 for 1-hop, 2 for multi-hop
    pack_type = Column(String(20))
    char_limit = Column(Integer)
    inbound_price = Column(Float)
    outbound_price = Column(Float)
    inbound_cost = Column(Float)
    outbound_cost = Column(Float)
    claimed_delivery_ratio = Column(Float)  # in percentage
    claimed_latency = Column(Integer)

    external_id = Column(String(64), nullable=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    modified_by = USER_ID_FOREIGN_KEY.copy()

    __table_args__ = (UniqueConstraint('product_id', name='_media_product_id_uc'),)


class Product(OneHopApiModel):
    __tablename__ = 'product'

    id = UNIQUE_ID.copy()

    name = Column(String(255), nullable=False)
    code = Column(String(31), unique=True, nullable=False)
    category = Column(String(20), ForeignKey('product_category.category'), nullable=False)
    type = Column(String(20), ForeignKey('product_type.type'), nullable=True)
    subtype = Column(String(20), ForeignKey('product_subtype.subtype'), nullable=True)
    merchant_id = Column(String(36), ForeignKey('merchant.id'), nullable=False)
    description = Column(Text, nullable=True)
    status = BOOLEAN_TRUE.copy()
    view_type = BOOLEAN_TRUE.copy()
    average_rating = Column(Float)
    review_count = Column(Integer)
    restriction = Column(Text, nullable=True)
    base_currency = CURRENCY_CODE_FOREIGN_KEY_NULLABLE_FALSE.copy()
    country_code = COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE.copy()
    usp = Column(String(255))
    sender_id = Column(String(255))
    parent_product_id = Column(String(36), ForeignKey('product.id'), nullable=True)
    partner_id = Column(String(36), ForeignKey('partner.id'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    modified_by = USER_ID_FOREIGN_KEY.copy()

    merchant = relationship("Merchant", uselist=False)
    incoming_product = relationship("IncomingProduct", cascade="save-update", uselist=False, backref="product")
    media_product = relationship("MediaProduct", cascade="save-update", uselist=False, backref="product")
    surcharge = relationship("Surcharge", cascade="save-update", backref="products")
    usecase = relationship("ProductUsecaseMapping", cascade="save-update", backref="products")
    partner = relationship("Partner", uselist=False, backref="products")
    product_category = relationship("ProductCategory", uselist=False)
    product_type = relationship("ProductType", uselist=False)
    product_subtype = relationship("ProductSubtype", uselist=False)


class IncomingProduct(OneHopApiModel):
    __tablename__ = 'incoming_product'

    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()
    # type = Column(String(20), ForeignKey('incoming_product_type.type'), nullable=False)
    incoming_product_subtype = Column(String(32), ForeignKey('incoming_product_subtype.subtype'), nullable=True)
    limit_per_day = Column(Integer)
    limit_per_second = Column(Integer)
    lock_in = Column(Integer)
    default_frequency = Column(Integer)  # integer in months
    initial_cost = Column(Float)
    initial_purchase = Column(Float)
    provisioning_time = Column(Text, nullable=True)
    number_cost_per_month = Column(Float)

    lock_in_external_id = Column(String(64), nullable=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    __table_args__ = (UniqueConstraint('product_id', name='_incoming_product_id_uc'),)

    incoming_product_pricing = relationship("IncomingProductPricing", cascade="save-update", backref="incoming_product")


class IncomingProductPricing(OneHopApiModel):
    __tablename__ = 'incoming_product_pricing'

    id = UNIQUE_ID.copy()

    incoming_product_id = Column(String(36), ForeignKey('incoming_product.id'), nullable=False)
    frequency = Column(Integer)  # integer in months
    is_default_frequency = BOOLEAN_FALSE.copy()
    recurring_price = Column(Float)

    external_id = Column(String(64), nullable=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def to_dict(self):
        return dict(
            cost=self.recurring_price,
            frequency=self.frequency,
            is_default_frequency=self.is_default_frequency
        )


class ProductReview(OneHopApiModel):
    __tablename__ = 'product_review'

    id = UNIQUE_ID.copy()
    product_id = PRODUCT_ID_FOREIGN_KEY.copy()
    rating = Column(Float)
    comment = Column(String(255))
    user_id = USER_ID_FOREIGN_KEY.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    user = relationship('User', uselist=False)


class Surcharge(OneHopApiModel):
    __tablename__ = 'surcharge'

    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()

    operator = Column(String(255))
    price_per_incoming = Column(Float, default=0)
    price_per_outgoing = Column(Float, default=0)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def to_dict(self):
        return dict(
            operator=self.operator,
            price_per_incoming=self.price_per_incoming,
            price_per_outgoing=self.price_per_outgoing,
        )


class GlobalProductPrice(OneHopApiModel):
    __tablename__='global_product_pricing'
    id = UNIQUE_ID.copy()

    product_id = PRODUCT_ID_FOREIGN_KEY.copy()
    custom_product_id=PRODUCT_ID_FOREIGN_KEY.copy()
    country_code = COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE.copy()
    price = Column(Float)
    available = GLOBAL_AVAILABILITY_VALUE.copy()
    alpha = BOOLEAN_FALSE.copy()
    numeric = BOOLEAN_FALSE.copy()
    sender_reg_info = Column(String(255), nullable=False)
    text_restriction = Column(String(255), nullable=False)
    comment = Column(String(255), nullable=True)

class ProductSubtype(OneHopApiModel):

    __tablename__ = 'product_subtype'

    subtype = Column(String(20), primary_key=True)

    def __unicode__(self):
        return self.subtype

    def to_dict(self):
        return dict(
            name=' '.join(map(lambda x: x.capitalize(), self.category.split('_'))),
            value=self.subtype
        )

class ProductType(OneHopApiModel):
    __tablename__ = 'product_type'

    type = Column(String(20), primary_key=True)

    def __unicode__(self):
        return self.type

    def to_dict(self):
        return dict(
            name=' '.join(map(lambda x: x.capitalize(), self.category.split('_'))),
            value=self.type
        )

class ProductCategory(OneHopApiModel):
    __tablename__ = 'product_category'

    category = Column(String(20), primary_key=True)

    def __unicode__(self):
        return self.category

    def to_dict(self):
        return dict(
            name=' '.join(map(lambda x: x.capitalize(), self.category.split('_'))),
            value=self.category
        )

# class GlobalProductPrice(OneHopApiModel):
#     __tablename__='global_product_pricing'
#     id = UNIQUE_ID.copy()
#
#     product_id = PRODUCT_ID_FOREIGN_KEY.copy()
#     custom_product_id=PRODUCT_ID_FOREIGN_KEY.copy()
#     country_code = COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE.copy()
#     price = Column(Float)
#     available = GLOBAL_AVAILABILITY_VALUE.copy()
#     alpha = GLOBAL_ALPHA_NUMERIC_VALUE.copy()
#     numeric = GLOBAL_ALPHA_NUMERIC_VALUE.copy()
#     sender_reg_info = Column(String(255), nullable=True)
#     text_restriction = Column(String(255), nullable=True)
#     comment = Column(String(255), nullable=True)



