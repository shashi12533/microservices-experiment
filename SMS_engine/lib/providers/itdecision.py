#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
from urllib import urlencode
import xml.etree.ElementTree as ET
from media_engine.provider import Provider


class Itdecision(Provider):

    def handle_response(self, response):
        response = super(Itdecision, self).handle_response(response)
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
        super(Itdecision, self).send_sms(**kwargs)
        self.message_tag = str(int(time.time()))

        post_data = """<?xml version="1.0" encoding="utf-8" ?>
<request>
<message type = 'sms'>
<sender> {0} </sender>
<text> sms text </text>
<abonent phone = {1} client_id_sms = {2} />
</message>
<security>
<login value = {3}/>
<password value = {4}/>
</security>
</request>""".format(self.senderId, self.mobilenumber, self.message_tag, self.login, self.password)

        response = self.send_sms_using_provider_api(
            self.api_url,
            post_data=post_data,
            headers={'Content-Type': 'text/xml; charset = utf-8'}
        )
        return self.response
