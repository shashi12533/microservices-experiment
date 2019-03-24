#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_paginator import EmptyPage, Paginator

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.sms_history import get_sms_history, get_incoming_sms_history
from media_engine.lib.validators import authenticate_account, not_empty
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

logger = get_logger()
crash_log = get_logger('crash')


sms_history_response_format = dict(
    total_pages=fields.Integer,
    page_number=fields.Integer,
    result=fields.List(fields.Nested(
        dict(
            id=fields.String,
            product_id=fields.String,
            mobile_number=fields.String,
            sender_id=fields.String,
            encoding=fields.Integer,
            source=fields.Integer,
            text=fields.String,
            number_of_sms=fields.Integer,
            account_id=fields.Integer,
            formatted_mobile_number=fields.String,
            provider_response_id=fields.String,
            delivery_status=fields.String,
            response_id=fields.String,
            sent_status=fields.String,
            status_message=fields.String,
            service_provider_id=fields.Integer,
            credits=fields.Float,
            currency_code=fields.String,
            resend_on=fields.DateTime,
            created_on=fields.DateTime,
            modified_on=fields.DateTime,
            is_international=fields.Float,
            label=fields.String,
            dr_received_on=fields.DateTime
        ))
    )
)


@not_empty('paginator', 'SMS-HISTORY-NULL-PAGINATOR', req=True, var_type=Paginator)
@not_empty('page_number', 'SMS-HISTORY-BAD-PAGE-NUMBER', req=False, default_val=1, var_type=int)
def transform_sms_page(paginator=None, page_number=None):
    page = paginator.page(page_number)
    return dict(
        total_pages=paginator.total_pages,
        page_number=page.number,
        result=[
            dict(
                id=sms.id,
                product_id=sms.product_id,
                mobile_number=sms.mobile_number,
                sender_id=sms.sender_id,
                encoding=sms.encoding,
                source=sms.source,
                text=sms.text,
                number_of_sms=sms.number_of_sms,
                account_id=sms.account_id,
                formatted_mobile_number=sms.formatted_mobile_number,
                provider_response_id=sms.provider_response_id,
                delivery_status=sms.delivery_status,

                # comes from provider
                response_id=sms.response_id,
                sent_status=sms.sent_status,
                status_message=sms.status_message,

                service_provider_id=sms.service_provider_id,
                credits=sms.credits,
                currency_code=sms.currency_code,
                resend_on=sms.resend_on,
                created_on=sms.created_on,
                modified_on=sms.modified_on,
                is_international=sms.is_international,
                label=sms.label,
                dr_received_on=sms.dr_received_on
            ) for sms in page.object_list
        ]
    )


class SmsHistory(Resource):
    method_decorators = [authenticate_account]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'customer_id', type=unicode, required=True, help='SMS-HISTORY-CUSTOMER-ID')
        self.request_parser.add_argument(
            'page_size', type=int, required=False, help='SMS-HISTORY-PAGE-SIZE')
        self.request_parser.add_argument(
            'page_number', type=int, required=False, help='SMS-HISTORY-PAGE-NUMBER')
        # self.request_parser.add_argument(
        #     'product_id', type=unicode, required=False)
        # self.request_parser.add_argument(
        #     'label', type=unicode, required=False)
        # self.request_parser.add_argument(
        #     'start_date', type=unicode, required=False)
        # self.request_parser.add_argument(
        #     'end_date', type=unicode, required=False)

    @marshal_with(sms_history_response_format)
    def get(self):
        """
        @api {get} /v1/sms/history/ SMS history
        @apiVersion 1.0.0
        @apiName sms history
        @apiGroup SMSHistory
        @apiHeader {String} apiKey Api key of onehop-api

        @apiParam {String} customer_id Customer id
        @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK
        {
          "page_number": 1,
          "total_pages": 1,
          "result": [
            {
              "is_international": null,
              "account_id": 1,
              "encoding": 0,
              "text": "",
              "sender_id": "",
              "credits": 0.05,
              "created_on": "Sun, 24 Dec 2016 12:45:56 -0000",
              "dr_received_on": null,
              "mobile_number": "",
              "modified_on": "Thu, 05 Jan 2017 15:03:56 -0000",
              "delivery_status": null,
              "id": "2",
              "resend_on": null,
              "formatted_mobile_number": null,
              "product_id": "bf612db8-91ff-446a-amj2f-2238732eb37b",
              "provider_response_id": "d5f8f8db-af16-4be4-86e8-18bae0568981a",
              "sent_status": "sent",
              "service_provider_id": 0,
              "label": null,
              "source": 0,
              "response_id": null,
              "currency_code": "US",
              "status_message": "sent",
              "number_of_sms": 0
            },
            {
              "is_international": null,
              "account_id": 1,
              "encoding": 0,
              "text": "",
              "sender_id": "",
              "credits": 0.05,
              "created_on": "Sat, 24 Dec 2016 12:45:56 -0000",
              "dr_received_on": null,
              "mobile_number": "",
              "modified_on": "Thu, 05 Jan 2017 15:03:56 -0000",
              "delivery_status": null,
              "id": "2",
              "resend_on": null,
              "formatted_mobile_number": null,
              "product_id": "bf612db8-91ff-446a-a92f-2238732eb37b",
              "provider_response_id": "d5f8f8db-af16-4be4-86e8-18bae056671a",
              "sent_status": "sent",
              "service_provider_id": 0,
              "label": null,
              "source": 0,
              "response_id": null,
              "currency_code": "US",
              "status_message": "sent",
              "number_of_sms": 0
            }
          ]
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
          "message": "Error"
        }

        """

        params = self.request_parser.parse_args()
        logger.debug('params : {}'.format(params))
        page_number = params.pop('page_number', None)

        try:
            paginator = get_sms_history(**params)
            m_session.commit()
            return transform_sms_page(paginator=paginator, page_number=page_number)
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            logger.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            logger.error(nf_err)
            m_session.rollback()
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
        except EmptyPage as emp_page:
            logger.error(emp_page)
            m_session.rollback()
            abort(400, message="BAD-PAGE")


incoming_sms_history_response_format = dict(
    total_pages=fields.Integer,
    page_number=fields.Integer,
    result=fields.List(fields.Nested(
        dict(
            id=fields.String,
            account_id=fields.Integer,
            product_id=fields.String,
            short_code=fields.String,
            keyword=fields.String,
            sub_keyword=fields.String,
            message=fields.String,
            mobile_number=fields.String,
            response=fields.String,
            push_url_status=fields.String,
            push_url_response=fields.String,
            incoming_provider_id=fields.String,
            created_on=fields.DateTime,
            modified_on=fields.DateTime,
        ))
    )
)


@not_empty('paginator', 'SMS-HISTORY-NULL-PAGINATOR', req=True, var_type=Paginator)
@not_empty('page_number', 'SMS-HISTORY-BAD-PAGE-NUMBER', req=False, default_val=1, var_type=int)
def transform_incoming_sms_page(paginator=None, page_number=None):
    page = paginator.page(page_number)
    return dict(
        total_pages=paginator.total_pages,
        page_number=page.number,
        result=[
            dict(

                id=incoming_sms.id,
                account_id=incoming_sms.account_id,
                product_id=incoming_sms.product_id,
                short_code=incoming_sms.short_code,
                keyword=incoming_sms.keyword,
                sub_keyword=incoming_sms.sub_keyword,
                message=incoming_sms.message,
                mobile_number=incoming_sms.mobile_number,
                response=incoming_sms.response,
                push_url_status=incoming_sms.push_url_status,
                push_url_response=incoming_sms.push_url_response,
                incoming_provider_id=incoming_sms.incoming_provider_id,
                created_on=incoming_sms.created_on,
                modified_on=incoming_sms.modified_on,
            ) for incoming_sms in page.object_list
        ]
    )


class IncomingSmsHistory(Resource):
    method_decorators = [authenticate_account]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'customer_id', type=unicode, required=True, help='INCOMING-SMS-HISTORY-CUSTOMER-ID')
        self.request_parser.add_argument(
            'page_size', type=int, required=False, help='INCOMING-SMS-HISTORY-PAGE-SIZE')
        self.request_parser.add_argument(
            'page_number', type=int, required=False, help='INCOMING-SMS-HISTORY-PAGE-NUMBER')

    @marshal_with(incoming_sms_history_response_format)
    def get(self):
        """
        @api {get} /v1/sms/incoming/history/ SMS history
        @apiVersion 1.0.0
        @apiName sms history
        @apiGroup SMSHistory
        @apiHeader {String} apiKey Api key of onehop-api

        @apiParam {String} customer_id Customer id
        @apiparam {String} page_size Page Size

        @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK

        {
          "page_number": 1,
          "total_pages": 1,
          "result": [
            {
              "push_url_status": "0",
              "product_id": null,
              "keyword": null,
              "short_code": null,
              "push_url_response": null,
              "response": null,
              "created_on": null,
              "sub_keyword": null,
              "mobile_number": null,
              "modified_on": "Thu, 16 Feb 2017 07:29:38 -0000",
              "incoming_provider_id": "",
              "message": null,
              "id": "2",
              "account_id": 5
            }
          ]
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
          "message": "Error Message"
        }

        """

        params = self.request_parser.parse_args()
        logger.debug('params : {}'.format(params))
        page_number = params.pop('page_number', None)

        try:
            paginator = get_incoming_sms_history(**params)
            m_session.commit()
            return transform_incoming_sms_page(paginator=paginator, page_number=page_number)
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            logger.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            logger.error(nf_err)
            m_session.rollback()
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
        except EmptyPage as emp_page:
            logger.error(emp_page)
            m_session.rollback()
            abort(400, message="BAD-PAGE")
