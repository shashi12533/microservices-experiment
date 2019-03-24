#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider


class Mrmessaging(Provider):

    def handle_response(self, response):
        response = super(Mrmessaging, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        response = [i.strip() for i in response.split('|')]
        self.log.info('Final response : %s' % response)
        return response

    def send_sms(self, **kwargs):
        super(Mrmessaging, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            request = '%s&coding=1' % request
            if len(self.message) > 70:
                request = '{}&type=longsms'.format(request)
        else :
            if len(self.message) > 160:
                request = '{}&type=longsms'.format(request)

        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
