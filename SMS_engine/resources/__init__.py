#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_cors import CORS
from flask_restful import Api

from media_engine.resources.accounts import Account
from media_engine.resources.api_key import Apikey
from media_engine.resources.customer import CustomerCredits, CustomerApikey
from media_engine.resources.customer_labels import CustomerLabelList
from media_engine.resources.credits import Balance, ProductCredits
from media_engine.resources.incoming import IncomingSMSHandler, IncomingConfig
from media_engine.resources.inventory import Inventory
from media_engine.resources.labels import LabelDetails
from media_engine.resources.send_sms import SendSms, SendSmsBulk
from media_engine.resources.sms_history import SmsHistory, IncomingSmsHistory
from media_engine.resources.stats import Stats
from media_engine.resources.sms_status import SmsStatus
from media_engine.resources.providers import Providers, ProviderParams, ProvidersConfig
from media_engine.resources.incoming_providers import IncomingProviders, IncomingProviderParams
from media_engine.resources.countries import Countries
from media_engine.resources.retry_sms import RetrySms
from media_engine.resources.default_product import DefaultProduct
from media_engine.resources.customer_details import CustomerDetails
from media_engine.resources.get_status import GetStatus


def create_restful_api(app):
    api = Api(app)

    CORS(app, resources={r"*": {"origins": "*"}})

    api.add_resource(Account, '/v1/accounts')

    api.add_resource(Apikey, '/v1/api_key/generate')
    api.add_resource(Balance, '/v1/save/credits', endpoint='save credits')
    api.add_resource(Balance, '/v1/customer/<string:customer_id>/product/<string:product_id>/credits',
                     endpoint='get credits')
    api.add_resource(ProductCredits, '/v1/customer/<string:customer_id>/products', endpoint='get credits for user products')
    api.add_resource(LabelDetails, '/v1/customer/<string:customer_id>/label_details', endpoint='get labels for customer')
    api.add_resource(LabelDetails, '/v1/customer/<string:customer_id>/label/<string:label_id>', endpoint='delete label')
    api.add_resource(LabelDetails, '/v1/label/save', endpoint='save a label for customer')
    api.add_resource(LabelDetails, '/v1/label/update', endpoint='update a label for customer')

    api.add_resource(SmsHistory, '/v1/sms/history')
    api.add_resource(IncomingSmsHistory, '/v1/sms/incoming/history')
    api.add_resource(Stats, '/v1/stats')

    api.add_resource(Inventory, '/v1/inventory')

    # Public
    api.add_resource(CustomerApikey, '/v1/api_key/validate/')
    api.add_resource(CustomerCredits, '/v1/credits/')
    api.add_resource(SendSms, '/v1/sms/send/', endpoint='send sms old')
    api.add_resource(SendSms, '/v1/sms/send/x/', endpoint='send sms new')
    api.add_resource(SendSmsBulk, '/v1/sms/send/bulk', endpoint='send sms bulk')
    api.add_resource(CustomerLabelList, '/v1/labels/', endpoint='label old')
    api.add_resource(CustomerLabelList, '/v1/labels/x/', endpoint='label new')
    api.add_resource(SmsStatus, '/v1/sms/status', endpoint='sms status')


    #Other_calls
    api.add_resource(IncomingSMSHandler, '/v1/incoming/<string:provider_name>',
                     endpoint='Handles Incoming SMS')

    api.add_resource(IncomingConfig, '/v1/customer/<string:customer_id>/product/<string:product_id>/incoming/',
                 endpoint='get incoming config')
    api.add_resource(Providers, '/v1/providers', endpoint='save a service provider')
    api.add_resource(ProviderParams, '/v1/provider_params', endpoint='save provider params ')
    api.add_resource(IncomingProviders, '/v1/incoming_provider', endpoint='save incoming provider')
    api.add_resource(IncomingProviderParams, '/v1/incoming_provider_param', endpoint='save incoming provider param')
    api.add_resource(Countries, '/v1/countries', endpoint='save country')
    #api.add_resource(Countries, '/v1/default_product', endpoint='save country')
    api.add_resource(RetrySms,'/v1/repushsms', endpoint="retry/repush failed incomming message")
    api.add_resource(DefaultProduct,'/v1/default_product', endpoint='default product')
    api.add_resource(CustomerDetails,'/v1/customer_details', endpoint='customer details')
    api.add_resource(GetStatus,'/v1/get_status', endpoint='get status')
    api.add_resource(ProvidersConfig, '/v1/providers_config', endpoint='save a service provider config')

