#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from media_engine.provider import Provider


class Plivo(Provider):

    def handle_response(self, response):

        response = super(Plivo, self).handle_response(str(response))
        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        try:
            response_dict = json.loads(response)
        except ValueError as e:
            self.log.error('Plivo :: {}'.format(e.message))
            return 'error', self.mobilenumber, 'invalid response'

        if response_dict.has_key('message'):
            response = 'success', self.mobilenumber, response_dict['message_uuid'][0]
        else:
            response = 'error', self.mobilenumber, '{}:{}'.format(
                response_dict.get('error', 'Unknown error'), response_dict.get('api_id', '400'))

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Plivo, self).send_sms(**kwargs)
        self.log.info("In sendSMS function of Plivo")
        auth_id, auth_token = [None] * 2
        for param in self.params:
            if param[0] == 'authId':
                auth_id = param[1]
            if param[0] == 'authToken':
                auth_token = param[1]

        payload = self.get_query_string()

        auth = (auth_id, auth_token) if auth_id and auth_token else None
        response = self.send_sms_using_provider_api(
            self.api_url,
            post_data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            auth=auth
        )

        self.log.info("http plivo row response : {}".format(response))

        return response
