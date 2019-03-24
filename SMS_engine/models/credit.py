from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from media_engine.models.configure import (
    Model, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID
)


class Credit(Model):
    __tablename__ = 'credits'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'), index=True)
    account = relationship("Account")
    product_id = Column(String(36), nullable=False, index=True)
    balance = Column(Float(precision='10,4'))
    used_balance = Column(Float(precision='10,4'), default=0.0)
    currency_code = Column(String(3), ForeignKey('currency.code'), nullable=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()

    def to_dict(self):
        return dict(
            account_id=self.account_id,
            product_id=self.product_id,
            balance=self.balance,
            currency_code=self.currency_code,
            used_balance=self.used_balance,
        )
