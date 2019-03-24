#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from urllib import urlencode
from media_engine.provider import Provider
from media_engine.helper import generate_unique_business_id


class Sendsmsprovider(Provider):

    def handle_response(self, response):
        logging.info("Response : {}".format(response))
        if not super(Sendsmsprovider, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'

        response = json.loads(response)
        if response.get('status', None) == 1:
            response = 'success', self.mobilenumber, self.message_tag
        else:
            response = 'error', self.mobilenumber, response['message']

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Sendsmsprovider, self).send_sms(**kwargs)
        self.message_tag = generate_unique_business_id()
        request = urlencode(self.query_string)
        final_url = '{0}{1}&smsid={2}'.format(self.api_url, request, self.message_tag)
        self.log.info('Final url: {}'.format(final_url))
        response = self.send_sms_using_provider_api(final_url)
        return response
