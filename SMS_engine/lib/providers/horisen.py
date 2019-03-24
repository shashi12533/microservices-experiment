#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
from media_engine.provider import Provider
import logging


class horisen(Provider):
    def create_error_response_dict(self):
            error_response = {'101': 'Internal application error',
                              '102': 'Encoding not supported or message not encoded with given encoding',
                              '103': 'No account with given username/password',
                              '104': 'Sending from clients IP address not allowed',
                              '105': 'Too many messages submitted withing short period of time. Resend later.',
                              '106': 'Sender contains words blacklisted on destination',
                              '107': 'Sender contains illegal characters',
                              '108': 'Message (not split automatically by Horisen BULK Service, but by customer) is too long.',
                              '109': 'Format of text/content parameter is wrong.',
                              '110': 'Mandatory parameter is missing',
                              '111': 'Unknown message type',
                              '112': 'Format of some parameter is wrong.',
                              '113': 'No credit on account balance',
                              '114': 'No route for given destination',
                              '115': 'Message cannot be split into concatenated messages (e.g. too many parts will be needed)'
                              }

            return error_response

    def handle_response(self,response):
        logging.warning("Response %s", response)
        error_dict=self.create_error_response_dict()
        response = super(horisen, self).handle_response(response)
        response_list=response.strip().split()
        if response_list[0] == 'OK': #sms sent successfully
            self.response = "success" , self.mobilenumber , response_list[1]
        else:#sms sent failed
            self.response = "error" , self.mobilenumber ,error_dict[response_list[1]]
        self.log.info('Final response : {}'.format(self.response))
        return self.response

    def send_sms(self, **kwargs):
        super(horisen, self).send_sms(**kwargs)
        request = urlencode(self.query_string)
        self.log.info('urlencoded request = %s' % request)
        if self.encoding == 2:
            request = '%s&MessageType=Unicode_Text' % request
        final_url = '%s%s' % (self.api_url, request)
        self.log.info('Final url: %s' % final_url)
        return self.send_sms_using_provider_api(final_url)











