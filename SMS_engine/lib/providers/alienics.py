#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from urllib import urlencode
from media_engine.provider import Provider
import xml.etree.ElementTree as ET


class Alienics(Provider):

    def __init__(self):
        super(Alienics, self).__init__()

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Alienics, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'
        try:
            data = ET.fromstring(response)
        except ET.ParseError as e:
            self.log.error(e.message)
            return 'error', self.mobilenumber, response

        status = data[0][0][2].text
        messageId = data[0][0][0].text

        if status == 0:
            response = "success", self.mobilenumber, messageId
        elif status == 2:
            response = "error", self.mobilenumber, messageId + "-Missing params"
        elif status == 3:
            response = "error", self.mobilenumber, messageId + "-Invalid params"
        elif status == 4:
            response = "error", self.mobilenumber, messageId + "Invalid credentials"
        else:
            response = "error", self.mobilenumber, messageId + "error"

        return response

    def send_sms(self, **kwargs):
        super(Alienics, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        if self.encoding == 2:
            request = '{}&type=unicode'.format(request)
        self.log.info('urlencoded request = %s' % request)
        self.final_url = '{0}{1}'.format(self.api_url, request)
        self.log.info('Final url: %s' % self.final_url)
        self.response = self.send_sms_using_provider_api(self.final_url)
        return self.response
