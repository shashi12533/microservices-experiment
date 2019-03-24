#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider
import xml.etree.ElementTree as ET


class Infobip(Provider):
    errorDict = {
        '-1': 'Error in processing the request',
        '-2': 'Not enough credits on a specific account',
        '-3': 'Targeted network is not covered on specific account',
        '-5': 'Username or password is invalid',
        '-6': 'Destination address is missing in the request',
        '-10': 'Username is missing in the request',
        '-11': 'Password is missing in the request',
        '-13': 'Number is not recognized by Infobip platform',
        '-22': 'Incorrect XML format, caused by syntax error',
        '-23': 'General error, reasons may vary',
        '-26': 'General API error, reasons may vary',
        '-27': 'Invalid scheduling parametar',
        '-28': 'Invalid PushURL in the request',
        '-30': 'Invalid APPID in the request',
        '-33': 'Duplicated MessageID in the request',
        '-34': 'Sender name is not allowed',
        '-99': 'Error in processing request, reasons may vary',
    }

    def handle_response(self, response):
        response = super(Infobip, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'
        root = ET.fromstring(response)
        status = root.findtext('.//status')
        if status == '0':
            message_id = root.findtext('.//messageid')
            response = "success", self.mobilenumber, message_id
        else:
            response = "error", self.mobilenumber, Infobip.errorDict[status]

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Infobip, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            if len(self.smsText) > 70:
                request = '%s&type=longSMS' % request
            request = '%s&datacoding=8' % request
        else :
            if len(self.smsText) > 160:
                request = '%s&type=longSMS' % request
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)
