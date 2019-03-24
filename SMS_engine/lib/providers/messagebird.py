#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from media_engine.provider import Provider


class Messagebird(Provider):

    def handle_response(self, response):

        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        if type(response) == 'unicode':
            response = response.decode('utf-8', 'ignore')

        try:
            response = json.loads(response)
        except ValueError as e:
            self.log.error('Messagebird :: {}'.format(e.message))
            return 'error', self.mobilenumber, 'invalid response'

        self.log.info('response : {}'.format(response))
        check_id = response.get('id', None)

        if check_id:
            response = ('success', self.mobilenumber, check_id)
        else:
            response = ('error', self.mobilenumber, response['errors'][0]['description'])

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Messagebird, self).send_sms(**kwargs)

        headers = {
            'Authorization': 'AccessKey ' + self.query_string['apikey'],
            'Content-type': "application/json",
        }

        payload = self.query_string
        payload['datacoding'] = 'plain' if self.encoding == 1 else 'unicode'
        payload['recipients'] = '+' + str(payload['recipients'])
        response = self.send_sms_using_provider_api(
            self.api_url,
            post_data=json.dumps(payload),
            headers=headers
        )
        return response
