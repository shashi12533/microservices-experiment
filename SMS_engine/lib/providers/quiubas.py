#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from urllib import urlencode
from media_engine.provider import Provider
from quiubas import Quiubas

class Quiubasprovider(Provider):

    def handle_response(self, response):
        logging.warning("Response %s", response)
        if not super(Quiubasprovider, self).handle_response(response):
            return 'error', self.mobilenumber, 'invalid response'
        try:
            a = int(response, 16)
            self.response = "success" , self.mobilenumber, response
        except ValueError:
            self.response = "error" , self.mobilenumber, response

        self.log.info('Final response : {}'.format(self.response))
        return self.response

    def send_sms(self, **kwargs):
        super(Quiubas, self).send_sms(**kwargs)
        quiubas = Quiubasprovider()
        quiubas.setAuth(self.username, self.password);

        self.response = quiubas.sms.send(
            {
                'to_number': self.mobilenumber,
                'message': self.text
            }
        )

        return self.response







