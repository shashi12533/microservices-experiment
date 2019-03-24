#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
from urllib import urlencode
from media_engine.provider import Provider


class Mobily(Provider):

    def __init__(self):
        self.messageTag = str(int(time.time()))
        super(Mobily, self).__init__()

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Mobily, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'
        if response == '1':
            self.response = "success", self.mobilenumber, self.message_tag
        else:
            self.response = "error", self.mobilenumber, self.message_tag

        self.log.info('Final response : {}'.format(self.response))
        return self.response
        

    def send_sms(self, **kwargs):
        super(Mobily, self).send_sms(**kwargs)
        self.message_tag = str(int(time.time()))
        self.sms_text = ''.join(['{:04x}'.format(ord(byte)).upper() for byte in (self.sms_text)])
        request = urlencode(self.query_string)
        request = '{0}&msgId={1}'.format(request, self.message_tag)
        self.log.info('urlencoded request = %s' % request)
        self.final_url = '{0}{1}'.format(self.api_url, request)
        self.log.info('Final url: %s' % self.final_url)
        self.response = self.send_sms_using_provider_api(self.final_url)
        return self.response
