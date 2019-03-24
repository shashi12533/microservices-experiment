#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from urllib import urlencode
from media_engine.provider import Provider
from media_engine.helper import generate_unique_api_key_hex


class Valuefirst(Provider):

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Valuefirst, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'

        if response == 'Sent.':
            response = "success", self.mobilenumber, self.message_tag
        else:
            response = "error", self.mobilenumber, response

        return response

    def send_sms(self, **kwargs):
        super(Valuefirst, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.message_tag = generate_unique_api_key_hex()
        dlr_request = "http://api.onehop.co/reports/valuefirst?myid=" + self.message_tag +"&status=%d&updated_on=%t&res=%2"
        if self.encoding == 2:
            request = '{}&coding=3&dlr-url={}'.format(request, dlr_request)
        else:
            request = '{}&dlr-url={}'.format(request, dlr_request)
        self.log.info('urlencoded request = %s' % request)
        self.final_url = '{0}{1}'.format(self.api_url, request)
        self.log.info('Final url: %s' % self.final_url)
        self.response = self.send_sms_using_provider_api(self.final_url)
        return self.response
