#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from media_engine.provider import Provider
from requests.exceptions import Timeout, TooManyRedirects, ConnectionError, RequestException
from media_engine.config import get_config
from media_engine.lib.errors import ProviderError
from media_engine.helper import generate_unique_api_key_hex
from xml.etree.ElementTree import Element, SubElement, tostring

config = get_config()


class Cmtelecom(Provider):

    def handle_response(self, response):
        self.log.info("Response from CM Telecom : {}".format(response))
        self.log.info("response.text: {}".format(response.text))
        try:
            if response.status_code == 200 and response.text == '':
                response = 'success', self.mobilenumber, self.message_tag
            else:
                response = 'error', self.mobilenumber, response.text, self.message_tag

        except Exception as exc:
            response = 'error', self.mobilenumber, exc.message

        self.log.info('Cmtelecom.handle_response.response : {}'.format(response))
        return response

    def send_sms(self, **kwargs):
        super(Cmtelecom, self).send_sms(**kwargs)
        self.message_tag = generate_unique_api_key_hex()
        mobilenumber = '00' + self.mobilenumber
        self.log.info("Mobile Number : %s " % mobilenumber)
        xml_data = self.create_xml2(
            self.params, self.smsText, self.senderId, mobilenumber, self.message_tag)
        headers = {'Content-type': 'application/xml'}
        response = self.send_sms_using_provider_api(
            self.api_url[:-1], post_data=xml_data.encode('utf-8'), headers=headers)

        self.log.info('send_sms.response = {}'.format(response))

        return response

    def create_xml2(self, xml_params, sms_text_updated, sender_id, mobile_number, message_tag):
        self.log.info('%s.create_xml :: and xml_params=%s'
                      % (self.sms_provider, xml_params))
        # <methodCall/>
        root = Element('MESSAGES')
        # <methodCall><methodName /><methodCall />

        returnxml1 = SubElement(root, 'AUTHENTICATION')
        # <methodCall><methodName>EAPIGateway.SendSMS</methodName>
        # <params><param /></params><methodCall />
        returnxml2 = SubElement(root, 'MSG')
        # <methodCall><methodName>EAPIGateway.SendSMS</methodName>
        # <params><param></value><param /></params><methodCall />

        for param in xml_params:
            key = param[0].strip().upper()
            value = param[1].strip()

            if key == 'SIGNATURE':
                sms_text_updated = '【' + value + '】' + sms_text_updated

            if key == 'CUSTOMGROUPING':
                if value == 'Marketing':
                    sms_text_updated = sms_text_updated + " 回T退订"

        self.smsText = sms_text_updated

        for param in xml_params:
            key = param[0].strip().upper()
            value = param[1].strip()
            if key == 'SIGNATURE' or key == 'CUSTOMGROUPING':
                continue
            elif key == 'PRODUCTTOKEN':
                member = SubElement(returnxml1, 'PRODUCTTOKEN')
                member.text = value
            elif value == '$smsText':
                member = SubElement(returnxml2, key)
                member.text = sms_text_updated
            elif value == '$mobilenumber':
                member = SubElement(returnxml2, key)
                member.text = mobile_number
            elif value == '$messageTag':
                member = SubElement(returnxml2, key)
                member.text = message_tag
            elif value == '$senderId':
                member = SubElement(returnxml2, key)
                member.text = sender_id

            else:
                member = SubElement(returnxml2, key)
                member.text = value
        created_xml = '<?xml version="1.0"?>%s' % tostring(root)
        self.log.info("CM Telecom's final XML : %s" % created_xml)
        return created_xml

    def send_sms_using_provider_api(
            self,
            url,
            post_data=None,
            headers=None,
            extra_params=None,
            verify=False,
            auth=None,
            timeout=(config.connect_timeout, config.read_timeout)):
        """
        Make the api call for sending an SMS and return a custom response
        :param url: The api url of an sms provider
        :param post_data: The post request data
        :param headers: headers if any
        :param extra_params: extra params if any
        :param verify: verify SSL certificates for HTTPS requests if True
        :param auth: (username, password) tuple for HTTPBasicAuthentication
        :param timeout: (connect timeout, read timeout) tuple
        """
        self.log.info(
            '{}.send_sms_using_provider_api :: url={}, post_data={} '
            'headers={} and auth={}'.format(
                self.sms_provider, url, post_data, headers, auth)
        )

        params = {
            'data': post_data,
            'headers': headers,
            'auth': auth,
            'timeout': timeout,
            'verify': verify,
        }
        if extra_params:
            params.update(extra_params)

        session = self.session
        try:
            response = session.request(
                method='POST' if post_data else 'GET',
                url=url,
                **params
            )
        except Timeout as exc:
            # Maybe set up for a retry, or continue in a retry loop
            self.log.error('Timeout Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Timeout Exception")
        except ConnectionError as exc:
            self.log.error('ConnectionError Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Connection Timeout Exception")
        except TooManyRedirects as exc:
            # Tell the user their URL was bad and try a different one
            self.log.error('TooManyRedirects Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Too Many Redirects Exception")
        except RequestException as exc:
            # catastrophic error. bail.
            self.log.error('RequestException in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Request Exception")
        except Exception as exc:
            self.log.error('Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise
        else:
            response = self.handle_response(response)
        self.log.info('{} response = {}'.format(self.sms_provider, response))
        return response
