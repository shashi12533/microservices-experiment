#!/usr/bin/env python
# -*- coding: utf-8 -*-
from media_engine.helper import get_logger

logger = get_logger()


class NotInstalledError(Exception):

    def __init__(self, mobile_number, error='Module Not Installed'):
        super(NotInstalledError, self).__init__()
        logger.critical('{} : {}'.format(error, mobile_number))


class StatdException(Exception):
    pass


class APIDisabled(Exception):
    pass


class NotFoundError(Exception):
    pass

class LabelNotFound(Exception):
    def __init__(self):
        self.message = "LABEL-NOT-FOUND"

class InvalidCountryForProduct(Exception):
    def __init__(self):
        self.message = "INVALID-COUNTRY-FOR-PRODUCT"

class LabelNotActiveError(Exception):

    def __init__(self, product_id):
        super(LabelNotActiveError, self).__init__()
        self.message = "LABEL-NOT-ACTIVE"
        self.product_id = product_id

class ProductNotFoundError(Exception):

    def __init__(self):
        self.message = "PRODUCT-NOT-FOUND-ERROR"


class SmsWorkerError(Exception):
    pass


class InvalidLabelError(Exception):
    pass


class InsufficientBalanceError(Exception):
    def __init__(self):
        self.message = "INSUFFICIENT-BALANCE-ERROR"


class InvalidMobileNumberError(Exception):

    def __init__(self, mobile_number, error='INVALID-MOBILE-NUMBER'):
        super(InvalidMobileNumberError, self).__init__()
        self.message = error
        logger.warn('{}: {}'.format(error, mobile_number))


class InvalidSMSTextError(Exception):

    def __init__(self, sms_text, error='InvalidSMSTextError'):
        super(InvalidSMSTextError, self).__init__()
        self.message = error
        logger.error('{} : {}'.format(error, sms_text))


class ProviderLibNotLoadedError(Exception):

    def __init__(self, error='ProviderLibNotLoadedError'):
        super(ProviderLibNotLoadedError, self).__init__()
        self.message = error
        logger.error('{}'.format(error))


class InvalidParamsError(Exception):
    pass


class ProviderError(Exception):
    pass
