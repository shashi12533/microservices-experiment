#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from urllib import urlencode
from media_engine.provider import Provider
from media_engine.helper import generate_unique_api_key_hex


class Voicecom(Provider):

    def __init__(self):
        super(Voicecom, self).__init__()

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Voicecom, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'

        response_dict = response.split(":")

        if response_dict[0] == 'SEND_OK':
            response = "success", self.mobilenumber, self.message_tag
        else:
            response = "error", self.mobilenumber, self.message_tag

        return response

    def send_sms(self, **kwargs):
        super(Voicecom, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.message_tag = generate_unique_api_key_hex()
        if self.encoding == 2:
            request = '{0}&encoding=utf-8&id={1}'.format(request, self.message_tag)
        else:
            request = '{0}&id={1}'.format(request, self.message_tag)
        self.log.info('urlencoded request = %s' % request)
        self.final_url = '{0}{1}'.format(self.api_url, request)
        self.log.info('Final url: %s' % self.final_url)
        self.response = self.send_sms_using_provider_api(self.final_url)
        return self.response
