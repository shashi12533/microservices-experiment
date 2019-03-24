#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import reqparse, fields, marshal_with
from media_engine.helper import get_logger
from media_engine.lib.accounting import get_account_id_by_customer_id
from media_engine.lib.inventory import get_inventory, save_incoming_url, save_delivery_ack_url
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.utils.resource_exceptions import handle_exceptions

log = get_logger()
crash_log = get_logger('crash')

inventory_response_format = dict(
    product_id=fields.String,
    incoming_url=fields.String,
    delivery_report_url=fields.String,
    acknowledgement_url=fields.String
)

get_inventory_request_parser = reqparse.RequestParser()
get_inventory_request_parser.add_argument('customer_id', type=unicode, required=True, help='API-KEY-REQ-CUSTOMER-ID')
get_inventory_request_parser.add_argument('product_id', type=unicode, required=True, help='LABEL-REQ-PRODUCT-ID')

save_inventory_request_parser = get_inventory_request_parser.copy()
save_inventory_request_parser.add_argument('incoming_url', type=unicode, required=False, help='LABEL-REQ-INCOMING_URL')
save_inventory_request_parser.add_argument('delivery_report_url', type=unicode, required=False,
                                           help='LABEL-REQ-DELIVERY_REPORT_URL')
save_inventory_request_parser.add_argument('acknowledgement_url', type=unicode, required=False,
                                           help='LABEL-REQ-ACKNOWLEDGEMENT_URL')


class Inventory(Resource):
    method_decorators = [handle_exceptions(), authenticate_account]

    @marshal_with(inventory_response_format)
    def get(self):
        """
        @api {get} /v1/inventory/ Get Incoming, Delivery report and Acknowledgment url
        @apiVersion 1.0.0
        @apiName get inventory
        @apiGroup Inventory

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id customer id
        @apiParam {String} product_id Product id

        @apiSuccess {String}  message
        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 201 OK
        {
            "product_id":"some_product",
            "delivery_report_url":"some_url",
            "incoming_url":"some_url",
            "acknowledgment_url": "some_url"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {"message": "error message string"}

        """
        params = get_inventory_request_parser.parse_args()
        log.debug('params : {}'.format(params))
        inventory_dict = get_inventory(**params)
        m_session.commit()
        return inventory_dict

    @marshal_with(inventory_response_format)
    def post(self):
        """
        @api {post} /v1/inventory/ Set Incoming, Delivery report and Acknowledgment url
        @apiVersion 1.0.0
        @apiName Set inventory
        @apiGroup Inventory

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id customer id
        @apiParam {String} product_id Product id
        @apiParam {String} [incoming_url] Incoming URL

        @apiSuccess {String}  message
        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 201 OK
        {
            "product_id":"some_product",
            "delivery_report_url":"some_url",
            "incoming_url":"some_url",
            "acknowledgment_url": "some_url"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {"message": "error" }

        """
        params = save_inventory_request_parser.parse_args()
        log.error('params : {}'.format(params))
        account_id = get_account_id_by_customer_id(customer_id=params['customer_id'])
        params.update(dict(account_id=account_id))
        incoming_obj = save_incoming_url(**params)
        account_info_obj = save_delivery_ack_url(**params)
        m_session.commit()
        return dict(
            product_id=params['product_id'],
            delivery_report_url=account_info_obj.delivery_report_url,
            incoming_url=incoming_obj.push_to_url,
            acknowledgment_url=account_info_obj.incoming_url
        )
