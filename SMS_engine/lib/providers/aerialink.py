#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class for Aerialink SMS Provider"""

import xml.etree.ElementTree as ET
from urllib import urlencode
from media_engine.provider import Provider
from media_engine.config import DEFAULT_SOURCE


class Aerialink(Provider):

    """Class for Aerialink SMS Provider"""

    def handle_response(self, response):
        response = super(Aerialink, self).handle_response(response)
        if response is None:
            return 'error', self.mobilenumber, 'invalid response'
        try:
            data = ET.fromstring(response)
        except ET.ParseError as e:
            self.log.error(e.message)
            return 'error', self.mobilenumber, response

        transaction_guid = data.findtext('.//transactionGUID')
        if transaction_guid:
            response = 'success', self.mobilenumber, transaction_guid
        else:
            error_code = data.findtext('.//errorCode')
            detail = data.findtext('.//detail')
            response = 'error', self.mobilenumber, '{}:{}'.format(error_code, detail)

        self.log.info('Final response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Aerialink, self).send_sms(**kwargs)
        sid, pwd = [None] * 2
        for param in self.params:
            if param[0] == 'sid':
                sid = param[1]
                self.log.info('sid = %s' % sid)
            if param[0] == 'pwd':
                pwd = param[1]
                self.log.info('pwd = %s' % pwd)
            if param[0] == 'source':
                # If sms source is not onehop api, set senderId = default incoming number
                # In onehop api, incoming number should be passed as senderId.
                # Aerialink providers product should be sold as package of incoming + outgoing product
                if self.sms_source == DEFAULT_SOURCE:
                    self.query_string['source'] = self.senderId
                else:
                    self.query_string['source'] = param[1]
                self.log.info('source = %s' % self.query_string['source'])

        if self.encoding == 2:
            headers = {
                'Accept': "application/json",
                'Content-type': "application/x-www-form-urlencoded;charset=utf-8",
            }
            self.query_string['dcs'] = 8
        else:
            headers = {
                'Accept': "application/json",
                'Content-type': "application/x-www-form-urlencoded"
            }

        auth = (sid, pwd) if sid and pwd else None

        response = self.send_sms_using_provider_api(
            self.api_url, urlencode(self.query_string), headers, auth=auth)

        return response
