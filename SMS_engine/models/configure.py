# pylint: disable=invalid-name

from __future__ import absolute_import

from sqlalchemy import (
    orm, create_engine, Column, String, DateTime, TIMESTAMP, text, event, select, exc
)

from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from media_engine.config import get_config
from media_engine.helper import generate_unique_business_id, get_date_time

CONFIG = get_config()

Model = declarative_base()
onehop_media_engine = create_engine(CONFIG.ONEHOP_BACKEND_DATABASE_URI,
                                    convert_unicode=CONFIG.SQLALCHEMY_CONVERT_UNICODE,
                                    pool_recycle=CONFIG.SQLALCHEMY_POOL_CYCLE,
                                    echo=CONFIG.SQLALCHEMY_ECHO)
# Why pool_recycle :
# http://docs.sqlalchemy.org/en/rel_0_9/dialects/mysql.html#connection-timeouts
_OnehopMediaSession = orm.sessionmaker(
    autocommit=False, autoflush=True, bind=onehop_media_engine)
onehop_media_session = orm.scoped_session(_OnehopMediaSession)
Model.metadata.bind = onehop_media_session
Model.query = onehop_media_session.query_property()


UNIQUE_ID = Column(String(36), primary_key=True,
                   default=generate_unique_business_id)

CREATED_ON = Column(DateTime, default=get_date_time)
CREATED_ON_INDEXED = Column(DateTime, default=get_date_time, index=True)
MODIFIED_ON = Column(TIMESTAMP, nullable=False, default=get_date_time,
                     server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
DELETED_ON = Column(DateTime)

BOOLEAN_TRUE = Column(TINYINT(1), default=1, nullable=False)
BOOLEAN_FALSE = Column(TINYINT(1), default=0, nullable=False)


@event.listens_for(onehop_media_engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        # "branch" refers to a sub-connection of a connection,
        # we don't want to bother pinging on these.
        return

    # turn off "close with result".  This flag is only used with
    # "connectionless" execution, otherwise will be False in any case
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        # run a SELECT 1.   use a core select() so that
        # the SELECT of a scalar value without a table is
        # appropriately formatted for the backend
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        # catch SQLAlchemy's DBAPIError, which is a wrapper
        # for the DBAPI's exception.  It includes a .connection_invalidated
        # attribute which specifies if this connection is a "disconnect"
        # condition, which is based on inspection of the original exception
        # by the dialect in use.
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.  The disconnect detection
            # here also causes the whole connection pool to be invalidated
            # so that all stale connections are discarded.
            connection.scalar(select([1]))
        else:
            raise
    finally:
        # restore "close with result"
        connection.should_close_with_result = save_should_close_with_result