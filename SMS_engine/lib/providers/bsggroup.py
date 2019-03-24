#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider


class Bsggroup(Provider):

    def handle_response(self, response):
        response = super(Bsggroup, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        if response:
            response = 'success', self.mobilenumber, response
        else:
            response = 'error', self.mobilenumber, response

        self.log.info('Final response : {}'.format(response))
        return response


    def send_sms(self, **kwargs):
        super(Bsggroup, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
