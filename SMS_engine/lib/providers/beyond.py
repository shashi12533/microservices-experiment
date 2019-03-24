#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider
from media_engine.helper import generate_unique_api_key_hex


class Beyond(Provider):

    def handle_response(self, response):
        response = super(Beyond, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        if response == "OK":
            return 'success', self.mobilenumber, self.message_tag
        else:
            return 'error', self.mobilenumber, self.message_tag

    def send_sms(self, **kwargs):
        super(Beyond, self).send_sms(**kwargs)
        self.message_tag = generate_unique_api_key_hex()
        request = urlencode(self.query_string)
        request = '{}&msgId={}'.format(request, self.message_tag)
        self.log.info('urlencoded request = %s' % request)
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
