#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Base class for SMS Providers"""

import requests
from requests.exceptions import Timeout, TooManyRedirects, ConnectionError, RequestException

from media_engine.config import get_config
from media_engine.lib.errors import ProviderError
from media_engine.helper import get_worker_logger

config = get_config()
logger = get_worker_logger('worker')


class Provider(object):
    """Base class for SMS Providers"""
    session = requests.session()
    session.mount(
        "http://", requests.adapters.HTTPAdapter(max_retries=config.max_retry_limit))
    session.mount(
        "https://", requests.adapters.HTTPAdapter(max_retries=config.max_retry_limit))

    def __init__(self, provider_id, api_url, params):
        self.sms_provider = self.__class__.__name__
        self.id = provider_id
        self.api_url = api_url
        self.params = params
        self.log = logger
        self.response = None
        self.encoding = None
        self.mms_api_url = None
        self.query_string = None
        self.mobilenumber = None
        logger.info('In constructor of {}'.format(self.sms_provider))

    def send_sms(self, **kwargs):
        """Prepare SMS for provider"""
        logger.info('In {}.send_sms'.format(self.__class__.__name__))
        logger.debug('kwargs = {}'.format(kwargs))
        map(lambda item: setattr(self, item[0], item[1]), kwargs.items())
        self.query_string = self.get_query_string()

    def handle_response(self, response):
        """Handle response from provider"""
        logger.info('{}.handle_response :: response = {}'.format(
            self.sms_provider, response))
        return response.strip()\
            if response or isinstance(response, basestring) else None

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
        logger.info(
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
            logger.error('Timeout Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Timeout Exception")
        except ConnectionError as exc:
            logger.error('ConnectionError Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Connection Timeout Exception")
        except TooManyRedirects as exc:
            # Tell the user their URL was bad and try a different one
            logger.error('TooManyRedirects Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Too Many Redirects Exception")
        except RequestException as exc:
            # catastrophic error. bail.
            logger.error('RequestException in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise ProviderError("Provider: Request Exception")
        except Exception as exc:
            logger.error('Exception in {}.send_sms :: '
                         '{}'.format(self.sms_provider, exc))
            raise
        else:
            response = self.handle_response(response.text)
        logger.info('{} response = {}'.format(self.sms_provider, response))
        return response

    def get_query_string(self):
        query_string = {}
        keys = ('paramName', 'paramValue', 'runTimeValue', 'encoding',
                'InQueryString', 'isMMSParam')
        params_list = (dict(zip(keys, param_tuple))
                        for param_tuple in self.params)
        for param in params_list:
            cond1 = int(param.get('InQueryString', 0)) == 0
            cond2 = int(param.get('isMMSParam', 0))
            if cond1 or cond2:
                continue
            key = param.get('paramName').strip()
            value = param.get('paramValue').strip()
            if param.get('runTimeValue') == 1:
                try:
                    value = getattr(self, value[1:])
                except NameError as err:
                    logger.info('get_query_string error :: {0}'.format(err))

            if isinstance(value, int):
                logger.info('key: {0} value: {1}'.format(key, value))
                value = str(value)

            try:
                value = value.decode('ascii')

            except:
                value = value.encode('utf-8')
            query_string[key] = value
        logger.info('query_string : {}'.format(query_string))
        return query_string
