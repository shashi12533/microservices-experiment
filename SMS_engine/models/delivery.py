from sqlalchemy import Column, String, Integer, ForeignKey

from media_engine.models.configure import (
    Model, CREATED_ON, MODIFIED_ON, DELETED_ON, UNIQUE_ID
)


class DeliveryReport(Model):
    __tablename__ = 'delivery_reports'

    id = UNIQUE_ID.copy()

    mobile_number = Column(String(255))
    message_id = Column(String(255))
    status = Column(String(255))
    report = Column(String(255))
    module = Column(String(50), nullable=False)

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()
