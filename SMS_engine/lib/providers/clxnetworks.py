#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from urllib import urlencode
from media_engine.provider import Provider


class Clxnetworks(Provider):

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Clxnetworks, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'
        try:
            a = int(response, 16)
            self.response = "success" , self.mobilenumber, response
        except ValueError:
            self.response = "error" , self.mobilenumber, response

        self.log.info('Final response : {}'.format(self.response))
        return self.response

    def send_sms(self, **kwargs):
        super(Clxnetworks, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = {}'.format(request))
        if self.encoding == 2:
            request = '{}&coding=2'.format(request)
        self.final_url = '{}{}'.format(self.api_url, request)
        self.log.info('Final url: {}'.format(self.final_url))
        self.response = self.send_sms_using_provider_api(self.final_url)
        return self.response
