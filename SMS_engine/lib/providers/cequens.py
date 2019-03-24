#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider
import json
import logging


class cequens(Provider):

    def handle_response(self, response):
        response = super(cequens, self).handle_response(response)
        string_response=json.loads(response) #converts dict i.e response into string
        logging.warning("Response %s", response)
        if string_response['errors'] == []: #sms sent successfully
            self.response = "success", self.mobilenumber, string_response['requestStatus']['RequestID']
        else:   # sms not sent successfully
            self.response = "error", self.mobilenumber, string_response['errors'][0][1]

        self.log.info('Final response : {}'.format(self.response))
        return self.response



    def send_sms(self, **kwargs):
        super(cequens, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            request = '%s&MessageType=Unicode_Text' % request
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)







