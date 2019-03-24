#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider

class bandwidth(Provider):

    def handle_response(self, response):
        response = super(bandwidth, self).handle_response(response)
        if not response:
             return 'error', self.mobilenumber, 'invalid response'

        if response[0]['result'] != "accepted":
            response = 'error', self.mobilenumber, 'invalid response'
        else:
            location=response[0]['location']
            response='success', self.mobilenumber, location[location.rindex('/')+1:]

        self.log.info('Final response : %s' % response)
        return response


    def send_sms(self, **kwargs):
        super(bandwidth, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            request = '%s&msg_type=Unicode_Text' % request
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)




