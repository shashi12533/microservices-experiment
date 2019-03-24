from functools import wraps

from flask_restful import abort
from media_engine.lib.errors import NotFoundError
from media_engine.helper import get_logger
from media_engine.models import m_session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

log = get_logger()
crash_log = get_logger('crash')


def handle_exceptions():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except ValueError as val_err:
                log.error(repr(val_err))
                m_session.rollback()
                abort(400, message=val_err.message)
            except KeyError as key_err:
                log.error(repr(key_err))
                m_session.rollback()
                abort(400, message=key_err.message)
            except IOError as io_err:
                crash_log.exception(io_err)
                m_session.rollback()
                abort(500, message="API-ERR-IO")
            except NotFoundError as nf_err:
                log.exception(repr(nf_err))
                m_session.rollback()
                abort(404, message=nf_err.message)
            except IntegrityError as err:
                crash_log.exception(err)
                m_session.rollback()
                # pattern = "\'[a-z]+(?:_[a-z]*)*\'"
                # matches = re.findall(pattern, err.orig[1])
                abort(400, message=err.message)
            except SQLAlchemyError as sa_err:
                crash_log.exception(sa_err)
                m_session.rollback()
                abort(500, message="API-ERR-DB")
            except Exception as exc:
                m_session.rollback()
                crash_log.exception(exc)
                raise

        return decorator

    return wrapper
