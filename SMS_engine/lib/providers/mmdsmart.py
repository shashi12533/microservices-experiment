#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider


class mmdsmart(Provider):

    def handle_response(self, response):
        response = super(mmdsmart, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        response = [i.strip() for i in response.split('|')]
        self.log.info('Final response : %s' % response)
        return response

    def send_sms(self, **kwargs):
        super(mmdsmart, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        if self.encoding == 2:
            if len(self.message) > 70:
                request = '{}&longMessageMode=split'.format(request)
        else:
            if len(self.message) > 160:
                request = '{}&longMessageMode=split'.format(request)

        self.log.info('urlencoded request = %s' % request)
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
