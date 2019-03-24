from sqlalchemy import Column, String, Integer, text

from media_engine.models.configure import (
    Model, BOOLEAN_FALSE, CREATED_ON, MODIFIED_ON, DELETED_ON
)


class CountryInfo(Model):
    __tablename__ = 'country_info'

    char_code = Column(String(3), primary_key=True)

    name = Column(String(100))
    code = Column(Integer, nullable=False)
    mobile_number_length = Column(Integer, server_default=text("'10'"))
    country_code_length = Column(Integer, nullable=False)
    is_top_country = BOOLEAN_FALSE.copy()

    created_on = CREATED_ON.copy()
    modified_on = MODIFIED_ON.copy()
    deleted_on = DELETED_ON.copy()


class Currency(Model):
    __tablename__ = 'currency'

    code = Column(String(3), primary_key=True)
    name = Column(String(255), unique=True)
    symbol = Column(String(15))

    def __unicode__(self):
        return self.name
