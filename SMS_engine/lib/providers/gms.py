#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider


class Gms(Provider):

    def handle_response(self, response):
        response = super(Gms, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        #s = u'62000\r\nEnvio realizado correctamente - Ref Web: 170118S26f5ac27'
        if response:
            response = 'success', self.mobilenumber, response[-15: ]
        else:
            response = 'error', self.mobilenumber, "error"

        self.log.info('GMS : Final response : {}'.format(response))
        return response


    def send_sms(self, **kwargs):
        self.log.info('Inside GMS Send SMS')
        super(Gms, self).send_sms(**kwargs)

        request = urlencode(self.query_string)
        if self.encoding == 2:
            request = '%s&charset=AUTO+UTF-8' % request

        self.log.info('urlencoded request = %s' % request)
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
