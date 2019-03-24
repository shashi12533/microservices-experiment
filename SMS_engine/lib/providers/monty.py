#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from urllib import urlencode
from media_engine.provider import Provider


class Monty(Provider):

    def handle_response(self, response):
        if response is None:
            return 'error', self.mobilenumber, 'invalid response'

        if type(response) == 'unicode':
            response = response.decode('utf-8', 'ignore')

        try:
            response = json.loads(response)
        except ValueError as e:
            self.log.error('Monty :: {}'.format(e.message))
            return 'error', self.mobilenumber, 'invalid response'

        if response['ErrorCode'] == 0:
            response_message_details = response['MsgDetails'][0]['Id']
            self.log.info("Monty :: success: response: {}".format(response_message_details))
            response = 'success', self.mobilenumber, response_message_details
        else:
            response_dict = {
                -1: 'No Text Message specified',
                -2: 'No Source',
                -3: 'No Destination',
                -4: 'Invalid Destination',
                -5: 'Invalid Credentials',
                -6: 'No Credit',
                -7: 'Invalid Data Coding'
            }
            response = 'error', self.mobilenumber,\
                response_dict.get(response['ErrorCode'], 'Unknown Error')

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        kwargs['mobilenumber'] = kwargs['mobilenumber'].replace('+', '')
        super(Monty, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = {}'.format(request))
        if self.encoding == 2:
            request += '&datacoding=2'

        final_url = '{}{}'.format(self.api_url, request)
        self.log.info('Final url: {}'.format(final_url))
        response = self.send_sms_using_provider_api(final_url)
        return response


if __name__ == '__main__':
    params = [(u'username', u'scrmagdr', 0, 1L, 1, 0), (u'password', u'5CRm@gDR', 0, 1L, 1, 0), (u'source', u'$senderId', 1, 1L, 1, 0), (u'destination', u'$mobilenumber', 1, 1L, 1, 0), (u'text', u'$smsText', 1, 1L, 1, 0)]
    m = Monty(1,'monty_url', params)
    response = json.dumps({u'ErrorCode': 0, u'MsgDetails': [{u'DestinationAddress': u'919552772600', u'MessageCount': -1, u'OriginatingAddress': u'ameya', u'CC': -1, u'MCC': -1, u'ErrorCode': 0, u'Rate': -1, u'MNC': -1, u'Id': u'8a89d68b-d24f-43ed-a7a1-54a07feb246b'}]})

    m.handle_response(response)
