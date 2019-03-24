#!/usr/bin/env python
# -*- coding: utf-8 -*-
from media_engine.config import get_config
from media_engine.lib import accounting, common, credits
from media_engine.lib.errors import InsufficientBalanceError
from media_engine.helper import get_worker_logger

config = get_config()
logger = get_worker_logger('worker')


class Product(object):

    def __init__(self, account_id, product_id):
        logger.debug('In constructor of {}'.format(self.__class__.__name__))
        self.id = product_id
        self.account_id = account_id
        self.provider, self.outbound_price, self.base_currency, self.country_code = \
            self.get_product_details()
        self._balance = None
        self._price = None
        self.balance()
        self.insufficient_balance()

    def get_product_details(self):
        return accounting.get_product_details(self.id)

    def balance(self):
        """Get available balance"""
        self._balance = credits.get_available_balance(
            account_id=int(self.account_id),
            product_id=self.id
        )

    def insufficient_balance(self):
        # Check for insuffient balance
        if self.outbound_price > self._balance:
            logger.error(
                'insufficient balance :: Account = {} : Product = {}'.format(
                    self.account_id, self.id))
            #raise InsufficientBalanceError("INSUFFICIENT-BALANCE")
            return None

    def check_balance(self):
        logger.debug("checking Balance, outbound price : {}, balance : {}".format(self.outbound_price, self._balance))
        if self.outbound_price > self._balance:
            return False
        else:
            return True

    def send_sms(self, **kwargs):
        return self.provider.send_sms(**kwargs)

    def update_balance(self, number_of_sms):
        if self.provider.sms_provider == 'Cmtelecom':
            if hasattr(self.provider, 'smsText'):
                number_of_sms = common.get_number_of_sms(2, self.provider.smsText)
        price = self.outbound_price * number_of_sms
        logger.info("update_balance :: number_of_sms = {} "
                    "and price = {}".format(number_of_sms, price))
        credits.update_credits_by_account_id(
            self.account_id,
            self.id,
            -price,
            self.base_currency)
        return price

