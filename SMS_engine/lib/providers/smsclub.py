#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from media_engine.provider import Provider
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

class Smsclub(Provider):

    def handle_response(self, response):

        if not response:
            return 'error', self.mobilenumber, 'invalid response'

        root = ET.fromstring(response)
        for child in root:
            attr_dict=child.attrib

        if (root[0].text).strip() == 'send':
            message_id=attr_dict['id_sms']
            response = "success", self.mobilenumber, message_id
        else:
            response = "error", self.mobilenumber, root[0].text

        return response


    def send_sms(self, **kwargs):
        super(Smsclub, self).send_sms(**kwargs)

        xml_data = self.create_xml2(
            self.params, self.smsText, self.senderId, self.mobilenumber)

        response = self.send_sms_using_provider_api(
            self.api_url,
            post_data=xml_data,
        )
        return response

    def create_xml2(self, xml_params, sms_text, sender_id, mobile_number):
        self.log.info('%s.create_xml :: and xml_params=%s'
                      % (self.sms_provider, xml_params))
        root = Element('request')

        returnxml1 = SubElement(root, 'message')
        returnxml2 = SubElement(root, 'security')

        for param in xml_params:
            key = param[0].strip().upper()
            value = param[1].strip()
            if key == 'login':
                member = SubElement(returnxml2, key)
                member.text = value
            elif key == 'password':
                member = SubElement(returnxml2, key)
                member.text = value
            elif value == '$smsText':
                member = SubElement(returnxml1, key)
                member.text = sms_text
            elif value == '$mobilenumber':
                member = SubElement(returnxml1, key)
                member.text = mobile_number
            elif value == '$sender':
                member = SubElement(returnxml1, key)
                member.text = sender_id
            else:
                member = SubElement(returnxml1, key)
                member.text = value
        created_xml = '<?xml version="1.0"?>%s' % tostring(root)
        self.log.info("Smsclub final XML : %s" % created_xml)
        return created_xml
