import json
from functools import wraps
from flask import request
from flask_restful import abort
from media_engine import config
from media_engine.config import config
from media_engine.helper import get_logger
from media_engine.lib import authenticate
from media_engine.lib.errors import InvalidParamsError

logger = get_logger()


def required_param(value):
    if value == '':
        abort(400)
    return value

def validate_label(value):
    if value is not None:
        value = value.strip()
        if value == '':
            return None
        value = value.strip()
        return value

    return None

def validate_encoding(encoding):
    if encoding == '':
        encoding = config.DEFAULT_ENCODING
    return encoding


def validate_source(source):
    if source == '':
        source = config.DEFAULT_SOURCE
    else:
        try:
            source = int(source)
        except ValueError:
            abort(400, message="REQ-SOURCE-NUMBER")
    if isinstance(source, int):
        return source
    abort(400, message="REQ-SOURCE-NUMBER")


def verify_account(account_id):
    if authenticate.verify_account_id(account_id):
        return account_id
    logger.warning("account_id : {} is not verified. Cannot create apiKey".format(account_id))
    abort(401)


def customer_authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # todo: Temporarly added for prestashop: should be removed once prestashop testing done
        # todo: prestashop people cannot add apiKey in headers in post call?
        method = request.args if request.method == 'GET' else request.form

        api_key = request.headers.get('apiKey') or method.get('apiKey')
        # api_key = request.headers.get('apiKey')
        if not api_key:
            try:
                method = json.loads(method.items()[0][0])
                api_key = method.get('apiKey')
                if not api_key:
                    raise Exception()
            except:
                logger.error('no api key')
                abort(401, message='REQ-API-KEY')

        account_id = authenticate.is_authenticated(api_key)
        if account_id:
            kwargs['account_id'] = account_id
            return func(*args, **kwargs)
        logger.warning("account_id : {} is not authenticated".format(account_id))
        abort(401, message='INVALID-API-KEY')
    return wrapper


def authenticate_account(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if config.ONEHOP_SECURE:
            encrypted_api_key = request.headers.get('apiKey')
            if not encrypted_api_key:
                logger.error('no api key')
                abort(401, message='REQ-API-KEY')
            onekey = config.ONEHOP_API_VERIFICATION_KEY
            if encrypted_api_key == onekey:
                return func(*args, **kwargs)
            logger.warning("Unauthorized Access :: apiKey : {}".format(encrypted_api_key))
            abort(401, message='FORBIDDEN')
        else:
            return func(*args, **kwargs)

    return wrapper


def validate_provider_params(method):
    def wrapper(self, *args, **kwargs):
        logger.info('validate_provider_params :: params = %s' % kwargs)
        required_args = {'sender_id', 'mobile_number', 'sms_text', 'encoding',
                         'service_provider_info', 'service_provider_params'}
        if 'mms_url' in kwargs and kwargs['mms_url'] is not None:
            required_args.add('mms_url')

        if not kwargs or not required_args.issubset(set(kwargs.keys())) or \
                any(not val for key, val in kwargs.items() if key != 'mms_url'):
            # check1 : params not empty
            # check2 : all required args present
            # check3 : all values are set / 'not empty'
            raise InvalidParamsError('Invalid params passed')
        return method(self, *args, **kwargs)
    return wrapper


def reject_non_text_args(method):
    """
    Use this decorator when a method is supposed to process only text
    :param method: decorated function
    :return: If text is passed, returns decorated function. otherwise None
    """

    def wrapper(self, *args, **kwargs):
        if args and any(not isinstance(arg, basestring) for arg in args):
            return None
        return method(self, *args, **kwargs)
    return wrapper


def not_empty(param, err_code, req=False, var_type=basestring, default_val=None):
    def wrapper(fn):
        # A side effect of using decorators is that the function that gets wrapped loses it's
        # natural __name__, __doc__, and __module__ attributes.
        # wraps decorator takes a function used in a decorator and adds the functionality of
        # copying over the function name, docstring, arguments list, etc.
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # val = kwargs[param] if req else kwargs.get(param)
                if req:
                    val = kwargs[param]
                else:
                    val = kwargs.get(param) if kwargs.get(param) is not None else default_val
                    kwargs.update({param: val})
            except KeyError:
                raise KeyError(err_code)
            if type(val) == bool and var_type == bool:
                return fn(*args, **kwargs)
            elif (var_type == int) and isinstance(val, var_type) and (val or val == 0):
                return fn(*args, **kwargs)
            elif (var_type == float) and isinstance(val, (int, float)) and (val or val == 0):
                return fn(*args, **kwargs)
            elif isinstance(val, var_type) and val:
                return fn(*args, **kwargs)
            elif (val in [None, []]) and (not req):
                return fn(*args, **kwargs)
            raise ValueError(err_code)
        return decorator

    return wrapper


def validate_country_code(param, err_code):
    def wrapper(fn):
        # A side effect of using decorators is that the function that gets wrapped loses it's
        # natural __name__, __doc__, and __module__ attributes.
        # wraps decorator takes a function used in a decorator and adds the functionality of
        # copying over the function name, docstring, arguments list, etc.
        @wraps(fn)
        def decorator(*args, **kwargs):
            if kwargs[param] in authenticate.get_all_country_char_codes():
                return fn(*args, **kwargs)
            raise ValueError(err_code)

        return decorator

    return wrapper
