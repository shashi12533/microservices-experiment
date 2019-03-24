from sqlalchemy import Column, String, Integer, ForeignKey

from media_engine.models.configure import Model
from media_engine.models.configure import BOOLEAN_TRUE, BOOLEAN_FALSE, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID
from sqlalchemy.orm import relationship

class Account(Model):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)

    customer_id = Column(String(36), nullable=False, unique=True)
    is_api_access = BOOLEAN_TRUE.copy()
    is_office_hours_opt_out = BOOLEAN_FALSE.copy()
    is_email_enabled = BOOLEAN_TRUE.copy()
    is_test_account = BOOLEAN_FALSE.copy()
    is_verified = BOOLEAN_TRUE.copy()
    is_mms_enabled = BOOLEAN_FALSE.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
    incoming_configs = relationship("IncomingConfig")
    credits = relationship("Credit")

class AccountApiKey(Model):
    __tablename__ = 'account_api_key'

    id = UNIQUE_ID.copy()

    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account")
    api_key = Column(String(36), nullable=False, unique=True)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
