from sqlalchemy import Column, String, Integer, ForeignKey

from media_engine.models.configure import (
    Model, CREATED_ON, MODIFIED_ON, DELETED_ON,
    UNIQUE_ID)


class AccountInfo(Model):
    __tablename__ = 'account_info'
    id = UNIQUE_ID.copy()
    account_id = Column(Integer, ForeignKey('account.id'), index=True)
    product_id = Column(String(36), nullable=False, index=True)
    incoming_url = Column(String(255), nullable=True)
    delivery_report_url = Column(String(255), nullable=True)
    http_method_for_delivery_url = Column(String(5), default='get')
    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
