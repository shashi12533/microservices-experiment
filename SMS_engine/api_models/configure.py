from sqlalchemy import create_engine, orm, Column, String, DateTime,\
    TIMESTAMP, text, ForeignKey, Integer
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from media_engine.config import get_config
from media_engine.helper import generate_unique_business_id, get_date_time

CONFIG = get_config()

OneHopApiModel = declarative_base()
onehop_api_engine = create_engine(CONFIG.ONEHOP_DATABASE_URI,
                                  convert_unicode=CONFIG.SQLALCHEMY_CONVERT_UNICODE,
                                  pool_recycle=CONFIG.SQLALCHEMY_POOL_CYCLE,
                                  echo=CONFIG.SQLALCHEMY_ECHO)
# Why pool_recycle :
# http://docs.sqlalchemy.org/en/rel_0_9/dialects/mysql.html#connection-timeouts
_OnehopApiSession = orm.sessionmaker(
    autocommit=False, autoflush=True, bind=onehop_api_engine)
onehop_api_session = orm.scoped_session(_OnehopApiSession)
OneHopApiModel.metadata.bind = onehop_api_engine
OneHopApiModel.query = onehop_api_session.query_property()
server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")

UNIQUE_ID = Column(String(36), primary_key=True, default=generate_unique_business_id)
EXTERNAL_ID_PRIMARY_KEY = Column(String(30), primary_key=True)
NAME = Column(String(255), unique=True)
NAME_NULLABLE_FALSE = Column(String(255), unique=True, nullable=False)
AUTO_INCREMENTAL_ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

PRODUCT_ID_FOREIGN_KEY = Column(String(36), ForeignKey('product.id'))
USER_ID_FOREIGN_KEY = Column(String(36), ForeignKey('user.id'))
CART_ID_FOREIGN_KEY = Column(String(36), ForeignKey('cart.id'))
CURRENCY_CODE_FOREIGN_KEY = Column(String(3), ForeignKey('currency.code'), nullable=False)
COUNTRY_CODE_FOREIGN_KEY = Column(String(3), ForeignKey('country.code'))
MERCHANT_ID_FOREIGN_KEY = Column(String(36), ForeignKey('merchant.id'))
CART_ITEM_ID_FOREIGN_KEY = Column(String(36), ForeignKey('cart_items.id'))
EXTERNAL_ID = Column(String(30), nullable=True)

PRODUCT_ID_FOREIGN_KEY_NULLABLE_FALSE = Column(String(36), ForeignKey('product.id'), nullable=False)
USER_ID_FOREIGN_KEY_NULLABLE_FALSE = Column(String(36), ForeignKey('user.id'), nullable=False)
CART_ID_FOREIGN_KEY_NULLABLE_FALSE = Column(String(36), ForeignKey('cart.id'), nullable=False)
CURRENCY_CODE_FOREIGN_KEY_NULLABLE_FALSE = Column(String(3), ForeignKey('currency.code'), nullable=False)
COUNTRY_CODE_FOREIGN_KEY_NULLABLE_FALSE = Column(String(3), ForeignKey('country.code'), nullable=False)
MERCHANT_ID_FOREIGN_KEY_NULLABLE_FALSE = Column(String(36), ForeignKey('merchant.id'), nullable=False)
CART_ITEM_ID_FOREIGN_KEY_NULLABLE_FALSE = Column(String(36), ForeignKey('cart_items.id'), nullable=False)
EXTERNAL_ID_NULLABLE_FALSE = Column(String(30), nullable=False)

CREATED_ON = Column(DateTime, default=get_date_time)
CREATED_ON_WITH_SERVER_DEFAULT = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
MODIFIED_ON = Column(TIMESTAMP, nullable=False, default=get_date_time,
                     server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
DELETED_ON = Column(DateTime)

BOOLEAN_TRUE = Column(TINYINT(1), default=1, nullable=False)
BOOLEAN_FALSE = Column(TINYINT(1), default=0, nullable=False)

GLOBAL_AVAILABILITY_VALUE=Column(String(255), ForeignKey('global_availability_product.available'), nullable=False)
GLOBAL_ALPHA_NUMERIC_VALUE=Column(String(255), ForeignKey('global_availability_product.alpha'), nullable=False)

