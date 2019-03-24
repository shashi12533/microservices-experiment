from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Text

from media_engine.models.configure import (
    Model, BOOLEAN_TRUE, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID
)


class Label(Model):
    __tablename__ = 'label'

    __table_args__ = (
        UniqueConstraint('label', 'account_id', name='uc_label_account'),
    )

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), index=True)
    product_id = Column(String(36), nullable=False)
    label = Column(String(100), nullable=True, index=True)
    comment = Column(Text(convert_unicode=True))
    is_active = BOOLEAN_TRUE.copy()
    country_code = Column(String(3), ForeignKey('country_info.char_code'), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    country = relationship("CountryInfo")


# class LabelMapping(Model):
#     __tablename__ = 'label_mapping'
#
#     id = UNIQUE_ID.copy()
#
#     label_id = Column(String(36), ForeignKey('label.id'), unique=True)
#
#     created_on = CREATED_ON.copy()
#     modified_on = MODIFIED_ON.copy()
