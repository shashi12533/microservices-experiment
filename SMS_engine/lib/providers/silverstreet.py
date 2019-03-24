#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class for Silver Street Provider"""

from urllib import urlencode
from media_engine.provider import Provider
from media_engine.lib import common
from media_engine.helper import generate_unique_api_key_hex


class Silverstreet(Provider):

    def handle_response(self, response):
        """Handle response from Silverstreet"""
        response = super(Silverstreet, self).handle_response(response)
        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        response = response.encode('ASCII', 'ignore')

        if response != '' and response == u'01':
            response = ('success', self.mobilenumber, self.messageTag)
        else:
            response = ('error', self.mobilenumber, response)
        return response

    def send_sms(self, **kwargs):
        """Prepare SMS for Silverstreet"""
        super(Silverstreet, self).send_sms(**kwargs)

        single_message_length = 160
        multipart_message_limit = 153

        self.messageTag = generate_unique_api_key_hex()
        body_type = 1

        self.log.info('Msg Length : %d' % len(self.smsText))
        self.log.info('Msg Text : %s' % self.smsText)

        if self.encoding == 2:
            body_type = 4
            self.log.info('BODYTYPE : %s' % body_type)
            self.smsText = self.smsText.encode('utf_16_be').encode('hex')
            self.log.info('Hex Text : %s' % self.smsText)
            single_message_length = 168
            multipart_message_limit = 168

        parts = self.get_number_of_parts(
            self.smsText,
            single_message_length,
            multipart_message_limit)

        number_of_parts = len(parts)
        self.log.info("numberOfParts : %s" % number_of_parts)

        if number_of_parts == 1:
            query_string = self.get_query_string()

            self.log.info(
                "sendViaSilverStreet querystring : %s"
                % query_string)
            request = urlencode(query_string)
            if self.encoding == 2:
                request = '%s&msg_type=Unicode_Text' % request

            extra_params = "&BODYTYPE=%s" % body_type
            self.final_url = '%s%s%s' % (self.api_url, request, extra_params)
            self.response = self.send_sms_using_provider_api(self.final_url)
        else:
            number_of_parts_in_hex = "".join(hex(number_of_parts).split('x'))
            start_limit = 0
            sms_text = self.smsText
            for i in range(number_of_parts):
                iHex = "".join(hex(i + 1).split('x'))
                number_of_characters = parts[i] - start_limit
                sms_text_part = sms_text[start_limit:][:number_of_characters]
                start_limit = parts[i] + 1
                sms_text_part = " ".join(sms_text_part.split('\n'))
                self.smsText = sms_text_part
                query_string = self.get_query_string()
                request = urlencode(query_string)
                if self.encoding == 2:
                    request = '%s&msg_type=Unicode_Text' % request

                self.log.info("sendViaSilverStreet querystring : %s"
                              % query_string)
                self.log.info("iHex: %s" % iHex)
                udh = '05000301' + number_of_parts_in_hex + iHex
                self.log.info("UDH %s" % udh)
                extra_params = "&BODYTYPE=%s&UDH=%s" % (body_type, udh)
                request += extra_params
                self.final_url = '%s%s' % (self.api_url, request)
                self.response = self.send_sms_using_provider_api(
                    self.final_url)
                self.log.info("sendViaSilverStreet response : {}".format(self.response))
        return self.response

    def get_number_of_parts(self, sms_text, single_message_length,
                            multipart_message_limit):
        parts = {}
        extended_characters = ('|', '{', '}', '[', ']', '^', '~', '\\')
        i, j, length = 0, 0, 0

        message_length = common.count_gsm0338_length(sms_text)

        self.log.info(
            "Msg Length after Special character : %s" %
            message_length)
        sms_word_list = list(sms_text)

        if message_length > single_message_length:
            for x in sms_word_list:
                length += 1
                if x in extended_characters:
                    length += 1
                    self.log.info("legth is increased by two as Character"
                                  "is special : %s" % x)
                if length >= (multipart_message_limit - 1):
                    nextchar = i + 1
                    if nextchar < message_length-1:

                        if not sms_word_list[nextchar] in extended_characters:
                            i += 1
                            length = 0
                        else:
                            length = 2
                        parts[j] = i
                        length = 0
                        j += 1
                i += 1

            parts[j] = i
        else:
            parts[j] = message_length

        return parts
