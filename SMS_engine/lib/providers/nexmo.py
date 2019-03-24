#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urllib import urlencode
import xml.etree.ElementTree as ET
from media_engine.provider import Provider


class Nexmo(Provider):

    def handle_response(self, response):
        response = super(Nexmo, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        try:
            root = ET.fromstring(response)
        except ET.ParseError as e:
            self.log.error(e.message)
            return 'error', self.mobilenumber, 'invalid response'

        for child in root:
            for counter, item in enumerate(child.findall('message')):
                status = item.find('status').text
                message_id = item.find('messageId')
                self.log.info('Nexmo message part={0}: status={1} and message_id={2}'.format(
                    counter, status, message_id))
                if message_id is not None and status == '0':
                    response = ('success', self.mobilenumber, message_id.text)
                else:
                    response = ('error', self.mobilenumber, item.find('errorText').text)
        self.log.info('Final response: {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Nexmo, self).send_sms(**kwargs)
        self.log.info('api_url : %s' % self.api_url)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            request = '%s&type=unicode' % request
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        response = self.send_sms_using_provider_api(final_url)
        return response
