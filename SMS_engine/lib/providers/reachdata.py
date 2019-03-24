#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Class for Reachdata SMS Provider"""

from urllib import urlencode
import xml.etree.ElementTree as ET
from media_engine.provider import Provider
from media_engine.lib import common


class Reachdata(Provider):

    """Class for Routesms SMS Provider"""

    def handle_response(self, response):
        response = super(Reachdata, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        try:
            root = ET.fromstring(response)
            message_id = root.findtext('.//BulkMessID')
            if message_id != '0':
                response = 'success', self.mobilenumber, message_id
            else:
                status_message = root.findtext('.//ReturnMessage')
                response = 'error', self.mobilenumber, status_message
        except Exception as e:
            self.log.error("Reachdata :: error = {}".format(e.message))
            response = 'error', self.mobilenumber, 'invalid response'
        self.log.info('Final response: {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Reachdata, self).send_sms(**kwargs)
        self.query_string['type'] = 2 if self.encoding == 2 else 0
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = {}'.format(request))
        final_url = '{}{}'.format(self.api_url, request)
        self.log.info('Final url: {}'.format(final_url))
        response = self.send_sms_using_provider_api(final_url)
        return response
