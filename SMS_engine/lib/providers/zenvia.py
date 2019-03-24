#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from urllib import urlencode
from media_engine.provider import Provider
from media_engine.helper import generate_unique_business_id


class Zenvia(Provider):

    def handle_response(self, response):
        logging.info("Response : {}".format(response))
        if not super(Zenvia, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'

        response = json.loads(response)
        if response.get('status', None) == 1:
            response = 'success', self.mobilenumber, self.message_tag
        else:
            response = 'error', self.mobilenumber, response['message']

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Zenvia, self).send_sms(**kwargs)
        self.message_tag = generate_unique_business_id()
        payload = self.get_query_string()
        payload['id'] = self.message_tag
        self.log.info('Payload : {}'.format(payload))
        response = self.send_sms_using_provider_api(
            self.api_url,
            post_data=payload,
        )
        return response
